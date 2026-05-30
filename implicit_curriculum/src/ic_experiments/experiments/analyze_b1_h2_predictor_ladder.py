from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

from ic_experiments.metrics import acquisition_times
from ic_experiments.run_management import append_registry, write_manifest

MODEL_SPECS: list[tuple[str, list[str]]] = [
    ("exposure_only", []),
    ("frequency_only", ["log_frequency"]),
    ("learnability_only", ["reference_learnability"]),
    ("utility_only", ["formal_utility"]),
    ("freq_learn", ["log_frequency", "reference_learnability"]),
    ("freq_utility", ["log_frequency", "formal_utility"]),
    ("learn_utility", ["reference_learnability", "formal_utility"]),
    ("three_factor", ["log_frequency", "reference_learnability", "formal_utility"]),
]
COMPLEXITY = {name: i for i, (name, _) in enumerate(MODEL_SPECS)}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="B1 H2 predictor ladder and atomic parallel-null residual analysis.")
    p.add_argument("--result-dir", type=Path, required=True, help="Existing B1 H1 shared-sweep result directory.")
    p.add_argument("--metric-family", type=str, default="token_accuracy")
    p.add_argument("--threshold", type=float, default=0.70)
    p.add_argument("--patience", type=int, default=2)
    p.add_argument("--top-k-pairs", type=int, default=10)
    p.add_argument("--n-permutations", type=int, default=100)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--code-version", type=str, default="v0.9")
    p.add_argument("--run-id", type=str, default=None)
    p.add_argument("--archive-root", type=Path, default=None, help="Optional archive root; writes registry entry if provided.")
    p.add_argument("--thesis-use", type=str, default="candidate")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    result_dir = args.result_dir
    eval_df = pd.read_csv(result_dir / "eval_curves.csv")
    structure = _load_structure(result_dir)
    acq = _load_or_compute_acq(result_dir, eval_df, args.metric_family, args.threshold, args.patience)
    acq = _prepare_rows(acq, structure, eval_df, result_dir, args.metric_family, args.threshold)
    acq.to_csv(result_dir / "h2_acquisition_table.csv", index=False)

    cv = cross_validated_ladder(acq)
    cv.to_csv(result_dir / "h2_predictor_ladder_cv.csv", index=False)

    selected = select_models(cv)
    selected.to_csv(result_dir / "h2_selected_models.csv", index=False)

    coeffs, preds = fit_selected_and_predict(acq, selected)
    coeffs.to_csv(result_dir / "h2_model_coefficients.csv", index=False)
    preds.to_csv(result_dir / "h2_atomic_parallel_predictions.csv", index=False)

    residuals = composite_residuals(preds)
    residuals.to_csv(result_dir / "h2_composite_residuals.csv", index=False)

    task_residuals = residual_summary_by_task(residuals)
    task_residuals.to_csv(result_dir / "h2_composite_residual_summary_by_task.csv", index=False)

    pairs = pair_selection(task_residuals, structure, top_k=args.top_k_pairs)
    pairs.to_csv(result_dir / "h2_pair_selection.csv", index=False)

    perm = permutation_null(acq, selected, n_permutations=args.n_permutations, seed=args.seed)
    perm.to_csv(result_dir / "h2_permutation_null.csv", index=False)

    report = make_report(acq, cv, selected, residuals, task_residuals, pairs, perm, args.metric_family, args.threshold)
    (result_dir / "h2_analysis_report.md").write_text(report, encoding="utf-8")

    manifest = write_manifest(
        result_dir,
        experiment="B1_H2_predictor_ladder_atomic_parallel_null",
        backend="B1_sequence_dsl",
        code_version=args.code_version,
        run_id=args.run_id or f"h2_from_{result_dir.name}",
        command=sys.argv,
        input_paths={"result_dir": str(result_dir)},
        extra={"metric_family": args.metric_family, "threshold": args.threshold, "thesis_use": args.thesis_use},
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

    print("Saved B1 H2 analysis outputs:")
    for name in [
        "h2_analysis_report.md",
        "h2_predictor_ladder_cv.csv",
        "h2_selected_models.csv",
        "h2_model_coefficients.csv",
        "h2_atomic_parallel_predictions.csv",
        "h2_composite_residuals.csv",
        "h2_composite_residual_summary_by_task.csv",
        "h2_pair_selection.csv",
        "h2_permutation_null.csv",
        "run_manifest.json",
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
        add_cols = [c for c in diff.columns if c == "task_name" or c not in structure.columns]
        structure = structure.merge(diff[add_cols].drop_duplicates("task_name"), on="task_name", how="left")
    return structure


def _load_or_compute_acq(result_dir: Path, eval_df: pd.DataFrame, metric_family: str, threshold: float, patience: int) -> pd.DataFrame:
    path = result_dir / "h1_acquisition_times_multi_metric.csv"
    if path.exists():
        acq = pd.read_csv(path)
        mask = (acq.get("metric_family") == metric_family) & np.isclose(acq.get("analysis_threshold"), threshold)
        out = acq[mask].copy()
        if not out.empty:
            return out
    out = acquisition_times(eval_df, threshold=threshold, patience=patience, metric=metric_family)
    out["metric_family"] = metric_family
    out["analysis_threshold"] = float(threshold)
    return out


def _prepare_rows(acq: pd.DataFrame, structure: pd.DataFrame, eval_df: pd.DataFrame, result_dir: Path, metric_family: str, threshold: float) -> pd.DataFrame:
    meta_cols = [
        "task_name", "structure_id", "kind", "op", "operation_type", "components", "frequency", "reference_learnability",
        "formal_utility", "composition_depth", "control_type", "output_entropy", "random_baseline_token_accuracy", "target_length",
    ]
    meta = structure[[c for c in meta_cols if c in structure.columns]].drop_duplicates("task_name")
    # Drop stale metadata columns to avoid suffix collisions.
    stale = [c for c in acq.columns if c.endswith("_meta")]
    acq = acq.drop(columns=stale, errors="ignore").copy()
    for c in [c for c in meta.columns if c != "task_name" and c in acq.columns]:
        acq = acq.drop(columns=[c])
    acq = acq.merge(meta, on="task_name", how="left")

    max_by_cond_seed = eval_df.groupby(["condition", "seed"], as_index=False)["data_seen"].max().rename(columns={"data_seen": "max_data_seen"})
    acq = acq.merge(max_by_cond_seed, on=["condition", "seed"], how="left")
    acq["censored_acquired_at"] = acq["acquired_at"].fillna(acq["max_data_seen"])
    acq["is_censored"] = acq["acquired_at"].isna()
    acq["log_acquired_at"] = np.log1p(acq["censored_acquired_at"].astype(float))
    acq["log_frequency"] = np.log(np.maximum(acq["frequency"].astype(float), 1e-12))
    acq["metric_family"] = metric_family
    acq["analysis_threshold"] = float(threshold)
    return acq


def cross_validated_ladder(acq: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for condition, cond_df in acq.groupby("condition"):
        atoms = cond_df[cond_df["kind"] == "atomic"].copy()
        task_names = sorted(atoms["task_name"].dropna().unique())
        for model_name, features in MODEL_SPECS:
            fold_errs = []
            for held_task in task_names:
                train = atoms[atoms["task_name"] != held_task]
                test = atoms[atoms["task_name"] == held_task]
                if len(train) < max(4, len(features) + 2) or test.empty:
                    continue
                fit = _fit_linear(train, features)
                yhat = _predict_linear(test, features, fit)
                err = test["log_acquired_at"].to_numpy(dtype=float) - yhat
                fold_errs.extend(err.tolist())
            if fold_errs:
                arr = np.asarray(fold_errs, dtype=float)
                rows.append({
                    "condition": condition,
                    "model": model_name,
                    "features": ",".join(features),
                    "complexity": COMPLEXITY[model_name],
                    "n_folds": len(task_names),
                    "n_errors": len(arr),
                    "cv_rmse_log_time": float(np.sqrt(np.mean(arr ** 2))),
                    "cv_mae_log_time": float(np.mean(np.abs(arr))),
                    "cv_se_log_time": float(np.std(np.abs(arr), ddof=1) / math.sqrt(len(arr))) if len(arr) > 1 else np.nan,
                })
    return pd.DataFrame(rows)


def select_models(cv: pd.DataFrame) -> pd.DataFrame:
    rows = []
    if cv.empty:
        return pd.DataFrame()
    for condition, g in cv.groupby("condition"):
        gg = g.dropna(subset=["cv_rmse_log_time"]).copy()
        if gg.empty:
            continue
        best = gg.loc[gg["cv_rmse_log_time"].idxmin()]
        # One-standard-error rule using the best model's SE; choose simplest within tolerance.
        tol = float(best["cv_rmse_log_time"] + (0 if pd.isna(best["cv_se_log_time"]) else best["cv_se_log_time"]))
        candidates = gg[gg["cv_rmse_log_time"] <= tol].sort_values(["complexity", "cv_rmse_log_time"])
        selected = candidates.iloc[0]
        row = selected.to_dict()
        row.update({
            "best_model": best["model"],
            "best_rmse_log_time": float(best["cv_rmse_log_time"]),
            "selection_rule": "one_standard_error_simplest",
            "rmse_tolerance": tol,
        })
        rows.append(row)
    return pd.DataFrame(rows)


def _fit_linear(df: pd.DataFrame, features: list[str]) -> dict:
    y = df["log_acquired_at"].to_numpy(dtype=float)
    if not features:
        return {"intercept": float(np.mean(y)), "coef": [], "features": [], "means": [], "stds": []}
    X = df[features].to_numpy(dtype=float)
    means = np.nanmean(X, axis=0)
    stds = np.nanstd(X, axis=0)
    stds = np.where(stds < 1e-8, 1.0, stds)
    Xz = (X - means) / stds
    Xdesign = np.column_stack([np.ones(len(Xz)), Xz])
    coef, *_ = np.linalg.lstsq(Xdesign, y, rcond=None)
    return {"intercept": float(coef[0]), "coef": [float(c) for c in coef[1:]], "features": features, "means": means.tolist(), "stds": stds.tolist()}


def _predict_linear(df: pd.DataFrame, features: list[str], fit: dict) -> np.ndarray:
    if not features:
        return np.full(len(df), fit["intercept"], dtype=float)
    X = df[features].to_numpy(dtype=float)
    means = np.asarray(fit["means"], dtype=float)
    stds = np.asarray(fit["stds"], dtype=float)
    Xz = (X - means) / stds
    coef = np.asarray(fit["coef"], dtype=float)
    return fit["intercept"] + Xz @ coef


def fit_selected_and_predict(acq: pd.DataFrame, selected: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    coef_rows: list[dict] = []
    pred_rows: list[pd.DataFrame] = []
    if selected.empty:
        return pd.DataFrame(), pd.DataFrame()
    for _, sel in selected.iterrows():
        condition = sel["condition"]
        model_name = sel["model"]
        features = next(features for name, features in MODEL_SPECS if name == model_name)
        cond_df = acq[acq["condition"] == condition].copy()
        atoms = cond_df[cond_df["kind"] == "atomic"].copy()
        if atoms.empty:
            continue
        fit = _fit_linear(atoms, features)
        for feat, coef in zip(features, fit["coef"]):
            coef_rows.append({"condition": condition, "model": model_name, "term": feat, "coef_standardized": coef})
        coef_rows.append({"condition": condition, "model": model_name, "term": "intercept", "coef_standardized": fit["intercept"]})
        cond_df["selected_model"] = model_name
        cond_df["parallel_pred_log_time"] = _predict_linear(cond_df, features, fit)
        cond_df["parallel_pred_time"] = np.expm1(cond_df["parallel_pred_log_time"])
        cond_df["parallel_residual_log_time"] = cond_df["log_acquired_at"] - cond_df["parallel_pred_log_time"]
        cond_df["parallel_residual_time"] = cond_df["censored_acquired_at"] - cond_df["parallel_pred_time"]
        pred_rows.append(cond_df)
    return pd.DataFrame(coef_rows), pd.concat(pred_rows, ignore_index=True) if pred_rows else pd.DataFrame()


def composite_residuals(preds: pd.DataFrame) -> pd.DataFrame:
    if preds.empty:
        return pd.DataFrame()
    return preds[preds["kind"] == "composite"].copy()


def residual_summary_by_task(residuals: pd.DataFrame) -> pd.DataFrame:
    if residuals.empty:
        return pd.DataFrame()
    rows = []
    group_cols = ["condition", "task_name"]
    for (condition, task), g in residuals.groupby(group_cols):
        rows.append({
            "condition": condition,
            "task_name": task,
            "n": int(len(g)),
            "acquisition_rate": float(g["acquired_at"].notna().mean()),
            "mean_residual_log_time": float(g["parallel_residual_log_time"].mean()),
            "median_residual_log_time": float(g["parallel_residual_log_time"].median()),
            "mean_residual_time": float(g["parallel_residual_time"].mean()),
            "positive_residual_rate": float((g["parallel_residual_log_time"] > 0).mean()),
            "mean_observed_time": float(g["censored_acquired_at"].mean()),
            "mean_predicted_time": float(g["parallel_pred_time"].mean()),
        })
    return pd.DataFrame(rows)


def pair_selection(task_residuals: pd.DataFrame, structure: pd.DataFrame, top_k: int = 10) -> pd.DataFrame:
    if task_residuals.empty:
        return pd.DataFrame()
    meta_cols = [c for c in ["task_name", "components", "op", "frequency", "reference_learnability", "formal_utility"] if c in structure.columns]
    meta = structure[meta_cols].drop_duplicates("task_name")
    df = task_residuals.merge(meta, on="task_name", how="left")
    rows = []
    df = df.sort_values(["mean_residual_log_time", "positive_residual_rate"], ascending=[False, False])
    for _, row in df.iterrows():
        components = _parse_components(row.get("components", ""))
        if not components:
            components = [""]
        for comp in components:
            rows.append({
                "condition": row["condition"],
                "component_id": comp,
                "composite_id": row["task_name"],
                "mean_residual_log_time": row["mean_residual_log_time"],
                "positive_residual_rate": row["positive_residual_rate"],
                "acquisition_rate": row["acquisition_rate"],
                "mean_observed_time": row["mean_observed_time"],
                "mean_predicted_time": row["mean_predicted_time"],
                "composite_op": row.get("op", ""),
                "frequency": row.get("frequency", np.nan),
                "reference_learnability": row.get("reference_learnability", np.nan),
                "formal_utility": row.get("formal_utility", np.nan),
            })
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return out.sort_values(["mean_residual_log_time", "positive_residual_rate"], ascending=[False, False]).head(top_k)


def _parse_components(value) -> list[str]:
    if pd.isna(value):
        return []
    if isinstance(value, str):
        txt = value.strip()
        if not txt:
            return []
        try:
            parsed = json.loads(txt)
            if isinstance(parsed, list):
                return [str(x) for x in parsed]
        except Exception:
            pass
        return [p.strip() for p in txt.replace(";", ",").split(",") if p.strip()]
    if isinstance(value, Iterable):
        return [str(x) for x in value]
    return []


def permutation_null(acq: pd.DataFrame, selected: pd.DataFrame, n_permutations: int = 100, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    if selected.empty or n_permutations <= 0:
        return pd.DataFrame()
    for _, sel in selected.iterrows():
        condition = sel["condition"]
        model_name = sel["model"]
        features = next(features for name, features in MODEL_SPECS if name == model_name)
        atoms = acq[(acq["condition"] == condition) & (acq["kind"] == "atomic")].copy()
        if atoms.empty:
            continue
        if not features:
            continue
        true_rmse = float(sel["cv_rmse_log_time"])
        for pidx in range(n_permutations):
            shuffled = atoms.copy()
            # Shuffle feature rows at task level, preserving per-seed repeated rows.
            unique_features = shuffled[["task_name"] + features].drop_duplicates("task_name").reset_index(drop=True)
            perm = unique_features.copy()
            perm[features] = perm[features].sample(frac=1.0, random_state=int(rng.integers(0, 2**31 - 1))).reset_index(drop=True)[features]
            shuffled = shuffled.drop(columns=features).merge(perm, on="task_name", how="left")
            cvp = cross_validated_ladder(shuffled)
            row = cvp[(cvp["condition"] == condition) & (cvp["model"] == model_name)]
            if row.empty:
                continue
            perm_rmse = float(row.iloc[0]["cv_rmse_log_time"])
            rows.append({
                "condition": condition,
                "model": model_name,
                "permutation_index": pidx,
                "true_cv_rmse_log_time": true_rmse,
                "permuted_cv_rmse_log_time": perm_rmse,
                "true_beats_permutation": bool(true_rmse < perm_rmse),
            })
    return pd.DataFrame(rows)


def make_report(acq: pd.DataFrame, cv: pd.DataFrame, selected: pd.DataFrame, residuals: pd.DataFrame, task_residuals: pd.DataFrame, pairs: pd.DataFrame, perm: pd.DataFrame, metric_family: str, threshold: float) -> str:
    lines = [
        "# B1 H2 predictor-ladder and atomic parallel-null analysis",
        "",
        "This analysis reuses the B1 H1 shared-sweep outputs. It fits predictor ladders on atomic structures, then predicts composite acquisition under an atomic parallel-rate null.",
        "",
        f"Primary metric: `{metric_family}` threshold `{threshold}`.",
        "",
        "## Acquisition table",
        "",
        f"- rows: `{len(acq)}`",
        f"- configs: `{acq['condition'].nunique() if 'condition' in acq else 0}`",
        f"- tasks: `{acq['task_name'].nunique() if 'task_name' in acq else 0}`",
        f"- atomic acquisition rate: `{_fmt(acq[acq['kind']=='atomic']['acquired_at'].notna().mean() if 'kind' in acq else np.nan)}`",
        f"- composite acquisition rate: `{_fmt(acq[acq['kind']=='composite']['acquired_at'].notna().mean() if 'kind' in acq else np.nan)}`",
        "",
        "## Selected predictor by config",
        "",
    ]
    if selected.empty:
        lines.append("No selected models were available.")
    else:
        for _, r in selected.iterrows():
            lines.append(f"- `{r['condition']}`: selected `{r['model']}` (CV RMSE log-time={_fmt(r['cv_rmse_log_time'])}; best=`{r['best_model']}`)")
    lines += ["", "## Composite residuals", ""]
    if residuals.empty:
        lines.append("No composite residuals were available.")
    else:
        lines.append(f"- composite rows: `{len(residuals)}`")
        lines.append(f"- mean residual log-time: `{_fmt(residuals['parallel_residual_log_time'].mean())}`")
        lines.append(f"- positive residual rate: `{_fmt((residuals['parallel_residual_log_time'] > 0).mean())}`")
        if not task_residuals.empty:
            top = task_residuals.sort_values("mean_residual_log_time", ascending=False).head(5)
            lines.append("")
            lines.append("Top delayed composites under the atomic parallel null:")
            for _, r in top.iterrows():
                lines.append(f"- `{r['condition']}` / `{r['task_name']}`: mean residual log-time={_fmt(r['mean_residual_log_time'])}, positive-rate={_fmt(r['positive_residual_rate'])}")
    lines += ["", "## Pair selection for future H3", ""]
    if pairs.empty:
        lines.append("No component-composite pairs selected.")
    else:
        for _, r in pairs.head(10).iterrows():
            comp = r.get("component_id", "") or "<unknown>"
            lines.append(f"- `{r['condition']}`: `{comp}` → `{r['composite_id']}` residual={_fmt(r['mean_residual_log_time'])}, positive-rate={_fmt(r['positive_residual_rate'])}")
    lines += ["", "## Permutation null", ""]
    if perm.empty:
        lines.append("Permutation null was skipped or unavailable.")
    else:
        summary = perm.groupby(["condition", "model"], as_index=False)["true_beats_permutation"].mean()
        for _, r in summary.iterrows():
            lines.append(f"- `{r['condition']}` / `{r['model']}`: true-beats-permutation rate={_fmt(r['true_beats_permutation'])}")
    lines += ["", "## Interpretation rule", "", "A clean H2 result requires a simple predictor to beat richer alternatives under cross-validation and permutation, while composites either follow the atomic parallel prediction or show structured residuals. Residuals are observational only; they select pairs for later H3 interventions but do not establish dependency."]
    return "\n".join(lines) + "\n"


def _fmt(x) -> str:
    try:
        if pd.isna(x):
            return "nan"
        return f"{float(x):.3f}"
    except Exception:
        return str(x)


if __name__ == "__main__":
    main()
