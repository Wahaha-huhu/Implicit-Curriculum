from __future__ import annotations

import json
import math
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

from ic_experiments.metrics import acquisition_times
from ic_experiments.sequence_analysis import final_metrics


CONTROL_KEYS = [
    "same_operation_control",
    "different_operation_control",
    "fake_component_control",
    "surface_control",
    "unrelated_control",
]

V2_STANDARD_CONDITIONS = [
    "baseline",
    "upweight_component",
    "upweight_same_operation_unrelated",
    "upweight_different_operation_matched",
    "upweight_fake_component",
    "upweight_surface_control",
    "delay_component",
    "delay_same_operation_unrelated",
    "delay_different_operation_matched",
    "corrupt_component",
    "corrupt_same_operation_unrelated",
    "corrupt_different_operation_matched",
]

V2_STRONG_CONDITIONS = [
    "baseline",
    "pretrain_component",
    "pretrain_same_operation_unrelated",
    "pretrain_different_operation_matched",
    "corrupt_component_strong",
    "corrupt_same_operation_unrelated_strong",
    "corrupt_different_operation_matched_strong",
    "delay_component_strong",
    "delay_same_operation_unrelated_strong",
    "delay_different_operation_matched_strong",
]

V2_FULL_CONDITIONS = list(dict.fromkeys(V2_STANDARD_CONDITIONS + V2_STRONG_CONDITIONS))

CONDITION_SETS = {
    "standard": V2_STANDARD_CONDITIONS,
    "strong": V2_STRONG_CONDITIONS,
    "full": V2_FULL_CONDITIONS,
}

# Primary exact-vs-control evidence used by the v2 verdict layer.  The H3 runner can
# emit more contrasts; this subset maps directly to the v2 control battery.
CONTRAST_CONDITION_MAP = [
    ("upweight", "same_operation", "upweight_component", "upweight_same_operation_unrelated", "earlier"),
    ("upweight", "different_operation", "upweight_component", "upweight_different_operation_matched", "earlier"),
    ("upweight", "fake_component", "upweight_component", "upweight_fake_component", "earlier"),
    ("upweight", "surface", "upweight_component", "upweight_surface_control", "earlier"),
    ("pretrain", "same_operation", "pretrain_component", "pretrain_same_operation_unrelated", "earlier"),
    ("pretrain", "different_operation", "pretrain_component", "pretrain_different_operation_matched", "earlier"),
    ("delay", "same_operation", "delay_component", "delay_same_operation_unrelated", "later"),
    ("delay", "different_operation", "delay_component", "delay_different_operation_matched", "later"),
    ("delay_strong", "same_operation", "delay_component_strong", "delay_same_operation_unrelated_strong", "later"),
    ("delay_strong", "different_operation", "delay_component_strong", "delay_different_operation_matched_strong", "later"),
    ("corrupt", "same_operation", "corrupt_component", "corrupt_same_operation_unrelated", "later"),
    ("corrupt", "different_operation", "corrupt_component", "corrupt_different_operation_matched", "later"),
    ("corrupt_strong", "same_operation", "corrupt_component_strong", "corrupt_same_operation_unrelated_strong", "later"),
    ("corrupt_strong", "different_operation", "corrupt_component_strong", "corrupt_different_operation_matched_strong", "later"),
]


def slug(text: str) -> str:
    text = str(text)
    return re.sub(r"[^A-Za-z0-9_.=-]+", "_", text).strip("_")


def make_pair_id(component: str, composite: str) -> str:
    return f"{slug(component)}__to__{slug(composite)}"


def normalize_structure_table(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "task_name" not in out.columns and "structure_id" in out.columns:
        out["task_name"] = out["structure_id"]
    if "structure_id" not in out.columns and "task_name" in out.columns:
        out["structure_id"] = out["task_name"]
    if "op" not in out.columns and "operation" in out.columns:
        out["op"] = out["operation"]
    for col in ["kind", "op", "components", "control_type", "control_for"]:
        if col not in out.columns:
            out[col] = ""
    for col in ["frequency", "reference_learnability", "formal_utility"]:
        if col not in out.columns:
            out[col] = np.nan
    return out


def split_components(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        raw = list(value)
    else:
        text = str(value).strip()
        if not text or text.lower() == "nan":
            return []
        # Support comma-separated strings, JSON-ish lists, and tuple reprs.
        text = text.strip("[]()")
        raw = re.split(r"[,;|]", text)
    return [str(x).strip().strip("'\"") for x in raw if str(x).strip().strip("'\"") and str(x).strip().lower() != "nan"]


def normalize_pair_selection(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    aliases = {
        "component_id": "component",
        "component_task": "component",
        "composite_id": "composite",
        "composite_task": "composite",
        "task_name": "composite",
        "mean_residual_log_time": "residual_log_time",
        "positive_residual_rate": "positive_rate",
    }
    for old, new in aliases.items():
        if old in out.columns and new not in out.columns:
            out[new] = out[old]
    if "component" not in out.columns or "composite" not in out.columns:
        raise ValueError(f"Pair-selection table must contain component/composite columns; columns={list(out.columns)}")
    if "h3_ready" not in out.columns:
        out["h3_ready"] = True
    if "h3_readiness_score" not in out.columns:
        out["h3_readiness_score"] = np.nan
    if "residual_log_time" not in out.columns:
        out["residual_log_time"] = np.nan
    if "positive_rate" not in out.columns:
        out["positive_rate"] = np.nan
    return out


def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "y", "ready"}


def _choose_controls(structure: pd.DataFrame, component: str, composite: str) -> dict[str, str]:
    # Imported lazily to avoid a module-level dependency cycle.  The existing H3
    # runner owns the task-matching heuristics; the census layer should reuse them
    # rather than fork control selection.
    from ic_experiments.experiments.run_b1_h3_interventions import choose_control, choose_operation_control

    same = choose_operation_control(structure, component, composite, same_operation=True) or ""
    diff = choose_operation_control(structure, component, composite, same_operation=False) or ""
    fake = choose_control(structure, "shortcut", component) or ""
    surface = choose_control(structure, "surface_control", component) or ""
    unrelated = same or choose_control(structure, "unrelated", composite) or ""
    return {
        "unrelated_control": unrelated,
        "same_operation_control": same,
        "different_operation_control": diff,
        "fake_component_control": fake,
        "surface_control": surface,
    }


def build_causal_census_plan(
    structure_df: pd.DataFrame,
    ready_pair_selection: pd.DataFrame | None = None,
    *,
    ready_only: bool = False,
    allow_not_ready: bool = False,
    min_readiness_score: float | None = None,
    max_pairs: int | None = None,
    include_composites: Iterable[str] | None = None,
    exclude_composites: Iterable[str] | None = None,
) -> pd.DataFrame:
    """Build the v2 pre-registered census membership table.

    If a readiness/pair-selection table is supplied, membership is based on those
    rows, optionally filtered to h3_ready rows.  Without such a table, membership is
    the formal task graph: every component listed on every composite row.
    """

    structure = normalize_structure_table(structure_df)
    by_task = {str(r["task_name"]): r for _, r in structure.iterrows()}
    include = set(str(x) for x in include_composites or [])
    exclude = set(str(x) for x in exclude_composites or [])

    source_rows: list[dict[str, Any]] = []
    if ready_pair_selection is not None and not ready_pair_selection.empty:
        ready = normalize_pair_selection(ready_pair_selection)
        if include:
            ready = ready[ready["composite"].astype(str).isin(include)].copy()
        if exclude:
            ready = ready[~ready["composite"].astype(str).isin(exclude)].copy()
        if min_readiness_score is not None:
            ready = ready[pd.to_numeric(ready["h3_readiness_score"], errors="coerce").fillna(-np.inf) >= float(min_readiness_score)].copy()
        if ready_only:
            ready_filtered = ready[ready["h3_ready"].map(as_bool)].copy()
            if not ready_filtered.empty or not allow_not_ready:
                ready = ready_filtered
        if ready.empty:
            return pd.DataFrame()
        sort_cols = [c for c in ["h3_ready", "h3_readiness_score", "residual_log_time", "positive_rate"] if c in ready.columns]
        if sort_cols:
            ready = ready.sort_values(sort_cols, ascending=[False] * len(sort_cols))
        for _, r in ready.iterrows():
            source_rows.append({
                "component": str(r["component"]),
                "composite": str(r["composite"]),
                "h3_ready": as_bool(r.get("h3_ready", True)),
                "h3_readiness_score": _safe_float(r.get("h3_readiness_score", np.nan)),
                "source_residual_log_time": _safe_float(r.get("residual_log_time", np.nan)),
                "source_positive_rate": _safe_float(r.get("positive_rate", np.nan)),
                "membership_source": "ready_pair_selection",
            })
    else:
        composites = structure[structure["kind"].astype(str).str.lower().eq("composite")].copy()
        if include:
            composites = composites[composites["task_name"].astype(str).isin(include)].copy()
        if exclude:
            composites = composites[~composites["task_name"].astype(str).isin(exclude)].copy()
        for _, c in composites.iterrows():
            composite = str(c["task_name"])
            for component in split_components(c.get("components", "")):
                source_rows.append({
                    "component": component,
                    "composite": composite,
                    "h3_ready": False,
                    "h3_readiness_score": np.nan,
                    "source_residual_log_time": np.nan,
                    "source_positive_rate": np.nan,
                    "membership_source": "formal_task_graph",
                })

    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for src in source_rows:
        component = str(src["component"])
        composite = str(src["composite"])
        if (component, composite) in seen:
            continue
        seen.add((component, composite))
        if component not in by_task or composite not in by_task:
            # Keep the row, but make missingness explicit for preregistration audit.
            controls = {k: "" for k in CONTROL_KEYS}
            complete = False
        else:
            controls = _choose_controls(structure, component, composite)
            complete = all(bool(controls.get(k, "")) for k in ["same_operation_control", "different_operation_control", "fake_component_control", "surface_control"])
        comp_meta = by_task.get(composite, {})
        component_meta = by_task.get(component, {})
        row = {
            "census_row": len(rows),
            "pair_id": make_pair_id(component, composite),
            "component": component,
            "composite": composite,
            **controls,
            "control_battery_complete": bool(complete),
            "h3_ready": bool(src.get("h3_ready", False)),
            "h3_readiness_score": src.get("h3_readiness_score", np.nan),
            "membership_source": src.get("membership_source", ""),
            "source_residual_log_time": src.get("source_residual_log_time", np.nan),
            "source_positive_rate": src.get("source_positive_rate", np.nan),
            "component_kind": str(component_meta.get("kind", "")),
            "component_op": str(component_meta.get("op", component_meta.get("operation", ""))),
            "component_frequency": _safe_float(component_meta.get("frequency", np.nan)),
            "component_reference_learnability": _safe_float(component_meta.get("reference_learnability", np.nan)),
            "component_formal_utility": _safe_float(component_meta.get("formal_utility", np.nan)),
            "composite_kind": str(comp_meta.get("kind", "")),
            "composite_op": str(comp_meta.get("op", comp_meta.get("operation", ""))),
            "composite_components": str(comp_meta.get("components", "")),
            "composite_frequency": _safe_float(comp_meta.get("frequency", np.nan)),
            "composite_reference_learnability": _safe_float(comp_meta.get("reference_learnability", np.nan)),
            "composite_formal_utility": _safe_float(comp_meta.get("formal_utility", np.nan)),
            "compositional_depth": max(1, len(split_components(comp_meta.get("components", "")))) if len(comp_meta) else np.nan,
        }
        rows.append(row)
        if max_pairs is not None and len(rows) >= int(max_pairs):
            break
    return pd.DataFrame(rows)


def render_causal_census_plan_report(plan: pd.DataFrame, *, structure_path: str = "", ready_path: str = "", condition_set: str = "strong") -> str:
    lines = [
        "# B1 v2 causal-census plan",
        "",
        "This file upgrades the earlier H3 pair intervention workflow into the v2 census unit: every row is a pre-registered component→composite causal test with the full matched-control battery.",
        "",
        f"- structure table: `{structure_path}`",
        f"- readiness/pair source: `{ready_path}`",
        f"- planned rows: `{len(plan)}`",
        f"- control-battery complete rows: `{int(plan.get('control_battery_complete', pd.Series(dtype=bool)).map(as_bool).sum()) if not plan.empty else 0}`",
        f"- condition set for generated commands: `{condition_set}`",
        "",
        "## Planned pairs",
    ]
    if plan.empty:
        lines.append("No rows selected.")
    else:
        for _, r in plan.iterrows():
            lines.append(
                f"- row `{int(r['census_row'])}` `{r['component']}` → `{r['composite']}`; "
                f"ready={bool(r.get('h3_ready', False))}, score={_fmt(r.get('h3_readiness_score', np.nan))}, "
                f"same-op=`{r.get('same_operation_control', '')}`, diff-op=`{r.get('different_operation_control', '')}`, "
                f"fake=`{r.get('fake_component_control', '')}`, surface=`{r.get('surface_control', '')}`, "
                f"battery_complete={bool(r.get('control_battery_complete', False))}"
            )
    lines += [
        "",
        "## Verdict rule",
        "A row is exact-dependent only if the exact component separates from same-operation, different-operation, fake-component, and surface controls. If same-operation controls match the exact component, the row is operation-family transfer. If no exact manipulation moves the composite beyond matched controls, the row is difficulty/parallel. Rows without measurable composite acquisition are excluded as hard-composite/non-learning and counted in coverage.",
    ]
    return "\n".join(lines)


def render_causal_census_run_script(
    plan: pd.DataFrame,
    *,
    structure_table: str,
    output_prefix: str,
    condition_set: str = "full",
    seeds: Iterable[int | str] = range(10),
    max_data_seen: int = 250000,
    batch_size: int = 256,
    n_checkpoints: int = 100,
    eval_examples_per_task: int = 512,
    d_model: int = 128,
    n_layers: int = 2,
    n_heads: int = 4,
    d_mlp: int = 512,
    device: str = "cuda",
    pretrain_data_seen: int = 50000,
    code_version: str = "v3.2",
    archive_root: str | None = None,
    thesis_use: str = "candidate",
) -> str:
    conditions = CONDITION_SETS[condition_set]
    seed_text = " ".join(str(s) for s in seeds)
    cond_text = " ".join(conditions)
    lines = ["#!/usr/bin/env bash", "set -euo pipefail", ""]
    for _, r in plan.iterrows():
        out = f"{output_prefix}/row{int(r['census_row']):03d}_{slug(r['pair_id'])}"
        common_archive = f" --archive-root {archive_root}" if archive_root else ""
        lines.append(f"echo '[census] row {int(r['census_row'])}: {r['component']} -> {r['composite']}'")
        lines.append(
            "PYTHONPATH=src python -m ic_experiments.experiments.run_b1_h3_interventions "
            f"--output-dir {out} --structure-table {structure_table} "
            f"--component {r['component']} --composite {r['composite']} "
            f"--same-operation-control {r.get('same_operation_control', '')} "
            f"--different-operation-control {r.get('different_operation_control', '')} "
            f"--fake-component-control {r.get('fake_component_control', '')} "
            f"--surface-control {r.get('surface_control', '')} "
            f"--unrelated-control {r.get('unrelated_control', '')} "
            f"--conditions {cond_text} --seeds {seed_text} --max-data-seen {max_data_seen} "
            f"--batch-size {batch_size} --n-checkpoints {n_checkpoints} --eval-examples-per-task {eval_examples_per_task} "
            f"--d-model {d_model} --n-layers {n_layers} --n-heads {n_heads} --d-mlp {d_mlp} "
            f"--device {device} --pretrain-data-seen {pretrain_data_seen} --code-version {code_version}{common_archive} --thesis-use {thesis_use}"
        )
        lines.append(
            "PYTHONPATH=src python -m ic_experiments.experiments.analyze_b1_h3_interventions "
            f"--result-dir {out} --metric-family token_accuracy --threshold 0.7 "
            f"--code-version {code_version}{common_archive} --thesis-use {thesis_use}"
        )
        lines.append("")
    return "\n".join(lines)


@dataclass(frozen=True)
class VerdictConfig:
    metric_family: str = "token_accuracy"
    threshold: float = 0.7
    patience: int = 2
    min_direction_rate: float = 0.60
    min_abs_censored_delta: float = 0.0
    alpha: float = 0.10
    bootstrap_samples: int = 2000
    random_seed: int = 0


def load_pair_config(result_dir: Path) -> dict[str, str]:
    path = result_dir / "h3_pair_config.csv"
    if path.exists():
        df = pd.read_csv(path)
        if not df.empty:
            return {k: str(v) for k, v in df.iloc[0].to_dict().items() if str(v) and str(v) != "nan"}
    summary = result_dir / "summary.json"
    if summary.exists():
        data = json.loads(summary.read_text(encoding="utf-8"))
        return {k: str(v) for k, v in data.get("pair", {}).items() if str(v) and str(v) != "nan"}
    raise FileNotFoundError(f"No h3_pair_config.csv or summary.json in {result_dir}")


def load_prepared_pair_outputs(result_dir: Path, cfg: VerdictConfig) -> tuple[dict[str, str], pd.DataFrame, pd.DataFrame]:
    pair = load_pair_config(result_dir)
    eval_path = result_dir / "eval_curves.csv"
    if (result_dir / "h3_acquisition_times.csv").exists():
        acq = pd.read_csv(result_dir / "h3_acquisition_times.csv")
    elif eval_path.exists():
        eval_df = pd.read_csv(eval_path)
        acq = acquisition_times(eval_df, threshold=cfg.threshold, patience=cfg.patience, metric=cfg.metric_family)
        max_by = eval_df.groupby(["condition", "seed"], as_index=False)["data_seen"].max().rename(columns={"data_seen": "max_data_seen"})
        acq = acq.merge(max_by, on=["condition", "seed"], how="left")
        acq["censored_acquired_at"] = acq["acquired_at"].fillna(acq["max_data_seen"])
        acq["is_censored"] = acq["acquired_at"].isna()
    else:
        raise FileNotFoundError(f"No h3_acquisition_times.csv or eval_curves.csv in {result_dir}")
    if (result_dir / "h3_final_metrics.csv").exists():
        final = pd.read_csv(result_dir / "h3_final_metrics.csv")
    elif (result_dir / "final_metrics.csv").exists():
        final = pd.read_csv(result_dir / "final_metrics.csv")
    elif eval_path.exists():
        final = final_metrics(pd.read_csv(eval_path))
    else:
        final = pd.DataFrame()
    if "max_data_seen" not in acq.columns and eval_path.exists():
        max_by = pd.read_csv(eval_path).groupby(["condition", "seed"], as_index=False)["data_seen"].max().rename(columns={"data_seen": "max_data_seen"})
        acq = acq.merge(max_by, on=["condition", "seed"], how="left")
    if "censored_acquired_at" not in acq.columns:
        acq["censored_acquired_at"] = acq["acquired_at"].fillna(acq.get("max_data_seen", np.nan))
    if "is_censored" not in acq.columns:
        acq["is_censored"] = acq["acquired_at"].isna()
    return pair, acq, final


def analyze_pair_result_dir(result_dir: Path, cfg: VerdictConfig | None = None, *, plan_row: pd.Series | dict[str, Any] | None = None) -> tuple[pd.DataFrame, dict[str, Any]]:
    cfg = cfg or VerdictConfig()
    pair, acq, final = load_prepared_pair_outputs(result_dir, cfg)
    rows = []
    for manipulation, control_type, exact_cond, control_cond, expected in CONTRAST_CONDITION_MAP:
        row = paired_condition_contrast(
            acq,
            final,
            composite=pair["composite"],
            exact_condition=exact_cond,
            control_condition=control_cond,
            expected=expected,
            metric_family=cfg.metric_family,
            bootstrap_samples=cfg.bootstrap_samples,
            random_seed=cfg.random_seed,
        )
        if row is not None:
            row.update({
                "result_dir": str(result_dir),
                "pair_id": make_pair_id(pair["component"], pair["composite"]),
                "component": pair["component"],
                "composite": pair["composite"],
                "manipulation": manipulation,
                "control_type": control_type,
                "exact_condition": exact_cond,
                "control_condition": control_cond,
            })
            rows.append(row)
    contrasts = pd.DataFrame(rows)
    verdict = classify_pair_verdict(pair, contrasts, cfg, plan_row=plan_row, result_dir=result_dir)
    return contrasts, verdict


def paired_condition_contrast(
    acq: pd.DataFrame,
    final: pd.DataFrame,
    *,
    composite: str,
    exact_condition: str,
    control_condition: str,
    expected: str,
    metric_family: str,
    bootstrap_samples: int,
    random_seed: int,
) -> dict[str, Any] | None:
    if exact_condition not in set(acq["condition"]) or control_condition not in set(acq["condition"]):
        return None
    left = acq[(acq["condition"] == exact_condition) & (acq["task_name"] == composite)][
        ["seed", "acquired_at", "censored_acquired_at", "is_censored"]
    ].rename(columns={
        "acquired_at": "exact_acquired_at",
        "censored_acquired_at": "exact_censored_acquired_at",
        "is_censored": "exact_is_censored",
    })
    right = acq[(acq["condition"] == control_condition) & (acq["task_name"] == composite)][
        ["seed", "acquired_at", "censored_acquired_at", "is_censored"]
    ].rename(columns={
        "acquired_at": "control_acquired_at",
        "censored_acquired_at": "control_censored_acquired_at",
        "is_censored": "control_is_censored",
    })
    merged = left.merge(right, on="seed", how="inner")
    if merged.empty:
        return None
    final_col = metric_family if metric_family in final.columns else "token_accuracy"
    if not final.empty and final_col in final.columns:
        ef = final[(final["condition"] == exact_condition) & (final["task_name"] == composite)][["seed", final_col]].rename(columns={final_col: "exact_final_metric"})
        cf = final[(final["condition"] == control_condition) & (final["task_name"] == composite)][["seed", final_col]].rename(columns={final_col: "control_final_metric"})
        merged = merged.merge(ef, on="seed", how="left").merge(cf, on="seed", how="left")
    else:
        merged["exact_final_metric"] = np.nan
        merged["control_final_metric"] = np.nan
    # Positive support means the exact component has the expected effect relative to
    # the control.  For earlier/helpful conditions exact-control time is negative;
    # for later/harmful conditions it is positive.  Convert both to signed support.
    raw_time_delta = merged["exact_censored_acquired_at"] - merged["control_censored_acquired_at"]
    raw_final_delta = merged["exact_final_metric"] - merged["control_final_metric"]
    if expected == "earlier":
        signed_time_effect = -raw_time_delta
        signed_final_effect = raw_final_delta
    elif expected == "later":
        signed_time_effect = raw_time_delta
        signed_final_effect = -raw_final_delta
    else:
        raise ValueError(expected)
    rng = np.random.default_rng(random_seed)
    ci_lo, ci_hi = bootstrap_mean_ci(signed_time_effect.to_numpy(dtype=float), rng, n=bootstrap_samples)
    p_sign = two_sided_sign_pvalue(signed_time_effect.to_numpy(dtype=float))
    direction = signed_time_effect > 0
    final_direction = signed_final_effect > 0
    return {
        "expected_direction": expected,
        "n_paired_seeds": int(len(merged)),
        "exact_acquisition_rate": float(merged["exact_acquired_at"].notna().mean()),
        "control_acquisition_rate": float(merged["control_acquired_at"].notna().mean()),
        "raw_censored_delta_acquired_at_mean": _safe_float(raw_time_delta.mean()),
        "signed_censored_time_effect_mean": _safe_float(signed_time_effect.mean()),
        "signed_censored_time_effect_ci_low": _safe_float(ci_lo),
        "signed_censored_time_effect_ci_high": _safe_float(ci_hi),
        "time_expected_direction_rate": _safe_float(direction.mean()),
        "time_sign_pvalue": _safe_float(p_sign),
        "signed_final_effect_mean": _safe_float(signed_final_effect.mean()),
        "final_expected_direction_rate": _safe_float(final_direction.mean()),
        "exact_final_metric_mean": _safe_float(merged["exact_final_metric"].mean()),
        "control_final_metric_mean": _safe_float(merged["control_final_metric"].mean()),
    }


def bootstrap_mean_ci(values: np.ndarray, rng: np.random.Generator, *, n: int = 2000, alpha: float = 0.05) -> tuple[float, float]:
    values = values[np.isfinite(values)]
    if len(values) == 0:
        return np.nan, np.nan
    if len(values) == 1 or n <= 0:
        return float(values.mean()), float(values.mean())
    draws = rng.choice(values, size=(int(n), len(values)), replace=True).mean(axis=1)
    return float(np.quantile(draws, alpha / 2)), float(np.quantile(draws, 1 - alpha / 2))


def two_sided_sign_pvalue(values: np.ndarray) -> float:
    vals = values[np.isfinite(values)]
    vals = vals[np.abs(vals) > 1e-12]
    n = len(vals)
    if n == 0:
        return 1.0
    k = int((vals > 0).sum())
    # Exact two-sided binomial sign test under p=0.5, without scipy.
    tail = sum(math.comb(n, i) for i in range(0, min(k, n - k) + 1)) / (2**n)
    return float(min(1.0, 2.0 * tail))


def classify_pair_verdict(pair: dict[str, str], contrasts: pd.DataFrame, cfg: VerdictConfig, *, plan_row: pd.Series | dict[str, Any] | None = None, result_dir: Path | None = None) -> dict[str, Any]:
    out: dict[str, Any] = {
        "pair_id": make_pair_id(pair["component"], pair["composite"]),
        "component": pair["component"],
        "composite": pair["composite"],
        "result_dir": str(result_dir or ""),
        "n_contrasts": int(len(contrasts)),
        "verdict": "insufficient_evidence",
        "verdict_tier": "excluded",
        "verdict_reason": "No usable exact-vs-control contrasts were available.",
    }
    if plan_row is not None:
        row = dict(plan_row)
        for col in [
            "census_row", "h3_ready", "h3_readiness_score", "source_residual_log_time", "source_positive_rate",
            "component_op", "composite_op", "component_frequency", "composite_frequency",
            "component_reference_learnability", "composite_reference_learnability", "composite_formal_utility", "compositional_depth",
        ]:
            if col in row:
                out[col] = row[col]
    if contrasts.empty:
        return out

    def passing(df: pd.DataFrame) -> pd.Series:
        if df.empty:
            return pd.Series(dtype=bool)
        return (
            (pd.to_numeric(df["time_expected_direction_rate"], errors="coerce") >= cfg.min_direction_rate)
            & (pd.to_numeric(df["signed_censored_time_effect_mean"], errors="coerce") > cfg.min_abs_censored_delta)
        )

    contrasts = contrasts.copy()
    contrasts["passes_direction"] = passing(contrasts)
    contrasts["passes_significance"] = pd.to_numeric(contrasts["time_sign_pvalue"], errors="coerce") <= cfg.alpha
    contrasts["passes_v2"] = contrasts["passes_direction"] & (contrasts["passes_significance"] | (contrasts["n_paired_seeds"] < 5))

    # Readiness / coverage: if even the most helpful exact manipulations do not
    # produce measurable composite performance, the row is a hard-composite/non-learning exclusion.
    helpful = contrasts[contrasts["manipulation"].isin(["upweight", "pretrain"])]
    if not helpful.empty:
        max_exact_acq = pd.to_numeric(helpful["exact_acquisition_rate"], errors="coerce").max()
        max_exact_final = pd.to_numeric(helpful["exact_final_metric_mean"], errors="coerce").max()
        if np.isfinite(max_exact_acq) and max_exact_acq <= 0.0 and (not np.isfinite(max_exact_final) or max_exact_final < cfg.threshold * 0.5):
            out.update({
                "verdict": "hard_composite_non_learning",
                "verdict_tier": "excluded",
                "verdict_reason": "Helpful exact-component interventions did not make the composite measurably acquire; coverage exclusion rather than causal negative.",
            })
            return _attach_contrast_summaries(out, contrasts)

    exact_same = contrasts[contrasts["control_type"].eq("same_operation")]
    exact_diff = contrasts[contrasts["control_type"].eq("different_operation")]
    exact_fake = contrasts[contrasts["control_type"].eq("fake_component")]
    exact_surface = contrasts[contrasts["control_type"].eq("surface")]

    same_pass = bool(exact_same["passes_v2"].any())
    diff_pass = bool(exact_diff["passes_v2"].any())
    fake_present = not exact_fake.empty
    surface_present = not exact_surface.empty
    fake_pass = bool(exact_fake["passes_v2"].any()) if fake_present else False
    surface_pass = bool(exact_surface["passes_v2"].any()) if surface_present else False

    # For exact dependency the exact intervention must beat the full v2 control
    # battery. Missing fake/surface evidence is intentionally not upgraded to a
    # Tier-1 exact-dependency claim.
    if same_pass and diff_pass and fake_pass and surface_pass:
        out.update({
            "verdict": "exact_component_dependency",
            "verdict_tier": "tier1_candidate",
            "verdict_reason": "Exact-component intervention separates from same-operation, different-operation, fake-component, and surface controls.",
        })
    elif same_pass and diff_pass and (not fake_present or not surface_present):
        out.update({
            "verdict": "candidate_exact_dependency_incomplete_battery",
            "verdict_tier": "ambiguous",
            "verdict_reason": "Exact component separates from same-operation and different-operation controls, but fake/surface evidence is missing; do not claim full v2 exact dependency.",
        })
    elif diff_pass and not same_pass:
        out.update({
            "verdict": "operation_family_transfer",
            "verdict_tier": "tier1_alternative",
            "verdict_reason": "Exact component separates from different-operation controls but not same-operation controls, consistent with operation-family transfer rather than exact dependency.",
        })
    elif same_pass and not diff_pass:
        out.update({
            "verdict": "difficulty_or_generic_transfer",
            "verdict_tier": "tier1_alternative",
            "verdict_reason": "Exact component does not clearly separate from different-operation controls; generic difficulty/transfer remains plausible.",
        })
    elif bool(contrasts["passes_v2"].any()):
        out.update({
            "verdict": "partial_or_control_specific_effect",
            "verdict_tier": "ambiguous",
            "verdict_reason": "Some contrasts pass but not the required same/different-operation pattern for exact dependency or operation-family transfer.",
        })
    else:
        out.update({
            "verdict": "difficulty_parallel_or_null",
            "verdict_tier": "tier1_negative",
            "verdict_reason": "No exact-component manipulation separates from matched controls under the preregistered direction rule.",
        })
    return _attach_contrast_summaries(out, contrasts)


def _attach_contrast_summaries(out: dict[str, Any], contrasts: pd.DataFrame) -> dict[str, Any]:
    for control_type, prefix in [
        ("same_operation", "same"),
        ("different_operation", "different"),
        ("fake_component", "fake"),
        ("surface", "surface"),
    ]:
        g = contrasts[contrasts["control_type"].eq(control_type)]
        out[f"{prefix}_n_contrasts"] = int(len(g))
        out[f"{prefix}_max_signed_time_effect"] = _safe_float(pd.to_numeric(g.get("signed_censored_time_effect_mean", pd.Series(dtype=float)), errors="coerce").max()) if not g.empty else np.nan
        out[f"{prefix}_max_direction_rate"] = _safe_float(pd.to_numeric(g.get("time_expected_direction_rate", pd.Series(dtype=float)), errors="coerce").max()) if not g.empty else np.nan
        out[f"{prefix}_min_pvalue"] = _safe_float(pd.to_numeric(g.get("time_sign_pvalue", pd.Series(dtype=float)), errors="coerce").min()) if not g.empty else np.nan
    out["max_signed_time_effect"] = _safe_float(pd.to_numeric(contrasts.get("signed_censored_time_effect_mean", pd.Series(dtype=float)), errors="coerce").max())
    out["max_direction_rate"] = _safe_float(pd.to_numeric(contrasts.get("time_expected_direction_rate", pd.Series(dtype=float)), errors="coerce").max())
    out["min_pvalue"] = _safe_float(pd.to_numeric(contrasts.get("time_sign_pvalue", pd.Series(dtype=float)), errors="coerce").min())
    return out


def benjamini_hochberg(pvalues: pd.Series) -> pd.Series:
    p = pd.to_numeric(pvalues, errors="coerce")
    out = pd.Series(np.nan, index=p.index, dtype=float)
    valid = p.dropna().sort_values()
    m = len(valid)
    if m == 0:
        return out
    vals = valid.to_numpy(dtype=float)
    adj = vals * m / np.arange(1, m + 1)
    adj = np.minimum.accumulate(adj[::-1])[::-1]
    adj = np.minimum(adj, 1.0)
    out.loc[valid.index] = adj
    return out


def census_verdict_summary(verdicts: pd.DataFrame, *, bootstrap_samples: int = 2000, random_seed: int = 0) -> pd.DataFrame:
    if verdicts.empty or "verdict" not in verdicts.columns:
        return pd.DataFrame()
    rng = np.random.default_rng(random_seed)
    labels = sorted(verdicts["verdict"].dropna().astype(str).unique())
    n = len(verdicts)
    rows = []
    for label in labels:
        arr = (verdicts["verdict"].astype(str) == label).to_numpy(dtype=float)
        lo, hi = bootstrap_mean_ci(arr, rng, n=bootstrap_samples)
        rows.append({
            "verdict": label,
            "n_pairs": int(arr.sum()),
            "total_pairs": int(n),
            "fraction": float(arr.mean()) if n else np.nan,
            "fraction_ci_low": lo,
            "fraction_ci_high": hi,
        })
    return pd.DataFrame(rows).sort_values(["n_pairs", "verdict"], ascending=[False, True]).reset_index(drop=True)


def auc_score(y_true: np.ndarray, scores: np.ndarray) -> float:
    y = np.asarray(y_true).astype(int)
    s = np.asarray(scores, dtype=float)
    mask = np.isfinite(s)
    y = y[mask]
    s = s[mask]
    if len(np.unique(y)) < 2:
        return np.nan
    pos = s[y == 1]
    neg = s[y == 0]
    total = len(pos) * len(neg)
    if total == 0:
        return np.nan
    wins = 0.0
    for v in pos:
        wins += float((v > neg).sum()) + 0.5 * float((v == neg).sum())
    return float(wins / total)


def leave_group_out_auc(df: pd.DataFrame, *, label_col: str, score_col: str, group_col: str) -> pd.DataFrame:
    if group_col not in df.columns:
        return pd.DataFrame()
    rows = []
    for group, g in df.groupby(group_col, dropna=False):
        rows.append({
            "held_out_group": group,
            "n_rows": int(len(g)),
            "auc": auc_score(g[label_col].to_numpy(), g[score_col].to_numpy()),
        })
    return pd.DataFrame(rows)


def run_subprocess(cmd: list[str], *, dry_run: bool = False) -> int:
    print(" ".join(cmd))
    if dry_run:
        return 0
    return int(subprocess.run(cmd, check=True).returncode)


def _safe_float(x: Any) -> float:
    try:
        return float(x)
    except Exception:
        return float("nan")


def _fmt(x: Any) -> str:
    try:
        if pd.isna(x):
            return "nan"
        return f"{float(x):.3f}"
    except Exception:
        return str(x)
