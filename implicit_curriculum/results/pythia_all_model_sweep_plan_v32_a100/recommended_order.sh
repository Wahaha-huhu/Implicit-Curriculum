#!/usr/bin/env bash
set -euo pipefail

echo 'Run tiers manually. Suggested order:'
echo '  bash results/pythia_all_model_sweep_plan_v32_a100/run_mid_full_n64.sh'
echo '  bash results/pythia_all_model_sweep_plan_v32_a100/run_large_smoke_n16.sh'
echo 'Then synthesize: bash results/pythia_all_model_sweep_plan_v32_a100/recommended_pythia_all_model_synthesis.sh'
