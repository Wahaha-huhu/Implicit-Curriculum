from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

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
from ic_experiments.sequence_analysis import (
    final_metrics,
    frequency_realization_table,
    make_checkpoint_table,
    realization_summary,
    sequence_difficulty_table,
)


CONFIG_PRESETS: dict[str, dict[str, float | int]] = {
    "base": {},
    "lr_low": {"learning_rate": 2.5e-4},
    "lr_high": {"learning_rate": 1.0e-3},
    "wd_zero": {"weight_decay": 0.0},
    "wd_high": {"weight_decay": 0.2},
    "batch_small": {"batch_size": 128},
    "batch_large": {"batch_size": 512},
    "short_budget": {"max_data_seen": 125_000},
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run B1 sequence-DSL shared H1 sweep across configs and seeds.")
    p.add_argument("--output-dir", type=Path, default=Path("results/b1_h1_shared_sweep"))
    p.add_argument("--structure-table", type=Path, required=True)
    p.add_argument("--configs", nargs="+", default=["base", "lr_low", "lr_high", "wd_zero", "batch_small", "batch_large"])
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
    p.add_argument("--acquisition-threshold", type=float, default=0.70, help="Default token-accuracy threshold for quick acquisition table.")
    p.add_argument("--acquisition-patience", type=int, default=2)
    p.add_argument("--device", type=str, default="cpu")
    p.add_argument("--skip-existing", action="store_true", help="Skip a config/seed run if its shard already exists.")
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
    structure_df.to_csv(output / "structure_table.csv", index=False)
    family.generic_structure_table().to_csv(output / "generic_structure_table.csv", index=False)
    sequence_difficulty_table(family, n_probe_examples=2048, seed=0).to_csv(output / "sequence_difficulty_table.csv", index=False)

    all_eval_paths: list[Path] = []
    all_count_paths: list[Path] = []
    config_rows = []
    checkpoint_tables = []
    quick_acq_paths: list[Path] = []

    for config_name in args.configs:
        if config_name not in CONFIG_PRESETS:
            raise ValueError(f"Unknown config preset {config_name!r}. Available: {sorted(CONFIG_PRESETS)}")
        run_cfg = _apply_preset(args, CONFIG_PRESETS[config_name])
        checkpoints = _log_checkpoints(int(run_cfg["max_data_seen"]), int(run_cfg["n_checkpoints"]))
        for seed in args.seeds:
            shard_prefix = f"config={config_name}__seed={seed}"
            eval_path = shard_dir / f"{shard_prefix}__eval_curves.csv"
            count_path = shard_dir / f"{shard_prefix}__frequency_counts.csv"
            acq_path = shard_dir / f"{shard_prefix}__quick_acquisition.csv"
            if args.skip_existing and eval_path.exists() and count_path.exists():
                all_eval_paths.append(eval_path)
                all_count_paths.append(count_path)
                if acq_path.exists():
                    quick_acq_paths.append(acq_path)
                continue
            print(f"[B1 H1 sweep] config={config_name} seed={seed}")
            eval_df, counts_df, acq_df, n_params = _train_one(family, cfg, run_cfg, config_name, seed, checkpoints)
            eval_df.to_csv(eval_path, index=False)
            counts_df.to_csv(count_path, index=False)
            acq_df.to_csv(acq_path, index=False)
            all_eval_paths.append(eval_path)
            all_count_paths.append(count_path)
            quick_acq_paths.append(acq_path)
            config_rows.append(_config_row(args, run_cfg, config_name, n_params))
        checkpoint_tables.append(make_checkpoint_table(checkpoints, int(run_cfg["max_data_seen"]), args.seeds, condition=config_name))
        if not any(r.get("config_name") == config_name for r in config_rows):
            config_rows.append(_config_row(args, run_cfg, config_name, None))

    eval_df = pd.concat([pd.read_csv(p) for p in all_eval_paths], ignore_index=True) if all_eval_paths else pd.DataFrame()
    counts = pd.concat([pd.read_csv(p) for p in all_count_paths], ignore_index=True) if all_count_paths else pd.DataFrame()
    quick_acq = pd.concat([pd.read_csv(p) for p in quick_acq_paths], ignore_index=True) if quick_acq_paths else pd.DataFrame()

    eval_df.to_csv(output / "eval_curves.csv", index=False)
    quick_acq.to_csv(output / "acquisition_times.csv", index=False)
    pd.DataFrame(config_rows).drop_duplicates("config_name").to_csv(output / "config_table.csv", index=False)
    pd.concat(checkpoint_tables, ignore_index=True).to_csv(output / "checkpoint_table.csv", index=False)
    final_metrics(eval_df).to_csv(output / "final_metrics.csv", index=False)

    if not counts.empty:
        realized = frequency_realization_table(counts.to_dict(orient="records"), structure_df, int(args.max_data_seen), cfg.input_len)
        # For non-base configs with different budgets, target_data_seen is only descriptive; realized fractions are correct.
        realized.to_csv(output / "frequency_realization.csv", index=False)
        realization_summary(realized).to_csv(output / "frequency_realization_summary.csv", index=False)
    else:
        pd.DataFrame().to_csv(output / "frequency_realization.csv", index=False)
        pd.DataFrame().to_csv(output / "frequency_realization_summary.csv", index=False)

    summary = {
        "backend": family.name,
        "version": "v0.8",
        "purpose": "B1 H1 shared sweep: ordering and sign-stability across configs/seeds.",
        "structure_table": str(args.structure_table),
        "configs": args.configs,
        "seeds": args.seeds,
        "base_args": _jsonable(vars(args)),
        "family": family.metadata(),
        "paths": {
            "structure_table": str(output / "structure_table.csv"),
            "config_table": str(output / "config_table.csv"),
            "checkpoint_table": str(output / "checkpoint_table.csv"),
            "eval_curves": str(output / "eval_curves.csv"),
            "acquisition_times": str(output / "acquisition_times.csv"),
            "final_metrics": str(output / "final_metrics.csv"),
            "frequency_realization": str(output / "frequency_realization.csv"),
            "sequence_difficulty_table": str(output / "sequence_difficulty_table.csv"),
        },
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (output / "b1_h1_shared_sweep_report.md").write_text(_report(args, eval_df, quick_acq), encoding="utf-8")
    print("Saved B1 H1 shared-sweep outputs:")
    for name in [
        "b1_h1_shared_sweep_report.md", "summary.json", "structure_table.csv", "generic_structure_table.csv",
        "config_table.csv", "checkpoint_table.csv", "eval_curves.csv", "acquisition_times.csv",
        "final_metrics.csv", "frequency_realization.csv", "frequency_realization_summary.csv", "sequence_difficulty_table.csv",
    ]:
        print(f"  {output / name}")


def _apply_preset(args: argparse.Namespace, preset: dict[str, float | int]) -> dict[str, float | int]:
    d = {
        "max_data_seen": args.max_data_seen,
        "batch_size": args.batch_size,
        "learning_rate": args.learning_rate,
        "weight_decay": args.weight_decay,
        "warmup_frac": args.warmup_frac,
        "n_checkpoints": args.n_checkpoints,
        "eval_examples_per_task": args.eval_examples_per_task,
        "d_model": args.d_model,
        "n_layers": args.n_layers,
        "n_heads": args.n_heads,
        "d_mlp": args.d_mlp,
        "dropout": args.dropout,
        "acquisition_threshold": args.acquisition_threshold,
        "acquisition_patience": args.acquisition_patience,
        "device": args.device,
    }
    d.update(preset)
    return d


def _train_one(family, cfg: SequenceDSLConfig, run_cfg: dict, condition: str, seed: int, checkpoints: list[int]):
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    device = torch.device(str(run_cfg["device"]))
    model = CausalTransformerLM(
        vocab_size=cfg.vocab_size,
        max_seq_len=1 + cfg.input_len + 1 + cfg.input_len,
        d_model=int(run_cfg["d_model"]),
        n_layers=int(run_cfg["n_layers"]),
        n_heads=int(run_cfg["n_heads"]),
        d_mlp=int(run_cfg["d_mlp"]),
        dropout=float(run_cfg["dropout"]),
    ).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    opt = torch.optim.AdamW(model.parameters(), lr=float(run_cfg["learning_rate"]), weight_decay=float(run_cfg["weight_decay"]), betas=(0.9, 0.98))
    criterion = nn.CrossEntropyLoss(ignore_index=-100)
    weights = torch.tensor([t.frequency for t in family.tasks], dtype=torch.float32, device=device)
    weights = weights / weights.sum()
    data_seen = 0
    ckpt_idx = 0
    eval_rows = []
    task_sample_counts = np.zeros(len(family.tasks), dtype=np.int64)
    eval_rows.extend(_add_fraction(evaluate_sequence_per_task(model, family.tasks, cfg, int(run_cfg["eval_examples_per_task"]), data_seen, condition, seed, device), int(run_cfg["max_data_seen"])))
    while data_seen < int(run_cfg["max_data_seen"]):
        tokens, labels, task_ids = make_lm_batch(family.tasks, cfg, int(run_cfg["batch_size"]), device, weights)
        task_sample_counts += torch.bincount(task_ids.detach().cpu(), minlength=len(family.tasks)).numpy().astype(np.int64)
        opt.zero_grad(set_to_none=True)
        logits = model(tokens)
        loss = criterion(logits.reshape(-1, logits.size(-1)), labels.reshape(-1))
        loss.backward()
        opt.step()
        data_seen += int(run_cfg["batch_size"])
        lr_scale = _lr_scale(data_seen, int(run_cfg["max_data_seen"]), float(run_cfg["warmup_frac"]))
        for group in opt.param_groups:
            group["lr"] = float(run_cfg["learning_rate"]) * lr_scale
        while ckpt_idx < len(checkpoints) and data_seen >= checkpoints[ckpt_idx]:
            eval_rows.extend(_add_fraction(evaluate_sequence_per_task(model, family.tasks, cfg, int(run_cfg["eval_examples_per_task"]), data_seen, condition, seed, device), int(run_cfg["max_data_seen"])))
            ckpt_idx += 1
    eval_df = pd.DataFrame(eval_rows)
    acq_df = acquisition_times(eval_df, threshold=float(run_cfg["acquisition_threshold"]), patience=int(run_cfg["acquisition_patience"]), metric="token_accuracy")
    acq_df["metric_family"] = "token_accuracy"
    acq_df["analysis_threshold"] = float(run_cfg["acquisition_threshold"])
    count_rows = [
        {"condition": condition, "seed": int(seed), "task_name": task.structure_id, "realized_sample_count": int(count)}
        for task, count in zip(family.tasks, task_sample_counts)
    ]
    return eval_df, pd.DataFrame(count_rows), acq_df, n_params


def _log_checkpoints(max_data_seen: int, n: int) -> list[int]:
    if n <= 1:
        return [max_data_seen]
    lo = max(1, max_data_seen // 1000)
    vals = sorted(set(int(x) for x in np.logspace(np.log10(float(lo)), np.log10(float(max_data_seen)), num=n).tolist()))
    return [v for v in vals if v > 0]


def _lr_scale(data_seen: int, max_data_seen: int, warmup_frac: float) -> float:
    warmup = max(1, int(max_data_seen * warmup_frac))
    return min(1.0, max(0.05, data_seen / warmup))


def _add_fraction(rows: list[dict], max_data_seen: int) -> list[dict]:
    for r in rows:
        r["checkpoint_fraction"] = float(r["data_seen"]) / max(1, max_data_seen)
    return rows


def _config_row(args: argparse.Namespace, run_cfg: dict, config_name: str, n_params: int | None) -> dict:
    row = {"config_name": config_name, "backend": "B1_sequence_dsl"}
    for key, value in run_cfg.items():
        if key != "device":
            row[key] = value
    row["device"] = args.device
    row["n_parameters"] = n_params if n_params is not None else np.nan
    row["n_seeds"] = len(args.seeds)
    return row


def _jsonable(d: dict) -> dict:
    out = {}
    for k, v in d.items():
        if isinstance(v, Path):
            out[k] = str(v)
        elif isinstance(v, (list, tuple)):
            out[k] = list(v)
        else:
            out[k] = v
    return out


def _report(args: argparse.Namespace, eval_df: pd.DataFrame, acq_df: pd.DataFrame) -> str:
    lines = [
        "# B1 H1 shared-sweep report",
        "",
        "This run is the first shared-sweep object for H1 ordering/sign-stability on the B1 sequence-DSL transformer substrate.",
        "It trains once across configs/seeds and stores the checkpoint/evaluation tables used by downstream H1/H2/H3 analyses.",
        "",
        "## Run summary",
        f"- configs: `{', '.join(args.configs)}`",
        f"- seeds: `{', '.join(map(str, args.seeds))}`",
        f"- max_data_seen: `{args.max_data_seen}`",
        f"- n_checkpoints: `{args.n_checkpoints}`",
        f"- rows in eval_curves: `{len(eval_df)}`",
    ]
    if not acq_df.empty:
        lines.append(f"- default token-threshold acquisition rate: `{acq_df['acquired_at'].notna().mean():.3f}`")
    lines += [
        "",
        "## Next step",
        "Run `analyze_b1_h1_shared_sweep` on this directory. H1 claims should be based on the analysis report, not this raw sweep report.",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
