#!/usr/bin/env bash
set -euo pipefail

echo '=== Synthesizing mid full n64 runs ==='
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_sweep_synthesis --run-dirs results/pythia_model_sweep_v32_a100/pythia-1b_n64 results/pythia_model_sweep_v32_a100/pythia-1p4b_n64 --output-dir results/pythia_all_model_sweep_plan_v32_a100/synthesis_mid_full_n64 --code-version v3.2 --archive-root results/archive --thesis-use diagnostic

echo '=== Synthesizing large smoke n16 runs ==='
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_sweep_synthesis --run-dirs results/pythia_model_sweep_v32_a100/pythia-2p8b_n16 results/pythia_model_sweep_v32_a100/pythia-6p9b_n16 results/pythia_model_sweep_v32_a100/pythia-12b_n16 --output-dir results/pythia_all_model_sweep_plan_v32_a100/synthesis_large_smoke_n16 --code-version v3.2 --archive-root results/archive --thesis-use diagnostic

echo '=== Synthesizing all available/planned runs ==='
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_sweep_synthesis --run-dirs results/pythia_model_sweep_v30/pythia-70m_n64 results/pythia_model_sweep_v30/pythia-160m_n64 results/pythia_model_sweep_v31_410m/pythia-410m_n64 results/pythia_model_sweep_v31_mid_smoke/pythia-1b_n16 results/pythia_model_sweep_v31_mid_smoke/pythia-1.4b_n16 results/pythia_model_sweep_v32_a100/pythia-1b_n64 results/pythia_model_sweep_v32_a100/pythia-1p4b_n64 results/pythia_model_sweep_v32_a100/pythia-2p8b_n16 results/pythia_model_sweep_v32_a100/pythia-6p9b_n16 results/pythia_model_sweep_v32_a100/pythia-12b_n16 --output-dir results/pythia_all_model_sweep_plan_v32_a100/synthesis_all_available --code-version v3.2 --archive-root results/archive --thesis-use diagnostic
