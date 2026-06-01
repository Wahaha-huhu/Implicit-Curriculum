#!/usr/bin/env bash
set -euo pipefail

PYTHONPATH=src python -m ic_experiments.experiments.make_pythia_focused_arithmetic_slice_suite   --output-dir results/pythia_arithmetic_slice_suite_v34   --n-per-slice 64   --code-version v3.4   --archive-root results/archive   --thesis-use diagnostic

PYTHONPATH=src python -m ic_experiments.experiments.make_pythia_sweep_plan   --slice-table results/pythia_arithmetic_slice_suite_v34/pythia_slice_table.csv   --examples results/pythia_arithmetic_slice_suite_v34/pythia_slice_examples.jsonl   --output-dir results/pythia_arithmetic_sweep_plan_v34   --run-root results/pythia_arithmetic_model_sweep_v34   --models EleutherAI/pythia-70m EleutherAI/pythia-160m EleutherAI/pythia-410m EleutherAI/pythia-1b EleutherAI/pythia-1.4b   --revisions step0 step1000 step10000 step143000   --max-examples-per-slice 64   --device cuda   --code-version v3.4   --archive-root results/archive   --thesis-use diagnostic

bash results/pythia_arithmetic_sweep_plan_v34/recommended_pythia_sweep_commands.sh

PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_sweep_synthesis   --run-dirs     results/pythia_arithmetic_model_sweep_v34/pythia-70m_n64     results/pythia_arithmetic_model_sweep_v34/pythia-160m_n64     results/pythia_arithmetic_model_sweep_v34/pythia-410m_n64     results/pythia_arithmetic_model_sweep_v34/pythia-1b_n64     results/pythia_arithmetic_model_sweep_v34/pythia-1.4b_n64   --output-dir results/pythia_arithmetic_sweep_synthesis_v34   --code-version v3.4   --archive-root results/archive   --thesis-use candidate
