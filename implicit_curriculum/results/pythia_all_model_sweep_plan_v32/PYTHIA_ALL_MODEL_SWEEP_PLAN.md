# Pythia all-model tiered sweep plan

This plan extends the existing 70M/160M/410M and 1B/1.4B smoke evidence toward a broader model-scale sweep. It remains observational: stable residuals across model scale strengthen the bridge result, but they do not establish causal dependency.

## Tier scripts

- `results/pythia_all_model_sweep_plan_v32/run_mid_full_n64.sh`: full n=64 run for `EleutherAI/pythia-1b, EleutherAI/pythia-1.4b`.
- `results/pythia_all_model_sweep_plan_v32/run_large_smoke_n16.sh`: large-model smoke n=16 run for `EleutherAI/pythia-2.8b, EleutherAI/pythia-6.9b, EleutherAI/pythia-12b`.
- `results/pythia_all_model_sweep_plan_v32/recommended_pythia_all_model_synthesis.sh`: synthesize mid-full, large-smoke, and all available runs.

## Suggested execution order

1. Run mid-full n=64 for 1B and 1.4B on the 4090 if feasible.
2. Synthesize all available runs to replace smoke evidence with full n=64 evidence for 1B/1.4B.
3. Move to A100 for the large-smoke tier: 2.8B, 6.9B, and 12B.
4. Only promote a large model to n=64 if its smoke run is H2-ready and residual refinement succeeds.

## Expected feedback files

For each synthesis directory, send:

- `PYTHIA_SWEEP_SYNTHESIS.md`
- `pythia_sweep_run_summary.csv`
- `pythia_sweep_residual_stability.csv`
- `pythia_sweep_family_stability.csv`

## Claim boundary

A stable residual across model/config sweeps is stronger observational evidence than a single-run residual, but it is still not causal evidence. Use it to motivate controlled follow-ups or more focused mechanistic probes, not to claim exact-component dependency in Pythia.
