#!/usr/bin/env bash
set -euo pipefail

# Auto-generated Pythia observational model/config sweep.
# Run section-by-section if you want to inspect each model before continuing.

echo '=== Running pythia-2.8b_n16 ==='
PYTHONPATH=src python -m ic_experiments.experiments.run_pythia_observational_pilot \
  --slice-table 'thesis_evidence/pythia_slice_suites/v27_h2_ready/pythia_slice_table.csv' \
  --examples 'thesis_evidence/pythia_slice_suites/v27_h2_ready/pythia_slice_examples.jsonl' \
  --output-dir 'results/pythia_model_sweep_v32_2p8b_smoke_a100/pythia-2.8b_n16' \
  --model-name 'EleutherAI/pythia-2.8b' \
  --revisions 'step0' 'step10000' 'step143000' \
  --max-examples-per-slice 16 \
  --device 'cuda' \
  --code-version 'v3.2' \
  --archive-root 'results/archive' \
  --thesis-use 'diagnostic'

echo '=== H2 readiness pythia-2.8b_n16 ==='
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_h2_readiness \
  --result-dir 'results/pythia_model_sweep_v32_2p8b_smoke_a100/pythia-2.8b_n16' \
  --code-version 'v3.2' \
  --archive-root 'results/archive' \
  --thesis-use 'diagnostic'

echo '=== Continuous analysis pythia-2.8b_n16 ==='
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_continuous_scores \
  --result-dir 'results/pythia_model_sweep_v32_2p8b_smoke_a100/pythia-2.8b_n16' \
  --code-version 'v3.2' \
  --archive-root 'results/archive' \
  --thesis-use 'diagnostic'

echo '=== Residual refinement pythia-2.8b_n16 ==='
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_residual_refinement \
  --result-dir 'results/pythia_model_sweep_v32_2p8b_smoke_a100/pythia-2.8b_n16' \
  --code-version 'v3.2' \
  --archive-root 'results/archive' \
  --thesis-use 'diagnostic'

