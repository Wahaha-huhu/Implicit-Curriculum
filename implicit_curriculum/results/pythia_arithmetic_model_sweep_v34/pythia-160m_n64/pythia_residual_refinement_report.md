# Pythia observational residual refinement

This report refines the Pythia observational bridge by asking whether primitive-to-composite residuals agree across continuous metrics and composite families. It remains observational and cannot establish causal dependency.

- result_dir: `results/pythia_arithmetic_model_sweep_v34/pythia-160m_n64`
- metrics included: `accuracy, mean_correct_margin, mean_correct_mrr, mean_logprob_correct, mean_logprob_margin`
- valid residual rows: `50`
- composites with residuals: `10`

## Composite residual agreement
- `comp_add_then_compare_lt` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.800, over-rate=0.200, median-z=-1.121; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct`
- `comp_add_then_even` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.800, over-rate=0.200, median-z=-0.835; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct`
- `comp_max_then_compare_gt` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.800, over-rate=0.200, median-z=-0.440; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct`
- `comp_add_then_compare_gt` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.800, over-rate=0.200, median-z=-0.096; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct`
- `comp_sub_then_odd` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.800, over-rate=0.200, median-z=0.000; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct`
- `comp_double_then_compare_gt` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.800, over-rate=0.200, median-z=0.449; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct`
- `comp_add_then_equals` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.800, over-rate=0.200, median-z=0.761; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct`
- `comp_sub_then_compare_gt` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.800, over-rate=0.200, median-z=0.782; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct`
- `comp_min_then_compare_lt` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.800, over-rate=0.200, median-z=1.163; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct`
- `comp_absdiff_then_even` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.600, over-rate=0.400, median-z=-0.463; under metrics=`accuracy;mean_correct_mrr;mean_logprob_correct`

## Composite-family summary
- `arithmetic`: n=10, mean under-rate=0.780, consistent-under=10, consistent-over=0, mixed=0; top=`comp_add_then_compare_lt;comp_add_then_even;comp_max_then_compare_gt;comp_add_then_compare_gt;comp_sub_then_odd`

## Component-coupling agreement
- `comp_add_then_compare_gt`: verdict=`component_lag_observational`, lag-rate=0.800, ahead-rate=0.200, mean final diff=-0.118
- `comp_sub_then_compare_gt`: verdict=`component_lag_observational`, lag-rate=0.800, ahead-rate=0.200, mean final diff=-0.079
- `comp_add_then_even`: verdict=`component_lag_observational`, lag-rate=0.800, ahead-rate=0.200, mean final diff=-0.068
- `comp_max_then_compare_gt`: verdict=`component_lag_observational`, lag-rate=0.800, ahead-rate=0.200, mean final diff=-0.053
- `comp_absdiff_then_even`: verdict=`component_lag_observational`, lag-rate=0.800, ahead-rate=0.200, mean final diff=-0.034
- `comp_double_then_compare_gt`: verdict=`component_lag_observational`, lag-rate=0.800, ahead-rate=0.200, mean final diff=-0.030
- `comp_sub_then_odd`: verdict=`component_lag_observational`, lag-rate=0.600, ahead-rate=0.400, mean final diff=-0.024
- `comp_add_then_compare_lt`: verdict=`mixed_component_coupling`, lag-rate=0.400, ahead-rate=0.400, mean final diff=-0.025
- `comp_min_then_compare_lt`: verdict=`composite_ahead_observational`, lag-rate=0.200, ahead-rate=0.800, mean final diff=0.047
- `comp_add_then_equals`: verdict=`composite_ahead_observational`, lag-rate=0.200, ahead-rate=0.800, mean final diff=0.049

## Claim boundary
A robust observational Pythia finding requires residual agreement across multiple continuous metrics and preferably across model sizes/checkpoint densities. These outputs can motivate controlled or observational follow-ups, but they are not H3 causal evidence.
