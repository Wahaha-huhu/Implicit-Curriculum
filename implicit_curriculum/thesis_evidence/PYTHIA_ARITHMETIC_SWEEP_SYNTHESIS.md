# Pythia observational sweep synthesis

This report aggregates Pythia-style observational runs across model sizes or evaluation configurations. It can show whether residual signatures are stable across settings, but it cannot establish causal dependency.

- runs included: `5`
- models/configs with residual refinement: `5`

## Run summary
- `EleutherAI/pythia-70m` / `results/pythia_arithmetic_model_sweep_v34/pythia-70m_n64`: slices=24, checkpoints=4, H2-ready metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct;mean_logprob_margin`, residual composites=10, under=0, over=10, mixed=0
- `EleutherAI/pythia-160m` / `results/pythia_arithmetic_model_sweep_v34/pythia-160m_n64`: slices=24, checkpoints=4, H2-ready metrics=`accuracy;mean_correct_margin;mean_logprob_correct;mean_logprob_margin`, residual composites=10, under=10, over=0, mixed=0
- `EleutherAI/pythia-410m` / `results/pythia_arithmetic_model_sweep_v34/pythia-410m_n64`: slices=24, checkpoints=4, H2-ready metrics=`accuracy;mean_correct_margin;mean_logprob_correct;mean_logprob_margin`, residual composites=10, under=10, over=0, mixed=0
- `EleutherAI/pythia-1b` / `results/pythia_arithmetic_model_sweep_v34/pythia-1b_n64`: slices=24, checkpoints=4, H2-ready metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct;mean_logprob_margin`, residual composites=10, under=10, over=0, mixed=0
- `EleutherAI/pythia-1.4b` / `results/pythia_arithmetic_model_sweep_v34/pythia-1.4b_n64`: slices=24, checkpoints=4, H2-ready metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct;mean_logprob_margin`, residual composites=10, under=10, over=0, mixed=0

## Cross-run composite stability
- `comp_add_then_even`: verdict=`stable_underperforming_observational`, runs=5, under-verdicts=4, over-verdicts=1, mean under-rate=0.720, models=`EleutherAI/pythia-1.4b;EleutherAI/pythia-160m;EleutherAI/pythia-1b;EleutherAI/pythia-410m;EleutherAI/pythia-70m`
- `comp_add_then_compare_lt`: verdict=`stable_underperforming_observational`, runs=5, under-verdicts=4, over-verdicts=1, mean under-rate=0.760, models=`EleutherAI/pythia-1.4b;EleutherAI/pythia-160m;EleutherAI/pythia-1b;EleutherAI/pythia-410m;EleutherAI/pythia-70m`
- `comp_absdiff_then_even`: verdict=`stable_underperforming_observational`, runs=5, under-verdicts=4, over-verdicts=1, mean under-rate=0.720, models=`EleutherAI/pythia-1.4b;EleutherAI/pythia-160m;EleutherAI/pythia-1b;EleutherAI/pythia-410m;EleutherAI/pythia-70m`
- `comp_max_then_compare_gt`: verdict=`stable_underperforming_observational`, runs=5, under-verdicts=4, over-verdicts=1, mean under-rate=0.760, models=`EleutherAI/pythia-1.4b;EleutherAI/pythia-160m;EleutherAI/pythia-1b;EleutherAI/pythia-410m;EleutherAI/pythia-70m`
- `comp_sub_then_odd`: verdict=`stable_underperforming_observational`, runs=5, under-verdicts=4, over-verdicts=1, mean under-rate=0.720, models=`EleutherAI/pythia-1.4b;EleutherAI/pythia-160m;EleutherAI/pythia-1b;EleutherAI/pythia-410m;EleutherAI/pythia-70m`
- `comp_double_then_compare_gt`: verdict=`stable_underperforming_observational`, runs=5, under-verdicts=4, over-verdicts=1, mean under-rate=0.720, models=`EleutherAI/pythia-1.4b;EleutherAI/pythia-160m;EleutherAI/pythia-1b;EleutherAI/pythia-410m;EleutherAI/pythia-70m`
- `comp_add_then_compare_gt`: verdict=`stable_underperforming_observational`, runs=5, under-verdicts=4, over-verdicts=1, mean under-rate=0.720, models=`EleutherAI/pythia-1.4b;EleutherAI/pythia-160m;EleutherAI/pythia-1b;EleutherAI/pythia-410m;EleutherAI/pythia-70m`
- `comp_sub_then_compare_gt`: verdict=`stable_underperforming_observational`, runs=5, under-verdicts=4, over-verdicts=1, mean under-rate=0.760, models=`EleutherAI/pythia-1.4b;EleutherAI/pythia-160m;EleutherAI/pythia-1b;EleutherAI/pythia-410m;EleutherAI/pythia-70m`
- `comp_add_then_equals`: verdict=`stable_underperforming_observational`, runs=5, under-verdicts=4, over-verdicts=1, mean under-rate=0.720, models=`EleutherAI/pythia-1.4b;EleutherAI/pythia-160m;EleutherAI/pythia-1b;EleutherAI/pythia-410m;EleutherAI/pythia-70m`
- `comp_min_then_compare_lt`: verdict=`stable_underperforming_observational`, runs=5, under-verdicts=4, over-verdicts=1, mean under-rate=0.760, models=`EleutherAI/pythia-1.4b;EleutherAI/pythia-160m;EleutherAI/pythia-1b;EleutherAI/pythia-410m;EleutherAI/pythia-70m`

## Composite-family stability
- `arithmetic`: runs=5, mean under-rate=0.736, consistent-under total=40, consistent-over total=10, models=`EleutherAI/pythia-1.4b;EleutherAI/pythia-160m;EleutherAI/pythia-1b;EleutherAI/pythia-410m;EleutherAI/pythia-70m`

## Claim boundary
A stable residual across model/config sweeps is stronger observational evidence than a single-run residual, but it is still not causal evidence. Use it to motivate controlled follow-ups or more focused mechanistic probes, not to claim exact-component dependency in Pythia.
