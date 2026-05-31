from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from ic_experiments.run_management import write_manifest, append_registry


def parse_args():
    p = argparse.ArgumentParser(description="Write a conservative next-experiment plan for completing the B1 evidence picture.")
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--base-structure-table", type=str, default="results/b1_h1_shared_sweep_v08/structure_table.csv")
    p.add_argument("--base-h2-dir", type=str, default="results/b1_h1_shared_sweep_v08")
    p.add_argument("--code-version", type=str, default="v1.4")
    p.add_argument("--archive-root", type=Path, default=None)
    p.add_argument("--thesis-use", type=str, default="planning")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    rows = [
        {
            "stage": "A",
            "experiment": "B1_H3_replicate_primary_pair_same_family",
            "goal": "Confirm A02_substitute -> C06 under strong pretrain/corrupt/delay conditions on full seeds.",
            "status": "completed_if_b1_h3_row0_strong_v12_exists",
            "why": "This is the current strongest pair-specific causal result.",
            "minimum_success": "pretrain exact beats same/different controls; strong corrupt exact hurts more than controls.",
        },
        {
            "stage": "B",
            "experiment": "B1_H3_secondary_pair_C07",
            "goal": "Test whether H3 pair-specific evidence generalizes to another H2-delayed composite.",
            "status": "next_candidate",
            "why": "A second composite reduces risk that C06 is idiosyncratic.",
            "minimum_success": "at least one exact component beats same/different controls under pretrain and corruption.",
        },
        {
            "stage": "C",
            "experiment": "B1_family_replication",
            "goal": "Generate a second B1 family and rerun calibration -> H1 -> H2 -> H3 on top residual pair.",
            "status": "next_after_C07_or_if_claim_needs_replication",
            "why": "Needed before broad claims about controlled sequence-transformer training.",
            "minimum_success": "H1 learnability stable; H2 structured residuals; H3 at least one pair-specific positive.",
        },
        {
            "stage": "D",
            "experiment": "Mechanistic_mediators_for_A02_C06",
            "goal": "Add gradient/representation/probe evidence for A02 reuse inside C06.",
            "status": "parallel_next",
            "why": "Moves from causal intervention evidence to gradient-mediated mechanism evidence.",
            "minimum_success": "early A02-C06 mediator exceeds same/different controls and predicts later C06 residual/intervention effect.",
        },
        {
            "stage": "E",
            "experiment": "B2_sparse_parity_strengthening",
            "goal": "Improve sparse-parity coverage for a cleaner quanta-style contrast table.",
            "status": "optional_for_thesis_baseline",
            "why": "Strengthens the frequency-dominated baseline contrast.",
            "minimum_success": "nontrivial acquisition coverage with strong frequency effect and degree difficulty effect.",
        },
    ]
    df = pd.DataFrame(rows)
    df.to_csv(out / "comprehensive_experiment_plan.csv", index=False)

    cmds = f'''#!/usr/bin/env bash
set -euo pipefail

# This script is a plan/checklist, not a fully automatic pipeline. Run stages selectively.

# Stage B: make a plan for the secondary delayed composite (increase --top-composites if needed)
PYTHONPATH=src python -m ic_experiments.experiments.make_b1_h3_operation_family_plan \
  --structure-table {args.base_tructure_table if False else args.base_structure_table} \
  --pair-selection {args.base_h2_dir}/h2_pair_selection.csv \
  --output-dir results/b1_h3_secondary_plan_v14 \
  --top-composites 2 \
  --components-per-composite 2

# Inspect results/b1_h3_secondary_plan_v14/h3_operation_family_plan_report.md.
# Then run selected rows using run_b1_h3_interventions with v1.2/v1.4 strong conditions.

# Stage C: start a new B1 family replication calibration.
PYTHONPATH=src python -m ic_experiments.experiments.run_sequence_dsl_calibration \
  --output-dir results/sequence_dsl_calibration_replication_v14 \
  --candidate-seeds 10 11 12 13 14 15 16 17 18 19 \
  --calibration-seeds 0 1 2 \
  --vocab-content 32 \
  --input-len 6 \
  --max-data-seen 200000 \
  --batch-size 256 \
  --learning-rate 5e-4 \
  --device cuda

# If calibration passes, run B1 H1 shared sweep on the new structure_table, then H2, then H3 plan.
'''
    (out / "recommended_commands.sh").write_text(cmds, encoding="utf-8")
    (out / "recommended_commands.sh").chmod(0o755)

    report = """# Comprehensive Experiment Plan after v1.4 Claim Audit

The current evidence is strong enough for a scoped pilot story, but not for a universal mechanism claim. The next experiments should widen the evidence base rather than simply repeat the same interpretation.

## Priority order

1. **Secondary composite/pair test:** use H2 pair selection to test another delayed composite such as C07. This checks whether the positive A02→C06 result is idiosyncratic.
2. **Second B1 family replication:** regenerate a new calibrated sequence-DSL family and rerun H1/H2/H3. This is the key step for making controlled claims robust.
3. **Mediator diagnostics for A02→C06:** add early gradient/representation/probe measurements. This supports the gradient-mediated mechanism rather than only interventional causality.
4. **B2 sparse parity strengthening:** improve acquisition coverage to make the frequency-dominated baseline more thesis-ready.

## Stop conditions

- If secondary pairs and replication families do not reproduce any pair-specific H3 effect, keep H3 as a boundary-map result rather than a dependency mechanism.
- If H1 remains stable but H3 is mixed, the thesis can still contribute an ordering/predictability result and a cautionary causal intervention result.
- If mediator diagnostics do not align with interventions, avoid the phrase “gradient-mediated mechanism” except as a candidate interpretation.
"""
    (out / "comprehensive_experiment_plan.md").write_text(report, encoding="utf-8")

    manifest = write_manifest(
        out,
        experiment="comprehensive_experiment_plan",
        backend="planning",
        code_version=args.code_version,
        run_id="comprehensive_experiment_plan_v14",
        command=None,
        input_paths={"base_structure_table": args.base_structure_table, "base_h2_dir": args.base_h2_dir},
        extra={"thesis_use": args.thesis_use},
    )
    if args.archive_root:
        append_registry(args.archive_root / "results_registry.csv", {
            "run_id": manifest["run_id"], "code_version": args.code_version, "git_sha": manifest["git_sha"],
            "experiment": manifest["experiment"], "backend": manifest["backend"], "output_path": str(out),
            "status": "planned", "thesis_use": args.thesis_use, "created_at_utc": manifest["created_at_utc"],
        })
    print(f"Wrote {out / 'comprehensive_experiment_plan.md'}")
    print(f"Wrote {out / 'recommended_commands.sh'}")


if __name__ == "__main__":
    main()
