#!/usr/bin/env bash
set -euo pipefail

# Auto-generated Pythia observational model/config sweep.
# Run section-by-section if you want to inspect each model before continuing.

echo '=== Running pythia-1b_n64 ==='
PYTHONPATH=src python -m ic_experiments.experiments.run_pythia_observational_pilot \
  --slice-table 'results/pythia_h2_ready_slice_suite_v27/pythia_slice_table.csv' \
  --examples 'results/pythia_h2_ready_slice_suite_v27/pythia_slice_examples.jsonl' \
  --output-dir 'results/pythia_model_sweep_v31_mid_smoke/pythia-1b_n64' \
  --model-name 'EleutherAI/pythia-1b' \
  --revisions 'step0' 'step10000' 'step143000' \
  --max-examples-per-slice 64 \
  --device 'cuda' \
  --code-version 'v3.1' \
  --archive-root 'results/archive' \
  --thesis-use 'diagnostic'

echo '=== H2 readiness pythia-1b_n64 ==='
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_h2_readiness \
  --result-dir 'results/pythia_model_sweep_v31_mid_smoke/pythia-1b_n64' \
  --code-version 'v3.1' \
  --archive-root 'results/archive' \
  --thesis-use 'diagnostic'

echo '=== Continuous analysis pythia-1b_n64 ==='
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_continuous_scores \
  --result-dir 'results/pythia_model_sweep_v31_mid_smoke/pythia-1b_n64' \
  --code-version 'v3.1' \
  --archive-root 'results/archive' \
  --thesis-use 'diagnostic'

echo '=== Residual refinement pythia-1b_n64 ==='
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_residual_refinement \
  --result-dir 'results/pythia_model_sweep_v31_mid_smoke/pythia-1b_n64' \
  --code-version 'v3.1' \
  --archive-root 'results/archive' \
  --thesis-use 'diagnostic'

echo '=== Running pythia-1.4b_n64 ==='
PYTHONPATH=src python -m ic_experiments.experiments.run_pythia_observational_pilot \
  --slice-table 'results/pythia_h2_ready_slice_suite_v27/pythia_slice_table.csv' \
  --examples 'results/pythia_h2_ready_slice_suite_v27/pythia_slice_examples.jsonl' \
  --output-dir 'results/pythia_model_sweep_v31_mid_smoke/pythia-1.4b_n64' \
  --model-name 'EleutherAI/pythia-1.4b' \
  --revisions 'step0' 'step10000' 'step143000' \
  --max-examples-per-slice 64 \
  --device 'cuda' \
  --code-version 'v3.1' \
  --archive-root 'results/archive' \
  --thesis-use 'diagnostic'

echo '=== H2 readiness pythia-1.4b_n64 ==='
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_h2_readiness \
  --result-dir 'results/pythia_model_sweep_v31_mid_smoke/pythia-1.4b_n64' \
  --code-version 'v3.1' \
  --archive-root 'results/archive' \
  --thesis-use 'diagnostic'

echo '=== Continuous analysis pythia-1.4b_n64 ==='
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_continuous_scores \
  --result-dir 'results/pythia_model_sweep_v31_mid_smoke/pythia-1.4b_n64' \
  --code-version 'v3.1' \
  --archive-root 'results/archive' \
  --thesis-use 'diagnostic'

echo '=== Residual refinement pythia-1.4b_n64 ==='
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_residual_refinement \
  --result-dir 'results/pythia_model_sweep_v31_mid_smoke/pythia-1.4b_n64' \
  --code-version 'v3.1' \
  --archive-root 'results/archive' \
  --thesis-use 'diagnostic'

