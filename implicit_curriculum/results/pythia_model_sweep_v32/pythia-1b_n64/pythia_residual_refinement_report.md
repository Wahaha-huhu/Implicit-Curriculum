# Pythia observational residual refinement

This report refines the Pythia observational bridge by asking whether primitive-to-composite residuals agree across continuous metrics and composite families. It remains observational and cannot establish causal dependency.

- result_dir: `results/pythia_model_sweep_v32/pythia-1b_n64`
- metrics included: `accuracy, mean_correct_margin, mean_correct_mrr, mean_logprob_correct, mean_logprob_margin`
- valid residual rows: `50`
- composites with residuals: `10`

## Composite residual agreement
- `comp_add_then_even` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.800, over-rate=0.200, median-z=-1.379; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct`
- `comp_first_then_same` (string): verdict=`consistent_underperforming_observational`, under-rate=0.800, over-rate=0.200, median-z=-0.807; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct`
- `comp_reverse_then_same` (string): verdict=`consistent_underperforming_observational`, under-rate=0.800, over-rate=0.200, median-z=0.209; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct`
- `comp_reverse_then_first` (string): verdict=`consistent_underperforming_observational`, under-rate=0.800, over-rate=0.200, median-z=0.503; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct`
- `comp_add_then_compare` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.600, over-rate=0.400, median-z=-1.043; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr`
- `comp_sub_then_compare` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.600, over-rate=0.400, median-z=-0.920; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr`
- `comp_reverse_then_last` (string): verdict=`consistent_underperforming_observational`, under-rate=0.600, over-rate=0.400, median-z=0.159; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr`
- `comp_retrieve_then_color` (retrieval): verdict=`consistent_underperforming_observational`, under-rate=0.600, over-rate=0.400, median-z=0.379; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr`
- `comp_max_then_compare` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.600, over-rate=0.400, median-z=0.520; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr`
- `comp_retrieve_then_compare` (retrieval): verdict=`consistent_outperforming_observational`, under-rate=0.400, over-rate=0.600, median-z=1.478; under metrics=`accuracy;mean_correct_mrr`

## Composite-family summary
- `string`: n=4, mean under-rate=0.750, consistent-under=4, consistent-over=0, mixed=0; top=`comp_first_then_same;comp_reverse_then_same;comp_reverse_then_first;comp_reverse_then_last`
- `arithmetic`: n=4, mean under-rate=0.650, consistent-under=4, consistent-over=0, mixed=0; top=`comp_add_then_even;comp_add_then_compare;comp_sub_then_compare;comp_max_then_compare`
- `retrieval`: n=2, mean under-rate=0.500, consistent-under=1, consistent-over=1, mixed=0; top=`comp_retrieve_then_color;comp_retrieve_then_compare`

## Component-coupling agreement
- `comp_reverse_then_same`: verdict=`component_lag_observational`, lag-rate=0.600, ahead-rate=0.200, mean final diff=-0.089
- `comp_sub_then_compare`: verdict=`component_lag_observational`, lag-rate=0.600, ahead-rate=0.400, mean final diff=-0.067
- `comp_first_then_same`: verdict=`component_lag_observational`, lag-rate=0.600, ahead-rate=0.400, mean final diff=0.033
- `comp_add_then_compare`: verdict=`component_lag_observational`, lag-rate=0.600, ahead-rate=0.400, mean final diff=0.052
- `comp_reverse_then_first`: verdict=`composite_ahead_observational`, lag-rate=0.400, ahead-rate=0.600, mean final diff=-0.008
- `comp_retrieve_then_compare`: verdict=`composite_ahead_observational`, lag-rate=0.400, ahead-rate=0.600, mean final diff=0.010
- `comp_add_then_even`: verdict=`composite_ahead_observational`, lag-rate=0.400, ahead-rate=0.600, mean final diff=0.069
- `comp_retrieve_then_color`: verdict=`composite_ahead_observational`, lag-rate=0.200, ahead-rate=0.800, mean final diff=0.033
- `comp_reverse_then_last`: verdict=`composite_ahead_observational`, lag-rate=0.200, ahead-rate=0.800, mean final diff=0.067
- `comp_max_then_compare`: verdict=`composite_ahead_observational`, lag-rate=0.000, ahead-rate=1.000, mean final diff=0.073

## Claim boundary
A robust observational Pythia finding requires residual agreement across multiple continuous metrics and preferably across model sizes/checkpoint densities. These outputs can motivate controlled or observational follow-ups, but they are not H3 causal evidence.
