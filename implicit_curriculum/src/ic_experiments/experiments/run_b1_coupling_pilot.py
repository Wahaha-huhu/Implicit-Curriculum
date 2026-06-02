from __future__ import annotations

import argparse
import json
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
    evaluate_sequence_per_task,
    load_sequence_family,
    make_lm_batch,
)
from ic_experiments.coupling import DEFAULT_DOSE_MULTIPLIERS, make_dose_weights, sanitize, trapezoid_auc
from ic_experiments.experiments.run_b1_mediator_diagnostics import (
    cosine,
    fixed_task_batch,
    gradient_stats_for_task,
    linear_cka,
    representation_for_task,
    select_params,
)
from ic_experiments.metrics import acquisition_times
from ic_experiments.run_management import append_registry, write_manifest
from ic_experiments.sequence_analysis import final_metrics, make_checkpoint_table


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run the N1 B1 cross-task coupling pilot.")
    p.add_argument("--output-dir", type=Path, default=Path("results/b1_coupling_pilot"))
    p.add_argument("--structure-table", type=Path, required=True)
    p.add_argument("--pair-plan", type=Path, required=True)
    p.add_argument("--pair-ids", nargs="*", default=None, help="Optional subset of pair_id values to run.")
    p.add_argument("--max-pairs", type=int, default=None, help="Optional first-N pair limit after --pair-ids filtering.")
    p.add_argument("--dose-multipliers", type=float, nargs="+", default=list(DEFAULT_DOSE_MULTIPLIERS))
    p.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    p.add_argument("--max-data-seen", type=int, default=120_000)
    p.add_argument("--batch-size", type=int, default=256)
    p.add_argument("--learning-rate", type=float, default=5e-4)
    p.add_argument("--weight-decay", type=float, default=0.1)
    p.add_argument("--warmup-frac", type=float, default=0.05)
    p.add_argument("--n-checkpoints", type=int, default=60)
    p.add_argument("--eval-examples-per-task", type=int, default=256)
    p.add_argument("--d-model", type=int, default=128)
    p.add_argument("--n-layers", type=int, default=2)
    p.add_argument("--n-heads", type=int, default=4)
    p.add_argument("--d-mlp", type=int, default=512)
    p.add_argument("--dropout", type=float, default=0.0)
    p.add_argument("--vocab-content", type=int, default=32)
    p.add_argument("--input-len", type=int, default=6)
    p.add_argument("--acquisition-threshold", type=float, default=0.70)
    p.add_argument("--acquisition-patience", type=int, default=2)
    p.add_argument("--early-probe-fraction", type=float, default=0.05)
    p.add_argument("--probe-examples", type=int, default=128)
    p.add_argument("--probe-microbatch", type=int, default=32)
    p.add_argument("--param-subset", type=str, default="last_block_ln_head", choices=["head_only", "ln_head", "last_block_ln_head", "all"])
    p.add_argument("--device", type=str, default="cpu")
    p.add_argument("--skip-existing", action="store_true")
    p.add_argument("--code-version", type=str, default="n1.0")
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
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    shard_dir = out / "shards"
    shard_dir.mkdir(exist_ok=True)

    cfg = SequenceDSLConfig(vocab_content=args.vocab_content, input_len=args.input_len)
    family = load_sequence_family(args.structure_table, cfg)
    structure = family.structure_table()
    pair_plan = pd.read_csv(args.pair_plan)
    if args.pair_ids:
        pair_plan = pair_plan[pair_plan["pair_id"].astype(str).isin(set(args.pair_ids))].copy()
    if args.max_pairs is not None:
        pair_plan = pair_plan.head(int(args.max_pairs)).copy()
    validate_pair_plan(pair_plan, {t.structure_id for t in family.tasks})
    pair_plan.to_csv(out / "b1_coupling_pair_plan.csv", index=False)
    structure.to_csv(out / "structure_table.csv", index=False)

    checkpoints = log_checkpoints(args.max_data_seen, args.n_checkpoints)
    early_probe_seen = int(round(args.max_data_seen * float(args.early_probe_fraction)))
    early_probe_seen = max(0, min(args.max_data_seen, early_probe_seen))

    eval_paths: list[Path] = []
    acq_paths: list[Path] = []
    counts_paths: list[Path] = []
    pred_paths: list[Path] = []
    outcome_rows: list[dict[str, Any]] = []
    config_rows: list[dict[str, Any]] = []

    for _, pair in pair_plan.iterrows():
        for multiplier in args.dose_multipliers:
            for seed in args.seeds:
                shard_prefix = f"pair={sanitize(pair['pair_id'])}__source_x{float(multiplier):g}__seed={seed}"
                eval_path = shard_dir / f"{shard_prefix}__eval_curves.csv"
                acq_path = shard_dir / f"{shard_prefix}__acquisition_times.csv"
                counts_path = shard_dir / f"{shard_prefix}__frequency_counts.csv"
                pred_path = shard_dir / f"{shard_prefix}__early_predictors.csv"
                outcome_path = shard_dir / f"{shard_prefix}__target_outcomes.json"
                if args.skip_existing and eval_path.exists() and acq_path.exists() and counts_path.exists() and pred_path.exists() and outcome_path.exists():
                    eval_paths.append(eval_path); acq_paths.append(acq_path); counts_paths.append(counts_path); pred_paths.append(pred_path)
                    outcome_rows.append(json.loads(outcome_path.read_text(encoding="utf-8")))
                    continue
                print(f"[B1 coupling] pair={pair['pair_id']} {pair['source_task']} -> {pair['target_task']} multiplier={multiplier:g} seed={seed}")
                eval_df, acq_df, counts_df, pred_df, outcome, n_params = train_one_dose_condition(
                    family=family,
                    cfg=cfg,
                    args=args,
                    pair=dict(pair),
                    multiplier=float(multiplier),
                    seed=int(seed),
                    checkpoints=checkpoints,
                    early_probe_seen=early_probe_seen,
                )
                eval_df.to_csv(eval_path, index=False)
                acq_df.to_csv(acq_path, index=False)
                counts_df.to_csv(counts_path, index=False)
                pred_df.to_csv(pred_path, index=False)
                outcome_path.write_text(json.dumps(outcome, indent=2), encoding="utf-8")
                eval_paths.append(eval_path); acq_paths.append(acq_path); counts_paths.append(counts_path); pred_paths.append(pred_path)
                outcome_rows.append(outcome)
                config_rows.append(config_row(args, pair, float(multiplier), n_params))

    eval_df = pd.concat([pd.read_csv(p) for p in eval_paths], ignore_index=True) if eval_paths else pd.DataFrame()
    acq_df = pd.concat([pd.read_csv(p) for p in acq_paths], ignore_index=True) if acq_paths else pd.DataFrame()
    counts_df = pd.concat([pd.read_csv(p) for p in counts_paths], ignore_index=True) if counts_paths else pd.DataFrame()
    pred_df = pd.concat([pd.read_csv(p) for p in pred_paths], ignore_index=True) if pred_paths else pd.DataFrame()
    outcomes_df = pd.DataFrame(outcome_rows)

    eval_df.to_csv(out / "eval_curves.csv", index=False)
    acq_df.to_csv(out / "acquisition_times.csv", index=False)
    counts_df.to_csv(out / "frequency_counts.csv", index=False)
    pred_df.to_csv(out / "early_coupling_predictors.csv", index=False)
    outcomes_df.to_csv(out / "target_outcomes.csv", index=False)
    final_metrics(eval_df).to_csv(out / "final_metrics.csv", index=False)
    pd.DataFrame(config_rows).drop_duplicates(["pair_id", "source_multiplier"]).to_csv(out / "config_table.csv", index=False)

    ckpt_tables = []
    for multiplier in args.dose_multipliers:
        condition = f"source_x{float(multiplier):g}"
        ckpt_tables.append(make_checkpoint_table(checkpoints, args.max_data_seen, args.seeds, condition=condition))
    pd.concat(ckpt_tables, ignore_index=True).to_csv(out / "checkpoint_table.csv", index=False)

    (out / "b1_coupling_pilot_run_report.md").write_text(render_run_report(args, pair_plan, outcomes_df, pred_df), encoding="utf-8")
    (out / "summary.json").write_text(
        json.dumps(
            {
                "backend": "B1_sequence_dsl",
                "experiment": "N1_B1_cross_task_coupling_pilot",
                "n_pairs": int(len(pair_plan)),
                "dose_multipliers": [float(x) for x in args.dose_multipliers],
                "seeds": [int(s) for s in args.seeds],
                "early_probe_fraction": float(args.early_probe_fraction),
                "paths": {
                    "pair_plan": str(out / "b1_coupling_pair_plan.csv"),
                    "target_outcomes": str(out / "target_outcomes.csv"),
                    "early_coupling_predictors": str(out / "early_coupling_predictors.csv"),
                    "eval_curves": str(out / "eval_curves.csv"),
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    manifest = write_manifest(
        out,
        experiment="N1_B1_cross_task_coupling_pilot",
        backend="B1_sequence_dsl",
        code_version=args.code_version,
        run_id=args.run_id or "b1_coupling_pilot",
        command=sys.argv,
        input_paths={"structure_table": str(args.structure_table), "pair_plan": str(args.pair_plan)},
        extra={"dose_multipliers": [float(x) for x in args.dose_multipliers], "seeds": args.seeds, "thesis_use": args.thesis_use},
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
                "output_path": str(out),
                "status": "trained",
                "thesis_use": args.thesis_use,
                "created_at_utc": manifest["created_at_utc"],
            },
        )

    print("Saved B1 coupling pilot outputs:")
    for name in ["b1_coupling_pilot_run_report.md", "target_outcomes.csv", "early_coupling_predictors.csv", "eval_curves.csv", "acquisition_times.csv", "run_manifest.json"]:
        print(f"  {out / name}")


def validate_pair_plan(plan: pd.DataFrame, task_names: set[str]) -> None:
    required = ["pair_id", "source_task", "target_task", "filler_task", "pair_type"]
    missing = [c for c in required if c not in plan.columns]
    if missing:
        raise ValueError(f"Pair plan missing required columns: {missing}")
    if plan.empty:
        raise ValueError("Pair plan is empty.")
    unknown = set(plan["source_task"].astype(str)) | set(plan["target_task"].astype(str)) | set(plan["filler_task"].astype(str))
    unknown = {x for x in unknown if x not in task_names}
    if unknown:
        raise ValueError(f"Pair plan contains unknown task names: {sorted(unknown)[:10]}")
    bad = plan[plan["source_task"].astype(str).eq(plan["target_task"].astype(str))]
    if not bad.empty:
        raise ValueError("Pair plan contains source_task == target_task rows.")


def train_one_dose_condition(family, cfg: SequenceDSLConfig, args: argparse.Namespace, pair: dict[str, Any], multiplier: float, seed: int, checkpoints: list[int], early_probe_seen: int):
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
    n_params = sum(p.numel() for p in model.parameters())
    opt = torch.optim.AdamW(model.parameters(), lr=args.learning_rate, weight_decay=args.weight_decay, betas=(0.9, 0.98))
    criterion = nn.CrossEntropyLoss(ignore_index=-100)
    task_index = {t.structure_id: i for i, t in enumerate(family.tasks)}
    source = str(pair["source_task"])
    target = str(pair["target_task"])
    filler = str(pair["filler_task"])
    source_idx = task_index[source]
    target_idx = task_index[target]
    filler_idx = task_index[filler]
    base_weights = torch.tensor([t.frequency for t in family.tasks], dtype=torch.float32, device=device)
    base_weights = base_weights / base_weights.sum().clamp_min(1e-12)
    weights = make_dose_weights(base_weights, source_idx=source_idx, target_idx=target_idx, filler_idx=filler_idx, multiplier=multiplier)
    condition = f"source_x{float(multiplier):g}"

    eval_rows: list[dict[str, Any]] = []
    pred_rows: list[dict[str, Any]] = []
    sample_counts = np.zeros(len(family.tasks), dtype=np.int64)
    data_seen = 0
    ckpt_idx = 0
    probed_initial = False
    probed_early = False

    pred_rows.extend(probe_pair(model, family, cfg, args, pair, multiplier, seed, data_seen, "init", criterion, device))
    probed_initial = True
    eval_rows.extend(add_metadata(evaluate_sequence_per_task(model, family.tasks, cfg, args.eval_examples_per_task, data_seen, condition, seed, device), pair, multiplier, args.max_data_seen))

    while data_seen < args.max_data_seen:
        tokens, labels, task_ids = make_lm_batch(family.tasks, cfg, args.batch_size, device, weights)
        sample_counts += torch.bincount(task_ids.detach().cpu(), minlength=len(family.tasks)).numpy().astype(np.int64)
        opt.zero_grad(set_to_none=True)
        logits = model(tokens)
        loss = criterion(logits.reshape(-1, logits.size(-1)), labels.reshape(-1))
        loss.backward()
        opt.step()
        data_seen += args.batch_size
        lr_scale = min(1.0, max(0.05, data_seen / max(1, int(args.max_data_seen * args.warmup_frac))))
        for group in opt.param_groups:
            group["lr"] = args.learning_rate * lr_scale
        if not probed_early and data_seen >= early_probe_seen:
            pred_rows.extend(probe_pair(model, family, cfg, args, pair, multiplier, seed, data_seen, "early", criterion, device))
            probed_early = True
        while ckpt_idx < len(checkpoints) and data_seen >= checkpoints[ckpt_idx]:
            eval_rows.extend(add_metadata(evaluate_sequence_per_task(model, family.tasks, cfg, args.eval_examples_per_task, data_seen, condition, seed, device), pair, multiplier, args.max_data_seen))
            ckpt_idx += 1
    if not probed_early:
        pred_rows.extend(probe_pair(model, family, cfg, args, pair, multiplier, seed, data_seen, "early", criterion, device))

    eval_df = pd.DataFrame(eval_rows)
    acq_df = acquisition_times(eval_df, threshold=args.acquisition_threshold, patience=args.acquisition_patience, metric="token_accuracy")
    for col, val in pair_identity(pair, multiplier, condition).items():
        acq_df[col] = val
    counts_df = pd.DataFrame([
        {**pair_identity(pair, multiplier, condition), "seed": int(seed), "task_name": task.structure_id, "realized_sample_count": int(count), "realized_fraction": float(count / max(1, int(sample_counts.sum())))}
        for task, count in zip(family.tasks, sample_counts)
    ])
    pred_df = pd.DataFrame(pred_rows)
    outcome = summarize_target_outcome(eval_df, acq_df, pair, multiplier, condition, seed, args.max_data_seen)
    return eval_df, acq_df, counts_df, pred_df, outcome, n_params


def probe_pair(model, family, cfg, args, pair: dict[str, Any], multiplier: float, seed: int, data_seen: int, probe_stage: str, criterion, device: torch.device) -> list[dict[str, Any]]:
    model.eval()
    params = select_params(model, args.param_subset)
    task_index = {t.structure_id: i for i, t in enumerate(family.tasks)}
    source = str(pair["source_task"])
    target = str(pair["target_task"])
    source_tokens, source_labels = fixed_task_batch(family, cfg, task_index[source], args.probe_examples, device, seed=stable_seed(seed, source, probe_stage))
    target_tokens, target_labels = fixed_task_batch(family, cfg, task_index[target], args.probe_examples, device, seed=stable_seed(seed, target, probe_stage))
    source_stats, source_grad = gradient_stats_for_task(model, source_tokens, source_labels, criterion, params, args.probe_microbatch)
    target_stats, target_grad = gradient_stats_for_task(model, target_tokens, target_labels, criterion, params, args.probe_microbatch)
    source_rep = representation_for_task(model, source_tokens, source_labels)
    target_rep = representation_for_task(model, target_tokens, target_labels)
    cos = cosine(source_grad.detach().cpu(), target_grad.detach().cpu())
    inner = float(torch.dot(source_grad.detach().cpu().flatten(), target_grad.detach().cpu().flatten()).item())
    source_norm = float(source_grad.detach().cpu().norm().item())
    target_norm = float(target_grad.detach().cpu().norm().item())
    row = {
        **pair_identity(pair, multiplier, f"source_x{float(multiplier):g}"),
        "seed": int(seed),
        "data_seen": int(data_seen),
        "checkpoint_fraction": float(data_seen) / max(1, int(args.max_data_seen)),
        "probe_stage": probe_stage,
        "param_subset": args.param_subset,
        "gradient_cosine": cos,
        "gradient_inner_product": inner,
        "first_order_transfer_score": float(source_norm * target_norm * cos) if np.isfinite(cos) else float("nan"),
        "source_gradient_norm": source_norm,
        "target_gradient_norm": target_norm,
        "source_gradient_snr": float(source_stats["gradient_snr"]),
        "target_gradient_snr": float(target_stats["gradient_snr"]),
        "source_within_gradient_alignment": float(source_stats["within_gradient_alignment"]),
        "target_within_gradient_alignment": float(target_stats["within_gradient_alignment"]),
        "linear_cka": linear_cka(source_rep, target_rep),
    }
    model.train()
    return [row]


def summarize_target_outcome(eval_df: pd.DataFrame, acq_df: pd.DataFrame, pair: dict[str, Any], multiplier: float, condition: str, seed: int, max_data_seen: int) -> dict[str, Any]:
    target = str(pair["target_task"])
    source = str(pair["source_task"])
    g = eval_df[eval_df["task_name"].astype(str).eq(target)].sort_values("data_seen")
    acq = acq_df[acq_df["task_name"].astype(str).eq(target)]
    acquired_at = float(acq.iloc[0]["acquired_at"]) if not acq.empty and pd.notna(acq.iloc[0]["acquired_at"]) else float("nan")
    return {
        **pair_identity(pair, multiplier, condition),
        "seed": int(seed),
        "source_task": source,
        "target_task": target,
        "target_final_token_accuracy": float(g["token_accuracy"].iloc[-1]) if not g.empty else float("nan"),
        "target_final_exact_match": float(g["exact_match"].iloc[-1]) if not g.empty else float("nan"),
        "target_final_loss": float(g["loss"].iloc[-1]) if not g.empty else float("nan"),
        "target_auc_token_accuracy": trapezoid_auc(g["data_seen"], g["token_accuracy"]) if not g.empty else float("nan"),
        "target_auc_exact_match": trapezoid_auc(g["data_seen"], g["exact_match"]) if not g.empty else float("nan"),
        "target_acquired_at": acquired_at,
        "target_acquired_by_end": bool(np.isfinite(acquired_at)),
        "max_data_seen": int(max_data_seen),
    }


def pair_identity(pair: dict[str, Any], multiplier: float, condition: str) -> dict[str, Any]:
    return {
        "pair_id": str(pair["pair_id"]),
        "pair_index": int(pair.get("pair_index", -1)) if str(pair.get("pair_index", "")).lstrip("-").isdigit() else pair.get("pair_index", -1),
        "pair_type": str(pair.get("pair_type", "")),
        "source_task": str(pair["source_task"]),
        "target_task": str(pair["target_task"]),
        "filler_task": str(pair.get("filler_task", "")),
        "source_multiplier": float(multiplier),
        "condition": condition,
    }


def add_metadata(rows: list[dict[str, Any]], pair: dict[str, Any], multiplier: float, max_data_seen: int) -> list[dict[str, Any]]:
    ident = pair_identity(pair, multiplier, f"source_x{float(multiplier):g}")
    out = []
    for r in rows:
        d = dict(r)
        d.update(ident)
        d["checkpoint_fraction"] = float(d.get("data_seen", 0)) / max(1, int(max_data_seen))
        out.append(d)
    return out


def stable_seed(seed: int, task_name: str, stage: str) -> int:
    return int((abs(hash((str(task_name), str(stage)))) + 1009 * int(seed)) % (2**31 - 1))


def log_checkpoints(max_data_seen: int, n: int) -> list[int]:
    if n <= 1:
        return [max_data_seen]
    lo = max(1, max_data_seen // 1000)
    return sorted(set(int(x) for x in np.logspace(np.log10(float(lo)), np.log10(float(max_data_seen)), num=n).tolist()))


def config_row(args: argparse.Namespace, pair: pd.Series, multiplier: float, n_params: int) -> dict[str, Any]:
    return {
        "pair_id": str(pair["pair_id"]),
        "source_task": str(pair["source_task"]),
        "target_task": str(pair["target_task"]),
        "filler_task": str(pair["filler_task"]),
        "pair_type": str(pair["pair_type"]),
        "source_multiplier": float(multiplier),
        "backend": "B1_sequence_dsl",
        "max_data_seen": int(args.max_data_seen),
        "batch_size": int(args.batch_size),
        "learning_rate": float(args.learning_rate),
        "weight_decay": float(args.weight_decay),
        "n_parameters": int(n_params),
        "early_probe_fraction": float(args.early_probe_fraction),
        "param_subset": args.param_subset,
    }


def render_run_report(args: argparse.Namespace, pair_plan: pd.DataFrame, outcomes: pd.DataFrame, predictors: pd.DataFrame) -> str:
    lines = [
        "# B1 N1 cross-task coupling pilot run",
        "",
        "This run estimates directional cross-task interaction I(A→B) by varying A's mixture weight and measuring B's learning, while logging leading-indicator gradient/representation couplings.",
        "",
        "## Setup",
        f"- pairs: `{len(pair_plan)}`",
        f"- dose multipliers: `{', '.join(map(str, args.dose_multipliers))}`",
        f"- seeds: `{', '.join(map(str, args.seeds))}`",
        f"- max_data_seen: `{args.max_data_seen}`",
        f"- early_probe_fraction: `{args.early_probe_fraction}`",
        f"- param_subset: `{args.param_subset}`",
        f"- outcome rows: `{len(outcomes)}`",
        f"- predictor rows: `{len(predictors)}`",
        "",
        "## Pair-type coverage",
    ]
    for pair_type, n in pair_plan["pair_type"].value_counts().sort_index().items():
        lines.append(f"- `{pair_type}`: `{int(n)}`")
    lines.extend(
        [
            "",
            "## Next analysis",
            "Run `python -m ic_experiments.experiments.analyze_b1_coupling_pilot --result-dir <this-dir> --output-dir <analysis-dir>` to estimate slopes, seed-level uncertainty, and predictor-vs-interaction correlations.",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    main()
