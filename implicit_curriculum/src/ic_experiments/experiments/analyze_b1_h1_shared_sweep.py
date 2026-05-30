from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from ic_experiments.metrics import acquisition_times
from ic_experiments.sequence_analysis import realization_summary, stratified_ordering_summary


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Analyze B1 H1 shared sweep for ordering and sign-stability.")
    p.add_argument("--result-dir", type=Path, required=True)
    p.add_argument("--token-thresholds", type=float, nargs="+", default=[0.50, 0.70, 0.85])
    p.add_argument("--exact-thresholds", type=float, nargs="+", default=[0.20, 0.50])
    p.add_argument("--patience", type=int, default=2)
    p.add_argument("--primary-metric", type=str, default="token_accuracy")
    p.add_argument("--primary-threshold", type=float, default=0.70)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    result_dir = args.result_dir
    eval_df = pd.read_csv(result_dir / "eval_curves.csv")
    structure = _load_structure(result_dir)
    final = eval_df.sort_values("data_seen").groupby(["condition", "seed", "task_name", "kind"], as_index=False).tail(1)
    meta = _meta(structure)
    if not meta.empty:
        final = final.merge(meta, on="task_name", how="left", suffixes=("", "_meta"))

    acq_tables = []
    for threshold in args.token_thresholds:
        acq = acquisition_times(eval_df, threshold=threshold, patience=args.patience, metric="token_accuracy")
        acq["metric_family"] = "token_accuracy"
        acq["analysis_threshold"] = float(threshold)
        acq_tables.append(acq)
    for threshold in args.exact_thresholds:
        acq = acquisition_times(eval_df, threshold=threshold, patience=args.patience, metric="exact_match")
        acq["metric_family"] = "exact_match"
        acq["analysis_threshold"] = float(threshold)
        acq_tables.append(acq)
    acq_all = pd.concat(acq_tables, ignore_index=True) if acq_tables else pd.DataFrame()
    if not meta.empty:
        acq_all = acq_all.merge(meta, on="task_name", how="left", suffixes=("", "_meta"))
    acq_all.to_csv(result_dir / "h1_acquisition_times_multi_metric.csv", index=False)

    threshold_summary = _threshold_summary(acq_all, final)
    threshold_summary.to_csv(result_dir / "h1_threshold_sensitivity.csv", index=False)

    sign = _sign_stability(acq_all, final, args.primary_metric, args.primary_threshold)
    sign.to_csv(result_dir / "h1_sign_stability.csv", index=False)

    config_summary = _config_summary(acq_all, final, args.primary_metric, args.primary_threshold)
    config_summary.to_csv(result_dir / "h1_config_summary.csv", index=False)

    seed_summary = _seed_summary(acq_all, args.primary_metric, args.primary_threshold)
    seed_summary.to_csv(result_dir / "h1_seed_summary.csv", index=False)

    stratified_parts = []
    for threshold in args.token_thresholds:
        stratified_parts.append(stratified_ordering_summary(acq_all, final, structure, "token_accuracy", threshold))
    for threshold in args.exact_thresholds:
        stratified_parts.append(stratified_ordering_summary(acq_all, final, structure, "exact_match", threshold))
    nonempty_strata = [p for p in stratified_parts if p is not None and not p.empty]
    stratified = pd.concat(nonempty_strata, ignore_index=True) if nonempty_strata else pd.DataFrame()
    stratified.to_csv(result_dir / "h1_stratified_ordering_summary.csv", index=False)

    bootstrap = _bootstrap_sign_ci(acq_all, args.primary_metric, args.primary_threshold, n_boot=500, seed=0)
    bootstrap.to_csv(result_dir / "h1_bootstrap_sign_ci.csv", index=False)

    freq_summary = pd.DataFrame()
    freq_path = result_dir / "frequency_realization.csv"
    if freq_path.exists():
        freq_summary = realization_summary(pd.read_csv(freq_path))
        freq_summary.to_csv(result_dir / "frequency_realization_summary.csv", index=False)

    report = _report(
        threshold_summary=threshold_summary,
        sign=sign,
        config_summary=config_summary,
        seed_summary=seed_summary,
        stratified=stratified,
        bootstrap=bootstrap,
        freq_summary=freq_summary,
        primary_metric=args.primary_metric,
        primary_threshold=args.primary_threshold,
    )
    (result_dir / "b1_h1_analysis_report.md").write_text(report, encoding="utf-8")
    print("Saved B1 H1 analysis outputs:")
    for name in [
        "b1_h1_analysis_report.md", "h1_acquisition_times_multi_metric.csv", "h1_threshold_sensitivity.csv",
        "h1_sign_stability.csv", "h1_config_summary.csv", "h1_seed_summary.csv",
        "h1_stratified_ordering_summary.csv", "h1_bootstrap_sign_ci.csv", "frequency_realization_summary.csv",
    ]:
        print(f"  {result_dir / name}")


def _load_structure(result_dir: Path) -> pd.DataFrame:
    structure = pd.read_csv(result_dir / "structure_table.csv")
    if "task_name" not in structure.columns and "structure_id" in structure.columns:
        structure["task_name"] = structure["structure_id"]
    diff_path = result_dir / "sequence_difficulty_table.csv"
    if diff_path.exists():
        diff = pd.read_csv(diff_path)
        if "task_name" not in diff.columns and "structure_id" in diff.columns:
            diff["task_name"] = diff["structure_id"]
        add_cols = [c for c in diff.columns if c not in structure.columns or c == "task_name"]
        structure = structure.merge(diff[add_cols].drop_duplicates("task_name"), on="task_name", how="left")
    return structure


def _meta(structure: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "task_name", "frequency", "reference_learnability", "formal_utility", "kind", "op", "operation_type",
        "target_length", "output_entropy", "random_baseline_token_accuracy", "copy_fraction", "composition_depth", "control_type",
    ]
    return structure[[c for c in cols if c in structure.columns]].drop_duplicates("task_name")


def _spearman(x: pd.Series, y: pd.Series) -> float:
    tmp = pd.DataFrame({"x": x, "y": y}).replace([np.inf, -np.inf], np.nan).dropna()
    if len(tmp) < 3 or tmp["x"].nunique() < 2 or tmp["y"].nunique() < 2:
        return np.nan
    return float(tmp["x"].rank().corr(tmp["y"].rank()))


def _expected_sign_ok(predictor: str, value: float) -> bool | float:
    if pd.isna(value):
        return np.nan
    if predictor in {"frequency", "formal_utility"}:
        return bool(value < 0)
    if predictor == "reference_learnability":
        return bool(value > 0)
    return np.nan


def _threshold_summary(acq: pd.DataFrame, final: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (metric_family, threshold, condition), g in acq.groupby(["metric_family", "analysis_threshold", "condition"]):
        f = final[final["condition"] == condition]
        metric_col = metric_family if metric_family in f else "token_accuracy"
        for stratum_name, gg, ff in _basic_strata(g, f):
            rows.append(_summary_row(metric_family, threshold, condition, stratum_name, gg, ff, metric_col))
    return pd.DataFrame(rows)


def _basic_strata(acq: pd.DataFrame, final: pd.DataFrame):
    yield "all", acq, final
    if "kind" in acq.columns:
        true = {"atomic", "composite"}
        yield "true_tasks_atomic_composite", acq[acq["kind"].isin(true)], final[final["kind"].isin(true)]
        for kind in sorted(acq["kind"].dropna().unique()):
            yield f"kind={kind}", acq[acq["kind"] == kind], final[final["kind"] == kind]


def _summary_row(metric_family: str, threshold: float, condition: str, stratum: str, g: pd.DataFrame, f: pd.DataFrame, metric_col: str) -> dict:
    row = {
        "metric_family": metric_family,
        "threshold": float(threshold),
        "condition": condition,
        "stratum": stratum,
        "n": int(len(g)),
        "n_tasks": int(g["task_name"].nunique()) if "task_name" in g else 0,
        "acquisition_rate": float(g["acquired_at"].notna().mean()) if len(g) else np.nan,
        "mean_acquired_at": float(g["acquired_at"].mean()) if len(g) and g["acquired_at"].notna().any() else np.nan,
    }
    for predictor in ["frequency", "reference_learnability", "formal_utility"]:
        val = _spearman(g.get(predictor, pd.Series(dtype=float)), g["acquired_at"] if "acquired_at" in g else pd.Series(dtype=float))
        row[f"time_spearman_{predictor}"] = val
        row[f"time_sign_ok_{predictor}"] = _expected_sign_ok(predictor, val)
        fval = _spearman(f.get(predictor, pd.Series(dtype=float)), f[metric_col] if metric_col in f else pd.Series(dtype=float))
        row[f"final_spearman_{predictor}"] = fval
    return row


def _sign_stability(acq: pd.DataFrame, final: pd.DataFrame, metric_family: str, threshold: float) -> pd.DataFrame:
    rows = []
    base = acq[(acq["metric_family"] == metric_family) & (np.isclose(acq["analysis_threshold"], threshold))]
    for stratum in ["all", "true_tasks_atomic_composite", "kind=atomic", "kind=composite"]:
        if stratum == "all":
            g = base
        elif stratum == "true_tasks_atomic_composite":
            g = base[base["kind"].isin({"atomic", "composite"})]
        elif stratum.startswith("kind="):
            kind = stratum.split("=", 1)[1]
            g = base[base["kind"] == kind]
        else:
            continue
        for predictor in ["frequency", "reference_learnability", "formal_utility"]:
            per_config = []
            for condition, gg in g.groupby("condition"):
                val = _spearman(gg.get(predictor, pd.Series(dtype=float)), gg["acquired_at"])
                ok = _expected_sign_ok(predictor, val)
                per_config.append((condition, val, ok))
            valid = [(c, v, ok) for c, v, ok in per_config if not pd.isna(ok)]
            rows.append({
                "metric_family": metric_family,
                "threshold": float(threshold),
                "stratum": stratum,
                "predictor": predictor,
                "n_configs_with_signal": len(valid),
                "sign_stability_rate": float(np.mean([ok for _, _, ok in valid])) if valid else np.nan,
                "mean_time_spearman": _nanmean([v for _, v, _ in per_config]),
                "min_time_spearman": _nanmin([v for _, v, _ in per_config]),
                "max_time_spearman": _nanmax([v for _, v, _ in per_config]),
                "per_config_values": ";".join(f"{c}:{v:.3f}" for c, v, _ in per_config if not pd.isna(v)),
            })
    return pd.DataFrame(rows)



def _nanmean(values) -> float:
    vals = np.array([v for v in values if not pd.isna(v)], dtype=float)
    return float(vals.mean()) if len(vals) else np.nan

def _nanmin(values) -> float:
    vals = np.array([v for v in values if not pd.isna(v)], dtype=float)
    return float(vals.min()) if len(vals) else np.nan

def _nanmax(values) -> float:
    vals = np.array([v for v in values if not pd.isna(v)], dtype=float)
    return float(vals.max()) if len(vals) else np.nan

def _config_summary(acq: pd.DataFrame, final: pd.DataFrame, metric_family: str, threshold: float) -> pd.DataFrame:
    sub = acq[(acq["metric_family"] == metric_family) & (np.isclose(acq["analysis_threshold"], threshold))]
    rows = []
    for condition, g in sub.groupby("condition"):
        f = final[final["condition"] == condition]
        rows.append(_summary_row(metric_family, threshold, condition, "all", g, f, metric_family))
        true = g[g["kind"].isin({"atomic", "composite"})]
        ftrue = f[f["kind"].isin({"atomic", "composite"})]
        rows.append(_summary_row(metric_family, threshold, condition, "true_tasks_atomic_composite", true, ftrue, metric_family))
    return pd.DataFrame(rows)


def _seed_summary(acq: pd.DataFrame, metric_family: str, threshold: float) -> pd.DataFrame:
    sub = acq[(acq["metric_family"] == metric_family) & (np.isclose(acq["analysis_threshold"], threshold))]
    rows = []
    for (condition, seed), g in sub.groupby(["condition", "seed"]):
        row = {"condition": condition, "seed": int(seed), "n": len(g), "acquisition_rate": float(g["acquired_at"].notna().mean())}
        for predictor in ["frequency", "reference_learnability", "formal_utility"]:
            val = _spearman(g.get(predictor, pd.Series(dtype=float)), g["acquired_at"])
            row[f"time_spearman_{predictor}"] = val
            row[f"time_sign_ok_{predictor}"] = _expected_sign_ok(predictor, val)
        rows.append(row)
    return pd.DataFrame(rows)


def _bootstrap_sign_ci(acq: pd.DataFrame, metric_family: str, threshold: float, n_boot: int = 500, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    sub = acq[(acq["metric_family"] == metric_family) & (np.isclose(acq["analysis_threshold"], threshold))].copy()
    rows = []
    for condition, g in sub.groupby("condition"):
        seeds = np.array(sorted(g["seed"].unique()))
        if len(seeds) < 2:
            continue
        for predictor in ["frequency", "reference_learnability", "formal_utility"]:
            vals = []
            for _ in range(n_boot):
                chosen = rng.choice(seeds, size=len(seeds), replace=True)
                sample = pd.concat([g[g["seed"] == s] for s in chosen], ignore_index=True)
                vals.append(_spearman(sample.get(predictor, pd.Series(dtype=float)), sample["acquired_at"]))
            vals = np.array([v for v in vals if not pd.isna(v)], dtype=float)
            rows.append({
                "condition": condition,
                "predictor": predictor,
                "n_boot": int(len(vals)),
                "mean": float(np.mean(vals)) if len(vals) else np.nan,
                "ci_low": float(np.quantile(vals, 0.025)) if len(vals) else np.nan,
                "ci_high": float(np.quantile(vals, 0.975)) if len(vals) else np.nan,
                "expected_sign_rate": float(np.mean([_expected_sign_ok(predictor, v) for v in vals])) if len(vals) else np.nan,
            })
    return pd.DataFrame(rows)


def _fmt(x) -> str:
    if pd.isna(x):
        return "nan"
    return f"{float(x):.3f}"


def _report(threshold_summary: pd.DataFrame, sign: pd.DataFrame, config_summary: pd.DataFrame, seed_summary: pd.DataFrame, stratified: pd.DataFrame, bootstrap: pd.DataFrame, freq_summary: pd.DataFrame, primary_metric: str, primary_threshold: float) -> str:
    lines = [
        "# B1 H1 shared-sweep analysis report",
        "",
        "This report analyzes ordering and sign-stability across B1 sequence-DSL transformer configs/seeds. It is an H1 analysis only; it does not test H2 mediation or H3 causal dependency.",
        "",
        f"Primary analysis metric: `{primary_metric}` threshold `{primary_threshold}`.",
        "",
        "## Threshold sensitivity, base config/all tasks",
        "",
    ]
    base = threshold_summary[(threshold_summary["condition"] == "base") & (threshold_summary["stratum"] == "all")]
    for row in base.to_dict(orient="records"):
        lines.append(
            f"- {row['metric_family']} threshold `{row['threshold']}`: acq={_fmt(row['acquisition_rate'])}, "
            f"freq={_fmt(row['time_spearman_frequency'])}, learn={_fmt(row['time_spearman_reference_learnability'])}, "
            f"utility={_fmt(row['time_spearman_formal_utility'])}"
        )
    lines += ["", "## Sign stability", ""]
    view = sign[(sign["metric_family"] == primary_metric) & (np.isclose(sign["threshold"], primary_threshold))]
    for row in view.to_dict(orient="records"):
        if row["stratum"] in {"all", "true_tasks_atomic_composite", "kind=atomic", "kind=composite"}:
            lines.append(
                f"- {row['stratum']} / {row['predictor']}: sign-rate={_fmt(row['sign_stability_rate'])}, "
                f"mean-rho={_fmt(row['mean_time_spearman'])}, n_configs={int(row['n_configs_with_signal'])}"
            )
    lines += ["", "## Config summary, primary metric", ""]
    for row in config_summary[config_summary["stratum"] == "true_tasks_atomic_composite"].to_dict(orient="records"):
        lines.append(
            f"- {row['condition']}: acq={_fmt(row['acquisition_rate'])}, freq={_fmt(row['time_spearman_frequency'])}, "
            f"learn={_fmt(row['time_spearman_reference_learnability'])}, utility={_fmt(row['time_spearman_formal_utility'])}"
        )
    if not freq_summary.empty:
        lines += ["", "## Frequency realization", ""]
        for row in freq_summary.to_dict(orient="records")[:10]:
            lines.append(
                f"- {row['condition']} seed `{int(row['seed'])}`: Spearman={_fmt(row['spearman_intended_realized'])}, MAE={_fmt(row['mae_frequency'])}"
            )
    lines += [
        "",
        "## Decision rule",
        "",
        "GREEN for H1 requires nonzero/non-saturated acquisition across configs and stable expected signs, especially learnability positive and frequency negative within true-task/atomic strata. Utility can remain exploratory until the task graph has deeper downstream structure.",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
