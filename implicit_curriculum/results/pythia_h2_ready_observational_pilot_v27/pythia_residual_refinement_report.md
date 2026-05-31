# Pythia observational residual refinement

This report refines the Pythia observational bridge by asking whether primitive-to-composite residuals agree across continuous metrics and composite families. It remains observational and cannot establish causal dependency.

- result_dir: `results/pythia_h2_ready_observational_pilot_v27`
- metrics included: `accuracy, mean_correct_margin, mean_correct_mrr, mean_logprob_correct, mean_logprob_margin`
- valid residual rows: `50`
- composites with residuals: `10`

## Composite residual agreement
- `comp_add_then_compare` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.600, over-rate=0.400, median-z=-1.072; under metrics=`accuracy;mean_correct_mrr;mean_logprob_margin`
- `comp_sub_then_compare` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.600, over-rate=0.400, median-z=-0.708; under metrics=`accuracy;mean_correct_mrr;mean_logprob_margin`
- `comp_add_then_even` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.600, over-rate=0.400, median-z=-0.417; under metrics=`accuracy;mean_correct_mrr;mean_logprob_margin`
- `comp_reverse_then_last` (string): verdict=`consistent_underperforming_observational`, under-rate=0.600, over-rate=0.400, median-z=-0.406; under metrics=`accuracy;mean_correct_mrr;mean_logprob_margin`
- `comp_first_then_same` (string): verdict=`consistent_underperforming_observational`, under-rate=0.600, over-rate=0.400, median-z=-0.285; under metrics=`accuracy;mean_correct_mrr;mean_logprob_margin`
- `comp_reverse_then_same` (string): verdict=`consistent_underperforming_observational`, under-rate=0.600, over-rate=0.400, median-z=0.278; under metrics=`accuracy;mean_correct_mrr;mean_logprob_margin`
- `comp_max_then_compare` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.600, over-rate=0.400, median-z=0.515; under metrics=`accuracy;mean_correct_mrr;mean_logprob_margin`
- `comp_retrieve_then_color` (retrieval): verdict=`consistent_outperforming_observational`, under-rate=0.400, over-rate=0.600, median-z=-0.096; under metrics=`accuracy;mean_correct_mrr`
- `comp_reverse_then_first` (string): verdict=`consistent_outperforming_observational`, under-rate=0.400, over-rate=0.600, median-z=0.130; under metrics=`mean_correct_mrr;mean_logprob_margin`
- `comp_retrieve_then_compare` (retrieval): verdict=`consistent_outperforming_observational`, under-rate=0.400, over-rate=0.600, median-z=1.404; under metrics=`mean_correct_mrr;mean_logprob_margin`

## Composite-family summary
- `arithmetic`: n=4, mean under-rate=0.600, consistent-under=4, consistent-over=0, mixed=0; top=`comp_add_then_compare;comp_sub_then_compare;comp_add_then_even;comp_max_then_compare`
- `string`: n=4, mean under-rate=0.550, consistent-under=3, consistent-over=1, mixed=0; top=`comp_reverse_then_last;comp_first_then_same;comp_reverse_then_same;comp_reverse_then_first`
- `retrieval`: n=2, mean under-rate=0.400, consistent-under=0, consistent-over=2, mixed=0; top=`comp_retrieve_then_color;comp_retrieve_then_compare`

## Component-coupling agreement
- `comp_reverse_then_last`: verdict=`component_lag_observational`, lag-rate=1.000, ahead-rate=0.000, mean final diff=-0.142
- `comp_reverse_then_first`: verdict=`component_lag_observational`, lag-rate=0.800, ahead-rate=0.200, mean final diff=-0.155
- `comp_sub_then_compare`: verdict=`component_lag_observational`, lag-rate=0.600, ahead-rate=0.400, mean final diff=-0.003
- `comp_add_then_compare`: verdict=`component_lag_observational`, lag-rate=0.600, ahead-rate=0.400, mean final diff=0.015
- `comp_first_then_same`: verdict=`composite_ahead_observational`, lag-rate=0.200, ahead-rate=0.800, mean final diff=0.003
- `comp_retrieve_then_color`: verdict=`composite_ahead_observational`, lag-rate=0.200, ahead-rate=0.800, mean final diff=0.087
- `comp_add_then_even`: verdict=`composite_ahead_observational`, lag-rate=0.200, ahead-rate=0.800, mean final diff=0.117
- `comp_reverse_then_same`: verdict=`composite_ahead_observational`, lag-rate=0.200, ahead-rate=0.600, mean final diff=0.123
- `comp_retrieve_then_compare`: verdict=`composite_ahead_observational`, lag-rate=0.000, ahead-rate=1.000, mean final diff=0.166
- `comp_max_then_compare`: verdict=`composite_ahead_observational`, lag-rate=0.000, ahead-rate=1.000, mean final diff=0.201

## Claim boundary
A robust observational Pythia finding requires residual agreement across multiple continuous metrics and preferably across model sizes/checkpoint densities. These outputs can motivate controlled or observational follow-ups, but they are not H3 causal evidence.
