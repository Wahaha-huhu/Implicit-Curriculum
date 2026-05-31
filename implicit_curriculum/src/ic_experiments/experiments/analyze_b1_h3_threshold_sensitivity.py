from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from ic_experiments.run_management import append_registry, write_manifest
from ic_experiments.sequence_analysis import final_metrics
from ic_experiments.experiments.analyze_b1_h3_interventions import (
    load_pair,
    load_or_compute_acq,
    prepare_acq,
    intervention_contrasts,
    summarize_pair,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Analyze H3 intervention runs across multiple acquisition thresholds.")
    p.add_argument("--result-dir", type=Path, required=True)
    p.add_argument("--metric-family", type=str, default="token_accuracy")
    p.add_argument("--thresholds", type=float, nargs="+", default=[0.3, 0.4, 0.5, 0.6, 0.7])
    p.add_argument("--patience", type=int, default=2)
    p.add_argument("--code-version", type=str, default="v2.1")
    p.add_argument("--run-id", type=str, default=None)
    p.add_argument("--archive-root", type=Path, default=None)
    p.add_argument("--thesis-use", type=str, default="diagnostic")
    return p.parse_args()


def auc_summary(eval_df: pd.DataFrame, metric_family: str) -> pd.DataFrame:
    if eval_df.empty:
        return pd.DataFrame()
    col = metric_family if metric_family in eval_df.columns else "token_accuracy"
    rows = []
    for (condition, seed, task_name), g in eval_df.groupby(["condition", "seed", "task_name"]):
        g = g.sort_values("data_seen")
        x = g["data_seen"].to_numpy(dtype=float)
        y = g[col].to_numpy(dtype=float)
        if len(x) >= 2 and np.nanmax(x) > np.nanmin(x):
            auc = float(np.trapz(y, x) / (np.nanmax(x) - np.nanmin(x)))
        else:
            auc = float(np.nanmean(y)) if len(y) else np.nan
        rows.append({"condition": condition, "seed": int(seed), "task_name": task_name, f"auc_{col}": auc})
    return pd.DataFrame(rows)


def main() -> None:
    args = parse_args()
    result_dir = args.result_dir
    eval_df = pd.read_csv(result_dir / "eval_curves.csv")
    pair = load_pair(result_dir)
    final = final_metrics(eval_df)
    auc = auc_summary(eval_df, args.metric_family)
    all_contrasts = []
    all_summaries = []
    for thr in args.thresholds:
        acq = load_or_compute_acq(result_dir, eval_df, args.metric_family, float(thr), args.patience)
        acq_p = prepare_acq(acq, eval_df, args.metric_family, float(thr))
        contrasts = intervention_contrasts(acq_p, final, pair, args.metric_family)
        contrasts.insert(0, "analysis_threshold", float(thr))
        summary = summarize_pair(acq_p, final, contrasts, pair, args.metric_family)
        summary.insert(0, "analysis_threshold", float(thr))
        all_contrasts.append(contrasts)
        all_summaries.append(summary)
    contrast_df = pd.concat(all_contrasts, ignore_index=True) if all_contrasts else pd.DataFrame()
    summary_df = pd.concat(all_summaries, ignore_index=True) if all_summaries else pd.DataFrame()
    contrast_df.to_csv(result_dir / "h3_threshold_sensitivity_contrasts.csv", index=False)
    summary_df.to_csv(result_dir / "h3_threshold_sensitivity_pair_summary.csv", index=False)
    auc.to_csv(result_dir / "h3_auc_by_condition_task.csv", index=False)
    report = make_report(pair, summary_df, contrast_df, auc, args.metric_family, args.thresholds)
    (result_dir / "h3_threshold_sensitivity_report.md").write_text(report, encoding="utf-8")

    manifest = write_manifest(
        result_dir,
        experiment="B1_H3_threshold_sensitivity_analysis",
        backend="B1_sequence_dsl",
        code_version=args.code_version,
        run_id=args.run_id or f"h3_threshold_sensitivity_{pair['component']}_to_{pair['composite']}",
        command=sys.argv,
        input_paths={"result_dir": str(result_dir)},
        extra={"pair": pair, "metric_family": args.metric_family, "thresholds": args.thresholds, "thesis_use": args.thesis_use},
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
                "output_path": str(result_dir),
                "status": "analyzed",
                "thesis_use": args.thesis_use,
                "created_at_utc": manifest["created_at_utc"],
            },
        )
    print("Saved H3 threshold-sensitivity outputs:")
    for name in ["h3_threshold_sensitivity_report.md", "h3_threshold_sensitivity_contrasts.csv", "h3_threshold_sensitivity_pair_summary.csv", "h3_auc_by_condition_task.csv", "run_manifest.json"]:
        print(f"  {result_dir / name}")


def _fmt(x: object) -> str:
    try:
        if pd.isna(x):
            return "nan"
        return f"{float(x):.3f}"
    except Exception:
        return str(x)


def make_report(pair: dict[str, str], summary: pd.DataFrame, contrasts: pd.DataFrame, auc: pd.DataFrame, metric_family: str, thresholds: list[float]) -> str:
    lines = [
        "# B1 H3 threshold-sensitivity analysis",
        "",
        "This analysis reuses an H3 intervention run and recomputes acquisition-time contrasts at several token-accuracy thresholds. It is intended to diagnose whether a candidate is truly negative or merely too hard for the default threshold.",
        "",
        f"Metric family: `{metric_family}`",
        f"Thresholds: `{', '.join(str(t) for t in thresholds)}`",
        "",
        "## Pair",
        f"- component: `{pair.get('component', '')}`",
        f"- composite: `{pair.get('composite', '')}`",
        f"- same_operation_control: `{pair.get('same_operation_control', '')}`",
        f"- different_operation_control: `{pair.get('different_operation_control', '')}`",
        "",
        "## Composite acquisition by threshold",
    ]
    comp = pair["composite"]
    comp_rows = summary[summary["task_name"] == comp]
    for _, r in comp_rows.iterrows():
        lines.append(f"- threshold `{r['analysis_threshold']}` / `{r['condition']}`: acq={r['acquisition_rate']:.3f}, final={r['mean_final_metric']:.3f}, censored_time={r['mean_censored_acquired_at']:.1f}")
    lines += ["", "## Key exact-vs-control contrasts"]
    key_types = [
        "exact_pretrain_vs_same_operation",
        "exact_pretrain_vs_different_operation",
        "exact_strong_corrupt_vs_same_operation",
        "exact_strong_corrupt_vs_different_operation",
        "exact_strong_delay_vs_same_operation",
        "exact_strong_delay_vs_different_operation",
        "exact_vs_same_operation",
        "exact_vs_different_operation",
    ]
    c = contrasts[contrasts["contrast_type"].isin(key_types)] if not contrasts.empty else pd.DataFrame()
    if c.empty:
        lines.append("No key contrasts found for the available condition set.")
    else:
        for _, r in c.iterrows():
            lines.append(
                f"- threshold `{r['analysis_threshold']}` / `{r['contrast_type']}`: "
                f"censored Δ={_fmt(r['censored_delta_acquired_at_mean'])}, "
                f"censored-rate={_fmt(r['censored_expected_direction_rate'])}, "
                f"Δfinal={_fmt(r['final_metric_delta_mean'])}"
            )
    lines += ["", "## AUC note"]
    if not auc.empty:
        comp_auc = auc[auc["task_name"] == comp]
        col = f"auc_{metric_family}"
        for cond, g in comp_auc.groupby("condition"):
            lines.append(f"- `{cond}`: mean AUC={g[col].mean():.3f}")
    lines += [
        "",
        "## Interpretation rule",
        "If contrasts appear only at very low thresholds, interpret them as subthreshold learning shifts rather than clear acquisition. If no threshold shows contrast and final/AUC are flat, the pair is non-informative. If exact-component contrasts persist across moderate thresholds and final/AUC agree, the result is stronger.",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
