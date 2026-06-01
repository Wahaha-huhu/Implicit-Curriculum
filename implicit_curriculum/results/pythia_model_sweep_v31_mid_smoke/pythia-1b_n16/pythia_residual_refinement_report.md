# Pythia observational residual refinement

This report refines the Pythia observational bridge by asking whether primitive-to-composite residuals agree across continuous metrics and composite families. It remains observational and cannot establish causal dependency.

- result_dir: `results/pythia_model_sweep_v31_mid_smoke/pythia-1b_n16`
- metrics included: `accuracy, mean_correct_margin, mean_correct_mrr, mean_logprob_correct, mean_logprob_margin`
- valid residual rows: `50`
- composites with residuals: `10`

## Composite residual agreement
- `comp_add_then_even` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.800, over-rate=0.200, median-z=-1.335; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct`
- `comp_reverse_then_same` (string): verdict=`consistent_underperforming_observational`, under-rate=0.800, over-rate=0.200, median-z=0.479; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct`
- `comp_add_then_compare` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.600, over-rate=0.400, median-z=-1.384; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr`
- `comp_retrieve_then_color` (retrieval): verdict=`consistent_underperforming_observational`, under-rate=0.600, over-rate=0.400, median-z=-0.647; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr`
- `comp_max_then_compare` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.600, over-rate=0.400, median-z=-0.418; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr`
- `comp_reverse_then_last` (string): verdict=`consistent_underperforming_observational`, under-rate=0.600, over-rate=0.400, median-z=-0.181; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr`
- `comp_sub_then_compare` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.600, over-rate=0.400, median-z=0.196; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr`
- `comp_reverse_then_first` (string): verdict=`consistent_underperforming_observational`, under-rate=0.600, over-rate=0.400, median-z=0.395; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr`
- `comp_first_then_same` (string): verdict=`consistent_underperforming_observational`, under-rate=0.600, over-rate=0.400, median-z=0.441; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr`
- `comp_retrieve_then_compare` (retrieval): verdict=`consistent_underperforming_observational`, under-rate=0.600, over-rate=0.400, median-z=1.740; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr`

## Composite-family summary
- `arithmetic`: n=4, mean under-rate=0.650, consistent-under=4, consistent-over=0, mixed=0; top=`comp_add_then_even;comp_add_then_compare;comp_max_then_compare;comp_sub_then_compare`
- `string`: n=4, mean under-rate=0.650, consistent-under=4, consistent-over=0, mixed=0; top=`comp_reverse_then_same;comp_reverse_then_last;comp_reverse_then_first;comp_first_then_same`
- `retrieval`: n=2, mean under-rate=0.600, consistent-under=2, consistent-over=0, mixed=0; top=`comp_retrieve_then_color;comp_retrieve_then_compare`

## Component-coupling agreement
- `comp_max_then_compare`: verdict=`component_lag_observational`, lag-rate=0.800, ahead-rate=0.200, mean final diff=-0.145
- `comp_retrieve_then_compare`: verdict=`component_lag_observational`, lag-rate=0.800, ahead-rate=0.200, mean final diff=-0.026
- `comp_retrieve_then_color`: verdict=`component_lag_observational`, lag-rate=0.600, ahead-rate=0.400, mean final diff=-0.120
- `comp_sub_then_compare`: verdict=`component_lag_observational`, lag-rate=0.600, ahead-rate=0.400, mean final diff=-0.105
- `comp_reverse_then_last`: verdict=`component_lag_observational`, lag-rate=0.600, ahead-rate=0.400, mean final diff=-0.086
- `comp_add_then_compare`: verdict=`component_lag_observational`, lag-rate=0.600, ahead-rate=0.400, mean final diff=-0.036
- `comp_reverse_then_same`: verdict=`composite_ahead_observational`, lag-rate=0.400, ahead-rate=0.600, mean final diff=-0.029
- `comp_add_then_even`: verdict=`mixed_component_coupling`, lag-rate=0.400, ahead-rate=0.400, mean final diff=0.057
- `comp_reverse_then_first`: verdict=`composite_ahead_observational`, lag-rate=0.200, ahead-rate=0.800, mean final diff=0.021
- `comp_first_then_same`: verdict=`composite_ahead_observational`, lag-rate=0.200, ahead-rate=0.800, mean final diff=0.201

## Claim boundary
A robust observational Pythia finding requires residual agreement across multiple continuous metrics and preferably across model sizes/checkpoint densities. These outputs can motivate controlled or observational follow-ups, but they are not H3 causal evidence.
