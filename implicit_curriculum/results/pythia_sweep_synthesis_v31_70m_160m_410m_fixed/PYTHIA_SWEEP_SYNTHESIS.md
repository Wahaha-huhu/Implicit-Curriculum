# Pythia observational sweep synthesis

This report aggregates Pythia-style observational runs across model sizes or evaluation configurations. It can show whether residual signatures are stable across settings, but it cannot establish causal dependency.

- runs included: `3`
- models/configs with residual refinement: `3`

## Run summary
- `EleutherAI/pythia-70m` / `results/pythia_model_sweep_v30/pythia-70m_n64`: slices=29, checkpoints=4, H2-ready metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct;mean_logprob_margin`, residual composites=10, under=7, over=3, mixed=0
- `EleutherAI/pythia-160m` / `results/pythia_model_sweep_v30/pythia-160m_n64`: slices=29, checkpoints=4, H2-ready metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct;mean_logprob_margin`, residual composites=10, under=10, over=0, mixed=0
- `EleutherAI/pythia-410m` / `results/pythia_model_sweep_v31_410m/pythia-410m_n64`: slices=29, checkpoints=4, H2-ready metrics=`accuracy;mean_correct_margin;mean_logprob_correct;mean_logprob_margin`, residual composites=10, under=10, over=0, mixed=0

## Cross-run composite stability
- `comp_add_then_compare`: verdict=`stable_underperforming_observational`, runs=3, under-verdicts=3, over-verdicts=0, mean under-rate=0.733, models=`EleutherAI/pythia-160m;EleutherAI/pythia-410m;EleutherAI/pythia-70m`
- `comp_add_then_even`: verdict=`stable_underperforming_observational`, runs=3, under-verdicts=3, over-verdicts=0, mean under-rate=0.800, models=`EleutherAI/pythia-160m;EleutherAI/pythia-410m;EleutherAI/pythia-70m`
- `comp_sub_then_compare`: verdict=`stable_underperforming_observational`, runs=3, under-verdicts=3, over-verdicts=0, mean under-rate=0.733, models=`EleutherAI/pythia-160m;EleutherAI/pythia-410m;EleutherAI/pythia-70m`
- `comp_first_then_same`: verdict=`stable_underperforming_observational`, runs=3, under-verdicts=3, over-verdicts=0, mean under-rate=0.667, models=`EleutherAI/pythia-160m;EleutherAI/pythia-410m;EleutherAI/pythia-70m`
- `comp_reverse_then_last`: verdict=`stable_underperforming_observational`, runs=3, under-verdicts=3, over-verdicts=0, mean under-rate=0.667, models=`EleutherAI/pythia-160m;EleutherAI/pythia-410m;EleutherAI/pythia-70m`
- `comp_reverse_then_same`: verdict=`stable_underperforming_observational`, runs=3, under-verdicts=3, over-verdicts=0, mean under-rate=0.600, models=`EleutherAI/pythia-160m;EleutherAI/pythia-410m;EleutherAI/pythia-70m`
- `comp_max_then_compare`: verdict=`stable_underperforming_observational`, runs=3, under-verdicts=3, over-verdicts=0, mean under-rate=0.667, models=`EleutherAI/pythia-160m;EleutherAI/pythia-410m;EleutherAI/pythia-70m`
- `comp_retrieve_then_color`: verdict=`stable_underperforming_observational`, runs=3, under-verdicts=2, over-verdicts=1, mean under-rate=0.533, models=`EleutherAI/pythia-160m;EleutherAI/pythia-410m;EleutherAI/pythia-70m`
- `comp_reverse_then_first`: verdict=`stable_underperforming_observational`, runs=3, under-verdicts=2, over-verdicts=1, mean under-rate=0.600, models=`EleutherAI/pythia-160m;EleutherAI/pythia-410m;EleutherAI/pythia-70m`
- `comp_retrieve_then_compare`: verdict=`stable_underperforming_observational`, runs=3, under-verdicts=2, over-verdicts=1, mean under-rate=0.533, models=`EleutherAI/pythia-160m;EleutherAI/pythia-410m;EleutherAI/pythia-70m`

## Composite-family stability
- `arithmetic`: runs=3, mean under-rate=0.733, consistent-under total=12, consistent-over total=0, models=`EleutherAI/pythia-160m;EleutherAI/pythia-410m;EleutherAI/pythia-70m`
- `string`: runs=3, mean under-rate=0.633, consistent-under total=11, consistent-over total=1, models=`EleutherAI/pythia-160m;EleutherAI/pythia-410m;EleutherAI/pythia-70m`
- `retrieval`: runs=3, mean under-rate=0.533, consistent-under total=4, consistent-over total=2, models=`EleutherAI/pythia-160m;EleutherAI/pythia-410m;EleutherAI/pythia-70m`

## Claim boundary
A stable residual across model/config sweeps is stronger observational evidence than a single-run residual, but it is still not causal evidence. Use it to motivate controlled follow-ups or more focused mechanistic probes, not to claim exact-component dependency in Pythia.
