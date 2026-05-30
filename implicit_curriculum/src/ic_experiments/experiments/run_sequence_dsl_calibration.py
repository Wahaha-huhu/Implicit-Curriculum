from __future__ import annotations

import argparse
import json
from pathlib import Path
from dataclasses import replace

import numpy as np
import pandas as pd
import torch
from torch import nn

from ic_experiments.backends.sequence_dsl import (
    CausalTransformerLM,
    SequenceDSLConfig,
    SequenceDSLFamily,
    evaluate_sequence_per_task,
    generate_sequence_dsl_family,
    make_lm_batch,
    save_sequence_dsl_family,
)
from ic_experiments.metrics import acquisition_times
from ic_experiments.experiments.run_sequence_dsl_pilot import _log_checkpoints, _lr_scale, _add_fraction


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Calibrate B1 sequence-DSL families for nontrivial acquisition coverage.")
    p.add_argument("--output-dir", type=Path, default=Path("results/sequence_dsl_calibration"))
    p.add_argument("--candidate-seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    p.add_argument("--calibration-seeds", type=int, nargs="+", default=[0, 1])
    p.add_argument("--vocab-content", type=int, default=32)
    p.add_argument("--input-len", type=int, default=6)
    p.add_argument("--n-atomic", type=int, default=8)
    p.add_argument("--n-composite", type=int, default=8)
    p.add_argument("--n-shortcut-controls", type=int, default=3)
    p.add_argument("--n-surface-controls", type=int, default=3)
    p.add_argument("--n-unrelated-controls", type=int, default=3)
    p.add_argument("--max-data-seen", type=int, default=120_000)
    p.add_argument("--batch-size", type=int, default=256)
    p.add_argument("--learning-rate", type=float, default=5e-4)
    p.add_argument("--weight-decay", type=float, default=0.05)
    p.add_argument("--warmup-frac", type=float, default=0.05)
    p.add_argument("--n-checkpoints", type=int, default=50)
    p.add_argument("--eval-examples-per-task", type=int, default=512)
    p.add_argument("--d-model", type=int, default=128)
    p.add_argument("--n-layers", type=int, default=2)
    p.add_argument("--n-heads", type=int, default=4)
    p.add_argument("--d-mlp", type=int, default=512)
    p.add_argument("--dropout", type=float, default=0.0)
    p.add_argument("--token-threshold", type=float, default=0.70)
    p.add_argument("--exact-threshold", type=float, default=0.30)
    p.add_argument("--target-min-acq", type=float, default=0.30)
    p.add_argument("--target-max-acq", type=float, default=0.85)
    p.add_argument("--min-composite-acq", type=float, default=0.20)
    p.add_argument("--device", type=str, default="cpu")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    try:
        torch.set_num_threads(1)
    except RuntimeError:
        pass
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    candidate_rows = []
    all_eval = []
    all_acq = []
    best: tuple[float, SequenceDSLFamily, pd.DataFrame, pd.DataFrame, dict] | None = None
    for candidate_seed in args.candidate_seeds:
        cfg = SequenceDSLConfig(
            vocab_content=args.vocab_content,
            input_len=args.input_len,
            n_atomic=args.n_atomic,
            n_composite=args.n_composite,
            n_shortcut_controls=args.n_shortcut_controls,
            n_surface_controls=args.n_surface_controls,
            n_unrelated_controls=args.n_unrelated_controls,
            seed=candidate_seed,
        )
        family = generate_sequence_dsl_family(cfg)
        eval_df = _train_family(family, args, candidate_seed)
        eval_df["candidate_seed"] = candidate_seed
        acq_token = acquisition_times(eval_df, threshold=args.token_threshold, patience=2, metric="token_accuracy")
        acq_token["candidate_seed"] = candidate_seed
        acq_token["metric_family"] = "token_accuracy"
        acq_token["analysis_threshold"] = args.token_threshold
        acq_exact = acquisition_times(eval_df, threshold=args.exact_threshold, patience=2, metric="exact_match")
        acq_exact["candidate_seed"] = candidate_seed
        acq_exact["metric_family"] = "exact_match"
        acq_exact["analysis_threshold"] = args.exact_threshold
        acq = pd.concat([acq_token, acq_exact], ignore_index=True)
        summary = _candidate_summary(candidate_seed, family, eval_df, acq_token, args)
        candidate_rows.append(summary)
        all_eval.append(eval_df)
        all_acq.append(acq)
        score = _score_candidate(summary, args)
        if best is None or score > best[0]:
            best = (score, family, eval_df, acq, summary)
        print(f"Candidate {candidate_seed}: score={score:.3f}, token_acq={summary['token_acquisition_rate']:.3f}, composite_token_acq={summary['composite_token_acquisition_rate']:.3f}, passed={summary['passed']}")

    cand_df = pd.DataFrame(candidate_rows)
    cand_df.to_csv(out / "candidate_calibration_summary.csv", index=False)
    pd.concat(all_eval, ignore_index=True).to_csv(out / "calibration_eval_curves.csv", index=False)
    pd.concat(all_acq, ignore_index=True).to_csv(out / "calibration_acquisition_times.csv", index=False)

    assert best is not None
    _, selected_family, selected_eval, selected_acq, selected_summary = best
    save_sequence_dsl_family(selected_family, out)
    selected_eval.to_csv(out / "selected_eval_curves.csv", index=False)
    selected_acq.to_csv(out / "selected_acquisition_times.csv", index=False)
    selected_summary = dict(selected_summary)
    selected_summary["calibration_passed"] = bool(selected_summary["passed"])
    selected_summary["paths"] = {
        "structure_table": str(out / "structure_table.csv"),
        "candidate_calibration_summary": str(out / "candidate_calibration_summary.csv"),
        "calibration_eval_curves": str(out / "calibration_eval_curves.csv"),
        "calibration_acquisition_times": str(out / "calibration_acquisition_times.csv"),
        "selected_eval_curves": str(out / "selected_eval_curves.csv"),
        "selected_acquisition_times": str(out / "selected_acquisition_times.csv"),
    }
    (out / "summary.json").write_text(json.dumps({"config": vars(args) | {"output_dir": str(args.output_dir)}, "selected": selected_summary}, indent=2), encoding="utf-8")
    (out / "sequence_dsl_calibration_report.md").write_text(_report(cand_df, selected_summary), encoding="utf-8")
    print("Saved sequence DSL calibration outputs:")
    for name in [
        "sequence_dsl_calibration_report.md",
        "candidate_calibration_summary.csv",
        "structure_table.csv",
        "design_diagnostics.csv",
        "selected_eval_curves.csv",
        "selected_acquisition_times.csv",
        "summary.json",
    ]:
        print(f"  {out / name}")


def _train_family(family: SequenceDSLFamily, args: argparse.Namespace, candidate_seed: int) -> pd.DataFrame:
    checkpoints = _log_checkpoints(args.max_data_seen, args.n_checkpoints)
    rows = []
    cfg = family.config
    for seed in args.calibration_seeds:
        torch.manual_seed(seed + 1000 * candidate_seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed + 1000 * candidate_seed)
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
        eval_rows = evaluate_sequence_per_task(model, family.tasks, cfg, args.eval_examples_per_task, data_seen, "baseline", seed, device)
        rows.extend(_add_fraction(eval_rows, args.max_data_seen))
        while data_seen < args.max_data_seen:
            tokens, labels, _ = make_lm_batch(family.tasks, cfg, args.batch_size, device, weights)
            opt.zero_grad(set_to_none=True)
            logits = model(tokens)
            loss = criterion(logits.reshape(-1, logits.size(-1)), labels.reshape(-1))
            loss.backward()
            opt.step()
            data_seen += args.batch_size
            scale = _lr_scale(data_seen, args.max_data_seen, args.warmup_frac)
            for group in opt.param_groups:
                group["lr"] = args.learning_rate * scale
            if ckpt_idx < len(checkpoints) and data_seen >= checkpoints[ckpt_idx]:
                eval_rows = evaluate_sequence_per_task(model, family.tasks, cfg, args.eval_examples_per_task, data_seen, "baseline", seed, device)
                rows.extend(_add_fraction(eval_rows, args.max_data_seen))
                ckpt_idx += 1
    return pd.DataFrame(rows)


def _candidate_summary(candidate_seed: int, family: SequenceDSLFamily, eval_df: pd.DataFrame, acq_token: pd.DataFrame, args: argparse.Namespace) -> dict:
    final = eval_df.sort_values("data_seen").groupby(["seed", "task_name", "kind"]).tail(1)
    token_rate = float(acq_token["acquired_at"].notna().mean()) if len(acq_token) else np.nan
    comp = acq_token[acq_token["kind"] == "composite"]
    comp_rate = float(comp["acquired_at"].notna().mean()) if len(comp) else 0.0
    atomic = acq_token[acq_token["kind"] == "atomic"]
    atomic_rate = float(atomic["acquired_at"].notna().mean()) if len(atomic) else 0.0
    mean_final_token = float(final["token_accuracy"].mean()) if len(final) else np.nan
    mean_final_exact = float(final["exact_match"].mean()) if len(final) else np.nan
    passed = bool(
        family.passed
        and token_rate >= args.target_min_acq
        and token_rate <= args.target_max_acq
        and comp_rate >= args.min_composite_acq
    )
    return {
        "candidate_seed": candidate_seed,
        "passed": passed,
        "family_design_passed": bool(family.passed),
        "token_acquisition_rate": token_rate,
        "composite_token_acquisition_rate": comp_rate,
        "atomic_token_acquisition_rate": atomic_rate,
        "mean_final_token_accuracy": mean_final_token,
        "mean_final_exact_match": mean_final_exact,
        "n_tasks": len(family.tasks),
        "n_composites": sum(t.kind == "composite" for t in family.tasks),
        "design_condition_number": float(family.diagnostics.get("design_condition_number", np.nan)),
    }


def _score_candidate(summary: dict, args: argparse.Namespace) -> float:
    # Prefer nontrivial coverage around the middle of the target interval, then composite coverage.
    target_mid = 0.5 * (args.target_min_acq + args.target_max_acq)
    token_rate = float(summary["token_acquisition_rate"])
    comp_rate = float(summary["composite_token_acquisition_rate"])
    score = -abs(token_rate - target_mid) + 0.75 * comp_rate + 0.25 * float(summary["mean_final_token_accuracy"])
    if summary["family_design_passed"]:
        score += 0.25
    if summary["passed"]:
        score += 1.0
    return float(score)


def _fmt(x) -> str:
    if pd.isna(x):
        return "nan"
    return f"{float(x):.3f}"


def _report(cand_df: pd.DataFrame, selected: dict) -> str:
    lines = [
        "# Sequence DSL calibration report",
        "",
        "This gate trains several B1 sequence-DSL candidate families briefly and selects the one with identifiable structure and nontrivial token-accuracy acquisition coverage.",
        "",
        "## Selected family",
        "",
        f"- passed: `{bool(selected['passed'])}`",
        f"- candidate_seed: `{selected['candidate_seed']}`",
        f"- token_acquisition_rate: `{_fmt(selected['token_acquisition_rate'])}`",
        f"- composite_token_acquisition_rate: `{_fmt(selected['composite_token_acquisition_rate'])}`",
        f"- atomic_token_acquisition_rate: `{_fmt(selected['atomic_token_acquisition_rate'])}`",
        f"- mean_final_token_accuracy: `{_fmt(selected['mean_final_token_accuracy'])}`",
        f"- mean_final_exact_match: `{_fmt(selected['mean_final_exact_match'])}`",
        "",
        "## Candidate summary",
        "",
        cand_df.to_markdown(index=False),
        "",
        "## Interpretation",
        "",
        "If this passes, use the selected `structure_table.csv` with `run_sequence_dsl_pilot` for a larger B1 pilot. If it fails, reduce sequence difficulty, increase budget, or simplify the task mix before running shared sweeps.",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
