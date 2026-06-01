# Pythia observational residual refinement

This report refines the Pythia observational bridge by asking whether primitive-to-composite residuals agree across continuous metrics and composite families. It remains observational and cannot establish causal dependency.

- result_dir: `results/pythia_arithmetic_model_sweep_v34/pythia-70m_n64`
- metrics included: `accuracy, mean_correct_margin, mean_correct_mrr, mean_logprob_correct, mean_logprob_margin`
- valid residual rows: `50`
- composites with residuals: `10`

## Composite residual agreement
- `comp_sub_then_compare_gt` (arithmetic): verdict=`consistent_outperforming_observational`, under-rate=0.400, over-rate=0.600, median-z=-0.823; under metrics=`mean_correct_margin;mean_correct_mrr`
- `comp_add_then_even` (arithmetic): verdict=`consistent_outperforming_observational`, under-rate=0.400, over-rate=0.600, median-z=-0.698; under metrics=`mean_correct_margin;mean_correct_mrr`
- `comp_max_then_compare_gt` (arithmetic): verdict=`consistent_outperforming_observational`, under-rate=0.400, over-rate=0.600, median-z=-0.391; under metrics=`mean_correct_margin;mean_correct_mrr`
- `comp_add_then_compare_gt` (arithmetic): verdict=`consistent_outperforming_observational`, under-rate=0.400, over-rate=0.600, median-z=-0.256; under metrics=`mean_correct_margin;mean_correct_mrr`
- `comp_add_then_compare_lt` (arithmetic): verdict=`consistent_outperforming_observational`, under-rate=0.400, over-rate=0.600, median-z=-0.241; under metrics=`mean_correct_margin;mean_correct_mrr`
- `comp_sub_then_odd` (arithmetic): verdict=`consistent_outperforming_observational`, under-rate=0.400, over-rate=0.600, median-z=-0.167; under metrics=`mean_correct_margin;mean_correct_mrr`
- `comp_double_then_compare_gt` (arithmetic): verdict=`consistent_outperforming_observational`, under-rate=0.400, over-rate=0.600, median-z=0.395; under metrics=`mean_correct_margin;mean_correct_mrr`
- `comp_absdiff_then_even` (arithmetic): verdict=`consistent_outperforming_observational`, under-rate=0.400, over-rate=0.600, median-z=0.516; under metrics=`mean_correct_margin;mean_correct_mrr`
- `comp_min_then_compare_lt` (arithmetic): verdict=`consistent_outperforming_observational`, under-rate=0.400, over-rate=0.600, median-z=1.123; under metrics=`mean_correct_margin;mean_correct_mrr`
- `comp_add_then_equals` (arithmetic): verdict=`consistent_outperforming_observational`, under-rate=0.400, over-rate=0.600, median-z=1.407; under metrics=`mean_correct_margin;mean_correct_mrr`

## Composite-family summary
- `arithmetic`: n=10, mean under-rate=0.400, consistent-under=0, consistent-over=10, mixed=0; top=`comp_sub_then_compare_gt;comp_add_then_even;comp_max_then_compare_gt;comp_add_then_compare_gt;comp_add_then_compare_lt`

## Component-coupling agreement
- `comp_sub_then_compare_gt`: verdict=`component_lag_observational`, lag-rate=0.600, ahead-rate=0.400, mean final diff=-0.021
- `comp_add_then_compare_gt`: verdict=`component_lag_observational`, lag-rate=0.600, ahead-rate=0.400, mean final diff=0.030
- `comp_absdiff_then_even`: verdict=`composite_ahead_observational`, lag-rate=0.400, ahead-rate=0.600, mean final diff=0.019
- `comp_double_then_compare_gt`: verdict=`composite_ahead_observational`, lag-rate=0.400, ahead-rate=0.600, mean final diff=0.033
- `comp_add_then_even`: verdict=`composite_ahead_observational`, lag-rate=0.400, ahead-rate=0.600, mean final diff=0.051
- `comp_max_then_compare_gt`: verdict=`composite_ahead_observational`, lag-rate=0.400, ahead-rate=0.600, mean final diff=0.085
- `comp_add_then_compare_lt`: verdict=`composite_ahead_observational`, lag-rate=0.200, ahead-rate=0.800, mean final diff=0.045
- `comp_sub_then_odd`: verdict=`composite_ahead_observational`, lag-rate=0.200, ahead-rate=0.600, mean final diff=0.045
- `comp_add_then_equals`: verdict=`composite_ahead_observational`, lag-rate=0.200, ahead-rate=0.800, mean final diff=0.169
- `comp_min_then_compare_lt`: verdict=`composite_ahead_observational`, lag-rate=0.000, ahead-rate=1.000, mean final diff=0.264

## Claim boundary
A robust observational Pythia finding requires residual agreement across multiple continuous metrics and preferably across model sizes/checkpoint densities. These outputs can motivate controlled or observational follow-ups, but they are not H3 causal evidence.
