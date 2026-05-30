from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from ic_experiments.metrics import acquisition_times


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Analyze B1 sequence-DSL pilot/calibration with sequence-appropriate metrics.")
    p.add_argument("--result-dir", type=Path, required=True)
    p.add_argument("--token-thresholds", type=float, nargs="+", default=[0.50, 0.70, 0.85])
    p.add_argument("--exact-thresholds", type=float, nargs="+", default=[0.20, 0.50, 0.80])
    p.add_argument("--patience", type=int, default=2)
    return p.parse_args()


def _spearman(x: pd.Series, y: pd.Series) -> float:
    tmp = pd.DataFrame({"x": x, "y": y}).replace([np.inf, -np.inf], np.nan).dropna()
    if len(tmp) < 3 or tmp["x"].nunique() < 2 or tmp["y"].nunique() < 2:
        return np.nan
    return float(tmp["x"].rank().corr(tmp["y"].rank()))


def _auc(eval_df: pd.DataFrame, metric: str) -> pd.DataFrame:
    rows = []
    for keys, g in eval_df.sort_values("data_seen").groupby(["condition", "seed", "task_name", "kind"]):
        condition, seed, task_name, kind = keys
        xs = g["data_seen"].to_numpy(dtype=float)
        ys = g[metric].to_numpy(dtype=float)
        auc = np.nan if len(xs) < 2 else float(np.trapz(ys, xs) / max(xs[-1] - xs[0], 1.0))
        rows.append({"condition": condition, "seed": int(seed), "task_name": task_name, "kind": kind, f"auc_{metric}": auc})
    return pd.DataFrame(rows)


def _load_structure(result_dir: Path) -> pd.DataFrame:
    path = result_dir / "structure_table.csv"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    if "task_name" not in df.columns and "structure_id" in df.columns:
        df["task_name"] = df["structure_id"]
    return df


def main() -> None:
    args = parse_args()
    result_dir = args.result_dir
    eval_df = pd.read_csv(result_dir / "eval_curves.csv")
    structure = _load_structure(result_dir)
    meta_cols = [c for c in ["task_name", "frequency", "reference_learnability", "formal_utility", "components", "control_type"] if c in structure.columns]
    meta = structure[meta_cols].drop_duplicates("task_name") if meta_cols else pd.DataFrame()

    acq_tables = []
    for threshold in args.token_thresholds:
        acq = acquisition_times(eval_df, threshold=threshold, patience=args.patience, metric="token_accuracy")
        acq["metric_family"] = "token_accuracy"
        acq["analysis_threshold"] = threshold
        acq_tables.append(acq)
    for threshold in args.exact_thresholds:
        acq = acquisition_times(eval_df, threshold=threshold, patience=args.patience, metric="exact_match")
        acq["metric_family"] = "exact_match"
        acq["analysis_threshold"] = threshold
        acq_tables.append(acq)
    acq_all = pd.concat(acq_tables, ignore_index=True)
    acq_all.to_csv(result_dir / "sequence_acquisition_times_multi_metric.csv", index=False)

    auc = _auc(eval_df, "token_accuracy").merge(_auc(eval_df, "exact_match"), on=["condition", "seed", "task_name", "kind"], how="outer")
    auc.to_csv(result_dir / "sequence_auc.csv", index=False)

    final = eval_df.sort_values("data_seen").groupby(["condition", "seed", "task_name", "kind"]).tail(1)
    if not meta.empty:
        final = final.merge(meta, on="task_name", how="left")
        acq_meta = acq_all.merge(meta, on="task_name", how="left")
    else:
        acq_meta = acq_all.copy()

    rows = []
    for (metric_family, threshold), g in acq_meta.groupby(["metric_family", "analysis_threshold"]):
        base = g[g["condition"] == "baseline"].copy()
        metric = metric_family
        final_base = final[final["condition"] == "baseline"].copy()
        rows.append(
            {
                "metric_family": metric_family,
                "threshold": float(threshold),
                "n": int(len(base)),
                "acquisition_rate": float(base["acquired_at"].notna().mean()) if len(base) else np.nan,
                "mean_acquired_at": float(base["acquired_at"].mean()) if base["acquired_at"].notna().any() else np.nan,
                "time_spearman_frequency": _spearman(base.get("frequency", pd.Series(dtype=float)), base["acquired_at"]),
                "time_spearman_reference_learnability": _spearman(base.get("reference_learnability", pd.Series(dtype=float)), base["acquired_at"]),
                "time_spearman_formal_utility": _spearman(base.get("formal_utility", pd.Series(dtype=float)), base["acquired_at"]),
                "final_spearman_frequency": _spearman(final_base.get("frequency", pd.Series(dtype=float)), final_base[metric] if metric in final_base else pd.Series(dtype=float)),
                "final_spearman_reference_learnability": _spearman(final_base.get("reference_learnability", pd.Series(dtype=float)), final_base[metric] if metric in final_base else pd.Series(dtype=float)),
                "final_spearman_formal_utility": _spearman(final_base.get("formal_utility", pd.Series(dtype=float)), final_base[metric] if metric in final_base else pd.Series(dtype=float)),
            }
        )
    summary = pd.DataFrame(rows)
    summary.to_csv(result_dir / "sequence_ordering_summary.csv", index=False)

    by_kind = final[final["condition"] == "baseline"].groupby("kind").agg(
        n=("task_name", "size"),
        mean_final_exact_match=("exact_match", "mean"),
        mean_final_token_accuracy=("token_accuracy", "mean"),
        mean_final_loss=("loss", "mean"),
    ).reset_index()
    by_kind.to_csv(result_dir / "sequence_final_by_kind.csv", index=False)

    (result_dir / "sequence_dsl_analysis_report.md").write_text(_report(summary, by_kind), encoding="utf-8")
    print("Saved sequence DSL analysis outputs:")
    for name in [
        "sequence_dsl_analysis_report.md",
        "sequence_acquisition_times_multi_metric.csv",
        "sequence_ordering_summary.csv",
        "sequence_final_by_kind.csv",
        "sequence_auc.csv",
    ]:
        print(f"  {result_dir / name}")


def _fmt(x) -> str:
    if pd.isna(x):
        return "nan"
    return f"{float(x):.3f}"


def _report(summary: pd.DataFrame, by_kind: pd.DataFrame) -> str:
    lines = [
        "# Sequence DSL analysis report",
        "",
        "This is B1-specific analysis. It treats token accuracy, exact match, loss/AUC, and right-censored acquisition as separate calibration observables rather than relying on a single exact-match threshold.",
        "",
        "## Acquisition threshold sensitivity",
        "",
    ]
    for row in summary.to_dict(orient="records"):
        lines.append(
            f"- {row['metric_family']} threshold `{row['threshold']}`: acquisition_rate={_fmt(row['acquisition_rate'])}, "
            f"time-Spearman(freq)={_fmt(row['time_spearman_frequency'])}, "
            f"time-Spearman(learnability)={_fmt(row['time_spearman_reference_learnability'])}, "
            f"time-Spearman(utility)={_fmt(row['time_spearman_formal_utility'])}"
        )
    lines += ["", "## Final metrics by kind", ""]
    for row in by_kind.to_dict(orient="records"):
        lines.append(
            f"- {row['kind']}: n={int(row['n'])}, exact={_fmt(row['mean_final_exact_match'])}, "
            f"token={_fmt(row['mean_final_token_accuracy'])}, loss={_fmt(row['mean_final_loss'])}"
        )
    lines += [
        "",
        "## Calibration decision rule",
        "",
        "GREEN requires nonzero and non-saturated token-accuracy acquisition, improving exact match or loss, and at least moderate composite/control coverage. Exact-match 0.90 is intentionally not required at this stage.",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
