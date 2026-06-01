#!/usr/bin/env bash
set -euo pipefail

# Auto-generated Pythia observational model/config sweep.
# Run section-by-section if you want to inspect each model before continuing.

echo '=== Running pythia-70m_n64 ==='
PYTHONPATH=src python -m ic_experiments.experiments.run_pythia_observational_pilot \
  --slice-table 'results/pythia_arithmetic_slice_suite_v34/pythia_slice_table.csv' \
  --examples 'results/pythia_arithmetic_slice_suite_v34/pythia_slice_examples.jsonl' \
  --output-dir 'results/pythia_arithmetic_model_sweep_v34/pythia-70m_n64' \
  --model-name 'EleutherAI/pythia-70m' \
  --revisions 'step0' 'step1000' 'step10000' 'step143000' \
  --max-examples-per-slice 64 \
  --device 'cuda' \
  --code-version 'v3.4' \
  --archive-root 'results/archive' \
  --thesis-use 'diagnostic'

echo '=== H2 readiness pythia-70m_n64 ==='
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_h2_readiness \
  --result-dir 'results/pythia_arithmetic_model_sweep_v34/pythia-70m_n64' \
  --code-version 'v3.4' \
  --archive-root 'results/archive' \
  --thesis-use 'diagnostic'

echo '=== Continuous analysis pythia-70m_n64 ==='
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_continuous_scores \
  --result-dir 'results/pythia_arithmetic_model_sweep_v34/pythia-70m_n64' \
  --code-version 'v3.4' \
  --archive-root 'results/archive' \
  --thesis-use 'diagnostic'

echo '=== Residual refinement pythia-70m_n64 ==='
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_residual_refinement \
  --result-dir 'results/pythia_arithmetic_model_sweep_v34/pythia-70m_n64' \
  --code-version 'v3.4' \
  --archive-root 'results/archive' \
  --thesis-use 'diagnostic'

echo '=== Running pythia-160m_n64 ==='
PYTHONPATH=src python -m ic_experiments.experiments.run_pythia_observational_pilot \
  --slice-table 'results/pythia_arithmetic_slice_suite_v34/pythia_slice_table.csv' \
  --examples 'results/pythia_arithmetic_slice_suite_v34/pythia_slice_examples.jsonl' \
  --output-dir 'results/pythia_arithmetic_model_sweep_v34/pythia-160m_n64' \
  --model-name 'EleutherAI/pythia-160m' \
  --revisions 'step0' 'step1000' 'step10000' 'step143000' \
  --max-examples-per-slice 64 \
  --device 'cuda' \
  --code-version 'v3.4' \
  --archive-root 'results/archive' \
  --thesis-use 'diagnostic'

echo '=== H2 readiness pythia-160m_n64 ==='
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_h2_readiness \
  --result-dir 'results/pythia_arithmetic_model_sweep_v34/pythia-160m_n64' \
  --code-version 'v3.4' \
  --archive-root 'results/archive' \
  --thesis-use 'diagnostic'

echo '=== Continuous analysis pythia-160m_n64 ==='
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_continuous_scores \
  --result-dir 'results/pythia_arithmetic_model_sweep_v34/pythia-160m_n64' \
  --code-version 'v3.4' \
  --archive-root 'results/archive' \
  --thesis-use 'diagnostic'

echo '=== Residual refinement pythia-160m_n64 ==='
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_residual_refinement \
  --result-dir 'results/pythia_arithmetic_model_sweep_v34/pythia-160m_n64' \
  --code-version 'v3.4' \
  --archive-root 'results/archive' \
  --thesis-use 'diagnostic'

echo '=== Running pythia-410m_n64 ==='
PYTHONPATH=src python -m ic_experiments.experiments.run_pythia_observational_pilot \
  --slice-table 'results/pythia_arithmetic_slice_suite_v34/pythia_slice_table.csv' \
  --examples 'results/pythia_arithmetic_slice_suite_v34/pythia_slice_examples.jsonl' \
  --output-dir 'results/pythia_arithmetic_model_sweep_v34/pythia-410m_n64' \
  --model-name 'EleutherAI/pythia-410m' \
  --revisions 'step0' 'step1000' 'step10000' 'step143000' \
  --max-examples-per-slice 64 \
  --device 'cuda' \
  --code-version 'v3.4' \
  --archive-root 'results/archive' \
  --thesis-use 'diagnostic'

echo '=== H2 readiness pythia-410m_n64 ==='
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_h2_readiness \
  --result-dir 'results/pythia_arithmetic_model_sweep_v34/pythia-410m_n64' \
  --code-version 'v3.4' \
  --archive-root 'results/archive' \
  --thesis-use 'diagnostic'

echo '=== Continuous analysis pythia-410m_n64 ==='
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_continuous_scores \
  --result-dir 'results/pythia_arithmetic_model_sweep_v34/pythia-410m_n64' \
  --code-version 'v3.4' \
  --archive-root 'results/archive' \
  --thesis-use 'diagnostic'

echo '=== Residual refinement pythia-410m_n64 ==='
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_residual_refinement \
  --result-dir 'results/pythia_arithmetic_model_sweep_v34/pythia-410m_n64' \
  --code-version 'v3.4' \
  --archive-root 'results/archive' \
  --thesis-use 'diagnostic'

echo '=== Running pythia-1b_n64 ==='
PYTHONPATH=src python -m ic_experiments.experiments.run_pythia_observational_pilot \
  --slice-table 'results/pythia_arithmetic_slice_suite_v34/pythia_slice_table.csv' \
  --examples 'results/pythia_arithmetic_slice_suite_v34/pythia_slice_examples.jsonl' \
  --output-dir 'results/pythia_arithmetic_model_sweep_v34/pythia-1b_n64' \
  --model-name 'EleutherAI/pythia-1b' \
  --revisions 'step0' 'step1000' 'step10000' 'step143000' \
  --max-examples-per-slice 64 \
  --device 'cuda' \
  --code-version 'v3.4' \
  --archive-root 'results/archive' \
  --thesis-use 'diagnostic'

echo '=== H2 readiness pythia-1b_n64 ==='
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_h2_readiness \
  --result-dir 'results/pythia_arithmetic_model_sweep_v34/pythia-1b_n64' \
  --code-version 'v3.4' \
  --archive-root 'results/archive' \
  --thesis-use 'diagnostic'

echo '=== Continuous analysis pythia-1b_n64 ==='
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_continuous_scores \
  --result-dir 'results/pythia_arithmetic_model_sweep_v34/pythia-1b_n64' \
  --code-version 'v3.4' \
  --archive-root 'results/archive' \
  --thesis-use 'diagnostic'

echo '=== Residual refinement pythia-1b_n64 ==='
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_residual_refinement \
  --result-dir 'results/pythia_arithmetic_model_sweep_v34/pythia-1b_n64' \
  --code-version 'v3.4' \
  --archive-root 'results/archive' \
  --thesis-use 'diagnostic'

echo '=== Running pythia-1.4b_n64 ==='
PYTHONPATH=src python -m ic_experiments.experiments.run_pythia_observational_pilot \
  --slice-table 'results/pythia_arithmetic_slice_suite_v34/pythia_slice_table.csv' \
  --examples 'results/pythia_arithmetic_slice_suite_v34/pythia_slice_examples.jsonl' \
  --output-dir 'results/pythia_arithmetic_model_sweep_v34/pythia-1.4b_n64' \
  --model-name 'EleutherAI/pythia-1.4b' \
  --revisions 'step0' 'step1000' 'step10000' 'step143000' \
  --max-examples-per-slice 64 \
  --device 'cuda' \
  --code-version 'v3.4' \
  --archive-root 'results/archive' \
  --thesis-use 'diagnostic'

echo '=== H2 readiness pythia-1.4b_n64 ==='
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_h2_readiness \
  --result-dir 'results/pythia_arithmetic_model_sweep_v34/pythia-1.4b_n64' \
  --code-version 'v3.4' \
  --archive-root 'results/archive' \
  --thesis-use 'diagnostic'

echo '=== Continuous analysis pythia-1.4b_n64 ==='
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_continuous_scores \
  --result-dir 'results/pythia_arithmetic_model_sweep_v34/pythia-1.4b_n64' \
  --code-version 'v3.4' \
  --archive-root 'results/archive' \
  --thesis-use 'diagnostic'

echo '=== Residual refinement pythia-1.4b_n64 ==='
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_residual_refinement \
  --result-dir 'results/pythia_arithmetic_model_sweep_v34/pythia-1.4b_n64' \
  --code-version 'v3.4' \
  --archive-root 'results/archive' \
  --thesis-use 'diagnostic'

