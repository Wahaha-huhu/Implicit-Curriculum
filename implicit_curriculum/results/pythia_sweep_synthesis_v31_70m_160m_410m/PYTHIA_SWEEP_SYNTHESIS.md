# Pythia observational sweep synthesis

This report aggregates Pythia-style observational runs across model sizes or evaluation configurations. It can show whether residual signatures are stable across settings, but it cannot establish causal dependency.

- runs included: `3`
- models/configs with residual refinement: `1`

## Run summary
- `pythia-70m_n64` / `results/pythia_model_sweep_v30/pythia-70m_n64`: slices=0, checkpoints=0, H2-ready metrics=``, residual composites=0, under=0, over=0, mixed=0
- `pythia-160m_n64` / `results/pythia_model_sweep_v30/pythia-160m_n64`: slices=0, checkpoints=0, H2-ready metrics=``, residual composites=0, under=0, over=0, mixed=0
- `EleutherAI/pythia-410m` / `results/pythia_model_sweep_v31_410m/pythia-410m_n64`: slices=29, checkpoints=4, H2-ready metrics=`accuracy;mean_correct_margin;mean_logprob_correct;mean_logprob_margin`, residual composites=10, under=10, over=0, mixed=0

## Cross-run composite stability
- `comp_add_then_even`: verdict=`stable_underperforming_observational`, runs=1, under-verdicts=1, over-verdicts=0, mean under-rate=1.000, models=`EleutherAI/pythia-410m`
- `comp_sub_then_compare`: verdict=`stable_underperforming_observational`, runs=1, under-verdicts=1, over-verdicts=0, mean under-rate=1.000, models=`EleutherAI/pythia-410m`
- `comp_add_then_compare`: verdict=`stable_underperforming_observational`, runs=1, under-verdicts=1, over-verdicts=0, mean under-rate=0.800, models=`EleutherAI/pythia-410m`
- `comp_first_then_same`: verdict=`stable_underperforming_observational`, runs=1, under-verdicts=1, over-verdicts=0, mean under-rate=0.600, models=`EleutherAI/pythia-410m`
- `comp_retrieve_then_color`: verdict=`stable_underperforming_observational`, runs=1, under-verdicts=1, over-verdicts=0, mean under-rate=0.600, models=`EleutherAI/pythia-410m`
- `comp_reverse_then_last`: verdict=`stable_underperforming_observational`, runs=1, under-verdicts=1, over-verdicts=0, mean under-rate=0.600, models=`EleutherAI/pythia-410m`
- `comp_reverse_then_same`: verdict=`stable_underperforming_observational`, runs=1, under-verdicts=1, over-verdicts=0, mean under-rate=0.600, models=`EleutherAI/pythia-410m`
- `comp_reverse_then_first`: verdict=`stable_underperforming_observational`, runs=1, under-verdicts=1, over-verdicts=0, mean under-rate=0.600, models=`EleutherAI/pythia-410m`
- `comp_max_then_compare`: verdict=`stable_underperforming_observational`, runs=1, under-verdicts=1, over-verdicts=0, mean under-rate=0.800, models=`EleutherAI/pythia-410m`
- `comp_retrieve_then_compare`: verdict=`stable_underperforming_observational`, runs=1, under-verdicts=1, over-verdicts=0, mean under-rate=0.600, models=`EleutherAI/pythia-410m`

## Composite-family stability
- `arithmetic`: runs=1, mean under-rate=0.900, consistent-under total=4, consistent-over total=0, models=`EleutherAI/pythia-410m`
- `string`: runs=1, mean under-rate=0.600, consistent-under total=4, consistent-over total=0, models=`EleutherAI/pythia-410m`
- `retrieval`: runs=1, mean under-rate=0.600, consistent-under total=2, consistent-over total=0, models=`EleutherAI/pythia-410m`

## Claim boundary
A stable residual across model/config sweeps is stronger observational evidence than a single-run residual, but it is still not causal evidence. Use it to motivate controlled follow-ups or more focused mechanistic probes, not to claim exact-component dependency in Pythia.
