from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np
import pandas as pd

from .neural_design import choose_default_component_and_controls
from .tasks import TaskSpec, task_table


@dataclass(frozen=True)
class CalibrationCriteria:
    """Criteria for deciding whether a generated neural family is trainable enough.

    These criteria are intentionally about *coverage*, not final scientific claims.
    A family can pass design identifiability but fail calibration if too few tasks
    cross the acquisition threshold under a baseline run.
    """

    target_min_mean_acquisition_rate: float = 0.45
    target_max_mean_acquisition_rate: float = 0.85
    min_atomic_composite_acquisition_rate: float = 0.35
    max_atomic_composite_acquisition_rate: float = 0.90
    usable_composite_min_rate: float = 0.30
    usable_composite_max_rate: float = 0.95
    min_usable_composites_for_component: int = 3
    min_component_acquisition_rate: float = 0.50
    target_composite_rate: float = 0.65

    def to_dict(self) -> dict:
        return asdict(self)


def acquisition_summary_from_times(acq: pd.DataFrame, structure: pd.DataFrame) -> pd.DataFrame:
    """Summarize threshold crossings by task for calibration and reporting."""

    rows = []
    for (condition, task_name), g in acq.groupby(["condition", "task_name"]):
        vals = g["acquired_at"].dropna().to_numpy(dtype=float)
        st = structure[structure["task_name"] == task_name].iloc[0].to_dict()
        rows.append(
            {
                "condition": condition,
                "task_name": task_name,
                "kind": st["kind"],
                "frequency": float(st["frequency"]),
                "reference_learnability": float(st["reference_learnability"]),
                "formal_utility": float(st["formal_utility"]),
                "n_seeds": int(len(g)),
                "n_acquired": int(g["acquired_at"].notna().sum()),
                "acquisition_rate": float(g["acquired_at"].notna().mean()),
                "mean_acquired_at": float(np.mean(vals)) if len(vals) else float("nan"),
                "median_acquired_at": float(np.median(vals)) if len(vals) else float("nan"),
                "mean_final_balanced_accuracy": float(g["final_balanced_accuracy"].mean()),
            }
        )
    return pd.DataFrame(rows).sort_values(["condition", "kind", "task_name"])


def choose_component_and_controls_from_calibration(
    tasks: list[TaskSpec],
    acq_summary: pd.DataFrame,
    criteria: CalibrationCriteria = CalibrationCriteria(),
) -> dict[str, str | list[str] | float | int | bool]:
    """Pick a focal component with multiple moderately acquired composites.

    v0.3 picked a high-utility component from the static graph. That sometimes
    selected a component whose composites were too hard, producing NaN contrasts.
    This function uses a brief baseline calibration run to select a component whose
    component task and downstream composites are actually in the measurable range.
    """

    static_choice = choose_default_component_and_controls(tasks)
    task_df = task_table(tasks)
    baseline = acq_summary[acq_summary["condition"] == "baseline"].copy()
    if baseline.empty:
        return {**static_choice, "calibration_passed": False, "reason": "no_baseline_rows"}

    rate_by_task = baseline.set_index("task_name")["acquisition_rate"].to_dict()
    final_by_task = baseline.set_index("task_name")["mean_final_balanced_accuracy"].to_dict()
    composite_tasks = [t for t in tasks if t.kind == "composite"]
    atomic_tasks = [t for t in tasks if t.kind == "atomic"]

    scored: list[dict] = []
    for component in atomic_tasks:
        comp_rate = float(rate_by_task.get(component.name, 0.0))
        comp_final = float(final_by_task.get(component.name, np.nan))
        downstream = [t for t in composite_tasks if component.name in t.components]
        usable = []
        too_easy = 0
        too_hard = 0
        for target in downstream:
            rate = float(rate_by_task.get(target.name, 0.0))
            if criteria.usable_composite_min_rate <= rate <= criteria.usable_composite_max_rate:
                usable.append(target.name)
            elif rate > criteria.usable_composite_max_rate:
                too_easy += 1
            else:
                too_hard += 1
        if downstream:
            mean_target_rate = float(np.mean([rate_by_task.get(t.name, 0.0) for t in downstream]))
        else:
            mean_target_rate = 0.0
        score = (
            10.0 * len(usable)
            + 2.0 * comp_rate
            + 2.0 * float(component.formal_utility)
            - abs(mean_target_rate - criteria.target_composite_rate)
            - 0.5 * too_hard
            - 0.25 * too_easy
        )
        scored.append(
            {
                "component": component.name,
                "component_acquisition_rate": comp_rate,
                "component_final_balanced_accuracy": comp_final,
                "n_downstream_composites": len(downstream),
                "n_usable_composites": len(usable),
                "usable_composites": usable,
                "mean_downstream_composite_acquisition_rate": mean_target_rate,
                "score": float(score),
            }
        )

    if not scored:
        return {**static_choice, "calibration_passed": False, "reason": "no_atomic_candidates"}
    best = max(scored, key=lambda r: r["score"])
    component = str(best["component"])
    composites = list(best["usable_composites"])
    if not composites:
        composites = [t.name for t in composite_tasks if component in t.components][:3]
    else:
        composites = composites[:3]

    # Reuse static matching logic for controls, but centered on the calibrated component.
    component_row = task_df[task_df["task_name"] == component].iloc[0]
    component_freq = float(component_row["frequency"])
    component_learn = float(component_row["reference_learnability"])
    controls = task_df[task_df["kind"].isin(["unrelated", "surface_control", "shortcut"])].copy()
    controls["match_distance"] = (
        (np.log(controls["frequency"] + 1e-12) - np.log(component_freq + 1e-12)).abs()
        + 0.25 * (controls["reference_learnability"] - component_learn).abs()
    )
    unrelated = controls[controls["kind"] == "unrelated"].sort_values("match_distance")
    fake = controls[controls["kind"] == "shortcut"].sort_values("match_distance")
    surface = controls[controls["kind"] == "surface_control"].sort_values("match_distance")

    passed = (
        best["component_acquisition_rate"] >= criteria.min_component_acquisition_rate
        and best["n_usable_composites"] >= criteria.min_usable_composites_for_component
    )
    return {
        "component": component,
        "composites": composites,
        "unrelated_control": str(unrelated.iloc[0]["task_name"]) if not unrelated.empty else str(controls.iloc[0]["task_name"]),
        "fake_component_control": str(fake.iloc[0]["task_name"]) if not fake.empty else str(controls.iloc[0]["task_name"]),
        "surface_control": str(surface.iloc[0]["task_name"]) if not surface.empty else str(controls.iloc[0]["task_name"]),
        "calibration_passed": bool(passed),
        "n_usable_composites": int(best["n_usable_composites"]),
        "component_acquisition_rate": float(best["component_acquisition_rate"]),
        "mean_downstream_composite_acquisition_rate": float(best["mean_downstream_composite_acquisition_rate"]),
        "reason": "passed" if passed else "insufficient_usable_composites_or_component_coverage",
        "candidate_scores": scored,
    }


def family_calibration_summary(
    tasks: list[TaskSpec],
    acq_summary: pd.DataFrame,
    criteria: CalibrationCriteria = CalibrationCriteria(),
) -> dict[str, float | int | bool | str]:
    """Return coverage-level summary and pass/fail verdict for a family."""

    baseline = acq_summary[acq_summary["condition"] == "baseline"].copy()
    if baseline.empty:
        return {"passed": False, "reason": "no_baseline_rows"}
    mean_rate = float(baseline["acquisition_rate"].mean())
    ac = baseline[baseline["kind"].isin(["atomic", "composite"])]
    ac_rate = float(ac["acquisition_rate"].mean()) if not ac.empty else float("nan")
    composite = baseline[baseline["kind"] == "composite"]
    composite_rate = float(composite["acquisition_rate"].mean()) if not composite.empty else float("nan")
    chosen = choose_component_and_controls_from_calibration(tasks, acq_summary, criteria)
    passed = (
        criteria.target_min_mean_acquisition_rate <= mean_rate <= criteria.target_max_mean_acquisition_rate
        and criteria.min_atomic_composite_acquisition_rate <= ac_rate <= criteria.max_atomic_composite_acquisition_rate
        and bool(chosen.get("calibration_passed", False))
    )
    reason = "passed" if passed else "coverage_or_component_target_failed"
    return {
        "passed": bool(passed),
        "reason": reason,
        "mean_acquisition_rate": mean_rate,
        "atomic_composite_acquisition_rate": ac_rate,
        "composite_acquisition_rate": composite_rate,
        "n_tasks": int(baseline["task_name"].nunique()),
        "chosen_component": str(chosen.get("component")),
        "n_usable_composites": int(chosen.get("n_usable_composites", 0)),
        "component_acquisition_rate": float(chosen.get("component_acquisition_rate", np.nan)),
        "mean_downstream_composite_acquisition_rate": float(chosen.get("mean_downstream_composite_acquisition_rate", np.nan)),
    }


def save_calibration_report(
    output_dir: str | Path,
    candidate_table: pd.DataFrame,
    selected: dict,
    criteria: CalibrationCriteria,
) -> Path:
    output = Path(output_dir)
    lines = [
        "# Calibrated neural design report",
        "",
        "This gate runs brief baseline neural training on generated families and selects a family whose tasks are identifiable *and* measurably trainable.",
        "",
        "## Criteria",
        "",
    ]
    for k, v in criteria.to_dict().items():
        lines.append(f"- {k}: `{v}`")
    lines.extend(["", "## Selected family", ""])
    for k, v in selected.items():
        if k == "candidate_scores":
            continue
        if isinstance(v, list):
            lines.append(f"- {k}: `{', '.join(map(str, v))}`")
        else:
            lines.append(f"- {k}: `{v}`")
    lines.extend(["", "## Candidate summary", ""])
    if candidate_table.empty:
        lines.append("No candidates were evaluated.")
    else:
        display_cols = [c for c in ["candidate_seed", "passed", "mean_acquisition_rate", "atomic_composite_acquisition_rate", "composite_acquisition_rate", "chosen_component", "n_usable_composites"] if c in candidate_table.columns]
        lines.append(candidate_table[display_cols].to_markdown(index=False))
    path = output / "calibrated_neural_design_report.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
