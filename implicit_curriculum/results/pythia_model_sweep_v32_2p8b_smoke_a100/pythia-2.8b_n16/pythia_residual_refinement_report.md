# Pythia observational residual refinement

This report refines the Pythia observational bridge by asking whether primitive-to-composite residuals agree across continuous metrics and composite families. It remains observational and cannot establish causal dependency.

- result_dir: `results/pythia_model_sweep_v32_2p8b_smoke_a100/pythia-2.8b_n16`
- metrics included: `accuracy, mean_correct_margin, mean_correct_mrr, mean_logprob_correct, mean_logprob_margin`
- valid residual rows: `50`
- composites with residuals: `10`

## Composite residual agreement
- `comp_max_then_compare` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=1.000, over-rate=0.000, median-z=-0.916; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct;mean_logprob_margin`
- `comp_reverse_then_last` (string): verdict=`consistent_underperforming_observational`, under-rate=1.000, over-rate=0.000, median-z=-0.351; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct;mean_logprob_margin`
- `comp_reverse_then_same` (string): verdict=`consistent_underperforming_observational`, under-rate=1.000, over-rate=0.000, median-z=-0.234; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct;mean_logprob_margin`
- `comp_reverse_then_first` (string): verdict=`consistent_underperforming_observational`, under-rate=1.000, over-rate=0.000, median-z=-0.092; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct;mean_logprob_margin`
- `comp_sub_then_compare` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=1.000, over-rate=0.000, median-z=0.547; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct;mean_logprob_margin`
- `comp_first_then_same` (string): verdict=`consistent_underperforming_observational`, under-rate=0.800, over-rate=0.200, median-z=-1.798; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_margin`
- `comp_retrieve_then_color` (retrieval): verdict=`consistent_underperforming_observational`, under-rate=0.800, over-rate=0.200, median-z=-1.165; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_margin`
- `comp_add_then_even` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.800, over-rate=0.200, median-z=0.572; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_margin`
- `comp_retrieve_then_compare` (retrieval): verdict=`consistent_underperforming_observational`, under-rate=0.800, over-rate=0.200, median-z=0.579; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_margin`
- `comp_add_then_compare` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.800, over-rate=0.200, median-z=1.105; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_margin`

## Composite-family summary
- `string`: n=4, mean under-rate=0.950, consistent-under=4, consistent-over=0, mixed=0; top=`comp_reverse_then_last;comp_reverse_then_same;comp_reverse_then_first;comp_first_then_same`
- `arithmetic`: n=4, mean under-rate=0.900, consistent-under=4, consistent-over=0, mixed=0; top=`comp_max_then_compare;comp_sub_then_compare;comp_add_then_even;comp_add_then_compare`
- `retrieval`: n=2, mean under-rate=0.800, consistent-under=2, consistent-over=0, mixed=0; top=`comp_retrieve_then_color;comp_retrieve_then_compare`

## Component-coupling agreement
- `comp_max_then_compare`: verdict=`component_lag_observational`, lag-rate=0.800, ahead-rate=0.200, mean final diff=-0.074
- `comp_first_then_same`: verdict=`component_lag_observational`, lag-rate=0.800, ahead-rate=0.200, mean final diff=-0.044
- `comp_retrieve_then_compare`: verdict=`component_lag_observational`, lag-rate=0.800, ahead-rate=0.200, mean final diff=-0.023
- `comp_reverse_then_first`: verdict=`composite_ahead_observational`, lag-rate=0.400, ahead-rate=0.600, mean final diff=0.000
- `comp_sub_then_compare`: verdict=`composite_ahead_observational`, lag-rate=0.400, ahead-rate=0.600, mean final diff=0.014
- `comp_retrieve_then_color`: verdict=`composite_ahead_observational`, lag-rate=0.400, ahead-rate=0.600, mean final diff=0.020
- `comp_reverse_then_last`: verdict=`composite_ahead_observational`, lag-rate=0.400, ahead-rate=0.600, mean final diff=0.046
- `comp_reverse_then_same`: verdict=`composite_ahead_observational`, lag-rate=0.200, ahead-rate=0.800, mean final diff=0.014
- `comp_add_then_compare`: verdict=`composite_ahead_observational`, lag-rate=0.200, ahead-rate=0.800, mean final diff=0.140
- `comp_add_then_even`: verdict=`composite_ahead_observational`, lag-rate=0.000, ahead-rate=1.000, mean final diff=0.091

## Claim boundary
A robust observational Pythia finding requires residual agreement across multiple continuous metrics and preferably across model sizes/checkpoint densities. These outputs can motivate controlled or observational follow-ups, but they are not H3 causal evidence.
