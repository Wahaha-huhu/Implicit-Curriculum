# Pythia observational residual refinement

This report refines the Pythia observational bridge by asking whether primitive-to-composite residuals agree across continuous metrics and composite families. It remains observational and cannot establish causal dependency.

- result_dir: `results/pythia_arithmetic_model_sweep_v34/pythia-1b_n64`
- metrics included: `accuracy, mean_correct_margin, mean_correct_mrr, mean_logprob_correct, mean_logprob_margin`
- valid residual rows: `50`
- composites with residuals: `10`

## Composite residual agreement
- `comp_add_then_even` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.800, over-rate=0.200, median-z=-1.536; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct`
- `comp_absdiff_then_even` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.800, over-rate=0.200, median-z=-1.019; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct`
- `comp_add_then_compare_lt` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.800, over-rate=0.200, median-z=-0.622; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct`
- `comp_sub_then_odd` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.800, over-rate=0.200, median-z=-0.282; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct`
- `comp_double_then_compare_gt` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.800, over-rate=0.200, median-z=-0.068; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct`
- `comp_sub_then_compare_gt` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.800, over-rate=0.200, median-z=0.293; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct`
- `comp_max_then_compare_gt` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.800, over-rate=0.200, median-z=0.324; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct`
- `comp_add_then_compare_gt` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.800, over-rate=0.200, median-z=0.411; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct`
- `comp_add_then_equals` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.800, over-rate=0.200, median-z=0.706; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct`
- `comp_min_then_compare_lt` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.800, over-rate=0.200, median-z=1.330; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct`

## Composite-family summary
- `arithmetic`: n=10, mean under-rate=0.800, consistent-under=10, consistent-over=0, mixed=0; top=`comp_add_then_even;comp_absdiff_then_even;comp_add_then_compare_lt;comp_sub_then_odd;comp_double_then_compare_gt`

## Component-coupling agreement
- `comp_sub_then_odd`: verdict=`component_lag_observational`, lag-rate=0.800, ahead-rate=0.200, mean final diff=-0.069
- `comp_max_then_compare_gt`: verdict=`component_lag_observational`, lag-rate=0.800, ahead-rate=0.200, mean final diff=-0.019
- `comp_sub_then_compare_gt`: verdict=`component_lag_observational`, lag-rate=0.600, ahead-rate=0.400, mean final diff=-0.066
- `comp_absdiff_then_even`: verdict=`component_lag_observational`, lag-rate=0.600, ahead-rate=0.400, mean final diff=-0.065
- `comp_add_then_compare_gt`: verdict=`component_lag_observational`, lag-rate=0.600, ahead-rate=0.400, mean final diff=-0.017
- `comp_add_then_even`: verdict=`component_lag_observational`, lag-rate=0.600, ahead-rate=0.400, mean final diff=-0.014
- `comp_double_then_compare_gt`: verdict=`component_lag_observational`, lag-rate=0.600, ahead-rate=0.400, mean final diff=-0.010
- `comp_add_then_compare_lt`: verdict=`mixed_component_coupling`, lag-rate=0.400, ahead-rate=0.400, mean final diff=0.004
- `comp_min_then_compare_lt`: verdict=`composite_ahead_observational`, lag-rate=0.200, ahead-rate=0.800, mean final diff=0.018
- `comp_add_then_equals`: verdict=`composite_ahead_observational`, lag-rate=0.200, ahead-rate=0.800, mean final diff=0.083

## Claim boundary
A robust observational Pythia finding requires residual agreement across multiple continuous metrics and preferably across model sizes/checkpoint densities. These outputs can motivate controlled or observational follow-ups, but they are not H3 causal evidence.
