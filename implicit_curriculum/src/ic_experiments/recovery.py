from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd

from .design import PropertyDesignConfig, design_diagnostics, sample_property_design

MechanismName = Literal["frequency_only", "learnability_only", "three_factor", "dependency_gated"]


@dataclass(frozen=True)
class RecoveryConfig:
    """Configuration for the simulated recovery gate.

    This gate checks whether the planned analysis can recover known synthetic
    worlds before we trust it on neural training runs.
    """

    seed: int = 0
    n_replicates: int = 30
    noise_sd: float = 0.18
    dependency_delay: float = 0.55
    n_folds: int = 5
    one_standard_error: bool = True
    property_design: PropertyDesignConfig = PropertyDesignConfig()


MODEL_SPECS: dict[str, list[str]] = {
    "frequency_only": ["log_frequency"],
    "learnability_only": ["reference_learnability"],
    "freq_learn": ["log_frequency", "reference_learnability"],
    "three_factor": ["log_frequency", "reference_learnability", "formal_utility"],
}
MODEL_COMPLEXITY = {name: len(cols) for name, cols in MODEL_SPECS.items()}


def make_synthetic_world(
    design_df: pd.DataFrame,
    mechanism: MechanismName,
    seed: int,
    noise_sd: float = 0.18,
    dependency_delay: float = 0.55,
) -> pd.DataFrame:
    """Generate synthetic acquisition times from a known mechanism.

    Times are represented in arbitrary data-seen units. The fitted analysis uses
    log acquisition time, matching the intended H1/H2 regression and collapse
    diagnostics.
    """

    rng = np.random.default_rng(seed)
    df = design_df.copy()
    eps = rng.normal(0.0, noise_sd, size=len(df))
    log_freq = np.log(df["frequency"].to_numpy(dtype=float) + 1e-12)
    learn = df["reference_learnability"].to_numpy(dtype=float)
    util = df["formal_utility"].to_numpy(dtype=float)

    # Coefficients are deliberately separated enough to be recoverable, but not
    # so large that the task becomes trivial.
    if mechanism == "frequency_only":
        log_tau = 8.2 - 0.90 * log_freq + eps
    elif mechanism == "learnability_only":
        log_tau = 8.2 + 0.55 * learn + eps
    elif mechanism == "three_factor":
        log_tau = 8.2 - 0.65 * log_freq + 0.48 * learn - 0.70 * util + eps
    elif mechanism == "dependency_gated":
        # Base static predictor exists but composites are additionally gated by
        # component acquisition state. This creates a structured residual beyond
        # a static property-only model fit on atomics.
        log_tau = 8.2 - 0.55 * log_freq + 0.42 * learn - 0.45 * util + eps
        by_id = {sid: i for i, sid in enumerate(df["structure_id"])}
        for i, row in df.iterrows():
            if row["kind"] != "composite":
                continue
            comps = [row.get("component_a", ""), row.get("component_b", "")]
            comp_indices = [by_id[c] for c in comps if isinstance(c, str) and c in by_id]
            if not comp_indices:
                continue
            # Composite cannot resolve before its slowest component in this
            # synthetic world, plus an extra gate delay.
            slowest_component = float(np.max(log_tau[comp_indices]))
            log_tau[int(i)] = max(float(log_tau[int(i)]), slowest_component + dependency_delay + rng.normal(0, noise_sd / 2))
    else:
        raise ValueError(f"Unknown synthetic mechanism: {mechanism}")

    # Keep units moderately human-readable.
    df["log_frequency"] = log_freq
    df["true_mechanism"] = mechanism
    df["log_acquired_at"] = log_tau
    df["acquired_at"] = np.exp(log_tau)
    return df


def fit_predict_linear(train: pd.DataFrame, test: pd.DataFrame, features: list[str]) -> tuple[np.ndarray, np.ndarray]:
    x_train = np.column_stack([np.ones(len(train)), train[features].to_numpy(dtype=float)])
    y_train = train["log_acquired_at"].to_numpy(dtype=float)
    beta, *_ = np.linalg.lstsq(x_train, y_train, rcond=None)
    x_test = np.column_stack([np.ones(len(test)), test[features].to_numpy(dtype=float)])
    pred = x_test @ beta
    return pred, beta


def kfold_cv_scores(df: pd.DataFrame, n_folds: int = 5, seed: int = 0) -> pd.DataFrame:
    """Cross-validated MSE for the predictor ladder."""

    rng = np.random.default_rng(seed)
    indices = np.arange(len(df))
    rng.shuffle(indices)
    folds = np.array_split(indices, min(n_folds, len(indices)))
    rows = []
    for model_name, features in MODEL_SPECS.items():
        fold_mse = []
        for fold_id, test_idx in enumerate(folds):
            train_idx = np.setdiff1d(indices, test_idx)
            train = df.iloc[train_idx]
            test = df.iloc[test_idx]
            pred, beta = fit_predict_linear(train, test, features)
            y = test["log_acquired_at"].to_numpy(dtype=float)
            mse = float(np.mean((y - pred) ** 2))
            fold_mse.append(mse)
            rows.append(
                {
                    "model": model_name,
                    "fold": fold_id,
                    "mse": mse,
                    "n_train": len(train),
                    "n_test": len(test),
                    "features": ",".join(features),
                    "complexity": MODEL_COMPLEXITY[model_name],
                }
            )
    summary = pd.DataFrame(rows)
    return summary


def summarize_cv(cv_df: pd.DataFrame, one_standard_error: bool = True) -> pd.DataFrame:
    grouped = cv_df.groupby("model", as_index=False).agg(
        mean_mse=("mse", "mean"),
        se_mse=("mse", lambda x: float(np.std(x, ddof=1) / np.sqrt(len(x))) if len(x) > 1 else 0.0),
        complexity=("complexity", "first"),
        features=("features", "first"),
    )
    grouped = grouped.sort_values(["mean_mse", "complexity"]).reset_index(drop=True)
    best = grouped.iloc[0]
    threshold = float(best["mean_mse"] + (best["se_mse"] if one_standard_error else 0.0))
    eligible = grouped[grouped["mean_mse"] <= threshold].sort_values(["complexity", "mean_mse"])
    selected = str(eligible.iloc[0]["model"])
    grouped["selected_by_parsimony"] = grouped["model"] == selected
    grouped["best_mean_mse"] = float(best["mean_mse"])
    grouped["selection_threshold"] = threshold
    return grouped


def dependency_residual_test(df: pd.DataFrame) -> dict[str, float | str]:
    """Fit static model on atomics and test composite residual sign.

    Positive residuals mean composites are later than the static property model
    trained on atomics would predict. This is only a synthetic recovery check; in
    neural runs, residuals must be paired with interventions before being called
    dependency evidence.
    """

    atomics = df[df["kind"] == "atomic"].copy()
    composites = df[df["kind"] == "composite"].copy()
    if len(atomics) < 4 or composites.empty:
        return {
            "dependency_signal": "insufficient_data",
            "mean_composite_residual": float("nan"),
            "frac_positive_composite_residual": float("nan"),
        }
    features = MODEL_SPECS["three_factor"]
    pred, beta = fit_predict_linear(atomics, composites, features)
    residual = composites["log_acquired_at"].to_numpy(dtype=float) - pred
    return {
        "dependency_signal": "positive_residual" if float(np.mean(residual)) > 0 else "no_positive_residual",
        "mean_composite_residual": float(np.mean(residual)),
        "median_composite_residual": float(np.median(residual)),
        "frac_positive_composite_residual": float(np.mean(residual > 0)),
    }


def run_recovery_suite(config: RecoveryConfig) -> dict[str, pd.DataFrame | dict]:
    """Run the simulated recovery gate across known mechanisms."""

    design_df, diag = sample_property_design(config.property_design)
    mechanisms: list[MechanismName] = ["frequency_only", "learnability_only", "three_factor", "dependency_gated"]
    all_worlds = []
    cv_summaries = []
    cv_folds = []
    dep_rows = []

    for mechanism in mechanisms:
        for rep in range(config.n_replicates):
            seed = config.seed + 10_000 * (mechanisms.index(mechanism) + 1) + rep
            world = make_synthetic_world(
                design_df,
                mechanism=mechanism,
                seed=seed,
                noise_sd=config.noise_sd,
                dependency_delay=config.dependency_delay,
            )
            world["replicate"] = rep
            all_worlds.append(world)

            # Static predictor ladder: fit all structures for frequency/learnability/three-factor worlds.
            cv = kfold_cv_scores(world, n_folds=config.n_folds, seed=seed)
            cv["true_mechanism"] = mechanism
            cv["replicate"] = rep
            cv_folds.append(cv)
            summary = summarize_cv(cv, one_standard_error=config.one_standard_error)
            summary["true_mechanism"] = mechanism
            summary["replicate"] = rep
            cv_summaries.append(summary)

            dep = dependency_residual_test(world)
            dep["true_mechanism"] = mechanism
            dep["replicate"] = rep
            dep_rows.append(dep)

    worlds_df = pd.concat(all_worlds, ignore_index=True)
    cv_folds_df = pd.concat(cv_folds, ignore_index=True)
    cv_summary_df = pd.concat(cv_summaries, ignore_index=True)
    dependency_df = pd.DataFrame(dep_rows)
    verdict_df = recovery_verdict(cv_summary_df, dependency_df)
    return {
        "design": design_df,
        "design_diagnostics": diag,
        "synthetic_worlds": worlds_df,
        "cv_folds": cv_folds_df,
        "cv_summary": cv_summary_df,
        "dependency_residuals": dependency_df,
        "verdict": verdict_df,
    }


def recovery_verdict(cv_summary_df: pd.DataFrame, dependency_df: pd.DataFrame) -> pd.DataFrame:
    selected = cv_summary_df[cv_summary_df["selected_by_parsimony"]].copy()
    rows = []
    for mechanism, g in selected.groupby("true_mechanism"):
        model_counts = g["model"].value_counts(normalize=True).to_dict()
        dep_g = dependency_df[dependency_df["true_mechanism"] == mechanism]
        rows.append(
            {
                "true_mechanism": mechanism,
                "n_replicates": int(len(g)),
                "selected_frequency_only_rate": float(model_counts.get("frequency_only", 0.0)),
                "selected_learnability_only_rate": float(model_counts.get("learnability_only", 0.0)),
                "selected_freq_learn_rate": float(model_counts.get("freq_learn", 0.0)),
                "selected_three_factor_rate": float(model_counts.get("three_factor", 0.0)),
                "mean_composite_residual": float(dep_g["mean_composite_residual"].mean()),
                "positive_residual_rate": float((dep_g["mean_composite_residual"] > 0).mean()),
            }
        )
    return pd.DataFrame(rows)
