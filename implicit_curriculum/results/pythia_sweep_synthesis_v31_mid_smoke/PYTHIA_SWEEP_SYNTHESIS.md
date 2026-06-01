# Pythia observational sweep synthesis

This report aggregates Pythia-style observational runs across model sizes or evaluation configurations. It can show whether residual signatures are stable across settings, but it cannot establish causal dependency.

- runs included: `2`
- models/configs with residual refinement: `2`

## Run summary
- `EleutherAI/pythia-1b` / `results/pythia_model_sweep_v31_mid_smoke/pythia-1b_n16`: slices=29, checkpoints=3, H2-ready metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct;mean_logprob_margin`, residual composites=10, under=10, over=0, mixed=0
- `EleutherAI/pythia-1.4b` / `results/pythia_model_sweep_v31_mid_smoke/pythia-1.4b_n16`: slices=29, checkpoints=3, H2-ready metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct;mean_logprob_margin`, residual composites=10, under=10, over=0, mixed=0

## Cross-run composite stability
- `comp_add_then_compare`: verdict=`stable_underperforming_observational`, runs=2, under-verdicts=2, over-verdicts=0, mean under-rate=0.800, models=`EleutherAI/pythia-1.4b;EleutherAI/pythia-1b`
- `comp_add_then_even`: verdict=`stable_underperforming_observational`, runs=2, under-verdicts=2, over-verdicts=0, mean under-rate=0.800, models=`EleutherAI/pythia-1.4b;EleutherAI/pythia-1b`
- `comp_retrieve_then_color`: verdict=`stable_underperforming_observational`, runs=2, under-verdicts=2, over-verdicts=0, mean under-rate=0.800, models=`EleutherAI/pythia-1.4b;EleutherAI/pythia-1b`
- `comp_reverse_then_last`: verdict=`stable_underperforming_observational`, runs=2, under-verdicts=2, over-verdicts=0, mean under-rate=0.700, models=`EleutherAI/pythia-1.4b;EleutherAI/pythia-1b`
- `comp_max_then_compare`: verdict=`stable_underperforming_observational`, runs=2, under-verdicts=2, over-verdicts=0, mean under-rate=0.800, models=`EleutherAI/pythia-1.4b;EleutherAI/pythia-1b`
- `comp_sub_then_compare`: verdict=`stable_underperforming_observational`, runs=2, under-verdicts=2, over-verdicts=0, mean under-rate=0.700, models=`EleutherAI/pythia-1.4b;EleutherAI/pythia-1b`
- `comp_first_then_same`: verdict=`stable_underperforming_observational`, runs=2, under-verdicts=2, over-verdicts=0, mean under-rate=0.700, models=`EleutherAI/pythia-1.4b;EleutherAI/pythia-1b`
- `comp_reverse_then_same`: verdict=`stable_underperforming_observational`, runs=2, under-verdicts=2, over-verdicts=0, mean under-rate=0.800, models=`EleutherAI/pythia-1.4b;EleutherAI/pythia-1b`
- `comp_reverse_then_first`: verdict=`stable_underperforming_observational`, runs=2, under-verdicts=2, over-verdicts=0, mean under-rate=0.700, models=`EleutherAI/pythia-1.4b;EleutherAI/pythia-1b`
- `comp_retrieve_then_compare`: verdict=`stable_underperforming_observational`, runs=2, under-verdicts=2, over-verdicts=0, mean under-rate=0.700, models=`EleutherAI/pythia-1.4b;EleutherAI/pythia-1b`

## Composite-family stability
- `arithmetic`: runs=2, mean under-rate=0.775, consistent-under total=8, consistent-over total=0, models=`EleutherAI/pythia-1.4b;EleutherAI/pythia-1b`
- `retrieval`: runs=2, mean under-rate=0.750, consistent-under total=4, consistent-over total=0, models=`EleutherAI/pythia-1.4b;EleutherAI/pythia-1b`
- `string`: runs=2, mean under-rate=0.725, consistent-under total=8, consistent-over total=0, models=`EleutherAI/pythia-1.4b;EleutherAI/pythia-1b`

## Claim boundary
A stable residual across model/config sweeps is stronger observational evidence than a single-run residual, but it is still not causal evidence. Use it to motivate controlled follow-ups or more focused mechanistic probes, not to claim exact-component dependency in Pythia.
