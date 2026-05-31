# Pythia observational residual refinement

This report refines the Pythia observational bridge by asking whether primitive-to-composite residuals agree across continuous metrics and composite families. It remains observational and cannot establish causal dependency.

- result_dir: `results/pythia_model_sweep_v30/pythia-160m_n64`
- metrics included: `accuracy, mean_correct_margin, mean_correct_mrr, mean_logprob_correct, mean_logprob_margin`
- valid residual rows: `50`
- composites with residuals: `10`

## Composite residual agreement
- `comp_add_then_compare` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.800, over-rate=0.200, median-z=-1.344; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct`
- `comp_reverse_then_last` (string): verdict=`consistent_underperforming_observational`, under-rate=0.800, over-rate=0.200, median-z=-0.693; under metrics=`accuracy;mean_correct_mrr;mean_logprob_correct;mean_logprob_margin`
- `comp_add_then_even` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.800, over-rate=0.200, median-z=-0.577; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct`
- `comp_first_then_same` (string): verdict=`consistent_underperforming_observational`, under-rate=0.800, over-rate=0.200, median-z=-0.558; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct`
- `comp_reverse_then_first` (string): verdict=`consistent_underperforming_observational`, under-rate=0.800, over-rate=0.200, median-z=0.740; under metrics=`accuracy;mean_correct_mrr;mean_logprob_correct;mean_logprob_margin`
- `comp_sub_then_compare` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.600, over-rate=0.400, median-z=-0.581; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr`
- `comp_retrieve_then_color` (retrieval): verdict=`consistent_underperforming_observational`, under-rate=0.600, over-rate=0.400, median-z=0.152; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr`
- `comp_reverse_then_same` (string): verdict=`consistent_underperforming_observational`, under-rate=0.600, over-rate=0.400, median-z=0.565; under metrics=`accuracy;mean_correct_mrr;mean_logprob_margin`
- `comp_max_then_compare` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.600, over-rate=0.400, median-z=0.883; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr`
- `comp_retrieve_then_compare` (retrieval): verdict=`consistent_underperforming_observational`, under-rate=0.600, over-rate=0.400, median-z=1.016; under metrics=`accuracy;mean_correct_mrr;mean_logprob_margin`

## Composite-family summary
- `string`: n=4, mean under-rate=0.750, consistent-under=4, consistent-over=0, mixed=0; top=`comp_reverse_then_last;comp_first_then_same;comp_reverse_then_first;comp_reverse_then_same`
- `arithmetic`: n=4, mean under-rate=0.700, consistent-under=4, consistent-over=0, mixed=0; top=`comp_add_then_compare;comp_add_then_even;comp_sub_then_compare;comp_max_then_compare`
- `retrieval`: n=2, mean under-rate=0.600, consistent-under=2, consistent-over=0, mixed=0; top=`comp_retrieve_then_color;comp_retrieve_then_compare`

## Component-coupling agreement
- `comp_first_then_same`: verdict=`component_lag_observational`, lag-rate=1.000, ahead-rate=0.000, mean final diff=-0.109
- `comp_sub_then_compare`: verdict=`component_lag_observational`, lag-rate=0.800, ahead-rate=0.200, mean final diff=-0.124
- `comp_add_then_compare`: verdict=`component_lag_observational`, lag-rate=0.800, ahead-rate=0.200, mean final diff=-0.090
- `comp_reverse_then_last`: verdict=`component_lag_observational`, lag-rate=0.800, ahead-rate=0.200, mean final diff=0.002
- `comp_retrieve_then_compare`: verdict=`composite_ahead_observational`, lag-rate=0.400, ahead-rate=0.600, mean final diff=-0.012
- `comp_reverse_then_first`: verdict=`composite_ahead_observational`, lag-rate=0.400, ahead-rate=0.600, mean final diff=0.032
- `comp_reverse_then_same`: verdict=`mixed_component_coupling`, lag-rate=0.200, ahead-rate=0.400, mean final diff=0.103
- `comp_add_then_even`: verdict=`composite_ahead_observational`, lag-rate=0.200, ahead-rate=0.800, mean final diff=0.113
- `comp_retrieve_then_color`: verdict=`composite_ahead_observational`, lag-rate=0.200, ahead-rate=0.800, mean final diff=0.129
- `comp_max_then_compare`: verdict=`composite_ahead_observational`, lag-rate=0.200, ahead-rate=0.800, mean final diff=0.145

## Claim boundary
A robust observational Pythia finding requires residual agreement across multiple continuous metrics and preferably across model sizes/checkpoint densities. These outputs can motivate controlled or observational follow-ups, but they are not H3 causal evidence.
