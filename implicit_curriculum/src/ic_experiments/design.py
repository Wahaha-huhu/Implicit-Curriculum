from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd


PROPERTY_COLUMNS = ["frequency", "reference_learnability", "formal_utility"]


@dataclass(frozen=True)
class DesignCriteria:
    """Identifiability criteria for structural-property designs.

    These criteria are gates, not theoretical assumptions. If a proposed task
    family fails them, the analysis should not claim separate effects of
    frequency, reference learnability, and formal utility.
    """

    max_vif: float = 5.0
    max_abs_pearson: float = 0.65
    max_abs_spearman: float = 0.70
    max_condition_number: float = 50.0
    min_rows: int = 12


@dataclass(frozen=True)
class PropertyDesignConfig:
    """Configuration for synthetic structural-property designs.

    This generator produces a property table used by the simulated recovery gate.
    It does not by itself construct neural tasks. The later H1/H2 task generator
    should use the same diagnostics after mapping properties into actual tasks.
    """

    n_atomic: int = 12
    n_composite: int = 8
    frequency_low: float = 0.02
    frequency_high: float = 0.30
    learnability_low: float = 1.0
    learnability_high: float = 5.0
    utility_low: float = 0.0
    utility_high: float = 1.0
    seed: int = 0
    max_attempts: int = 20_000
    criteria: DesignCriteria = DesignCriteria()


def _rankdata(x: np.ndarray) -> np.ndarray:
    """Return average ranks without depending on scipy."""

    order = np.argsort(x, kind="mergesort")
    ranks = np.empty(len(x), dtype=float)
    ranks[order] = np.arange(len(x), dtype=float)
    # Average ranks for ties.
    values = x[order]
    start = 0
    while start < len(x):
        end = start + 1
        while end < len(x) and values[end] == values[start]:
            end += 1
        if end - start > 1:
            ranks[order[start:end]] = float(np.mean(np.arange(start, end)))
        start = end
    return ranks


def _safe_corrcoef(x: np.ndarray, y: np.ndarray) -> float:
    if np.std(x) < 1e-12 or np.std(y) < 1e-12:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def vif_values(x: np.ndarray, names: list[str] | None = None) -> dict[str, float]:
    """Variance inflation factor for each column of x."""

    if names is None:
        names = [f"x{i}" for i in range(x.shape[1])]
    out: dict[str, float] = {}
    for i, name in enumerate(names):
        y = x[:, i]
        other = np.delete(x, i, axis=1)
        design = np.column_stack([np.ones(len(y)), other])
        beta, *_ = np.linalg.lstsq(design, y, rcond=None)
        pred = design @ beta
        ss_res = float(((y - pred) ** 2).sum())
        ss_tot = float(((y - y.mean()) ** 2).sum())
        r2 = 1.0 - ss_res / max(ss_tot, 1e-12)
        out[f"vif_{name}"] = float(1.0 / max(1.0 - r2, 1e-12))
    return out


def binned_mutual_information(x: np.ndarray, y: np.ndarray, bins: int = 4) -> float:
    """Small nonlinear-dependence diagnostic using equal-frequency bins.

    This is intentionally lightweight. It is not a formal independence test, but
    it catches designs where linear VIF is acceptable while predictors are still
    strongly coupled by a monotone or nonlinear relation.
    """

    if len(x) < 4 or np.std(x) < 1e-12 or np.std(y) < 1e-12:
        return 0.0
    # Equal-frequency bin edges are robust for skewed frequencies.
    q = np.linspace(0, 1, bins + 1)
    bx_edges = np.unique(np.quantile(x, q))
    by_edges = np.unique(np.quantile(y, q))
    if len(bx_edges) <= 2 or len(by_edges) <= 2:
        return 0.0
    bx = np.digitize(x, bx_edges[1:-1], right=True)
    by = np.digitize(y, by_edges[1:-1], right=True)
    joint = np.zeros((bx.max() + 1, by.max() + 1), dtype=float)
    for a, b in zip(bx, by):
        joint[a, b] += 1.0
    joint /= joint.sum()
    px = joint.sum(axis=1, keepdims=True)
    py = joint.sum(axis=0, keepdims=True)
    expected = px @ py
    mask = joint > 0
    mi = float((joint[mask] * np.log(joint[mask] / expected[mask])).sum())
    return mi


def design_diagnostics(df: pd.DataFrame, columns: Iterable[str] = PROPERTY_COLUMNS) -> dict[str, float | bool]:
    """Compute linear and lightweight nonlinear diagnostics for property designs."""

    cols = list(columns)
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing design columns: {missing}")
    x = df[cols].to_numpy(dtype=float)
    x_std = (x - x.mean(axis=0, keepdims=True)) / np.maximum(x.std(axis=0, keepdims=True), 1e-12)
    out: dict[str, float | bool] = {
        "n_rows": float(len(df)),
        "design_condition_number": float(np.linalg.cond(np.column_stack([np.ones(len(x_std)), x_std]))),
    }
    out.update(vif_values(x, cols))
    for i, ci in enumerate(cols):
        for j, cj in enumerate(cols):
            if i >= j:
                continue
            xi = x[:, i]
            xj = x[:, j]
            out[f"pearson_{ci}__{cj}"] = _safe_corrcoef(xi, xj)
            out[f"spearman_{ci}__{cj}"] = _safe_corrcoef(_rankdata(xi), _rankdata(xj))
            out[f"binned_mi_{ci}__{cj}"] = binned_mutual_information(xi, xj)
    return out


def passes_design_criteria(diagnostics: dict[str, float | bool], criteria: DesignCriteria) -> bool:
    if float(diagnostics["n_rows"]) < criteria.min_rows:
        return False
    if float(diagnostics["design_condition_number"]) > criteria.max_condition_number:
        return False
    for key, value in diagnostics.items():
        if key.startswith("vif_") and float(value) > criteria.max_vif:
            return False
        if key.startswith("pearson_") and abs(float(value)) > criteria.max_abs_pearson:
            return False
        if key.startswith("spearman_") and abs(float(value)) > criteria.max_abs_spearman:
            return False
    return True


def sample_property_design(config: PropertyDesignConfig) -> tuple[pd.DataFrame, dict[str, float | bool]]:
    """Sample a decorrelated synthetic property table.

    The frequency column is normalized to sum to one, but diagnostics use the
    resulting normalized rates. Composites receive randomly sampled formal
    components so dependency-recovery tests can be run on the table.
    """

    rng = np.random.default_rng(config.seed)
    n = config.n_atomic + config.n_composite
    best_df: pd.DataFrame | None = None
    best_diag: dict[str, float | bool] | None = None
    best_score = float("inf")

    for attempt in range(config.max_attempts):
        # Oversample independent latent variables and then shuffle each property
        # independently. This encourages factorial coverage without imposing
        # linear dependence.
        freq = np.exp(rng.uniform(np.log(config.frequency_low), np.log(config.frequency_high), size=n))
        freq = freq / freq.sum()
        learn = rng.uniform(config.learnability_low, config.learnability_high, size=n)
        util = rng.uniform(config.utility_low, config.utility_high, size=n)

        # Force utility to be mostly carried by atomic structures, while keeping
        # enough composite variation for diagnostics. This mirrors formal utility
        # in dependency graphs: components are often atomics, but composites can
        # also serve as components of later structures.
        kinds = np.array(["atomic"] * config.n_atomic + ["composite"] * config.n_composite)
        util[config.n_atomic :] *= 0.35

        df = pd.DataFrame(
            {
                "structure_id": [f"S{i:02d}" for i in range(n)],
                "kind": kinds,
                "frequency": freq,
                "reference_learnability": learn,
                "formal_utility": util,
            }
        )

        # Assign components to composites from earlier structures. This is used
        # only by the synthetic dependency-gated world.
        component_a: list[str] = [""] * n
        component_b: list[str] = [""] * n
        for row_idx in range(config.n_atomic, n):
            choices = rng.choice(np.arange(0, row_idx), size=2, replace=False)
            component_a[row_idx] = df.loc[int(choices[0]), "structure_id"]
            component_b[row_idx] = df.loc[int(choices[1]), "structure_id"]
        df["component_a"] = component_a
        df["component_b"] = component_b

        diag = design_diagnostics(df)
        score = _design_score(diag, config.criteria)
        if score < best_score:
            best_score = score
            best_df = df.copy()
            best_diag = dict(diag)
            best_diag["attempts_used"] = float(attempt + 1)
            best_diag["passed"] = passes_design_criteria(best_diag, config.criteria)
        if passes_design_criteria(diag, config.criteria):
            diag["attempts_used"] = float(attempt + 1)
            diag["passed"] = True
            return df, diag

    assert best_df is not None and best_diag is not None
    best_diag["passed"] = False
    return best_df, best_diag


def _design_score(diag: dict[str, float | bool], criteria: DesignCriteria) -> float:
    score = max(0.0, float(diag["design_condition_number"]) / criteria.max_condition_number - 1.0)
    for key, value in diag.items():
        if key.startswith("vif_"):
            score += max(0.0, float(value) / criteria.max_vif - 1.0)
        elif key.startswith("pearson_"):
            score += max(0.0, abs(float(value)) / criteria.max_abs_pearson - 1.0)
        elif key.startswith("spearman_"):
            score += max(0.0, abs(float(value)) / criteria.max_abs_spearman - 1.0)
    return score
