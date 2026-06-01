# Pythia observational sweep synthesis

This report aggregates Pythia-style observational runs across model sizes or evaluation configurations. It can show whether residual signatures are stable across settings, but it cannot establish causal dependency.

- runs included: `3`
- models/configs with residual refinement: `0`

## Run summary
- `pythia-2p8b_n16` / `results/pythia_model_sweep_v32/pythia-2p8b_n16`: slices=0, checkpoints=0, H2-ready metrics=``, residual composites=0, under=0, over=0, mixed=0
- `pythia-6p9b_n16` / `results/pythia_model_sweep_v32/pythia-6p9b_n16`: slices=0, checkpoints=0, H2-ready metrics=``, residual composites=0, under=0, over=0, mixed=0
- `pythia-12b_n16` / `results/pythia_model_sweep_v32/pythia-12b_n16`: slices=0, checkpoints=0, H2-ready metrics=``, residual composites=0, under=0, over=0, mixed=0

## Cross-run composite stability
- No residual stability rows available. Run continuous analysis and residual refinement for each sweep directory first.

## Composite-family stability
- No family stability rows available.

## Claim boundary
A stable residual across model/config sweeps is stronger observational evidence than a single-run residual, but it is still not causal evidence. Use it to motivate controlled follow-ups or more focused mechanistic probes, not to claim exact-component dependency in Pythia.
