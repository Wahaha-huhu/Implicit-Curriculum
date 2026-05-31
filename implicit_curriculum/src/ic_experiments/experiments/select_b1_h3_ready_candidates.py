from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from ic_experiments.metrics import acquisition_times
from ic_experiments.run_management import append_registry, write_manifest
from ic_experiments.sequence_analysis import final_metrics


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Select H3-ready composite candidates using H2 residuals plus H1 learning/readiness metrics.")
    p.add_argument("--h1-result-dir", type=Path, required=True, help="B1 H1 shared-sweep directory containing eval_curves.csv and structure_table.csv")
    p.add_argument("--pair-selection", type=Path, required=True, help="h2_pair_selection.csv from the same family")
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--metric-family", type=str, default="token_accuracy")
    p.add_argument("--thresholds", type=float, nargs="+", default=[0.3, 0.4, 0.5, 0.6, 0.7])
    p.add_argument("--target-threshold", type=float, default=0.5, help="Threshold used as a moderate H3-readiness indicator.")
    p.add_argument("--min-final", type=float, default=0.15)
    p.add_argument("--max-final", type=float, default=0.90)
    p.add_argument("--min-acq-rate", type=float, default=0.05)
    p.add_argument("--min-residual", type=float, default=0.0)
    p.add_argument("--top-n", type=int, default=20)
    p.add_argument("--code-version", type=str, default="v2.1")
    p.add_argument("--archive-root", type=Path, default=None)
    p.add_argument("--thesis-use", type=str, default="diagnostic")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    eval_df = pd.read_csv(args.h1_result_dir / "eval_curves.csv")
    structure = pd.read_csv(args.h1_result_dir / "structure_table.csv")
    pairs = pd.read_csv(args.pair_selection)
    final = final_metrics(eval_df)
    final_col = args.metric_family if args.metric_family in final.columns else "token_accuracy"

    comp_final = final.groupby("task_name", as_index=False).agg(
        mean_final_metric=(final_col, "mean"),
        max_final_metric=(final_col, "max"),
        min_final_metric=(final_col, "min"),
    )
    readiness = comp_final.copy()
    for thr in args.thresholds:
        acq = acquisition_times(eval_df, threshold=float(thr), patience=2, metric=args.metric_family)
        rate = acq.groupby("task_name", as_index=False).agg(**{f"acq_rate_t{_safe_thr(thr)}": ("acquired_at", lambda s: float(s.notna().mean()))})
        readiness = readiness.merge(rate, on="task_name", how="left")

    # Pull residual and pair information; support either task/composite columns or infer from common schema.
    p = normalize_pair_selection(pairs)
    comp_res = p.groupby("composite", as_index=False).agg(
        mean_residual_log_time=("residual_log_time", "mean"),
        max_residual_log_time=("residual_log_time", "max"),
        positive_rate=("positive_rate", "max"),
        n_candidate_components=("component", "nunique"),
    )
    table = comp_res.merge(readiness.rename(columns={"task_name": "composite"}), on="composite", how="left")
    meta_cols = [c for c in ["task_name", "kind", "op", "frequency", "reference_learnability", "formal_utility", "components"] if c in structure.columns]
    if meta_cols:
        table = table.merge(structure[meta_cols].drop_duplicates("task_name").rename(columns={"task_name": "composite"}), on="composite", how="left")
    target_col = f"acq_rate_t{_safe_thr(args.target_threshold)}"
    if target_col not in table.columns:
        target_col = next((c for c in table.columns if c.startswith("acq_rate_t")), "")
    table["residual_pass"] = table["max_residual_log_time"].fillna(-np.inf) >= args.min_residual
    table["final_pass"] = table["mean_final_metric"].between(args.min_final, args.max_final, inclusive="both")
    table["acq_pass"] = table[target_col].fillna(0.0) >= args.min_acq_rate if target_col else False
    table["h3_ready"] = table["residual_pass"] & table["final_pass"] & table["acq_pass"]
    # Score prefers residuals that are large but measurable, with partial acquisition and final score away from floor/ceiling.
    mid = (args.min_final + args.max_final) / 2.0
    final_mid_score = 1.0 - (table["mean_final_metric"].fillna(0.0) - mid).abs() / max(1e-6, (args.max_final - args.min_final) / 2.0)
    final_mid_score = final_mid_score.clip(0.0, 1.0)
    table["h3_readiness_score"] = (
        table["max_residual_log_time"].fillna(0.0).clip(lower=0.0)
        + 2.0 * table.get(target_col, pd.Series(0.0, index=table.index)).fillna(0.0)
        + final_mid_score
        + table["h3_ready"].astype(float)
    )
    table = table.sort_values(["h3_ready", "h3_readiness_score", "max_residual_log_time"], ascending=[False, False, False])
    table.to_csv(args.output_dir / "h3_readiness_composite_table.csv", index=False)

    pair_ready = p.merge(table[["composite", "h3_ready", "h3_readiness_score", "mean_final_metric", target_col, "max_residual_log_time"]], on="composite", how="left")
    pair_ready = pair_ready.sort_values(["h3_ready", "h3_readiness_score", "residual_log_time"], ascending=[False, False, False])
    pair_ready.head(args.top_n).to_csv(args.output_dir / "h3_ready_pair_selection.csv", index=False)
    report = make_report(args, table, pair_ready, target_col)
    (args.output_dir / "h3_readiness_report.md").write_text(report, encoding="utf-8")
    manifest = write_manifest(
        args.output_dir,
        experiment="B1_H3_readiness_selection",
        backend="B1_sequence_dsl",
        code_version=args.code_version,
        run_id="b1_h3_readiness_selection",
        command=sys.argv,
        input_paths={"h1_result_dir": str(args.h1_result_dir), "pair_selection": str(args.pair_selection)},
        extra={"metric_family": args.metric_family, "thresholds": args.thresholds, "thesis_use": args.thesis_use},
    )
    if args.archive_root is not None:
        append_registry(args.archive_root / "results_registry.csv", {
            "run_id": manifest["run_id"], "code_version": args.code_version, "git_sha": manifest["git_sha"],
            "experiment": manifest["experiment"], "backend": manifest["backend"], "output_path": str(args.output_dir),
            "status": "analyzed", "thesis_use": args.thesis_use, "created_at_utc": manifest["created_at_utc"],
        })
    print("Saved H3-readiness outputs:")
    for name in ["h3_readiness_report.md", "h3_readiness_composite_table.csv", "h3_ready_pair_selection.csv", "run_manifest.json"]:
        print(f"  {args.output_dir / name}")


def normalize_pair_selection(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    # v0.9/v2.0 files use component/composite/residual_log_time/positive_rate.
    aliases = {
        "component_task": "component",
        "component_id": "component",
        "composite_task": "composite",
        "composite_id": "composite",
        "mean_residual_log_time": "residual_log_time",
        "residual": "residual_log_time",
    }
    for old, new in aliases.items():
        if old in out.columns and new not in out.columns:
            out[new] = out[old]
    for col in ["component", "composite"]:
        if col not in out.columns:
            raise ValueError(f"pair selection file must contain {col!r} column; columns={list(out.columns)}")
    if "residual_log_time" not in out.columns:
        out["residual_log_time"] = 0.0
    if "positive_rate" not in out.columns:
        out["positive_rate"] = np.nan
    return out


def _safe_thr(x: float) -> str:
    return str(float(x)).replace(".", "p")


def make_report(args: argparse.Namespace, table: pd.DataFrame, pair_ready: pd.DataFrame, target_col: str) -> str:
    lines = [
        "# B1 H3-readiness selection report",
        "",
        "This report combines H2 residuals with H1 learning/readiness metrics. It is designed to avoid selecting composites that are maximally delayed but too hard to test by intervention.",
        "",
        f"Metric: `{args.metric_family}`",
        f"Readiness threshold column: `{target_col}`",
        "",
        "## Composite readiness summary",
        f"- candidate composites: `{len(table)}`",
        f"- H3-ready composites: `{int(table['h3_ready'].sum())}`",
        f"- min_final: `{args.min_final}`; max_final: `{args.max_final}`; min_acq_rate: `{args.min_acq_rate}`; min_residual: `{args.min_residual}`",
        "",
        "## Top composites",
    ]
    for _, r in table.head(10).iterrows():
        lines.append(
            f"- `{r['composite']}`: ready={bool(r['h3_ready'])}, score={r['h3_readiness_score']:.3f}, "
            f"residual={r['max_residual_log_time']:.3f}, final={r['mean_final_metric']:.3f}, {target_col}={r.get(target_col, np.nan):.3f}"
        )
    lines += ["", "## Top pair candidates"]
    for _, r in pair_ready.head(12).iterrows():
        lines.append(
            f"- `{r['component']}` → `{r['composite']}`: ready={bool(r.get('h3_ready', False))}, "
            f"score={r.get('h3_readiness_score', np.nan):.3f}, residual={r.get('residual_log_time', np.nan):.3f}"
        )
    lines += [
        "",
        "## Interpretation rule",
        "Use this selector before expensive H3 runs. Very large residuals with near-zero final metric or zero low-threshold acquisition should be considered hard-composite failures rather than good intervention candidates.",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
