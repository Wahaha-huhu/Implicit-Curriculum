#!/usr/bin/env bash
set -euo pipefail

PYTHONPATH=src python -m ic_experiments.experiments.run_sparse_parity_pilot   --output-dir results/b2_sparse_parity_strengthened_v34   --family-seed 0   --seeds 0 1 2 3 4 5 6 7 8 9   --n-bits 40   --n-tasks 36   --degrees 1 2 3   --frequency-mode zipf   --zipf-alpha 1.1   --max-data-seen 1000000   --checkpoint-every 10000   --batch-size 1024   --learning-rate 0.002   --hidden-dim 512   --depth 3   --eval-examples-per-task 4096   --device cuda

PYTHONPATH=src python -m ic_experiments.experiments.analyze_sparse_parity_pilot   --result-dir results/b2_sparse_parity_strengthened_v34   --thresholds 0.65 0.75 0.85 0.90   --metric balanced_accuracy   --patience 2

PYTHONPATH=src python -m ic_experiments.experiments.analyze_b2_strengthening_synthesis   --run-dirs results/b2_sparse_parity_strengthened_v34   --output-dir results/b2_strengthening_synthesis_v34   --code-version v3.4   --archive-root results/archive   --thesis-use candidate
