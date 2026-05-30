from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch import nn

from ic_experiments.backends.sequence_dsl import (
    CausalTransformerLM,
    SequenceDSLConfig,
    evaluate_sequence_per_task,
    generate_sequence_dsl_family,
    load_sequence_family,
    make_lm_batch,
    save_sequence_dsl_family,
)
from ic_experiments.metrics import acquisition_times
from ic_experiments.sequence_analysis import (
    final_metrics,
    frequency_realization_table,
    make_checkpoint_table,
    make_config_table,
    realization_summary,
    sequence_difficulty_table,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run a smoke/pilot training loop on B1 sequence-DSL backend.")
    p.add_argument("--output-dir", type=Path, default=Path("results/sequence_dsl_pilot"))
    p.add_argument("--structure-table", type=Path, default=None)
    p.add_argument("--family-seed", type=int, default=0)
    p.add_argument("--seeds", type=int, nargs="+", default=[0])
    p.add_argument("--max-data-seen", type=int, default=20_000)
    p.add_argument("--batch-size", type=int, default=128)
    p.add_argument("--learning-rate", type=float, default=3e-4)
    p.add_argument("--weight-decay", type=float, default=0.1)
    p.add_argument("--warmup-frac", type=float, default=0.05)
    p.add_argument("--n-checkpoints", type=int, default=30)
    p.add_argument("--eval-examples-per-task", type=int, default=256)
    p.add_argument("--d-model", type=int, default=128)
    p.add_argument("--n-layers", type=int, default=2)
    p.add_argument("--n-heads", type=int, default=4)
    p.add_argument("--d-mlp", type=int, default=512)
    p.add_argument("--dropout", type=float, default=0.0)
    p.add_argument("--vocab-content", type=int, default=64)
    p.add_argument("--input-len", type=int, default=8)
    p.add_argument("--acquisition-threshold", type=float, default=0.90)
    p.add_argument("--acquisition-patience", type=int, default=2)
    p.add_argument("--device", type=str, default="cpu")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    try:
        torch.set_num_threads(1)
    except RuntimeError:
        pass
    output = args.output_dir
    output.mkdir(parents=True, exist_ok=True)
    cfg = SequenceDSLConfig(vocab_content=args.vocab_content, input_len=args.input_len, seed=args.family_seed)
    if args.structure_table:
        family = load_sequence_family(args.structure_table, cfg)
    else:
        family = generate_sequence_dsl_family(cfg)
        save_sequence_dsl_family(family, output / "generated_family")
    all_eval = []
    all_acq = []
    count_rows = []
    checkpoints = _log_checkpoints(args.max_data_seen, args.n_checkpoints)
    for seed in args.seeds:
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
        data_seen = 0
        ckpt_idx = 0
        task_sample_counts = np.zeros(len(family.tasks), dtype=np.int64)
        eval_rows = evaluate_sequence_per_task(model, family.tasks, cfg, args.eval_examples_per_task, data_seen, "baseline", seed, device)
        all_eval.extend(_add_fraction(eval_rows, args.max_data_seen))
        while data_seen < args.max_data_seen:
            tokens, labels, task_ids = make_lm_batch(family.tasks, cfg, args.batch_size, device, weights)
            batch_counts = torch.bincount(task_ids.detach().cpu(), minlength=len(family.tasks)).numpy()
            task_sample_counts += batch_counts.astype(np.int64)
            opt.zero_grad(set_to_none=True)
            logits = model(tokens)
            loss = criterion(logits.reshape(-1, logits.size(-1)), labels.reshape(-1))
            loss.backward()
            opt.step()
            data_seen += args.batch_size
            lr_scale = _lr_scale(data_seen, args.max_data_seen, args.warmup_frac)
            for group in opt.param_groups:
                group["lr"] = args.learning_rate * lr_scale
            if ckpt_idx < len(checkpoints) and data_seen >= checkpoints[ckpt_idx]:
                rows = evaluate_sequence_per_task(model, family.tasks, cfg, args.eval_examples_per_task, data_seen, "baseline", seed, device)
                all_eval.extend(_add_fraction(rows, args.max_data_seen))
                ckpt_idx += 1
        eval_df = pd.DataFrame(all_eval)
        seed_acq = acquisition_times(eval_df[eval_df["seed"] == seed], threshold=args.acquisition_threshold, patience=args.acquisition_patience, metric="exact_match")
        all_acq.append(seed_acq)
        for task, count in zip(family.tasks, task_sample_counts):
            count_rows.append({
                "condition": "baseline",
                "seed": int(seed),
                "task_name": task.structure_id,
                "realized_sample_count": int(count),
            })
    eval_df = pd.DataFrame(all_eval)
    acq_df = pd.concat(all_acq, ignore_index=True) if all_acq else pd.DataFrame()
    structure_df = family.structure_table()
    structure_df.to_csv(output / "structure_table.csv", index=False)
    try:
        family.generic_structure_table().to_csv(output / "generic_structure_table.csv", index=False)
    except Exception:
        pass
    eval_df.to_csv(output / "eval_curves.csv", index=False)
    acq_df.to_csv(output / "acquisition_times.csv", index=False)

    # Shared-sweep-style auxiliary tables. These make B1 pilots analyzable as
    # the same expensive object for ordering, mediation, and residual analyses.
    n_parameters = sum(p.numel() for p in model.parameters())
    make_config_table(args, backend=family.name, n_parameters=n_parameters).to_csv(output / "config_table.csv", index=False)
    make_checkpoint_table(checkpoints, args.max_data_seen, args.seeds).to_csv(output / "checkpoint_table.csv", index=False)
    final_metrics(eval_df).to_csv(output / "final_metrics.csv", index=False)
    sequence_difficulty_table(family, n_probe_examples=2048, seed=args.family_seed).to_csv(output / "sequence_difficulty_table.csv", index=False)
    if count_rows:
        realized = frequency_realization_table(count_rows, structure_df, args.max_data_seen, cfg.input_len)
        realized.to_csv(output / "frequency_realization.csv", index=False)
        realization_summary(realized).to_csv(output / "frequency_realization_summary.csv", index=False)
    else:
        pd.DataFrame().to_csv(output / "frequency_realization.csv", index=False)
        pd.DataFrame().to_csv(output / "frequency_realization_summary.csv", index=False)

    summary = {
        "backend": family.name,
        "family": family.metadata(),
        "training": vars(args) | {"output_dir": str(args.output_dir), "structure_table": str(args.structure_table) if args.structure_table else None},
        "n_parameters": n_parameters,
        "paths": {
            "structure_table": str(output / "structure_table.csv"),
            "generic_structure_table": str(output / "generic_structure_table.csv"),
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
    (output / "sequence_dsl_pilot_report.md").write_text(_report(eval_df, acq_df, family.passed), encoding="utf-8")
    print("Saved sequence DSL pilot outputs:")
    for name in [
        "sequence_dsl_pilot_report.md", "structure_table.csv", "generic_structure_table.csv", "config_table.csv",
        "checkpoint_table.csv", "eval_curves.csv", "acquisition_times.csv", "final_metrics.csv",
        "frequency_realization.csv", "frequency_realization_summary.csv", "sequence_difficulty_table.csv", "summary.json"
    ]:
        print(f"  {output / name}")


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


def _report(eval_df: pd.DataFrame, acq_df: pd.DataFrame, family_passed: bool) -> str:
    acq_rate = float(acq_df["acquired_at"].notna().mean()) if not acq_df.empty else float("nan")
    final = eval_df.sort_values("data_seen").groupby(["seed", "task_name"]).tail(1)
    return "\n".join(
        [
            "# Sequence DSL pilot report",
            "",
            f"Family design passed: **{family_passed}**",
            f"Mean acquisition rate: `{acq_rate:.3f}`",
            f"Mean final exact match: `{final['exact_match'].mean():.3f}`",
            f"Mean final token accuracy: `{final['token_accuracy'].mean():.3f}`",
            "",
            "This is a B1 smoke/pilot path. It is not yet the full shared sweep; it verifies that the sequence DSL and transformer training loop run end-to-end.",
        ]
    )


if __name__ == "__main__":
    main()
