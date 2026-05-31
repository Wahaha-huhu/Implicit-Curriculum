from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
from torch import nn

from ic_experiments.backends.sequence_dsl import (
    CausalTransformerLM,
    SequenceDSLConfig,
    load_sequence_family,
    make_lm_batch,
)
from ic_experiments.run_management import append_registry, write_manifest


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run B1 mediator diagnostics for H3 component-composite pairs.")
    p.add_argument("--output-dir", type=Path, default=Path("results/b1_mediator_diagnostics"))
    p.add_argument("--structure-table", type=Path, required=True)
    p.add_argument("--row-dirs", type=Path, nargs="*", default=[], help="H3 result directories containing h3_pair_config.csv.")
    p.add_argument("--pair-configs", type=Path, nargs="*", default=[], help="Explicit h3_pair_config.csv files.")
    p.add_argument("--component", type=str, default=None)
    p.add_argument("--composite", type=str, default=None)
    p.add_argument("--same-operation-control", type=str, default=None)
    p.add_argument("--different-operation-control", type=str, default=None)
    p.add_argument("--fake-component-control", type=str, default=None)
    p.add_argument("--surface-control", type=str, default=None)
    p.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    p.add_argument("--max-data-seen", type=int, default=120_000)
    p.add_argument("--batch-size", type=int, default=256)
    p.add_argument("--learning-rate", type=float, default=5e-4)
    p.add_argument("--weight-decay", type=float, default=0.1)
    p.add_argument("--warmup-frac", type=float, default=0.05)
    p.add_argument("--probe-fractions", type=float, nargs="+", default=[0.0, 0.05, 0.10, 0.20, 0.40, 1.0])
    p.add_argument("--probe-examples", type=int, default=128)
    p.add_argument("--probe-microbatch", type=int, default=32)
    p.add_argument("--eval-examples-per-task", type=int, default=256)
    p.add_argument("--d-model", type=int, default=128)
    p.add_argument("--n-layers", type=int, default=2)
    p.add_argument("--n-heads", type=int, default=4)
    p.add_argument("--d-mlp", type=int, default=512)
    p.add_argument("--dropout", type=float, default=0.0)
    p.add_argument("--vocab-content", type=int, default=32)
    p.add_argument("--input-len", type=int, default=6)
    p.add_argument("--param-subset", type=str, default="last_block_ln_head", choices=["head_only", "ln_head", "last_block_ln_head", "all"])
    p.add_argument("--device", type=str, default="cpu")
    p.add_argument("--code-version", type=str, default="v1.8")
    p.add_argument("--run-id", type=str, default=None)
    p.add_argument("--archive-root", type=Path, default=None)
    p.add_argument("--thesis-use", type=str, default="candidate")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    try:
        torch.set_num_threads(1)
    except RuntimeError:
        pass
    output = args.output_dir
    output.mkdir(parents=True, exist_ok=True)

    cfg = SequenceDSLConfig(vocab_content=args.vocab_content, input_len=args.input_len)
    family = load_sequence_family(args.structure_table, cfg)
    structure = family.structure_table()
    pairs = resolve_pairs(args)
    validate_pairs(pairs, {t.structure_id for t in family.tasks})
    pairs_df = pd.DataFrame(pairs)
    pairs_df.to_csv(output / "mediator_pair_config.csv", index=False)
    structure.to_csv(output / "structure_table.csv", index=False)

    probe_points = sorted(set(int(round(float(f) * args.max_data_seen)) for f in args.probe_fractions))
    probe_points = [min(args.max_data_seen, max(0, p)) for p in probe_points]
    probe_points = sorted(set(probe_points + [args.max_data_seen]))

    task_rows: list[dict[str, Any]] = []
    pair_rows: list[dict[str, Any]] = []
    eval_rows: list[dict[str, Any]] = []

    for seed in args.seeds:
        print(f"[B1 mediator] seed={seed} probe_points={probe_points}")
        tr, pr, er = train_and_probe_one_seed(family, cfg, args, seed, probe_points, pairs)
        task_rows.extend(tr)
        pair_rows.extend(pr)
        eval_rows.extend(er)

    task_df = pd.DataFrame(task_rows)
    pair_df = pd.DataFrame(pair_rows)
    eval_df = pd.DataFrame(eval_rows)
    task_df.to_csv(output / "mediator_task_stats.csv", index=False)
    pair_df.to_csv(output / "mediator_pair_stats.csv", index=False)
    eval_df.to_csv(output / "mediator_eval_curves.csv", index=False)
    pd.DataFrame(
        [{"probe_data_seen": p, "checkpoint_fraction": p / max(1, args.max_data_seen)} for p in probe_points]
    ).to_csv(output / "mediator_checkpoint_table.csv", index=False)

    (output / "mediator_run_report.md").write_text(render_run_report(args, pairs, task_df, pair_df), encoding="utf-8")
    (output / "summary.json").write_text(
        json.dumps(
            {
                "backend": "B1_sequence_dsl",
                "experiment": "B1_mediator_diagnostics",
                "pairs": pairs,
                "seeds": args.seeds,
                "probe_fractions": args.probe_fractions,
                "param_subset": args.param_subset,
                "paths": {
                    "task_stats": str(output / "mediator_task_stats.csv"),
                    "pair_stats": str(output / "mediator_pair_stats.csv"),
                    "eval_curves": str(output / "mediator_eval_curves.csv"),
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    manifest = write_manifest(
        output,
        experiment="B1_mediator_diagnostics",
        backend="B1_sequence_dsl",
        code_version=args.code_version,
        run_id=args.run_id or "b1_mediator_diagnostics",
        command=sys.argv,
        input_paths={
            "structure_table": str(args.structure_table),
            "row_dirs": ";".join(str(p) for p in args.row_dirs),
            "pair_configs": ";".join(str(p) for p in args.pair_configs),
        },
        extra={"pairs": pairs, "thesis_use": args.thesis_use, "param_subset": args.param_subset},
    )
    if args.archive_root is not None:
        append_registry(
            args.archive_root / "results_registry.csv",
            {
                "run_id": manifest["run_id"],
                "code_version": args.code_version,
                "git_sha": manifest["git_sha"],
                "experiment": manifest["experiment"],
                "backend": manifest["backend"],
                "output_path": str(output),
                "status": "analyzed",
                "thesis_use": args.thesis_use,
                "created_at_utc": manifest["created_at_utc"],
            },
        )

    print("Saved B1 mediator diagnostics outputs:")
    for name in ["mediator_run_report.md", "mediator_task_stats.csv", "mediator_pair_stats.csv", "mediator_eval_curves.csv", "mediator_pair_config.csv", "run_manifest.json"]:
        print(f"  {output / name}")


def resolve_pairs(args: argparse.Namespace) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for rd in args.row_dirs:
        cfg_path = rd / "h3_pair_config.csv"
        if cfg_path.exists():
            rows.extend(pd.read_csv(cfg_path).to_dict(orient="records"))
    for pc in args.pair_configs:
        if pc.exists():
            rows.extend(pd.read_csv(pc).to_dict(orient="records"))
    if args.component and args.composite:
        rows.append(
            {
                "component": args.component,
                "composite": args.composite,
                "same_operation_control": args.same_operation_control or "",
                "different_operation_control": args.different_operation_control or "",
                "fake_component_control": args.fake_component_control or "",
                "surface_control": args.surface_control or "",
                "unrelated_control": args.same_operation_control or "",
            }
        )
    out: list[dict[str, str]] = []
    seen = set()
    for r in rows:
        d = {k: str(r.get(k, "")) for k in ["component", "composite", "same_operation_control", "different_operation_control", "fake_component_control", "surface_control", "unrelated_control"]}
        if not d["same_operation_control"] and d.get("unrelated_control"):
            d["same_operation_control"] = d["unrelated_control"]
        key = (d["component"], d["composite"])
        if key[0] and key[1] and key not in seen:
            seen.add(key)
            out.append(d)
    if not out:
        raise ValueError("No mediator pairs resolved. Provide --row-dirs, --pair-configs, or --component/--composite.")
    return out


def validate_pairs(pairs: list[dict[str, str]], task_names: set[str]) -> None:
    for p in pairs:
        required = ["component", "composite"]
        missing = [k for k in required if not p.get(k)]
        if missing:
            raise ValueError(f"Missing required pair fields {missing}: {p}")
        unknown = {k: v for k, v in p.items() if v and v not in task_names}
        if unknown:
            raise ValueError(f"Unknown task names in pair config: {unknown}")


def train_and_probe_one_seed(family, cfg: SequenceDSLConfig, args: argparse.Namespace, seed: int, probe_points: list[int], pairs: list[dict[str, str]]):
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    device = torch.device(args.device)
    model = CausalTransformerLM(
        vocab_size=cfg.vocab_size,
        max_seq_len=1 + cfg.input_len + 1 + cfg.input_len,
        d_model=args.d_model,
        n_layers=args.n_layers,
        n_heads=args.n_heads,
        d_mlp=args.d_mlp,
        dropout=args.dropout,
    ).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.learning_rate, weight_decay=args.weight_decay, betas=(0.9, 0.98))
    criterion = nn.CrossEntropyLoss(ignore_index=-100)
    weights = torch.tensor([t.frequency for t in family.tasks], dtype=torch.float32, device=device)
    weights = weights / weights.sum()

    task_index = {t.structure_id: i for i, t in enumerate(family.tasks)}
    probe_task_names = sorted({x for p in pairs for x in pair_task_names(p) if x})
    probe_task_names = [t for t in probe_task_names if t in task_index]

    task_rows: list[dict[str, Any]] = []
    pair_rows: list[dict[str, Any]] = []
    eval_rows: list[dict[str, Any]] = []

    data_seen = 0
    next_probe_idx = 0
    # Probe initial model.
    tr, pr, er = probe_model(model, family, cfg, args, seed, data_seen, pairs, probe_task_names, criterion, device)
    task_rows.extend(tr); pair_rows.extend(pr); eval_rows.extend(er)
    next_probe_idx = 1 if probe_points and probe_points[0] == 0 else 0

    while data_seen < args.max_data_seen:
        tokens, labels, _ = make_lm_batch(family.tasks, cfg, args.batch_size, device, weights)
        opt.zero_grad(set_to_none=True)
        logits = model(tokens)
        loss = criterion(logits.reshape(-1, logits.size(-1)), labels.reshape(-1))
        loss.backward()
        opt.step()
        data_seen += args.batch_size
        lr_scale = min(1.0, max(0.05, data_seen / max(1, int(args.max_data_seen * args.warmup_frac))))
        for group in opt.param_groups:
            group["lr"] = args.learning_rate * lr_scale
        while next_probe_idx < len(probe_points) and data_seen >= probe_points[next_probe_idx]:
            tr, pr, er = probe_model(model, family, cfg, args, seed, data_seen, pairs, probe_task_names, criterion, device)
            task_rows.extend(tr); pair_rows.extend(pr); eval_rows.extend(er)
            next_probe_idx += 1
    return task_rows, pair_rows, eval_rows


def pair_task_names(pair: dict[str, str]) -> list[str]:
    return [
        pair.get("component", ""),
        pair.get("composite", ""),
        pair.get("same_operation_control", ""),
        pair.get("different_operation_control", ""),
        pair.get("fake_component_control", ""),
        pair.get("surface_control", ""),
    ]


def probe_model(model, family, cfg, args, seed: int, data_seen: int, pairs: list[dict[str, str]], probe_task_names: list[str], criterion, device):
    model.eval()
    params = select_params(model, args.param_subset)
    tasks_by_name = {t.structure_id: i for i, t in enumerate(family.tasks)}
    task_stats: dict[str, dict[str, Any]] = {}
    reps: dict[str, torch.Tensor] = {}
    eval_rows: list[dict[str, Any]] = []
    for name in probe_task_names:
        idx = tasks_by_name[name]
        tokens, labels = fixed_task_batch(family, cfg, idx, args.probe_examples, device, seed=stable_seed(seed, name))
        grad_rows, grad_mean = gradient_stats_for_task(model, tokens, labels, criterion, params, args.probe_microbatch)
        rep = representation_for_task(model, tokens, labels)
        reps[name] = rep.detach().cpu()
        row = {
            "seed": seed,
            "data_seen": data_seen,
            "checkpoint_fraction": data_seen / max(1, args.max_data_seen),
            "task_name": name,
            "gradient_norm": grad_rows["gradient_norm"],
            "gradient_noise_rms": grad_rows["gradient_noise_rms"],
            "gradient_snr": grad_rows["gradient_snr"],
            "within_gradient_alignment": grad_rows["within_gradient_alignment"],
            "param_subset": args.param_subset,
        }
        task_stats[name] = {**row, "grad_mean": grad_mean.detach().cpu()}
        eval_rows.append(eval_existing_probe_batch(model, tokens, labels, name, data_seen, seed, args.max_data_seen))
    pair_rows: list[dict[str, Any]] = []
    for pair_id, pair in enumerate(pairs):
        composite = pair["composite"]
        for role, task_name in [
            ("exact_component", pair.get("component", "")),
            ("same_operation_control", pair.get("same_operation_control", "")),
            ("different_operation_control", pair.get("different_operation_control", "")),
            ("fake_component_control", pair.get("fake_component_control", "")),
            ("surface_control", pair.get("surface_control", "")),
        ]:
            if not task_name or task_name not in task_stats or composite not in task_stats:
                continue
            g1 = task_stats[task_name]["grad_mean"]
            g2 = task_stats[composite]["grad_mean"]
            pair_rows.append(
                {
                    "pair_id": pair_id,
                    "component": pair.get("component", ""),
                    "composite": composite,
                    "source_role": role,
                    "source_task": task_name,
                    "target_task": composite,
                    "seed": seed,
                    "data_seen": data_seen,
                    "checkpoint_fraction": data_seen / max(1, args.max_data_seen),
                    "gradient_cosine": cosine(g1, g2),
                    "source_gradient_norm": float(g1.norm().item()),
                    "target_gradient_norm": float(g2.norm().item()),
                    "linear_cka": linear_cka(reps[task_name], reps[composite]),
                    "param_subset": args.param_subset,
                }
            )
    # Remove non-serializable grad means.
    rows = []
    for v in task_stats.values():
        d = dict(v)
        d.pop("grad_mean", None)
        rows.append(d)
    model.train()
    return rows, pair_rows, eval_rows


def fixed_task_batch(family, cfg, task_idx: int, n: int, device: torch.device, seed: int):
    weights = torch.zeros(len(family.tasks), dtype=torch.float32, device=device)
    weights[task_idx] = 1.0
    devices = [device] if device.type == "cuda" else []
    with torch.random.fork_rng(devices=devices):
        torch.manual_seed(int(seed))
        if device.type == "cuda":
            torch.cuda.manual_seed_all(int(seed))
        tokens, labels, _ = make_lm_batch(family.tasks, cfg, n, device, weights)
    return tokens, labels


def stable_seed(seed: int, name: str) -> int:
    return int((abs(hash(name)) + 1009 * int(seed)) % (2**31 - 1))


def select_params(model: nn.Module, subset: str) -> list[nn.Parameter]:
    if subset == "all":
        return [p for p in model.parameters() if p.requires_grad]
    params: list[nn.Parameter] = []
    if subset in {"last_block_ln_head", "ln_head"}:
        if subset == "last_block_ln_head" and hasattr(model.blocks, "layers"):
            params.extend([p for p in model.blocks.layers[-1].parameters() if p.requires_grad])
        params.extend([p for p in model.ln.parameters() if p.requires_grad])
        params.extend([p for p in model.head.parameters() if p.requires_grad])
    elif subset == "head_only":
        params.extend([p for p in model.head.parameters() if p.requires_grad])
    if not params:
        params = [p for p in model.parameters() if p.requires_grad]
    return params


def flatten_grads(params: list[nn.Parameter]) -> torch.Tensor:
    pieces = []
    for p in params:
        if p.grad is None:
            pieces.append(torch.zeros_like(p, memory_format=torch.preserve_format).reshape(-1))
        else:
            pieces.append(p.grad.detach().reshape(-1))
    return torch.cat(pieces)


def gradient_stats_for_task(model, tokens, labels, criterion, params, microbatch: int) -> tuple[dict[str, float], torch.Tensor]:
    grads = []
    n = tokens.shape[0]
    for start in range(0, n, max(1, microbatch)):
        end = min(n, start + max(1, microbatch))
        model.zero_grad(set_to_none=True)
        logits = model(tokens[start:end])
        loss = criterion(logits.reshape(-1, logits.size(-1)), labels[start:end].reshape(-1))
        loss.backward()
        grads.append(flatten_grads(params).detach())
    model.zero_grad(set_to_none=True)
    G = torch.stack(grads, dim=0)
    mean = G.mean(dim=0)
    centered = G - mean[None, :]
    norm = float(mean.norm().item())
    noise = float(torch.sqrt(torch.mean(torch.sum(centered * centered, dim=1))).item()) if G.shape[0] > 1 else 0.0
    snr = float((mean.norm().item() ** 2) / max(1e-12, torch.mean(torch.sum(centered * centered, dim=1)).item())) if G.shape[0] > 1 else math.inf
    align = mean_pairwise_cosine(G)
    return {"gradient_norm": norm, "gradient_noise_rms": noise, "gradient_snr": snr, "within_gradient_alignment": align}, mean


def representation_for_task(model, tokens, labels) -> torch.Tensor:
    with torch.no_grad():
        _, h = model(tokens, return_hidden=True)
        mask = labels != -100
        rep = h[mask]
        if rep.shape[0] > 2048:
            rep = rep[:2048]
        return rep.float().detach()


def cosine(a: torch.Tensor, b: torch.Tensor) -> float:
    denom = float(a.norm().item() * b.norm().item())
    if denom <= 1e-12:
        return float("nan")
    return float(torch.dot(a.flatten(), b.flatten()).item() / denom)


def mean_pairwise_cosine(G: torch.Tensor) -> float:
    if G.shape[0] < 2:
        return float("nan")
    G = G.float()
    norms = G.norm(dim=1).clamp_min(1e-12)
    Gn = G / norms[:, None]
    sim = Gn @ Gn.T
    mask = ~torch.eye(G.shape[0], dtype=torch.bool, device=G.device)
    return float(sim[mask].mean().item())


def linear_cka(X: torch.Tensor, Y: torch.Tensor) -> float:
    n = min(X.shape[0], Y.shape[0])
    if n < 2:
        return float("nan")
    X = X[:n].float()
    Y = Y[:n].float()
    X = X - X.mean(dim=0, keepdim=True)
    Y = Y - Y.mean(dim=0, keepdim=True)
    xty = X.T @ Y
    num = torch.sum(xty * xty)
    den = torch.sqrt(torch.sum((X.T @ X) ** 2) * torch.sum((Y.T @ Y) ** 2)).clamp_min(1e-12)
    return float((num / den).item())



def eval_existing_probe_batch(model, tokens: torch.Tensor, labels: torch.Tensor, task_name: str, data_seen: int, seed: int, max_data_seen: int) -> dict[str, Any]:
    criterion = nn.CrossEntropyLoss(ignore_index=-100)
    with torch.no_grad():
        logits = model(tokens)
        loss = criterion(logits.reshape(-1, logits.size(-1)), labels.reshape(-1)).item()
        pred = logits.argmax(dim=-1)
        mask = labels != -100
        token_acc = (pred[mask] == labels[mask]).float().mean().item() if mask.any() else float("nan")
        exact = ((pred == labels) | ~mask).all(dim=1).float().mean().item()
    return {
        "condition": "mediator_probe",
        "seed": seed,
        "data_seen": data_seen,
        "checkpoint_fraction": data_seen / max(1, max_data_seen),
        "task_name": task_name,
        "loss": float(loss),
        "token_accuracy": float(token_acc),
        "exact_match": float(exact),
        "balanced_accuracy": float(exact),
        "accuracy": float(exact),
    }

def render_run_report(args: argparse.Namespace, pairs: list[dict[str, str]], task_df: pd.DataFrame, pair_df: pd.DataFrame) -> str:
    lines = [
        "# B1 mediator diagnostics run report",
        "",
        "This run logs leading-indicator gradient and representation diagnostics for selected H3 pairs.",
        "It is mechanistic corroboration only; it does not by itself establish causality.",
        "",
        "## Setup",
        f"- pairs: `{len(pairs)}`",
        f"- seeds: `{', '.join(map(str, args.seeds))}`",
        f"- probe_fractions: `{', '.join(map(str, args.probe_fractions))}`",
        f"- param_subset: `{args.param_subset}`",
        f"- task-stat rows: `{len(task_df)}`",
        f"- pair-stat rows: `{len(pair_df)}`",
        "",
        "## Pairs",
    ]
    for p in pairs:
        lines.append(f"- `{p['component']}` → `{p['composite']}`; same-op=`{p.get('same_operation_control','')}`, diff-op=`{p.get('different_operation_control','')}`")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
