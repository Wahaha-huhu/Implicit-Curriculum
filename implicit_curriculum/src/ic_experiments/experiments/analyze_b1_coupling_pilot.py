from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from ic_experiments.coupling import bootstrap_ci, linear_slope
from ic_experiments.run_management import append_registry, write_manifest


OUTCOME_COLUMNS = [
    "target_final_token_accuracy",
    "target_auc_token_accuracy",
    "target_final_exact_match",
    "target_auc_exact_match",
    "target_final_loss",
]

DEFAULT_BASELINE_COLUMNS = [
    "source_frequency",
    "target_frequency",
    "source_reference_learnability",
    "target_reference_learnability",
    "surface_overlap_proxy",
]

DEFAULT_CATEGORICAL_BASELINES = ["pair_type", "formal_relation", "source_op", "target_op"]

PREDICTOR_KEYWORDS = ["gradient_cosine", "gradient_inner_product", "transfer_score", "gradient_norm", "gradient_snr", "linear_cka"]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Analyze N1 B1 cross-task coupling pilot outputs with baseline-controlled tests.")
    p.add_argument("--result-dir", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, default=None)
    p.add_argument("--bootstrap-samples", type=int, default=2000)
    p.add_argument("--predictor-stage", type=str, default="early", choices=["init", "early"])
    p.add_argument("--predictor-multiplier", type=float, default=1.0, help="Use predictors from this source multiplier as the leading-indicator baseline.")
    p.add_argument("--primary-outcome", type=str, default="mean_slope_target_auc_token_accuracy", help="Pair-level interaction column used for baseline-controlled gate diagnostics.")
    p.add_argument("--baseline-columns", type=str, nargs="*", default=DEFAULT_BASELINE_COLUMNS)
    p.add_argument("--categorical-baselines", type=str, nargs="*", default=DEFAULT_CATEGORICAL_BASELINES)
    p.add_argument("--min-pairs-for-categorical", type=int, default=30, help="Only include categorical baselines in regressions when there are at least this many pairs.")
    p.add_argument("--code-version", type=str, default="n1.1")
    p.add_argument("--run-id", type=str, default=None)
    p.add_argument("--archive-root", type=Path, default=None)
    p.add_argument("--thesis-use", type=str, default="candidate")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    result_dir = args.result_dir
    out = args.output_dir or (result_dir / "analysis")
    out.mkdir(parents=True, exist_ok=True)

    outcomes = pd.read_csv(result_dir / "target_outcomes.csv")
    predictors = pd.read_csv(result_dir / "early_coupling_predictors.csv")
    pair_plan_path = result_dir / "b1_coupling_pair_plan.csv"
    pair_plan = pd.read_csv(pair_plan_path) if pair_plan_path.exists() else pd.DataFrame()

    per_seed = estimate_seed_slopes(outcomes)
    per_seed.to_csv(out / "b1_coupling_seed_interaction_effects.csv", index=False)
    pair_summary = summarize_pair_effects(per_seed, args.bootstrap_samples)
    pair_summary.to_csv(out / "b1_coupling_pair_interaction_summary.csv", index=False)

    predictor_summary = summarize_predictors(predictors, args.predictor_stage, args.predictor_multiplier)
    predictor_summary.to_csv(out / "b1_coupling_pair_predictor_summary.csv", index=False)

    merged = pair_summary.merge(predictor_summary, on="pair_id", how="left", suffixes=("", "_predictor"))
    if not pair_plan.empty:
        keep_cols = [c for c in pair_plan.columns if c not in merged.columns or c == "pair_id"]
        merged = merged.merge(pair_plan[keep_cols], on="pair_id", how="left")
    merged.to_csv(out / "b1_coupling_predictor_vs_interaction.csv", index=False)

    correlations = predictor_correlations(merged)
    correlations.to_csv(out / "b1_coupling_predictor_correlations.csv", index=False)

    baseline_correlations = baseline_correlations_table(merged, args)
    baseline_correlations.to_csv(out / "b1_coupling_baseline_correlations.csv", index=False)

    residualized = residualized_predictor_correlations(merged, args)
    residualized.to_csv(out / "b1_coupling_residualized_predictor_correlations.csv", index=False)

    incremental = incremental_model_table(merged, args)
    incremental.to_csv(out / "b1_coupling_incremental_models.csv", index=False)

    diagnostics = data_diagnostics(outcomes, predictors, merged, args)
    gate = pilot_gate_summary(merged, correlations, baseline_correlations, residualized, incremental, diagnostics, args)
    (out / "b1_coupling_pilot_analysis_report.md").write_text(
        render_report(args, outcomes, predictors, per_seed, merged, correlations, baseline_correlations, residualized, incremental, diagnostics, gate),
        encoding="utf-8",
    )
    (out / "summary.json").write_text(
        json.dumps(
            {
                "experiment": "N1_B1_cross_task_coupling_pilot_analysis",
                "result_dir": str(result_dir),
                "n_pairs": int(merged["pair_id"].nunique()) if "pair_id" in merged else 0,
                "n_outcome_rows": int(len(outcomes)),
                "n_predictor_rows": int(len(predictors)),
                "primary_outcome": args.primary_outcome,
                "baseline_columns": args.baseline_columns,
                "categorical_baselines": args.categorical_baselines,
                "pilot_gate": gate,
                "diagnostics": diagnostics,
                "paths": {
                    "seed_interaction_effects": str(out / "b1_coupling_seed_interaction_effects.csv"),
                    "pair_interaction_summary": str(out / "b1_coupling_pair_interaction_summary.csv"),
                    "predictor_vs_interaction": str(out / "b1_coupling_predictor_vs_interaction.csv"),
                    "predictor_correlations": str(out / "b1_coupling_predictor_correlations.csv"),
                    "baseline_correlations": str(out / "b1_coupling_baseline_correlations.csv"),
                    "residualized_predictor_correlations": str(out / "b1_coupling_residualized_predictor_correlations.csv"),
                    "incremental_models": str(out / "b1_coupling_incremental_models.csv"),
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    manifest = write_manifest(
        out,
        experiment="N1_B1_cross_task_coupling_pilot_analysis",
        backend="B1_sequence_dsl",
        code_version=args.code_version,
        run_id=args.run_id or "b1_coupling_pilot_analysis",
        command=sys.argv,
        input_paths={"result_dir": str(result_dir)},
        extra={"thesis_use": args.thesis_use, "pilot_gate": gate},
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
                "output_path": str(out),
                "status": "analyzed",
                "thesis_use": args.thesis_use,
                "created_at_utc": manifest["created_at_utc"],
            },
        )

    print("Saved B1 coupling pilot analysis outputs:")
    for name in [
        "b1_coupling_pilot_analysis_report.md",
        "b1_coupling_seed_interaction_effects.csv",
        "b1_coupling_pair_interaction_summary.csv",
        "b1_coupling_predictor_vs_interaction.csv",
        "b1_coupling_predictor_correlations.csv",
        "b1_coupling_baseline_correlations.csv",
        "b1_coupling_residualized_predictor_correlations.csv",
        "b1_coupling_incremental_models.csv",
        "run_manifest.json",
    ]:
        print(f"  {out / name}")


def estimate_seed_slopes(outcomes: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    group_cols = ["pair_id", "pair_type", "source_task", "target_task", "filler_task", "seed"]
    for keys, g in outcomes.groupby(group_cols, dropna=False):
        pair_id, pair_type, source, target, filler, seed = keys
        x = g["source_multiplier"].astype(float).to_numpy()
        row = {
            "pair_id": pair_id,
            "pair_type": pair_type,
            "source_task": source,
            "target_task": target,
            "filler_task": filler,
            "seed": int(seed),
            "n_dose_levels": int(g["source_multiplier"].nunique()),
        }
        for col in OUTCOME_COLUMNS:
            if col in g.columns:
                y = g[col].astype(float).to_numpy()
                slope = linear_slope(x, y)
                if col == "target_final_loss":
                    # For all interaction columns, positive means source-dose helps target.
                    slope = -slope if np.isfinite(slope) else slope
                row[f"slope_{col}"] = slope
        if "target_acquired_at" in g.columns:
            acq = g["target_acquired_at"].astype(float).to_numpy()
            max_seen = float(g["max_data_seen"].iloc[0]) if "max_data_seen" in g.columns else np.nan
            # Earlier acquisition is beneficial, so reverse the sign and normalize.
            slope_acq = linear_slope(x, acq)
            row["slope_target_acquisition_transfer"] = float(-slope_acq / max(1.0, max_seen)) if np.isfinite(slope_acq) else float("nan")
        rows.append(row)
    return pd.DataFrame(rows)


def summarize_pair_effects(per_seed: pd.DataFrame, n_bootstrap: int) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    effect_cols = [c for c in per_seed.columns if c.startswith("slope_")]
    base_cols = ["pair_id", "pair_type", "source_task", "target_task", "filler_task"]
    for keys, g in per_seed.groupby(base_cols, dropna=False):
        row = dict(zip(base_cols, keys))
        row["n_seeds"] = int(g["seed"].nunique())
        for c in effect_cols:
            mean, lo, hi = bootstrap_ci(g[c].astype(float).to_numpy(), n_bootstrap=n_bootstrap, seed=stable_int_seed(str(keys) + c))
            row[f"mean_{c}"] = mean
            row[f"ci_low_{c}"] = lo
            row[f"ci_high_{c}"] = hi
            row[f"positive_rate_{c}"] = float(np.nanmean(g[c].astype(float).to_numpy() > 0)) if len(g) else float("nan")
        rows.append(row)
    return pd.DataFrame(rows)


def summarize_predictors(predictors: pd.DataFrame, stage: str, multiplier: float) -> pd.DataFrame:
    pred = predictors.copy()
    if "probe_stage" in pred.columns:
        pred = pred[pred["probe_stage"].astype(str).eq(stage)].copy()
    if "source_multiplier" in pred.columns:
        # Prefer baseline multiplier, but fall back to all rows if absent.
        base = pred[np.isclose(pred["source_multiplier"].astype(float), float(multiplier))].copy()
        if not base.empty:
            pred = base
    predictor_cols = [
        "gradient_cosine",
        "gradient_inner_product",
        "first_order_transfer_score",
        "source_gradient_norm",
        "target_gradient_norm",
        "source_gradient_snr",
        "target_gradient_snr",
        "source_within_gradient_alignment",
        "target_within_gradient_alignment",
        "linear_cka",
    ]
    rows = []
    for pair_id, g in pred.groupby("pair_id"):
        row = {"pair_id": pair_id, "predictor_stage": stage, "predictor_multiplier": float(multiplier), "n_predictor_rows": int(len(g))}
        for c in predictor_cols:
            if c in g.columns:
                row[f"mean_{c}"] = float(np.nanmean(g[c].astype(float)))
                row[f"std_{c}"] = float(np.nanstd(g[c].astype(float)))
        rows.append(row)
    return pd.DataFrame(rows)


def predictor_columns(merged: pd.DataFrame) -> list[str]:
    return [c for c in merged.columns if c.startswith("mean_") and any(k in c for k in PREDICTOR_KEYWORDS)]


def outcome_columns(merged: pd.DataFrame) -> list[str]:
    return [c for c in merged.columns if c.startswith("mean_slope_target_")]


def predictor_correlations(merged: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for p in predictor_columns(merged):
        for o in outcome_columns(merged):
            rows.append(correlation_row(merged, p, o, kind="raw_predictor"))
    return pd.DataFrame(rows)


def baseline_correlations_table(merged: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    cols = [c for c in list(args.baseline_columns) + list(args.categorical_baselines) if c in merged.columns]
    rows = []
    for b in cols:
        if b in args.categorical_baselines or not pd.api.types.is_numeric_dtype(merged[b]):
            for o in outcome_columns(merged):
                rows.append(categorical_baseline_strength(merged, b, o))
        else:
            for o in outcome_columns(merged):
                rows.append(correlation_row(merged, b, o, kind="numeric_baseline"))
    return pd.DataFrame(rows)


def residualized_predictor_correlations(merged: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    primary = select_primary_outcome(merged, args.primary_outcome)
    base_cols = usable_baseline_columns(merged, args, include_categorical=False)
    rows = []
    for p in predictor_columns(merged):
        sub = merged[[primary, p] + base_cols].copy()
        y = pd.to_numeric(sub[primary], errors="coerce").to_numpy(dtype=float)
        X, ok = design_matrix(sub, base_cols)
        pred = pd.to_numeric(sub[p], errors="coerce").to_numpy(dtype=float)
        ok = ok & np.isfinite(y) & np.isfinite(pred)
        if int(ok.sum()) < 4:
            rows.append({"predictor": p, "outcome": primary, "n_pairs": int(ok.sum()), "residualized_pearson_r": float("nan"), "residualized_sign_accuracy": float("nan"), "baseline_columns": ",".join(base_cols)})
            continue
        resid = residuals_from_design(y[ok], X[ok])
        r = np.corrcoef(pred[ok], resid)[0, 1] if np.nanstd(pred[ok]) > 1e-12 and np.nanstd(resid) > 1e-12 else np.nan
        rows.append({
            "predictor": p,
            "outcome": primary,
            "n_pairs": int(ok.sum()),
            "residualized_pearson_r": float(r) if np.isfinite(r) else float("nan"),
            "residualized_sign_accuracy": sign_accuracy(pred[ok], resid),
            "baseline_columns": ",".join(base_cols),
        })
    return pd.DataFrame(rows)


def incremental_model_table(merged: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    primary = select_primary_outcome(merged, args.primary_outcome)
    numeric_base = usable_baseline_columns(merged, args, include_categorical=False)
    cat_base = []
    if int(merged["pair_id"].nunique()) >= int(args.min_pairs_for_categorical):
        cat_base = [c for c in args.categorical_baselines if c in merged.columns]
    baseline_cols = numeric_base + cat_base
    rows = []
    y = pd.to_numeric(merged[primary], errors="coerce").to_numpy(dtype=float)
    X_base, ok_base = design_matrix(merged, baseline_cols)
    ok_base = ok_base & np.isfinite(y)
    baseline_r2 = full_sample_r2(y[ok_base], X_base[ok_base]) if int(ok_base.sum()) >= max(4, len(baseline_cols) + 2) else float("nan")
    baseline_cv_r2 = loo_cv_r2(merged, primary, baseline_cols) if int(ok_base.sum()) >= 6 else float("nan")
    rows.append({
        "model": "baseline_only",
        "outcome": primary,
        "predictor_added": "",
        "n_pairs": int(ok_base.sum()),
        "n_features": int(X_base.shape[1]) if X_base.size else 0,
        "full_sample_r2": baseline_r2,
        "loo_cv_r2": baseline_cv_r2,
        "delta_full_sample_r2_vs_baseline": float("nan"),
        "delta_loo_cv_r2_vs_baseline": float("nan"),
        "columns": ",".join(baseline_cols),
    })
    for p in predictor_columns(merged):
        cols = baseline_cols + [p]
        X, ok = design_matrix(merged, cols)
        ok = ok & np.isfinite(y)
        r2 = full_sample_r2(y[ok], X[ok]) if int(ok.sum()) >= max(4, len(cols) + 2) else float("nan")
        cv = loo_cv_r2(merged, primary, cols) if int(ok.sum()) >= 6 else float("nan")
        rows.append({
            "model": "baseline_plus_predictor",
            "outcome": primary,
            "predictor_added": p,
            "n_pairs": int(ok.sum()),
            "n_features": int(X.shape[1]) if X.size else 0,
            "full_sample_r2": r2,
            "loo_cv_r2": cv,
            "delta_full_sample_r2_vs_baseline": float(r2 - baseline_r2) if np.isfinite(r2) and np.isfinite(baseline_r2) else float("nan"),
            "delta_loo_cv_r2_vs_baseline": float(cv - baseline_cv_r2) if np.isfinite(cv) and np.isfinite(baseline_cv_r2) else float("nan"),
            "columns": ",".join(cols),
        })
    return pd.DataFrame(rows)


def usable_baseline_columns(merged: pd.DataFrame, args: argparse.Namespace, include_categorical: bool) -> list[str]:
    cols = [c for c in args.baseline_columns if c in merged.columns]
    if include_categorical and int(merged["pair_id"].nunique()) >= int(args.min_pairs_for_categorical):
        cols += [c for c in args.categorical_baselines if c in merged.columns]
    # Drop numeric baseline columns with effectively zero variance.
    keep = []
    for c in cols:
        if c in args.categorical_baselines or not pd.api.types.is_numeric_dtype(merged[c]):
            if merged[c].astype(str).nunique(dropna=True) > 1:
                keep.append(c)
        else:
            vals = pd.to_numeric(merged[c], errors="coerce").to_numpy(dtype=float)
            if np.isfinite(vals).sum() >= 3 and np.nanstd(vals) > 1e-12:
                keep.append(c)
    return keep


def select_primary_outcome(merged: pd.DataFrame, requested: str) -> str:
    if requested in merged.columns:
        return requested
    for fallback in ["mean_slope_target_auc_token_accuracy", "mean_slope_target_final_token_accuracy", "mean_slope_target_final_loss"]:
        if fallback in merged.columns:
            return fallback
    outs = outcome_columns(merged)
    if not outs:
        raise ValueError("No pair-level outcome columns found in merged predictor-vs-interaction table.")
    return outs[0]


def correlation_row(df: pd.DataFrame, x_col: str, y_col: str, kind: str) -> dict[str, Any]:
    x = pd.to_numeric(df[x_col], errors="coerce").to_numpy(dtype=float)
    y = pd.to_numeric(df[y_col], errors="coerce").to_numpy(dtype=float)
    ok = np.isfinite(x) & np.isfinite(y)
    if ok.sum() < 3 or np.nanstd(x[ok]) <= 1e-12 or np.nanstd(y[ok]) <= 1e-12:
        corr = float("nan")
    else:
        corr = float(np.corrcoef(x[ok], y[ok])[0, 1])
    return {"kind": kind, "predictor": x_col, "outcome": y_col, "n_pairs": int(ok.sum()), "pearson_r": corr, "sign_accuracy": sign_accuracy(x[ok], y[ok]) if ok.sum() else float("nan")}


def categorical_baseline_strength(df: pd.DataFrame, col: str, outcome: str) -> dict[str, Any]:
    sub = df[[col, outcome]].copy()
    y = pd.to_numeric(sub[outcome], errors="coerce")
    ok = y.notna() & sub[col].notna()
    sub = sub[ok]
    if len(sub) < 3 or sub[col].astype(str).nunique() < 2:
        eta2 = float("nan")
    else:
        yv = pd.to_numeric(sub[outcome], errors="coerce").to_numpy(dtype=float)
        overall = float(np.nanmean(yv))
        ss_total = float(np.nansum((yv - overall) ** 2))
        ss_between = 0.0
        for _, g in sub.groupby(col):
            vals = pd.to_numeric(g[outcome], errors="coerce").to_numpy(dtype=float)
            ss_between += len(vals) * float((np.nanmean(vals) - overall) ** 2)
        eta2 = ss_between / ss_total if ss_total > 1e-12 else float("nan")
    return {"kind": "categorical_baseline", "predictor": col, "outcome": outcome, "n_pairs": int(len(sub)), "pearson_r": float("nan"), "eta_squared": eta2, "sign_accuracy": float("nan")}


def design_matrix(df: pd.DataFrame, cols: list[str], categories: dict[str, list[str]] | None = None, means: dict[str, float] | None = None, stds: dict[str, float] | None = None) -> tuple[np.ndarray, np.ndarray]:
    parts = [np.ones((len(df), 1), dtype=float)]
    ok = np.ones(len(df), dtype=bool)
    categories = categories or {}
    means = means or {}
    stds = stds or {}
    for c in cols:
        if c not in df.columns:
            continue
        if pd.api.types.is_numeric_dtype(df[c]):
            vals = pd.to_numeric(df[c], errors="coerce").to_numpy(dtype=float)
            finite = np.isfinite(vals)
            if c in means:
                mean = means[c]
            else:
                mean = float(np.nanmean(vals[finite])) if finite.any() else 0.0
            if c in stds:
                std = stds[c]
            else:
                std = float(np.nanstd(vals[finite])) if finite.any() else 1.0
            std = std if std > 1e-12 else 1.0
            vals = np.where(finite, vals, mean)
            parts.append(((vals - mean) / std).reshape(-1, 1))
            ok &= finite | np.isfinite(mean)
        else:
            series = df[c].astype(str).fillna("__nan__")
            levels = categories.get(c) or sorted(series.unique().tolist())
            # Drop first level to avoid exact collinearity with intercept.
            for level in levels[1:]:
                parts.append((series == level).astype(float).to_numpy().reshape(-1, 1))
    X = np.hstack(parts) if parts else np.ones((len(df), 1), dtype=float)
    return X, ok


def fit_beta(X: np.ndarray, y: np.ndarray, ridge: float = 1e-6) -> np.ndarray:
    if len(y) == 0:
        return np.zeros(X.shape[1], dtype=float)
    reg = ridge * np.eye(X.shape[1])
    reg[0, 0] = 0.0
    try:
        return np.linalg.solve(X.T @ X + reg, X.T @ y)
    except np.linalg.LinAlgError:
        return np.linalg.pinv(X.T @ X + reg) @ X.T @ y


def residuals_from_design(y: np.ndarray, X: np.ndarray) -> np.ndarray:
    beta = fit_beta(X, y)
    return y - X @ beta


def full_sample_r2(y: np.ndarray, X: np.ndarray) -> float:
    if len(y) < 3 or np.nanstd(y) <= 1e-12:
        return float("nan")
    beta = fit_beta(X, y)
    pred = X @ beta
    ss_res = float(np.nansum((y - pred) ** 2))
    ss_tot = float(np.nansum((y - np.nanmean(y)) ** 2))
    return float(1.0 - ss_res / ss_tot) if ss_tot > 1e-12 else float("nan")


def loo_cv_r2(df: pd.DataFrame, outcome: str, cols: list[str]) -> float:
    y_all = pd.to_numeric(df[outcome], errors="coerce").to_numpy(dtype=float)
    ok_all = np.isfinite(y_all)
    if ok_all.sum() < 6 or np.nanstd(y_all[ok_all]) <= 1e-12:
        return float("nan")
    preds = np.full(len(df), np.nan, dtype=float)
    for i in range(len(df)):
        train = df.iloc[np.arange(len(df)) != i].copy()
        test = df.iloc[[i]].copy()
        y_train = pd.to_numeric(train[outcome], errors="coerce").to_numpy(dtype=float)
        ok_train = np.isfinite(y_train)
        if not np.isfinite(y_all[i]) or ok_train.sum() < 4:
            continue
        categories = {c: sorted(train[c].astype(str).fillna("__nan__").unique().tolist()) for c in cols if c in train.columns and not pd.api.types.is_numeric_dtype(train[c])}
        means = {}
        stds = {}
        for c in cols:
            if c in train.columns and pd.api.types.is_numeric_dtype(train[c]):
                vals = pd.to_numeric(train[c], errors="coerce").to_numpy(dtype=float)
                finite = np.isfinite(vals)
                means[c] = float(np.nanmean(vals[finite])) if finite.any() else 0.0
                stds[c] = float(np.nanstd(vals[finite])) if finite.any() else 1.0
        X_train, ok_x_train = design_matrix(train, cols, categories=categories, means=means, stds=stds)
        train_ok = ok_train & ok_x_train
        if train_ok.sum() < 4:
            continue
        beta = fit_beta(X_train[train_ok], y_train[train_ok])
        X_test, _ = design_matrix(test, cols, categories=categories, means=means, stds=stds)
        preds[i] = float((X_test @ beta).item())
    ok = ok_all & np.isfinite(preds)
    if ok.sum() < 4:
        return float("nan")
    ss_res = float(np.nansum((y_all[ok] - preds[ok]) ** 2))
    ss_tot = float(np.nansum((y_all[ok] - np.nanmean(y_all[ok])) ** 2))
    return float(1.0 - ss_res / ss_tot) if ss_tot > 1e-12 else float("nan")


def sign_accuracy(x: np.ndarray, y: np.ndarray) -> float:
    if len(x) == 0:
        return float("nan")
    ok = np.isfinite(x) & np.isfinite(y) & (np.abs(x) > 1e-12) & (np.abs(y) > 1e-12)
    if ok.sum() == 0:
        return float("nan")
    return float(np.mean(np.sign(x[ok]) == np.sign(y[ok])))


def data_diagnostics(outcomes: pd.DataFrame, predictors: pd.DataFrame, merged: pd.DataFrame, args: argparse.Namespace) -> dict[str, Any]:
    diagnostics: dict[str, Any] = {}
    if "target_acquired_by_end" in outcomes.columns:
        diagnostics["target_acquired_by_end_rate"] = float(pd.to_numeric(outcomes["target_acquired_by_end"], errors="coerce").fillna(0).mean())
    for c in ["mean_linear_cka", "mean_gradient_cosine", "mean_first_order_transfer_score"]:
        if c in merged.columns:
            vals = pd.to_numeric(merged[c], errors="coerce").to_numpy(dtype=float)
            diagnostics[f"{c}_std"] = float(np.nanstd(vals)) if np.isfinite(vals).any() else float("nan")
            diagnostics[f"{c}_range"] = [float(np.nanmin(vals)), float(np.nanmax(vals))] if np.isfinite(vals).any() else [float("nan"), float("nan")]
    primary = select_primary_outcome(merged, args.primary_outcome)
    vals = pd.to_numeric(merged[primary], errors="coerce").to_numpy(dtype=float)
    diagnostics["primary_outcome"] = primary
    diagnostics["primary_outcome_std"] = float(np.nanstd(vals)) if np.isfinite(vals).any() else float("nan")
    diagnostics["primary_outcome_nonzero_rate_abs_gt_1e_minus_4"] = float(np.nanmean(np.abs(vals) > 1e-4)) if len(vals) else float("nan")
    diagnostics["n_pairs"] = int(merged["pair_id"].nunique()) if "pair_id" in merged else 0
    diagnostics["n_predictor_rows"] = int(len(predictors))
    return diagnostics


def pilot_gate_summary(
    merged: pd.DataFrame,
    correlations: pd.DataFrame,
    baseline_correlations: pd.DataFrame,
    residualized: pd.DataFrame,
    incremental: pd.DataFrame,
    diagnostics: dict[str, Any],
    args: argparse.Namespace,
) -> dict[str, Any]:
    primary = select_primary_outcome(merged, args.primary_outcome)
    effects = pd.to_numeric(merged.get(primary, pd.Series(dtype=float)), errors="coerce").to_numpy(dtype=float)
    effect_var = float(np.nanstd(effects)) if len(effects) else float("nan")
    nonzero_rate = float(np.nanmean(np.abs(effects) > 1e-4)) if len(effects) else float("nan")
    primary_raw = correlations[correlations["outcome"].eq(primary)].copy() if not correlations.empty else pd.DataFrame()
    best_raw = primary_raw.sort_values("pearson_r", key=lambda s: s.abs(), ascending=False).head(1) if not primary_raw.empty else pd.DataFrame()
    primary_base = baseline_correlations[baseline_correlations["outcome"].eq(primary)].copy() if not baseline_correlations.empty else pd.DataFrame()
    if not primary_base.empty and "eta_squared" in primary_base.columns:
        primary_base["strength"] = primary_base["pearson_r"].abs().fillna(0.0).combine(primary_base["eta_squared"].fillna(0.0), max)
    elif not primary_base.empty:
        primary_base["strength"] = primary_base["pearson_r"].abs()
    best_base = primary_base.sort_values("strength", ascending=False).head(1) if not primary_base.empty else pd.DataFrame()
    grad_resid = residualized[residualized["predictor"].str.contains("gradient_cosine|transfer_score|gradient_inner_product", regex=True, na=False)].copy() if not residualized.empty else pd.DataFrame()
    best_resid = grad_resid.sort_values("residualized_pearson_r", key=lambda s: s.abs(), ascending=False).head(1) if not grad_resid.empty else pd.DataFrame()
    incr = incremental[incremental["model"].eq("baseline_plus_predictor")].copy() if not incremental.empty else pd.DataFrame()
    grad_incr = incr[incr["predictor_added"].str.contains("gradient_cosine|transfer_score|gradient_inner_product", regex=True, na=False)] if not incr.empty else pd.DataFrame()
    best_incr = grad_incr.sort_values("delta_full_sample_r2_vs_baseline", ascending=False).head(1) if not grad_incr.empty else pd.DataFrame()
    acquired_rate = diagnostics.get("target_acquired_by_end_rate", float("nan"))
    warnings = []
    if np.isfinite(acquired_rate) and acquired_rate < 0.25:
        warnings.append("Few targets acquired by threshold; treat acquisition-time and exact-match outcomes as exploratory, use continuous token-AUC as primary.")
    if diagnostics.get("mean_linear_cka_std", np.nan) < 1e-3:
        warnings.append("Linear CKA is nearly constant across pairs; do not interpret it as a useful N2 signal without improved representation measurement.")
    if not best_base.empty and not best_raw.empty:
        try:
            if float(best_base.iloc[0].get("strength", np.nan)) > abs(float(best_raw.iloc[0].get("pearson_r", np.nan))):
                warnings.append("A baseline is stronger than the best raw coupling predictor; require residualized/incremental survival before scaling claims.")
        except Exception:
            pass
    return {
        "primary_effect_column": primary,
        "n_pairs": int(merged["pair_id"].nunique()) if "pair_id" in merged else 0,
        "effect_std": effect_var,
        "nonzero_effect_rate_abs_gt_1e_minus_4": nonzero_rate,
        "best_raw_predictor_on_primary": None if best_raw.empty else best_raw.iloc[0].to_dict(),
        "best_baseline_on_primary": None if best_base.empty else best_base.iloc[0].to_dict(),
        "best_residualized_gradient_on_primary": None if best_resid.empty else best_resid.iloc[0].to_dict(),
        "best_incremental_gradient_model_on_primary": None if best_incr.empty else best_incr.iloc[0].to_dict(),
        "warnings": warnings,
        "pilot_interpretation": "scale_only_if_interactions_have_variance_and_gradient_predictors_survive_baseline_controls",
    }


def render_report(
    args: argparse.Namespace,
    outcomes: pd.DataFrame,
    predictors: pd.DataFrame,
    per_seed: pd.DataFrame,
    merged: pd.DataFrame,
    correlations: pd.DataFrame,
    baseline_correlations: pd.DataFrame,
    residualized: pd.DataFrame,
    incremental: pd.DataFrame,
    diagnostics: dict[str, Any],
    gate: dict[str, Any],
) -> str:
    primary = gate.get("primary_effect_column")
    lines = [
        "# B1 N1 cross-task coupling pilot analysis",
        "",
        "This analysis estimates directional interaction effects from source-dose slopes and tests whether early coupling predictors track those effects after frequency/difficulty/surface baselines.",
        "",
        "## Data",
        f"- result_dir: `{args.result_dir}`",
        f"- outcome rows: `{len(outcomes)}`",
        f"- predictor rows: `{len(predictors)}`",
        f"- seed-level effect rows: `{len(per_seed)}`",
        f"- pair summary rows: `{len(merged)}`",
        f"- primary outcome: `{primary}`",
        "",
        "## Pilot gate diagnostics",
        f"- n_pairs: `{gate.get('n_pairs')}`",
        f"- primary effect std: `{gate.get('effect_std')}`",
        f"- nonzero effect rate |effect|>1e-4: `{gate.get('nonzero_effect_rate_abs_gt_1e_minus_4')}`",
        f"- target acquired-by-end rate: `{diagnostics.get('target_acquired_by_end_rate', 'NA')}`",
        "",
    ]
    warnings = gate.get("warnings") or []
    if warnings:
        lines.append("## Warnings")
        for w in warnings:
            lines.append(f"- {w}")
        lines.append("")

    lines.append("## Raw coupling-predictor correlations on primary outcome")
    show = correlations[correlations["outcome"].eq(primary)].copy() if not correlations.empty else pd.DataFrame()
    if show.empty:
        lines.append("No raw predictor correlations were estimable.")
    else:
        show = show.sort_values("pearson_r", key=lambda s: s.abs(), ascending=False).head(10)
        for _, r in show.iterrows():
            lines.append(f"- `{r['predictor']}`: r=`{r['pearson_r']}`, sign_acc=`{r['sign_accuracy']}`, n=`{int(r['n_pairs'])}`")
    lines.append("")

    lines.append("## Baseline correlations on primary outcome")
    showb = baseline_correlations[baseline_correlations["outcome"].eq(primary)].copy() if not baseline_correlations.empty else pd.DataFrame()
    if showb.empty:
        lines.append("No baseline correlations were estimable.")
    else:
        if "eta_squared" in showb.columns:
            showb["strength"] = showb["pearson_r"].abs().fillna(0.0).combine(showb["eta_squared"].fillna(0.0), max)
        else:
            showb["strength"] = showb["pearson_r"].abs()
        showb = showb.sort_values("strength", ascending=False).head(10)
        for _, r in showb.iterrows():
            eta = r.get("eta_squared", np.nan)
            eta_s = f", eta2=`{eta}`" if np.isfinite(eta) else ""
            lines.append(f"- `{r['predictor']}`: r=`{r.get('pearson_r', np.nan)}`{eta_s}, n=`{int(r['n_pairs'])}`")
    lines.append("")

    lines.append("## Residualized gradient/coupling signal")
    showr = residualized.copy() if not residualized.empty else pd.DataFrame()
    if showr.empty:
        lines.append("No residualized predictor correlations were estimable.")
    else:
        showr = showr.sort_values("residualized_pearson_r", key=lambda s: s.abs(), ascending=False).head(10)
        for _, r in showr.iterrows():
            lines.append(f"- `{r['predictor']}` vs residualized `{r['outcome']}`: r=`{r['residualized_pearson_r']}`, sign_acc=`{r['residualized_sign_accuracy']}`, n=`{int(r['n_pairs'])}`")
    lines.append("")

    lines.append("## Incremental model checks")
    if incremental.empty:
        lines.append("No incremental model checks were estimable.")
    else:
        showi = incremental.sort_values("delta_full_sample_r2_vs_baseline", ascending=False).head(10)
        for _, r in showi.iterrows():
            lines.append(f"- `{r['model']}` + `{r['predictor_added']}`: full R2=`{r['full_sample_r2']}`, ΔR2=`{r['delta_full_sample_r2_vs_baseline']}`, LOO CV R2=`{r['loo_cv_r2']}`, ΔCVR2=`{r['delta_loo_cv_r2_vs_baseline']}`")
    lines.extend(
        [
            "",
            "## How to read this validation analysis",
            "This is still not a thesis-grade claim. It decides whether a larger N1 run is worth launching. Scaling is justified only if interaction effects have nontrivial variance and early gradient/first-order predictors survive baseline-controlled or residualized tests, not merely raw correlations.",
        ]
    )
    return "\n".join(lines)


def stable_int_seed(s: str) -> int:
    # Use a stable string hash rather than Python's salted process hash.
    import hashlib

    return int(hashlib.sha256(s.encode("utf-8")).hexdigest()[:8], 16) % (2**31 - 1)


if __name__ == "__main__":
    main()
