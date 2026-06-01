#!/usr/bin/env bash
set -euo pipefail

echo '=== Running EleutherAI/pythia-1b (mid_full_n64) ==='
PYTHONPATH=src python -m ic_experiments.experiments.run_pythia_observational_pilot --slice-table thesis_evidence/pythia_slice_suites/v27_h2_ready/pythia_slice_table.csv --examples thesis_evidence/pythia_slice_suites/v27_h2_ready/pythia_slice_examples.jsonl --output-dir results/pythia_model_sweep_v32/pythia-1b_n64 --model-name EleutherAI/pythia-1b --revisions step0 step1000 step10000 step143000 --max-examples-per-slice 64 --device cuda --code-version v3.2 --archive-root results/archive --thesis-use diagnostic
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_h2_readiness --result-dir results/pythia_model_sweep_v32/pythia-1b_n64 --code-version v3.2 --archive-root results/archive --thesis-use diagnostic
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_continuous_scores --result-dir results/pythia_model_sweep_v32/pythia-1b_n64 --code-version v3.2 --archive-root results/archive --thesis-use diagnostic
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_residual_refinement --result-dir results/pythia_model_sweep_v32/pythia-1b_n64 --code-version v3.2 --archive-root results/archive --thesis-use diagnostic

echo '=== Running EleutherAI/pythia-1.4b (mid_full_n64) ==='
PYTHONPATH=src python -m ic_experiments.experiments.run_pythia_observational_pilot --slice-table thesis_evidence/pythia_slice_suites/v27_h2_ready/pythia_slice_table.csv --examples thesis_evidence/pythia_slice_suites/v27_h2_ready/pythia_slice_examples.jsonl --output-dir results/pythia_model_sweep_v32/pythia-1p4b_n64 --model-name EleutherAI/pythia-1.4b --revisions step0 step1000 step10000 step143000 --max-examples-per-slice 64 --device cuda --code-version v3.2 --archive-root results/archive --thesis-use diagnostic
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_h2_readiness --result-dir results/pythia_model_sweep_v32/pythia-1p4b_n64 --code-version v3.2 --archive-root results/archive --thesis-use diagnostic
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_continuous_scores --result-dir results/pythia_model_sweep_v32/pythia-1p4b_n64 --code-version v3.2 --archive-root results/archive --thesis-use diagnostic
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_residual_refinement --result-dir results/pythia_model_sweep_v32/pythia-1p4b_n64 --code-version v3.2 --archive-root results/archive --thesis-use diagnostic

