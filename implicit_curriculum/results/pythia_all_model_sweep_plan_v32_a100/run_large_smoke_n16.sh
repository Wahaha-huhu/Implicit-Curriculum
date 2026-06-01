#!/usr/bin/env bash
set -euo pipefail

echo '=== Running EleutherAI/pythia-2.8b (large_smoke_n16) ==='
PYTHONPATH=src python -m ic_experiments.experiments.run_pythia_observational_pilot --slice-table thesis_evidence/pythia_slice_suites/v27_h2_ready/pythia_slice_table.csv --examples thesis_evidence/pythia_slice_suites/v27_h2_ready/pythia_slice_examples.jsonl --output-dir results/pythia_model_sweep_v32_a100/pythia-2p8b_n16 --model-name EleutherAI/pythia-2.8b --revisions step0 step10000 step143000 --max-examples-per-slice 16 --device cuda --code-version v3.2 --archive-root results/archive --thesis-use diagnostic
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_h2_readiness --result-dir results/pythia_model_sweep_v32_a100/pythia-2p8b_n16 --code-version v3.2 --archive-root results/archive --thesis-use diagnostic
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_continuous_scores --result-dir results/pythia_model_sweep_v32_a100/pythia-2p8b_n16 --code-version v3.2 --archive-root results/archive --thesis-use diagnostic
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_residual_refinement --result-dir results/pythia_model_sweep_v32_a100/pythia-2p8b_n16 --code-version v3.2 --archive-root results/archive --thesis-use diagnostic

echo '=== Running EleutherAI/pythia-6.9b (large_smoke_n16) ==='
PYTHONPATH=src python -m ic_experiments.experiments.run_pythia_observational_pilot --slice-table thesis_evidence/pythia_slice_suites/v27_h2_ready/pythia_slice_table.csv --examples thesis_evidence/pythia_slice_suites/v27_h2_ready/pythia_slice_examples.jsonl --output-dir results/pythia_model_sweep_v32_a100/pythia-6p9b_n16 --model-name EleutherAI/pythia-6.9b --revisions step0 step10000 step143000 --max-examples-per-slice 16 --device cuda --code-version v3.2 --archive-root results/archive --thesis-use diagnostic
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_h2_readiness --result-dir results/pythia_model_sweep_v32_a100/pythia-6p9b_n16 --code-version v3.2 --archive-root results/archive --thesis-use diagnostic
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_continuous_scores --result-dir results/pythia_model_sweep_v32_a100/pythia-6p9b_n16 --code-version v3.2 --archive-root results/archive --thesis-use diagnostic
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_residual_refinement --result-dir results/pythia_model_sweep_v32_a100/pythia-6p9b_n16 --code-version v3.2 --archive-root results/archive --thesis-use diagnostic

echo '=== Running EleutherAI/pythia-12b (large_smoke_n16) ==='
PYTHONPATH=src python -m ic_experiments.experiments.run_pythia_observational_pilot --slice-table thesis_evidence/pythia_slice_suites/v27_h2_ready/pythia_slice_table.csv --examples thesis_evidence/pythia_slice_suites/v27_h2_ready/pythia_slice_examples.jsonl --output-dir results/pythia_model_sweep_v32_a100/pythia-12b_n16 --model-name EleutherAI/pythia-12b --revisions step0 step10000 step143000 --max-examples-per-slice 16 --device cuda --code-version v3.2 --archive-root results/archive --thesis-use diagnostic
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_h2_readiness --result-dir results/pythia_model_sweep_v32_a100/pythia-12b_n16 --code-version v3.2 --archive-root results/archive --thesis-use diagnostic
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_continuous_scores --result-dir results/pythia_model_sweep_v32_a100/pythia-12b_n16 --code-version v3.2 --archive-root results/archive --thesis-use diagnostic
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_residual_refinement --result-dir results/pythia_model_sweep_v32_a100/pythia-12b_n16 --code-version v3.2 --archive-root results/archive --thesis-use diagnostic

