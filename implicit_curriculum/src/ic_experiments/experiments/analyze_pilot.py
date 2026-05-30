from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze pilot outputs into compact comparison tables.")
    parser.add_argument("--result-dir", type=Path, required=True)
    parser.add_argument("--component", type=str, default="A_bit0")
    parser.add_argument("--matched-control", type=str, default="U_unrelated_xor910")
    parser.add_argument("--composites", type=str, nargs="+", default=["AB_and", "AC_xor"])
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result_dir = args.result_dir
    acq = pd.read_csv(result_dir / "acquisition_times.csv")
    eval_df = pd.read_csv(result_dir / "eval_curves.csv")
    grad_cross = pd.read_csv(result_dir / "grad_cross_task.csv") if (result_dir / "grad_cross_task.csv").exists() else pd.DataFrame()
    cka = pd.read_csv(result_dir / "representation_cka.csv") if (result_dir / "representation_cka.csv").exists() else pd.DataFrame()

    # Final evaluation metric by task/condition/seed.
    idx = eval_df.groupby(["condition", "seed"])["data_seen"].transform("max") == eval_df["data_seen"]
    final_eval = eval_df.loc[idx].copy()
    metric_col = "balanced_accuracy" if "balanced_accuracy" in final_eval.columns else "accuracy"

    acq_pivot = acq.pivot_table(index=["seed", "task_name"], columns="condition", values="acquired_at", aggfunc="first")
    final_pivot = final_eval.pivot_table(index=["seed", "task_name"], columns="condition", values=metric_col, aggfunc="first")

    rows = []
    conditions = sorted(final_eval["condition"].unique())
    for seed in sorted(final_eval["seed"].unique()):
        for task in sorted(final_eval["task_name"].unique()):
            baseline_final = _lookup(final_pivot, seed, task, "baseline")
            baseline_acq = _lookup(acq_pivot, seed, task, "baseline")
            for condition in conditions:
                if condition == "baseline":
                    continue
                rows.append(
                    {
                        "seed": seed,
                        "task_name": task,
                        "condition": condition,
                        "final_metric": _lookup(final_pivot, seed, task, condition),
                        "baseline_final_metric": baseline_final,
                        "delta_final_metric_vs_baseline": _lookup(final_pivot, seed, task, condition) - baseline_final,
                        "acquired_at": _lookup(acq_pivot, seed, task, condition),
                        "baseline_acquired_at": baseline_acq,
                        "delta_acquired_at_vs_baseline": _lookup(acq_pivot, seed, task, condition) - baseline_acq,
                    }
                )
    comparison = pd.DataFrame(rows)
    comparison.to_csv(result_dir / "pilot_condition_comparison.csv", index=False)

    diag_rows = []
    if not grad_cross.empty:
        final_grad = grad_cross.loc[grad_cross.groupby(["condition", "seed"])["data_seen"].transform("max") == grad_cross["data_seen"]]
        for condition in sorted(final_grad["condition"].unique()):
            for seed in sorted(final_grad["seed"].unique()):
                for comp in args.composites:
                    diag_rows.append(
                        {
                            "condition": condition,
                            "seed": seed,
                            "component": args.component,
                            "target_task": comp,
                            "component_target_grad_cosine": _pair_lookup(final_grad, condition, seed, args.component, comp, "grad_cosine_mean"),
                        }
                    )
    diag = pd.DataFrame(diag_rows)

    if not cka.empty and not diag.empty:
        final_cka = cka.loc[cka.groupby(["condition", "seed"])["data_seen"].transform("max") == cka["data_seen"]]
        diag["component_target_cka"] = [
            _pair_lookup(final_cka, row.condition, row.seed, row.component, row.target_task, "linear_cka")
            for row in diag.itertuples(index=False)
        ]
    diag.to_csv(result_dir / "component_composite_diagnostics.csv", index=False)

    lines = [
        "# Pilot analysis summary",
        "",
        f"Primary final metric: `{metric_col}`",
        "",
        "This script computes descriptive deltas only. It does not perform the mixed-effects inference needed for the full experiment.",
        "",
        "Generated files:",
        "- `pilot_condition_comparison.csv`",
        "- `component_composite_diagnostics.csv`",
    ]
    (result_dir / "analysis_summary.md").write_text("\n".join(lines), encoding="utf-8")
    print("Saved pilot analysis tables.")


def _lookup(pivot: pd.DataFrame, seed: int, task: str, condition: str) -> float:
    try:
        return float(pivot.loc[(seed, task), condition])
    except Exception:
        return float("nan")


def _pair_lookup(df: pd.DataFrame, condition: str, seed: int, ti: str, tj: str, col: str) -> float:
    rows = df[(df["condition"] == condition) & (df["seed"] == seed) & (df["task_i"] == ti) & (df["task_j"] == tj)]
    if rows.empty:
        return float("nan")
    return float(rows.iloc[0][col])


if __name__ == "__main__":
    main()
