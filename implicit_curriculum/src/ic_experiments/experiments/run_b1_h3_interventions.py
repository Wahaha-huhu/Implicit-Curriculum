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
from ic_experiments.metrics import acquisition_times
from ic_experiments.run_management import append_registry, write_manifest
from ic_experiments.sequence_analysis import (
    final_metrics,
    frequency_realization_table,
    make_checkpoint_table,
    realization_summary,
    sequence_difficulty_table,
)


DEFAULT_CONDITIONS = [
    "baseline",
    "upweight_component",
    "upweight_unrelated_matched",
    "upweight_fake_component",
    "upweight_surface_control",
    "delay_component",
    "delay_unrelated_matched",
    "corrupt_component",
    "corrupt_unrelated_matched",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run B1 H3 pair-specific intervention training for selected component-composite pairs.")
    p.add_argument("--output-dir", type=Path, default=Path("results/b1_h3_interventions"))
    p.add_argument("--structure-table", type=Path, required=True)
    p.add_argument("--pair-selection", type=Path, default=None, help="Optional h2_pair_selection.csv. If supplied, the first/highest residual pair is used unless explicit pair args are set.")
    p.add_argument("--component", type=str, default=None)
    p.add_argument("--composite", type=str, default=None)
    p.add_argument("--unrelated-control", type=str, default=None)
    p.add_argument("--fake-component-control", type=str, default=None)
    p.add_argument("--surface-control", type=str, default=None)
    p.add_argument("--conditions", nargs="+", default=DEFAULT_CONDITIONS)
    p.add_argument("--seeds", type=int, nargs="+", default=list(range(10)))
    p.add_argument("--max-data-seen", type=int, default=250_000)
    p.add_argument("--batch-size", type=int, default=256)
    p.add_argument("--learning-rate", type=float, default=5e-4)
    p.add_argument("--weight-decay", type=float, default=0.1)
    p.add_argument("--warmup-frac", type=float, default=0.05)
    p.add_argument("--n-checkpoints", type=int, default=100)
    p.add_argument("--eval-examples-per-task", type=int, default=512)
    p.add_argument("--d-model", type=int, default=128)
    p.add_argument("--n-layers", type=int, default=2)
    p.add_argument("--n-heads", type=int, default=4)
    p.add_argument("--d-mlp", type=int, default=512)
    p.add_argument("--dropout", type=float, default=0.0)
    p.add_argument("--vocab-content", type=int, default=32)
    p.add_argument("--input-len", type=int, default=6)
    p.add_argument("--acquisition-threshold", type=float, default=0.70)
    p.add_argument("--acquisition-patience", type=int, default=2)
    p.add_argument("--upweight-factor", type=float, default=2.0)
    p.add_argument("--delay-fraction", type=float, default=0.35)
    p.add_argument("--corrupt-prob", type=float, default=0.25)
    p.add_argument("--device", type=str, default="cpu")
    p.add_argument("--skip-existing", action="store_true")
    p.add_argument("--code-version", type=str, default="v1.0")
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
    shard_dir = output / "shards"
    shard_dir.mkdir(exist_ok=True)

    cfg = SequenceDSLConfig(vocab_content=args.vocab_content, input_len=args.input_len)
    family = load_sequence_family(args.structure_table, cfg)
    structure_df = family.structure_table()
    pair = resolve_pair_and_controls(args, structure_df)
    tasks_by_name = {t.structure_id: i for i, t in enumerate(family.tasks)}
    validate_pair(pair, tasks_by_name)

    structure_df.to_csv(output / "structure_table.csv", index=False)
    family.generic_structure_table().to_csv(output / "generic_structure_table.csv", index=False)
    sequence_difficulty_table(family, n_probe_examples=2048, seed=0).to_csv(output / "sequence_difficulty_table.csv", index=False)
    pd.DataFrame([pair]).to_csv(output / "h3_pair_config.csv", index=False)

    checkpoints = log_checkpoints(args.max_data_seen, args.n_checkpoints)
    all_eval_paths: list[Path] = []
    all_count_paths: list[Path] = []
    quick_acq_paths: list[Path] = []
    checkpoint_tables = []
    config_rows = []

    for condition in args.conditions:
        for seed in args.seeds:
            shard_prefix = f"condition={condition}__seed={seed}"
            eval_path = shard_dir / f"{shard_prefix}__eval_curves.csv"
            count_path = shard_dir / f"{shard_prefix}__frequency_counts.csv"
            acq_path = shard_dir / f"{shard_prefix}__quick_acquisition.csv"
            if args.skip_existing and eval_path.exists() and count_path.exists():
                all_eval_paths.append(eval_path)
                all_count_paths.append(count_path)
                if acq_path.exists():
                    quick_acq_paths.append(acq_path)
                continue
            print(f"[B1 H3] condition={condition} seed={seed} component={pair['component']} composite={pair['composite']}")
            eval_df, counts_df, acq_df, n_params = train_one_intervention(family, cfg, args, condition, seed, checkpoints, pair)
            eval_df.to_csv(eval_path, index=False)
            counts_df.to_csv(count_path, index=False)
            acq_df.to_csv(acq_path, index=False)
            all_eval_paths.append(eval_path)
            all_count_paths.append(count_path)
            quick_acq_paths.append(acq_path)
            config_rows.append(config_row(args, condition, n_params, pair))
        checkpoint_tables.append(make_checkpoint_table(checkpoints, args.max_data_seen, args.seeds, condition=condition))

    eval_df = pd.concat([pd.read_csv(p) for p in all_eval_paths], ignore_index=True) if all_eval_paths else pd.DataFrame()
    counts = pd.concat([pd.read_csv(p) for p in all_count_paths], ignore_index=True) if all_count_paths else pd.DataFrame()
    quick_acq = pd.concat([pd.read_csv(p) for p in quick_acq_paths], ignore_index=True) if quick_acq_paths else pd.DataFrame()

    eval_df.to_csv(output / "eval_curves.csv", index=False)
    quick_acq.to_csv(output / "acquisition_times.csv", index=False)
    final_metrics(eval_df).to_csv(output / "final_metrics.csv", index=False)
    pd.DataFrame(config_rows).drop_duplicates("condition").to_csv(output / "config_table.csv", index=False)
    pd.concat(checkpoint_tables, ignore_index=True).to_csv(output / "checkpoint_table.csv", index=False)
    if not counts.empty:
        realized = frequency_realization_table(counts.to_dict(orient="records"), structure_df, args.max_data_seen, cfg.input_len)
        realized.to_csv(output / "frequency_realization.csv", index=False)
        realization_summary(realized).to_csv(output / "frequency_realization_summary.csv", index=False)
    else:
        pd.DataFrame().to_csv(output / "frequency_realization.csv", index=False)
        pd.DataFrame().to_csv(output / "frequency_realization_summary.csv", index=False)

    summary = {
        "backend": family.name,
        "version": "v1.0",
        "purpose": "B1 H3 pair-specific intervention training.",
        "pair": pair,
        "conditions": args.conditions,
        "seeds": args.seeds,
        "paths": {
            "eval_curves": str(output / "eval_curves.csv"),
            "acquisition_times": str(output / "acquisition_times.csv"),
            "final_metrics": str(output / "final_metrics.csv"),
            "pair_config": str(output / "h3_pair_config.csv"),
        },
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (output / "b1_h3_intervention_run_report.md").write_text(run_report(args, pair, eval_df, quick_acq), encoding="utf-8")

    manifest = write_manifest(
        output,
        experiment="B1_H3_pair_specific_interventions",
        backend="B1_sequence_dsl",
        code_version=args.code_version,
        run_id=args.run_id or f"h3_{pair['component']}_to_{pair['composite']}",
        command=sys.argv,
        input_paths={"structure_table": str(args.structure_table), "pair_selection": str(args.pair_selection) if args.pair_selection else ""},
        extra={"pair": pair, "conditions": args.conditions, "thesis_use": args.thesis_use},
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
                "status": "trained",
                "thesis_use": args.thesis_use,
                "created_at_utc": manifest["created_at_utc"],
            },
        )

    print("Saved B1 H3 intervention outputs:")
    for name in [
        "b1_h3_intervention_run_report.md", "summary.json", "run_manifest.json", "h3_pair_config.csv",
        "eval_curves.csv", "acquisition_times.csv", "final_metrics.csv", "frequency_realization_summary.csv",
    ]:
        print(f"  {output / name}")


def resolve_pair_and_controls(args: argparse.Namespace, structure: pd.DataFrame) -> dict[str, str]:
    pair: dict[str, str | None] = {
        "component": args.component,
        "composite": args.composite,
        "unrelated_control": args.unrelated_control,
        "fake_component_control": args.fake_component_control,
        "surface_control": args.surface_control,
    }
    if args.pair_selection is not None and args.pair_selection.exists():
        pairs = pd.read_csv(args.pair_selection)
        if not pairs.empty:
            # Prefer highest residual and positive rate if available.
            sort_cols = [c for c in ["positive_rate", "mean_residual_log_time", "residual_log_time"] if c in pairs.columns]
            if sort_cols:
                pairs = pairs.sort_values(sort_cols, ascending=[False] + [False] * (len(sort_cols) - 1))
            row = pairs.iloc[0]
            pair["component"] = pair["component"] or str(row.get("component", row.get("component_id", "")))
            pair["composite"] = pair["composite"] or str(row.get("composite", row.get("composite_id", row.get("task_name", ""))))
    # Fallback to known H2 naming if present.
    names = set(structure["task_name"] if "task_name" in structure.columns else structure["structure_id"])
    pair["component"] = pair["component"] or ("A02_substitute" if "A02_substitute" in names else None)
    pair["composite"] = pair["composite"] or ("C06_reverse_then_substitute_02_00" if "C06_reverse_then_substitute_02_00" in names else None)
    pair["unrelated_control"] = pair["unrelated_control"] or choose_control(structure, "unrelated", pair["composite"])
    pair["fake_component_control"] = pair["fake_component_control"] or choose_control(structure, "shortcut", pair["component"])
    pair["surface_control"] = pair["surface_control"] or choose_control(structure, "surface_control", pair["component"])
    return {k: str(v) for k, v in pair.items() if v is not None and str(v) and str(v) != "nan"}


def choose_control(structure: pd.DataFrame, kind: str, target: str | None) -> str | None:
    if structure.empty:
        return None
    df = structure.copy()
    if "task_name" not in df.columns and "structure_id" in df.columns:
        df["task_name"] = df["structure_id"]
    cand = df[df.get("kind") == kind].copy()
    if cand.empty:
        # control_type fallback.
        cand = df[df.get("control_type", "").astype(str).str.contains(kind.replace("_control", ""), na=False)].copy()
    if cand.empty:
        return None
    target_freq = np.nan
    target_learn = np.nan
    if target and target in set(df["task_name"]):
        row = df[df["task_name"] == target].iloc[0]
        target_freq = float(row.get("frequency", np.nan))
        target_learn = float(row.get("reference_learnability", np.nan))
    if np.isfinite(target_freq) and "frequency" in cand.columns:
        cand["match_score"] = (np.log(np.maximum(cand["frequency"].astype(float), 1e-12)) - np.log(max(target_freq, 1e-12))).abs()
        if np.isfinite(target_learn) and "reference_learnability" in cand.columns:
            cand["match_score"] += 0.25 * (cand["reference_learnability"].astype(float) - target_learn).abs()
        cand = cand.sort_values("match_score")
    return str(cand.iloc[0]["task_name"])


def validate_pair(pair: dict[str, str], tasks_by_name: dict[str, int]) -> None:
    needed = ["component", "composite", "unrelated_control", "fake_component_control", "surface_control"]
    missing = [k for k in needed if not pair.get(k)]
    if missing:
        raise ValueError(f"Could not resolve H3 pair/control fields: {missing}. Pair={pair}")
    unknown = {k: v for k, v in pair.items() if v not in tasks_by_name}
    if unknown:
        raise ValueError(f"Pair/control task names are not in the structure table: {unknown}")


def train_one_intervention(family, cfg: SequenceDSLConfig, args: argparse.Namespace, condition: str, seed: int, checkpoints: list[int], pair: dict[str, str]):
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
    base_weights = torch.tensor([t.frequency for t in family.tasks], dtype=torch.float32, device=device)
    base_weights = base_weights / base_weights.sum()
    task_index = {t.structure_id: i for i, t in enumerate(family.tasks)}
    intervention_task = intervention_target(condition, pair)
    intervention_idx = task_index.get(intervention_task, -1)

    data_seen = 0
    ckpt_idx = 0
    eval_rows = []
    task_sample_counts = np.zeros(len(family.tasks), dtype=np.int64)
    eval_rows.extend(add_fraction(evaluate_sequence_per_task(model, family.tasks, cfg, args.eval_examples_per_task, data_seen, condition, seed, device), args.max_data_seen))
    while data_seen < args.max_data_seen:
        weights = intervention_weights(base_weights, condition, intervention_idx, data_seen, args)
        tokens, labels, task_ids = make_lm_batch(family.tasks, cfg, args.batch_size, device, weights)
        if condition.startswith("corrupt_") and intervention_idx >= 0:
            labels = corrupt_labels(labels, task_ids, intervention_idx, cfg, args.corrupt_prob)
        task_sample_counts += torch.bincount(task_ids.detach().cpu(), minlength=len(family.tasks)).numpy().astype(np.int64)
        opt.zero_grad(set_to_none=True)
        logits = model(tokens)
        loss = criterion(logits.reshape(-1, logits.size(-1)), labels.reshape(-1))
        loss.backward()
        opt.step()
        data_seen += args.batch_size
        lr_scale = lr_scale_fn(data_seen, args.max_data_seen, args.warmup_frac)
        for group in opt.param_groups:
            group["lr"] = args.learning_rate * lr_scale
        while ckpt_idx < len(checkpoints) and data_seen >= checkpoints[ckpt_idx]:
            eval_rows.extend(add_fraction(evaluate_sequence_per_task(model, family.tasks, cfg, args.eval_examples_per_task, data_seen, condition, seed, device), args.max_data_seen))
            ckpt_idx += 1
    eval_df = pd.DataFrame(eval_rows)
    acq_df = acquisition_times(eval_df, threshold=args.acquisition_threshold, patience=args.acquisition_patience, metric="token_accuracy")
    acq_df["metric_family"] = "token_accuracy"
    acq_df["analysis_threshold"] = float(args.acquisition_threshold)
    counts_df = pd.DataFrame([
        {"condition": condition, "seed": int(seed), "task_name": task.structure_id, "realized_sample_count": int(count)}
        for task, count in zip(family.tasks, task_sample_counts)
    ])
    return eval_df, counts_df, acq_df, n_params


def intervention_target(condition: str, pair: dict[str, str]) -> str | None:
    if condition in {"upweight_component", "delay_component", "corrupt_component"}:
        return pair["component"]
    if condition in {"upweight_unrelated_matched", "delay_unrelated_matched", "corrupt_unrelated_matched"}:
        return pair["unrelated_control"]
    if condition == "upweight_fake_component":
        return pair["fake_component_control"]
    if condition == "upweight_surface_control":
        return pair["surface_control"]
    return None


def intervention_weights(base_weights: torch.Tensor, condition: str, idx: int, data_seen: int, args: argparse.Namespace) -> torch.Tensor:
    weights = base_weights.clone()
    if idx < 0 or condition == "baseline":
        return weights / weights.sum()
    if condition.startswith("upweight_"):
        weights[idx] = weights[idx] * float(args.upweight_factor)
    elif condition.startswith("delay_") and data_seen < int(args.max_data_seen * args.delay_fraction):
        weights[idx] = 0.0
    # Corruption does not alter sampling; it only corrupts labels for target task.
    s = weights.sum()
    if float(s) <= 0:
        return base_weights / base_weights.sum()
    return weights / s


def corrupt_labels(labels: torch.Tensor, task_ids: torch.Tensor, intervention_idx: int, cfg: SequenceDSLConfig, prob: float) -> torch.Tensor:
    if prob <= 0:
        return labels
    out = labels.clone()
    row_mask = task_ids == intervention_idx
    if not row_mask.any():
        return out
    target_mask = (out != -100) & row_mask[:, None]
    corrupt_mask = target_mask & (torch.rand_like(out.float()) < float(prob))
    if corrupt_mask.any():
        rand = torch.randint(low=4, high=cfg.vocab_size, size=out.shape, device=out.device, dtype=out.dtype)
        out[corrupt_mask] = rand[corrupt_mask]
    return out


def log_checkpoints(max_data_seen: int, n: int) -> list[int]:
    if n <= 1:
        return [max_data_seen]
    lo = max(1, max_data_seen // 1000)
    return sorted(set(int(x) for x in np.logspace(np.log10(float(lo)), np.log10(float(max_data_seen)), num=n).tolist()))


def lr_scale_fn(data_seen: int, max_data_seen: int, warmup_frac: float) -> float:
    warmup = max(1, int(max_data_seen * warmup_frac))
    return min(1.0, max(0.05, data_seen / warmup))


def add_fraction(rows: list[dict], max_data_seen: int) -> list[dict]:
    for r in rows:
        r["checkpoint_fraction"] = float(r["data_seen"]) / max(1, max_data_seen)
    return rows


def config_row(args: argparse.Namespace, condition: str, n_params: int, pair: dict[str, str]) -> dict[str, Any]:
    return {
        "condition": condition,
        "backend": "B1_sequence_dsl",
        "max_data_seen": args.max_data_seen,
        "batch_size": args.batch_size,
        "learning_rate": args.learning_rate,
        "weight_decay": args.weight_decay,
        "n_parameters": n_params,
        "component": pair["component"],
        "composite": pair["composite"],
        "upweight_factor": args.upweight_factor,
        "delay_fraction": args.delay_fraction,
        "corrupt_prob": args.corrupt_prob,
    }


def run_report(args: argparse.Namespace, pair: dict[str, str], eval_df: pd.DataFrame, acq_df: pd.DataFrame) -> str:
    lines = [
        "# B1 H3 intervention run report",
        "",
        "This is the training output for pair-specific B1 H3 interventions. It is not the final H3 verdict; run `analyze_b1_h3_interventions` on this directory.",
        "",
        "## Pair",
        f"- component: `{pair['component']}`",
        f"- composite: `{pair['composite']}`",
        f"- unrelated_control: `{pair['unrelated_control']}`",
        f"- fake_component_control: `{pair['fake_component_control']}`",
        f"- surface_control: `{pair['surface_control']}`",
        "",
        "## Run summary",
        f"- conditions: `{', '.join(args.conditions)}`",
        f"- seeds: `{', '.join(map(str, args.seeds))}`",
        f"- max_data_seen: `{args.max_data_seen}`",
        f"- eval rows: `{len(eval_df)}`",
    ]
    if not acq_df.empty:
        comp_acq = acq_df[acq_df["task_name"] == pair["composite"]]["acquired_at"].notna().mean()
        lines.append(f"- quick composite acquisition rate across conditions/seeds: `{comp_acq:.3f}`")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
