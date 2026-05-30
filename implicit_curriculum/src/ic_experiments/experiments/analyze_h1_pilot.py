from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from ic_experiments.neural_design import choose_default_component_and_controls, load_neural_family

PROPERTY_COLUMNS = ["frequency", "reference_learnability", "formal_utility"]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Analyze generated-family H1/intervention pilot outputs.")
    p.add_argument("--result-dir", type=Path, required=True)
    p.add_argument("--component", type=str, default=None)
    p.add_argument("--composites", type=str, nargs="+", default=None)
    p.add_argument("--unrelated-control", type=str, default=None)
    p.add_argument("--fake-component-control", type=str, default=None)
    p.add_argument("--surface-control", type=str, default=None)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    result_dir = args.result_dir
    structure_path = result_dir / "structure_table.csv"
    if not structure_path.exists():
        raise SystemExit(f"Missing {structure_path}")
    structure = pd.read_csv(structure_path)
    tasks = load_neural_family(structure_path)
    chosen = _load_or_choose(result_dir, tasks)
    component = args.component or str(chosen["component"])
    composites = args.composites or list(chosen["composites"])
    unrelated = args.unrelated_control or str(chosen["unrelated_control"])
    fake = args.fake_component_control or str(chosen["fake_component_control"])
    surface = args.surface_control or str(chosen["surface_control"])
    controls = [unrelated, fake, surface]

    acq = pd.read_csv(result_dir / "acquisition_times.csv")
    eval_df = pd.read_csv(result_dir / "eval_curves.csv")
    grad_cross = _read_optional(result_dir / "grad_cross_task.csv")
    cka = _read_optional(result_dir / "representation_cka.csv")

    acq_summary = summarize_acquisition(acq, structure)
    acq_summary.to_csv(result_dir / "acquisition_summary_by_task.csv", index=False)

    ordering = ordering_summary(acq, structure)
    ordering.to_csv(result_dir / "ordering_summary.csv", index=False)

    intervention = intervention_pair_tests(acq, eval_df, composites=composites)
    intervention.to_csv(result_dir / "intervention_pair_tests.csv", index=False)

    diag = component_control_diagnostics(grad_cross, cka, component=component, composites=composites, controls=controls)
    diag.to_csv(result_dir / "component_control_diagnostics.csv", index=False)

    report = render_report(acq_summary, ordering, intervention, diag, component, composites, controls)
    (result_dir / "h1_analysis_report.md").write_text(report, encoding="utf-8")
    print("Saved generated-family analysis tables.")


def _read_optional(path: Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def _load_or_choose(result_dir: Path, tasks) -> dict:
    summary_path = result_dir / "summary.json"
    if summary_path.exists():
        try:
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            chosen = summary.get("chosen_component_and_controls")
            if chosen:
                return chosen
        except Exception:
            pass
    return choose_default_component_and_controls(tasks)


def summarize_acquisition(acq: pd.DataFrame, structure: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (condition, task_name), g in acq.groupby(["condition", "task_name"]):
        vals = g["acquired_at"].dropna().to_numpy(dtype=float)
        final_vals = g["final_balanced_accuracy"].dropna().to_numpy(dtype=float)
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
                "acquisition_rate": float(g["acquired_at"].notna().mean()),
                "mean_acquired_at": float(np.mean(vals)) if len(vals) else float("nan"),
                "median_acquired_at": float(np.median(vals)) if len(vals) else float("nan"),
                "std_acquired_at": float(np.std(vals, ddof=1)) if len(vals) > 1 else float("nan"),
                "mean_final_balanced_accuracy": float(np.mean(final_vals)) if len(final_vals) else float("nan"),
            }
        )
    return pd.DataFrame(rows).sort_values(["condition", "mean_acquired_at", "task_name"])


def ordering_summary(acq: pd.DataFrame, structure: pd.DataFrame) -> pd.DataFrame:
    baseline = acq[acq["condition"] == "baseline"].merge(structure, on=["task_name", "kind"], how="left")
    rows = []
    subsets = [("all", baseline), ("atomic", baseline[baseline["kind"] == "atomic"]), ("atomic_composite", baseline[baseline["kind"].isin(["atomic", "composite"])])]
    for kind_group, df in subsets:
        if df.empty:
            continue
        # Penalize non-acquisition by assigning max observed + one checkpoint-like unit.
        finite = df["acquired_at"].dropna()
        fill = float(finite.max() + max(1.0, finite.diff().dropna().median() if len(finite) > 2 else 1.0)) if len(finite) else 1e12
        y_time = df["acquired_at"].fillna(fill).to_numpy(dtype=float)
        y_final = df["final_balanced_accuracy"].to_numpy(dtype=float)
        for prop in PROPERTY_COLUMNS:
            x = df[prop].to_numpy(dtype=float)
            sp_time = _corr(_rankdata(x), _rankdata(y_time))
            sp_final = _corr(_rankdata(x), _rankdata(y_final))
            rows.append(
                {
                    "condition": "baseline",
                    "task_subset": kind_group,
                    "property": prop,
                    "n_rows": int(len(df)),
                    "acquisition_rate": float(df["acquired_at"].notna().mean()),
                    "pearson_acquisition_time": _corr(x, y_time),
                    "spearman_acquisition_time": sp_time,
                    "spearman_final_balanced_accuracy": sp_final,
                    "expected_time_direction": _expected_direction(prop),
                    "time_sign_matches_expected": _sign_matches(sp_time, prop),
                    "expected_final_metric_direction": _expected_final_direction(prop),
                    "final_metric_sign_matches_expected": _final_sign_matches(sp_final, prop),
                }
            )
    return pd.DataFrame(rows)


def intervention_pair_tests(acq: pd.DataFrame, eval_df: pd.DataFrame, composites: list[str]) -> pd.DataFrame:
    pairs = [
        ("upweight_component", "upweight_unrelated_matched", "earlier"),
        ("upweight_component", "upweight_fake_component", "earlier"),
        ("upweight_component", "upweight_surface_control", "earlier"),
        ("corrupt_component", "corrupt_unrelated_matched", "later"),
        ("delay_component", "delay_unrelated_matched", "later"),
    ]
    final_idx = eval_df.groupby(["condition", "seed"]) ["data_seen"].transform("max") == eval_df["data_seen"]
    final_eval = eval_df.loc[final_idx].copy()
    rows = []
    for task in composites:
        for focal, matched, expected in pairs:
            if focal not in set(acq["condition"]) or matched not in set(acq["condition"]):
                continue
            for_metric = _paired_metric(acq, final_eval, task, focal, matched)
            delta = for_metric["delta_acquired_at_focal_minus_matched"].dropna().to_numpy(dtype=float)
            if expected == "earlier":
                expected_flags = delta < 0
            else:
                expected_flags = delta > 0
            rows.append(
                {
                    "target_task": task,
                    "focal_condition": focal,
                    "matched_condition": matched,
                    "expected_focal_effect": expected,
                    "n_paired_acq": int(len(delta)),
                    "mean_delta_acquired_at_focal_minus_matched": float(np.mean(delta)) if len(delta) else float("nan"),
                    "median_delta_acquired_at_focal_minus_matched": float(np.median(delta)) if len(delta) else float("nan"),
                    "expected_direction_rate": float(np.mean(expected_flags)) if len(delta) else float("nan"),
                    "mean_delta_final_metric_focal_minus_matched": float(for_metric["delta_final_metric_focal_minus_matched"].mean()),
                }
            )
    return pd.DataFrame(rows)


def _paired_metric(acq: pd.DataFrame, final_eval: pd.DataFrame, task: str, focal: str, matched: str) -> pd.DataFrame:
    a = acq[(acq["task_name"] == task) & (acq["condition"] == focal)][["seed", "acquired_at"]].rename(columns={"acquired_at": "focal_acq"})
    b = acq[(acq["task_name"] == task) & (acq["condition"] == matched)][["seed", "acquired_at"]].rename(columns={"acquired_at": "matched_acq"})
    fa = final_eval[(final_eval["task_name"] == task) & (final_eval["condition"] == focal)][["seed", "balanced_accuracy"]].rename(columns={"balanced_accuracy": "focal_final"})
    fb = final_eval[(final_eval["task_name"] == task) & (final_eval["condition"] == matched)][["seed", "balanced_accuracy"]].rename(columns={"balanced_accuracy": "matched_final"})
    out = a.merge(b, on="seed", how="inner").merge(fa, on="seed", how="left").merge(fb, on="seed", how="left")
    out["delta_acquired_at_focal_minus_matched"] = out["focal_acq"] - out["matched_acq"]
    out["delta_final_metric_focal_minus_matched"] = out["focal_final"] - out["matched_final"]
    return out


def component_control_diagnostics(grad_cross: pd.DataFrame, cka: pd.DataFrame, component: str, composites: list[str], controls: list[str]) -> pd.DataFrame:
    if grad_cross.empty and cka.empty:
        return pd.DataFrame()
    final_grad = _final_by_condition_seed(grad_cross) if not grad_cross.empty else pd.DataFrame()
    final_cka = _final_by_condition_seed(cka) if not cka.empty else pd.DataFrame()
    rows = []
    sources = [("component", component)] + [("control", c) for c in controls]
    for condition in sorted(set(final_grad.get("condition", pd.Series(dtype=str))).union(set(final_cka.get("condition", pd.Series(dtype=str))))):
        seeds = sorted(set(final_grad[final_grad["condition"] == condition]["seed"]) if not final_grad.empty else set(final_cka[final_cka["condition"] == condition]["seed"]))
        for seed in seeds:
            for comp in composites:
                for source_role, source in sources:
                    rows.append(
                        {
                            "condition": condition,
                            "seed": seed,
                            "target_task": comp,
                            "source_role": source_role,
                            "source_task": source,
                            "grad_cosine": _pair_lookup(final_grad, condition, seed, source, comp, "grad_cosine_mean") if not final_grad.empty else float("nan"),
                            "linear_cka": _pair_lookup(final_cka, condition, seed, source, comp, "linear_cka") if not final_cka.empty else float("nan"),
                        }
                    )
    df = pd.DataFrame(rows)
    if not df.empty:
        # Add per-condition/seed/target contrasts: component minus mean controls.
        contrasts = []
        for keys, g in df.groupby(["condition", "seed", "target_task"]):
            comp_row = g[g["source_role"] == "component"]
            ctrl = g[g["source_role"] == "control"]
            if comp_row.empty or ctrl.empty:
                continue
            contrasts.append(
                {
                    "condition": keys[0],
                    "seed": keys[1],
                    "target_task": keys[2],
                    "source_role": "component_minus_controls",
                    "source_task": "component_minus_mean_controls",
                    "grad_cosine": float(comp_row["grad_cosine"].iloc[0] - ctrl["grad_cosine"].mean()),
                    "linear_cka": float(comp_row["linear_cka"].iloc[0] - ctrl["linear_cka"].mean()),
                }
            )
        df = pd.concat([df, pd.DataFrame(contrasts)], ignore_index=True)
    return df


def _final_by_condition_seed(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    idx = df.groupby(["condition", "seed"])["data_seen"].transform("max") == df["data_seen"]
    return df.loc[idx].copy()


def _pair_lookup(df: pd.DataFrame, condition: str, seed: int, ti: str, tj: str, col: str) -> float:
    if df.empty:
        return float("nan")
    rows = df[(df["condition"] == condition) & (df["seed"] == seed) & (df["task_i"] == ti) & (df["task_j"] == tj)]
    if rows.empty:
        return float("nan")
    return float(rows.iloc[0][col])


def _rankdata(x: np.ndarray) -> np.ndarray:
    order = np.argsort(x, kind="mergesort")
    ranks = np.empty(len(x), dtype=float)
    ranks[order] = np.arange(len(x), dtype=float)
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


def _corr(x: np.ndarray, y: np.ndarray) -> float:
    mask = np.isfinite(x) & np.isfinite(y)
    x = x[mask]
    y = y[mask]
    if len(x) < 3 or np.std(x) < 1e-12 or np.std(y) < 1e-12:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def _expected_direction(prop: str) -> str:
    if prop in {"frequency", "formal_utility"}:
        return "negative_more_property_earlier"
    if prop == "reference_learnability":
        return "positive_more_difficult_later"
    return "unknown"


def _expected_final_direction(prop: str) -> str:
    if prop in {"frequency", "formal_utility"}:
        return "positive_more_property_higher_final_metric"
    if prop == "reference_learnability":
        return "negative_more_difficult_lower_final_metric"
    return "unknown"


def _sign_matches(value: float, prop: str) -> bool | float:
    if not np.isfinite(value):
        return float("nan")
    if prop in {"frequency", "formal_utility"}:
        return bool(value < 0)
    if prop == "reference_learnability":
        return bool(value > 0)
    return float("nan")


def _final_sign_matches(value: float, prop: str) -> bool | float:
    if not np.isfinite(value):
        return float("nan")
    if prop in {"frequency", "formal_utility"}:
        return bool(value > 0)
    if prop == "reference_learnability":
        return bool(value < 0)
    return float("nan")


def render_report(acq_summary: pd.DataFrame, ordering: pd.DataFrame, intervention: pd.DataFrame, diag: pd.DataFrame, component: str, composites: list[str], controls: list[str]) -> str:
    baseline = acq_summary[acq_summary["condition"] == "baseline"]
    n_tasks = baseline["task_name"].nunique()
    mean_rate = baseline["acquisition_rate"].mean() if not baseline.empty else float("nan")
    lines = [
        "# Generated-family pilot analysis report",
        "",
        f"Chosen component: `{component}`",
        f"Composite targets: `{', '.join(composites)}`",
        f"Controls: `{', '.join(controls)}`",
        "",
        "## Baseline acquisition coverage",
        "",
        f"- n baseline tasks: `{n_tasks}`",
        f"- mean acquisition rate across tasks: `{mean_rate:.3f}`",
        "",
        "## Ordering summary",
        "",
    ]
    if ordering.empty:
        lines.append("No ordering summary was available.")
    else:
        for row in ordering.to_dict(orient="records"):
            lines.append(f"- {row['task_subset']} / {row['property']}: time-Spearman={row['spearman_acquisition_time']:.3f}, time-sign={row['time_sign_matches_expected']}, final-metric-Spearman={row['spearman_final_balanced_accuracy']:.3f}, final-sign={row['final_metric_sign_matches_expected']}")
    lines.extend(["", "## Intervention contrasts", ""])
    if intervention.empty:
        lines.append("No intervention contrasts were available. Run with intervention conditions to populate this section.")
    else:
        for row in intervention.to_dict(orient="records"):
            lines.append(
                f"- {row['target_task']}: {row['focal_condition']} vs {row['matched_condition']} "
                f"mean Δacq={row['mean_delta_acquired_at_focal_minus_matched']:.1f}, expected-direction-rate={row['expected_direction_rate']:.2f}"
            )
    lines.extend(["", "## Component-vs-control diagnostics", ""])
    if diag.empty:
        lines.append("No gradient/CKA diagnostics were available.")
    else:
        contrast = diag[diag["source_role"] == "component_minus_controls"]
        if contrast.empty:
            lines.append("Component-minus-control contrasts were unavailable.")
        else:
            lines.append(f"- mean component-minus-controls gradient cosine: `{contrast['grad_cosine'].mean():.4f}`")
            lines.append(f"- mean component-minus-controls linear CKA: `{contrast['linear_cka'].mean():.4f}`")
    lines.extend([
        "",
        "## Decision rule",
        "",
        "GREEN requires nontrivial acquisition coverage, expected ordering signs on baseline atomics/composites, and component interventions/diagnostics that beat fake, surface, and unrelated controls. YELLOW means redesign or tune before scaling. RED means fix the task family or analysis gate.",
    ])
    return "\n".join(lines)


if __name__ == "__main__":
    main()
