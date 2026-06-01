from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

from ic_experiments.census import CONDITION_SETS, render_causal_census_plan_report
from ic_experiments.run_management import append_registry, write_manifest


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Write a frozen B1 v2 preregistration scaffold for the causal census and alignment predictor.")
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--structure-table", type=Path, default=None)
    p.add_argument("--census-plan", type=Path, default=None)
    p.add_argument("--ready-pair-selection", type=Path, default=None)
    p.add_argument("--condition-set", choices=sorted(CONDITION_SETS), default="full")
    p.add_argument("--metric-family", type=str, default="token_accuracy")
    p.add_argument("--threshold", type=float, default=0.7)
    p.add_argument("--patience", type=int, default=2)
    p.add_argument("--min-direction-rate", type=float, default=0.60)
    p.add_argument("--alpha", type=float, default=0.10)
    p.add_argument("--early-max-fraction", type=float, default=0.20)
    p.add_argument("--code-version", type=str, default="v3.2")
    p.add_argument("--archive-root", type=Path, default=None)
    p.add_argument("--thesis-use", type=str, default="preregistered")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    plan = pd.read_csv(args.census_plan) if args.census_plan and args.census_plan.exists() else pd.DataFrame()
    spec = {
        "version": "b1_v2_causal_census_v3.2",
        "purpose": "Freeze the Exp 2 causal census and Exp 3 alignment-predicts-verdict analysis before running/adding more rows.",
        "inputs": {
            "structure_table": str(args.structure_table or ""),
            "ready_pair_selection": str(args.ready_pair_selection or ""),
            "census_plan": str(args.census_plan or ""),
        },
        "census_membership_rule": "Every formal component→composite pair that passes the readiness gate, with non-ready rows excluded as hard-composite/non-learning coverage when requested.",
        "control_battery": [
            "exact_component",
            "same_operation_control",
            "different_operation_control",
            "fake_component_control",
            "surface_control",
            "unrelated_matched_displacement_twin",
            "readiness_gate",
        ],
        "condition_set": args.condition_set,
        "conditions": CONDITION_SETS[args.condition_set],
        "primary_metric": args.metric_family,
        "acquisition_threshold": args.threshold,
        "acquisition_patience": args.patience,
        "verdict_rule": {
            "exact_component_dependency": "Exact component separates from same-operation and different-operation controls, and from fake/surface controls when those rows are available.",
            "operation_family_transfer": "Exact separates from different-operation controls but not same-operation controls.",
            "difficulty_parallel_or_null": "No exact-component manipulation separates from matched controls.",
            "hard_composite_non_learning": "Helpful exact-component interventions fail to make the composite measurable; row is a coverage exclusion.",
            "min_direction_rate": args.min_direction_rate,
            "alpha": args.alpha,
        },
        "alignment_predictor_rule": {
            "ground_truth": "census verdicts from Exp 2 intervention rows",
            "primary_score": "early exact-minus-control gradient cosine, measured no later than early_max_fraction of training",
            "early_max_fraction": args.early_max_fraction,
            "evaluation": "AUC against exact_component_dependency labels; leave-family-out when family_id is present, otherwise pair-level AUC only.",
        },
        "claim_tiers": {
            "controlled_intervention": "Tier 1 causal within the controlled Sequence DSL setting only",
            "mediator_alignment": "Tier 1/2 mechanism if validated against census ground truth",
            "pythia": "Tier 3 observational corroboration only; no causal LLM claim",
        },
        "n_planned_rows": int(len(plan)),
    }
    (args.output_dir / "b1_v2_preregistration.json").write_text(json.dumps(spec, indent=2, sort_keys=True), encoding="utf-8")
    (args.output_dir / "b1_v2_preregistration.md").write_text(render_preregistration_md(spec, plan), encoding="utf-8")
    if not plan.empty:
        plan.to_csv(args.output_dir / "frozen_causal_census_plan.csv", index=False)
    manifest = write_manifest(
        args.output_dir,
        experiment="B1_v2_preregistration",
        backend="B1_sequence_dsl",
        code_version=args.code_version,
        run_id="b1_v2_preregistration",
        command=sys.argv,
        input_paths={
            "structure_table": str(args.structure_table or ""),
            "ready_pair_selection": str(args.ready_pair_selection or ""),
            "census_plan": str(args.census_plan or ""),
        },
        extra={"thesis_use": args.thesis_use, "condition_set": args.condition_set},
    )
    if args.archive_root is not None:
        append_registry(args.archive_root / "results_registry.csv", {
            "run_id": manifest["run_id"], "code_version": args.code_version, "git_sha": manifest["git_sha"],
            "experiment": manifest["experiment"], "backend": manifest["backend"], "output_path": str(args.output_dir),
            "status": "preregistered", "thesis_use": args.thesis_use, "created_at_utc": manifest["created_at_utc"],
        })
    print("Saved B1 v2 preregistration outputs:")
    for name in ["b1_v2_preregistration.md", "b1_v2_preregistration.json", "frozen_causal_census_plan.csv", "run_manifest.json"]:
        p = args.output_dir / name
        if p.exists():
            print(f"  {p}")


def render_preregistration_md(spec: dict, plan: pd.DataFrame) -> str:
    lines = [
        "# B1 v2 preregistration: causal census and alignment predictor",
        "",
        spec["purpose"],
        "",
        "## Frozen inputs",
    ]
    for k, v in spec["inputs"].items():
        lines.append(f"- {k}: `{v}`")
    lines += [
        "",
        "## Census membership rule",
        spec["census_membership_rule"],
        "",
        "## Control battery",
    ]
    for item in spec["control_battery"]:
        lines.append(f"- `{item}`")
    lines += [
        "",
        "## Conditions",
        f"Condition set: `{spec['condition_set']}`",
        "",
        "```text",
        " ".join(spec["conditions"]),
        "```",
        "",
        "## Verdict rule",
    ]
    for k, v in spec["verdict_rule"].items():
        lines.append(f"- `{k}`: {v}")
    lines += [
        "",
        "## Alignment predictor",
    ]
    for k, v in spec["alignment_predictor_rule"].items():
        lines.append(f"- `{k}`: {v}")
    lines += [
        "",
        "## Planned census rows",
        f"Rows frozen: `{len(plan)}`",
    ]
    if not plan.empty:
        for _, r in plan.head(50).iterrows():
            lines.append(f"- row `{int(r['census_row'])}`: `{r['component']}` → `{r['composite']}`; ready=`{r.get('h3_ready', '')}`; battery_complete=`{r.get('control_battery_complete', '')}`")
        if len(plan) > 50:
            lines.append(f"- ... {len(plan) - 50} additional rows omitted from preview; see frozen CSV.")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
