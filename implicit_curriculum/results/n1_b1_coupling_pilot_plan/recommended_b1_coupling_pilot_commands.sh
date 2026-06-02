#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH=${PYTHONPATH:-$(pwd)/src}
python -m ic_experiments.experiments.run_b1_coupling_pilot \
  --structure-table results/n1_b1_coupling_pilot_plan/structure_table.csv \
  --pair-plan results/n1_b1_coupling_pilot_plan/b1_coupling_pair_plan.csv \
  --output-dir results/b1_coupling_pilot \
  --seeds 0 1 2 \
  --dose-multipliers 0.0 0.5 1.0 2.0 \
  --device cuda \
  --max-data-seen 120000 \
  --batch-size 256 \
  --n-checkpoints 60 \
  --eval-examples-per-task 256 \
  --skip-existing

python -m ic_experiments.experiments.analyze_b1_coupling_pilot \
  --result-dir results/b1_coupling_pilot \
  --output-dir results/b1_coupling_pilot_analysis
