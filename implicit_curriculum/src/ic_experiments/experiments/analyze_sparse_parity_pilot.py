from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from ic_experiments.metrics import acquisition_times


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Analyze B2 sparse-parity pilot without component/control assumptions.")
    p.add_argument("--result-dir", type=Path, required=True)
    p.add_argument("--thresholds", type=float, nargs="+", default=[0.75, 0.85, 0.90])
    p.add_argument("--metric", type=str, default="balanced_accuracy")
    p.add_argument("--patience", type=int, default=2)
    return p.parse_args()


def _load_structure_table(result_dir: Path) -> pd.DataFrame:
    for candidate in [result_dir / "structure_table.csv", result_dir.parent / "sparse_parity_design" / "structure_table.csv"]:
        if candidate.exists():
            return pd.read_csv(candidate)
    raise FileNotFoundError("Could not find structure_table.csv in result dir or sibling sparse_parity_design directory")


def _degree_from_row(row: pd.Series) -> float:
    if "reference_learnability" in row and pd.notna(row["reference_learnability"]):
        return float(row["reference_learnability"])
    name = str(row.get("task_name", row.get("structure_id", "")))
    if "_d" in name:
        try:
            return float(name.split("_d", 1)[1].split("_", 1)[0])
        except Exception:
            pass
    return np.nan


def _spearman(x: pd.Series, y: pd.Series) -> float:
    tmp = pd.DataFrame({"x": x, "y": y}).replace([np.inf, -np.inf], np.nan).dropna()
    if len(tmp) < 3 or tmp["x"].nunique() < 2 or tmp["y"].nunique() < 2:
        return np.nan
    return float(tmp["x"].rank().corr(tmp["y"].rank()))


def _auc_summary(eval_df: pd.DataFrame, metric: str) -> pd.DataFrame:
    rows = []
    for keys, g in eval_df.sort_values("data_seen").groupby(["condition", "seed", "task_name", "kind"]):
        condition, seed, task_name, kind = keys
        xs = g["data_seen"].to_numpy(dtype=float)
        ys = g[metric].to_numpy(dtype=float)
        if len(xs) < 2:
            auc = np.nan
        else:
            denom = max(xs[-1] - xs[0], 1.0)
            auc = float(np.trapz(ys, xs) / denom)
        rows.append({"condition": condition, "seed": int(seed), "task_name": task_name, "kind": kind, f"auc_{metric}": auc})
    return pd.DataFrame(rows)


def main() -> None:
    args = parse_args()
    result_dir = args.result_dir
    eval_path = result_dir / "eval_curves.csv"
    if not eval_path.exists():
        raise FileNotFoundError(eval_path)
    eval_df = pd.read_csv(eval_path)
    structure = _load_structure_table(result_dir)
    if "task_name" not in structure.columns:
        structure["task_name"] = structure.get("structure_id")
    structure["degree"] = structure.apply(_degree_from_row, axis=1)
    keep_cols = [c for c in ["task_name", "frequency", "reference_learnability", "degree"] if c in structure.columns]
    meta = structure[keep_cols].drop_duplicates("task_name")

    # Recompute acquisition for multiple thresholds. The generic pilot may have
    # produced a single 0.90 file, but sparse parity needs threshold sensitivity.
    acq_tables = []
    for threshold in args.thresholds:
        acq = acquisition_times(eval_df, threshold=threshold, patience=args.patience, metric=args.metric)
        acq["analysis_threshold"] = threshold
        acq_tables.append(acq)
    acq_all = pd.concat(acq_tables, ignore_index=True)
    acq_all.to_csv(result_dir / "sparse_parity_acquisition_times.csv", index=False)

    auc = _auc_summary(eval_df, args.metric)
    auc.to_csv(result_dir / "sparse_parity_auc.csv", index=False)

    final = eval_df.sort_values("data_seen").groupby(["condition", "seed", "task_name", "kind"]).tail(1)
    final = final.merge(meta, on="task_name", how="left")
    acq_meta = acq_all.merge(meta, on="task_name", how="left")

    rows = []
    for threshold, g in acq_meta.groupby("analysis_threshold"):
        baseline = g[g["condition"] == "baseline"].copy()
        final_base = final[final["condition"] == "baseline"].copy()
        rows.append(
            {
                "threshold": float(threshold),
                "metric": args.metric,
                "n_rows": int(len(baseline)),
                "acquisition_rate": float(baseline["acquired_at"].notna().mean()) if len(baseline) else np.nan,
                "mean_acquired_at": float(baseline["acquired_at"].mean()) if baseline["acquired_at"].notna().any() else np.nan,
                "time_spearman_frequency": _spearman(baseline["frequency"], baseline["acquired_at"]),
                "time_spearman_degree": _spearman(baseline["degree"], baseline["acquired_at"]),
                "final_spearman_frequency": _spearman(final_base["frequency"], final_base[args.metric]),
                "final_spearman_degree": _spearman(final_base["degree"], final_base[args.metric]),
            }
        )
    summary = pd.DataFrame(rows)
    summary.to_csv(result_dir / "sparse_parity_ordering_summary.csv", index=False)

    by_degree = final[final["condition"] == "baseline"].groupby("degree").agg(
        n=(args.metric, "size"),
        mean_final_metric=(args.metric, "mean"),
        mean_final_loss=("loss", "mean"),
    ).reset_index()
    by_degree.to_csv(result_dir / "sparse_parity_degree_summary.csv", index=False)

    (result_dir / "sparse_parity_analysis_report.md").write_text(_report(summary, by_degree, args.metric), encoding="utf-8")
    print("Saved sparse parity analysis outputs:")
    for name in [
        "sparse_parity_analysis_report.md",
        "sparse_parity_acquisition_times.csv",
        "sparse_parity_ordering_summary.csv",
        "sparse_parity_degree_summary.csv",
        "sparse_parity_auc.csv",
    ]:
        print(f"  {result_dir / name}")


def _fmt(x: float) -> str:
    if pd.isna(x):
        return "nan"
    return f"{float(x):.3f}"


def _report(summary: pd.DataFrame, by_degree: pd.DataFrame, metric: str) -> str:
    lines = [
        "# Sparse parity pilot analysis report",
        "",
        "This is B2-specific analysis. It intentionally ignores components, controls, and formal utility because sparse parity is the quanta-comparable baseline, not a dependency test.",
        "",
        f"Metric: `{metric}`",
        "",
        "## Threshold sensitivity",
        "",
    ]
    for row in summary.to_dict(orient="records"):
        lines.append(
            f"- threshold `{row['threshold']}`: acquisition_rate={_fmt(row['acquisition_rate'])}, "
            f"time-Spearman(freq)={_fmt(row['time_spearman_frequency'])}, "
            f"time-Spearman(degree)={_fmt(row['time_spearman_degree'])}, "
            f"final-Spearman(freq)={_fmt(row['final_spearman_frequency'])}, "
            f"final-Spearman(degree)={_fmt(row['final_spearman_degree'])}"
        )
    lines += ["", "## Final metric by degree", ""]
    for row in by_degree.to_dict(orient="records"):
        lines.append(f"- degree `{row['degree']}`: n={int(row['n'])}, mean_final_metric={_fmt(row['mean_final_metric'])}, mean_final_loss={_fmt(row['mean_final_loss'])}")
    lines += [
        "",
        "## Decision rule",
        "",
        "GREEN requires nontrivial acquisition coverage under at least one threshold, frequency/final-metric signs in the expected direction, and degree making harder parities worse or later. If acquisition remains near zero, tune degree/budget before using B2 as a quanta baseline.",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
