#!/usr/bin/env bash
set -euo pipefail

# This script is a plan/checklist, not a fully automatic pipeline. Run stages selectively.

# Stage B: make a plan for the secondary delayed composite (increase --top-composites if needed)
PYTHONPATH=src python -m ic_experiments.experiments.make_b1_h3_operation_family_plan   --structure-table results/b1_h1_shared_sweep_v08/structure_table.csv   --pair-selection results/b1_h1_shared_sweep_v08/h2_pair_selection.csv   --output-dir results/b1_h3_secondary_plan_v14   --top-composites 2   --components-per-composite 2

# Inspect results/b1_h3_secondary_plan_v14/h3_operation_family_plan_report.md.
# Then run selected rows using run_b1_h3_interventions with v1.2/v1.4 strong conditions.

# Stage C: start a new B1 family replication calibration.
PYTHONPATH=src python -m ic_experiments.experiments.run_sequence_dsl_calibration   --output-dir results/sequence_dsl_calibration_replication_v14   --candidate-seeds 10 11 12 13 14 15 16 17 18 19   --calibration-seeds 0 1 2   --vocab-content 32   --input-len 6   --max-data-seen 200000   --batch-size 256   --learning-rate 5e-4   --device cuda

# If calibration passes, run B1 H1 shared sweep on the new structure_table, then H2, then H3 plan.
