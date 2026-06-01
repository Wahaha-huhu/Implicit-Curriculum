# Pythia observational sweep synthesis

This report aggregates Pythia-style observational runs across model sizes or evaluation configurations. It can show whether residual signatures are stable across settings, but it cannot establish causal dependency.

- runs included: `10`
- models/configs with residual refinement: `7`

## Run summary
- `EleutherAI/pythia-70m` / `results/pythia_model_sweep_v30/pythia-70m_n64`: slices=29, checkpoints=4, H2-ready metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct;mean_logprob_margin`, residual composites=10, under=7, over=3, mixed=0
- `EleutherAI/pythia-160m` / `results/pythia_model_sweep_v30/pythia-160m_n64`: slices=29, checkpoints=4, H2-ready metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct;mean_logprob_margin`, residual composites=10, under=10, over=0, mixed=0
- `EleutherAI/pythia-410m` / `results/pythia_model_sweep_v31_410m/pythia-410m_n64`: slices=29, checkpoints=4, H2-ready metrics=`accuracy;mean_correct_margin;mean_logprob_correct;mean_logprob_margin`, residual composites=10, under=10, over=0, mixed=0
- `EleutherAI/pythia-1b` / `results/pythia_model_sweep_v31_mid_smoke/pythia-1b_n16`: slices=29, checkpoints=3, H2-ready metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct;mean_logprob_margin`, residual composites=10, under=10, over=0, mixed=0
- `EleutherAI/pythia-1.4b` / `results/pythia_model_sweep_v31_mid_smoke/pythia-1.4b_n16`: slices=29, checkpoints=3, H2-ready metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct;mean_logprob_margin`, residual composites=10, under=10, over=0, mixed=0
- `EleutherAI/pythia-1b` / `results/pythia_model_sweep_v32/pythia-1b_n64`: slices=29, checkpoints=4, H2-ready metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct;mean_logprob_margin`, residual composites=10, under=9, over=1, mixed=0
- `EleutherAI/pythia-1.4b` / `results/pythia_model_sweep_v32/pythia-1p4b_n64`: slices=29, checkpoints=4, H2-ready metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct;mean_logprob_margin`, residual composites=10, under=10, over=0, mixed=0
- `pythia-2p8b_n16` / `results/pythia_model_sweep_v32/pythia-2p8b_n16`: slices=0, checkpoints=0, H2-ready metrics=``, residual composites=0, under=0, over=0, mixed=0
- `pythia-6p9b_n16` / `results/pythia_model_sweep_v32/pythia-6p9b_n16`: slices=0, checkpoints=0, H2-ready metrics=``, residual composites=0, under=0, over=0, mixed=0
- `pythia-12b_n16` / `results/pythia_model_sweep_v32/pythia-12b_n16`: slices=0, checkpoints=0, H2-ready metrics=``, residual composites=0, under=0, over=0, mixed=0

## Cross-run composite stability
- `comp_add_then_compare`: verdict=`stable_underperforming_observational`, runs=7, under-verdicts=7, over-verdicts=0, mean under-rate=0.771, models=`EleutherAI/pythia-1.4b;EleutherAI/pythia-160m;EleutherAI/pythia-1b;EleutherAI/pythia-410m;EleutherAI/pythia-70m`
- `comp_add_then_even`: verdict=`stable_underperforming_observational`, runs=7, under-verdicts=7, over-verdicts=0, mean under-rate=0.800, models=`EleutherAI/pythia-1.4b;EleutherAI/pythia-160m;EleutherAI/pythia-1b;EleutherAI/pythia-410m;EleutherAI/pythia-70m`
- `comp_sub_then_compare`: verdict=`stable_underperforming_observational`, runs=7, under-verdicts=7, over-verdicts=0, mean under-rate=0.743, models=`EleutherAI/pythia-1.4b;EleutherAI/pythia-160m;EleutherAI/pythia-1b;EleutherAI/pythia-410m;EleutherAI/pythia-70m`
- `comp_first_then_same`: verdict=`stable_underperforming_observational`, runs=7, under-verdicts=7, over-verdicts=0, mean under-rate=0.714, models=`EleutherAI/pythia-1.4b;EleutherAI/pythia-160m;EleutherAI/pythia-1b;EleutherAI/pythia-410m;EleutherAI/pythia-70m`
- `comp_reverse_then_last`: verdict=`stable_underperforming_observational`, runs=7, under-verdicts=7, over-verdicts=0, mean under-rate=0.686, models=`EleutherAI/pythia-1.4b;EleutherAI/pythia-160m;EleutherAI/pythia-1b;EleutherAI/pythia-410m;EleutherAI/pythia-70m`
- `comp_max_then_compare`: verdict=`stable_underperforming_observational`, runs=7, under-verdicts=7, over-verdicts=0, mean under-rate=0.743, models=`EleutherAI/pythia-1.4b;EleutherAI/pythia-160m;EleutherAI/pythia-1b;EleutherAI/pythia-410m;EleutherAI/pythia-70m`
- `comp_reverse_then_same`: verdict=`stable_underperforming_observational`, runs=7, under-verdicts=7, over-verdicts=0, mean under-rate=0.714, models=`EleutherAI/pythia-1.4b;EleutherAI/pythia-160m;EleutherAI/pythia-1b;EleutherAI/pythia-410m;EleutherAI/pythia-70m`
- `comp_retrieve_then_color`: verdict=`stable_underperforming_observational`, runs=7, under-verdicts=6, over-verdicts=1, mean under-rate=0.657, models=`EleutherAI/pythia-1.4b;EleutherAI/pythia-160m;EleutherAI/pythia-1b;EleutherAI/pythia-410m;EleutherAI/pythia-70m`
- `comp_reverse_then_first`: verdict=`stable_underperforming_observational`, runs=7, under-verdicts=6, over-verdicts=1, mean under-rate=0.686, models=`EleutherAI/pythia-1.4b;EleutherAI/pythia-160m;EleutherAI/pythia-1b;EleutherAI/pythia-410m;EleutherAI/pythia-70m`
- `comp_retrieve_then_compare`: verdict=`stable_underperforming_observational`, runs=7, under-verdicts=5, over-verdicts=2, mean under-rate=0.571, models=`EleutherAI/pythia-1.4b;EleutherAI/pythia-160m;EleutherAI/pythia-1b;EleutherAI/pythia-410m;EleutherAI/pythia-70m`

## Composite-family stability
- `arithmetic`: runs=7, mean under-rate=0.764, consistent-under total=28, consistent-over total=0, models=`EleutherAI/pythia-1.4b;EleutherAI/pythia-160m;EleutherAI/pythia-1b;EleutherAI/pythia-410m;EleutherAI/pythia-70m`
- `string`: runs=7, mean under-rate=0.700, consistent-under total=27, consistent-over total=1, models=`EleutherAI/pythia-1.4b;EleutherAI/pythia-160m;EleutherAI/pythia-1b;EleutherAI/pythia-410m;EleutherAI/pythia-70m`
- `retrieval`: runs=7, mean under-rate=0.614, consistent-under total=11, consistent-over total=3, models=`EleutherAI/pythia-1.4b;EleutherAI/pythia-160m;EleutherAI/pythia-1b;EleutherAI/pythia-410m;EleutherAI/pythia-70m`

## Claim boundary
A stable residual across model/config sweeps is stronger observational evidence than a single-run residual, but it is still not causal evidence. Use it to motivate controlled follow-ups or more focused mechanistic probes, not to claim exact-component dependency in Pythia.
