# Pythia observational residual refinement

This report refines the Pythia observational bridge by asking whether primitive-to-composite residuals agree across continuous metrics and composite families. It remains observational and cannot establish causal dependency.

- result_dir: `results/pythia_arithmetic_model_sweep_v34/pythia-1.4b_n64`
- metrics included: `accuracy, mean_correct_margin, mean_correct_mrr, mean_logprob_correct, mean_logprob_margin`
- valid residual rows: `50`
- composites with residuals: `10`

## Composite residual agreement
- `comp_absdiff_then_even` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=1.000, over-rate=0.000, median-z=-0.966; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct;mean_logprob_margin`
- `comp_max_then_compare_gt` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=1.000, over-rate=0.000, median-z=-0.657; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct;mean_logprob_margin`
- `comp_min_then_compare_lt` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=1.000, over-rate=0.000, median-z=-0.464; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct;mean_logprob_margin`
- `comp_add_then_compare_lt` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=1.000, over-rate=0.000, median-z=0.022; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct;mean_logprob_margin`
- `comp_sub_then_compare_gt` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=1.000, over-rate=0.000, median-z=0.906; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct;mean_logprob_margin`
- `comp_add_then_even` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.800, over-rate=0.200, median-z=-0.930; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct`
- `comp_double_then_compare_gt` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.800, over-rate=0.200, median-z=-0.148; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct`
- `comp_add_then_equals` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.800, over-rate=0.200, median-z=0.029; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct`
- `comp_add_then_compare_gt` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.800, over-rate=0.200, median-z=0.335; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct`
- `comp_sub_then_odd` (arithmetic): verdict=`consistent_underperforming_observational`, under-rate=0.800, over-rate=0.200, median-z=0.761; under metrics=`accuracy;mean_correct_margin;mean_correct_mrr;mean_logprob_correct`

## Composite-family summary
- `arithmetic`: n=10, mean under-rate=0.900, consistent-under=10, consistent-over=0, mixed=0; top=`comp_absdiff_then_even;comp_max_then_compare_gt;comp_min_then_compare_lt;comp_add_then_compare_lt;comp_sub_then_compare_gt`

## Component-coupling agreement
- `comp_max_then_compare_gt`: verdict=`component_lag_observational`, lag-rate=1.000, ahead-rate=0.000, mean final diff=-0.057
- `comp_min_then_compare_lt`: verdict=`component_lag_observational`, lag-rate=0.800, ahead-rate=0.200, mean final diff=-0.042
- `comp_absdiff_then_even`: verdict=`component_lag_observational`, lag-rate=0.600, ahead-rate=0.400, mean final diff=-0.023
- `comp_double_then_compare_gt`: verdict=`component_lag_observational`, lag-rate=0.600, ahead-rate=0.400, mean final diff=0.010
- `comp_add_then_compare_gt`: verdict=`component_lag_observational`, lag-rate=0.600, ahead-rate=0.400, mean final diff=0.023
- `comp_add_then_even`: verdict=`composite_ahead_observational`, lag-rate=0.400, ahead-rate=0.600, mean final diff=0.045
- `comp_sub_then_compare_gt`: verdict=`composite_ahead_observational`, lag-rate=0.200, ahead-rate=0.800, mean final diff=0.040
- `comp_add_then_equals`: verdict=`composite_ahead_observational`, lag-rate=0.200, ahead-rate=0.800, mean final diff=0.041
- `comp_add_then_compare_lt`: verdict=`composite_ahead_observational`, lag-rate=0.200, ahead-rate=0.800, mean final diff=0.051
- `comp_sub_then_odd`: verdict=`composite_ahead_observational`, lag-rate=0.200, ahead-rate=0.600, mean final diff=0.074

## Claim boundary
A robust observational Pythia finding requires residual agreement across multiple continuous metrics and preferably across model sizes/checkpoint densities. These outputs can motivate controlled or observational follow-ups, but they are not H3 causal evidence.
