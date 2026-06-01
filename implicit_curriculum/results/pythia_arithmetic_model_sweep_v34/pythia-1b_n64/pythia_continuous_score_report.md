# Pythia observational continuous-score analysis

This analysis is observational. Continuous scores can reveal subthreshold movement, but they do not establish causal dependency.

- metrics analyzed: `accuracy, mean_logprob_correct, mean_correct_margin, mean_correct_mrr, mean_logprob_margin`
- H2 target summary: `final_metric`
- slices: `24`
- models: `1`

## Best final slices by metric
### `accuracy`
- `arith_min2` (atomic): final=0.328, delta=0.141, AUC=0.293, status=usable_or_near_usable
- `arith_absdiff` (atomic): final=0.297, delta=0.109, AUC=0.270, status=weak_or_uninformative
- `comp_min_then_compare_lt` (composite): final=0.297, delta=0.000, AUC=0.297, status=weak_or_uninformative
- `arith_compare_gt` (atomic): final=0.297, delta=0.094, AUC=0.273, status=weak_or_uninformative
- `arith_sub_small` (atomic): final=0.281, delta=0.109, AUC=0.254, status=weak_or_uninformative
- `arith_max2` (atomic): final=0.266, delta=0.031, AUC=0.258, status=weak_or_uninformative
- `comp_add_then_equals` (composite): final=0.266, delta=0.016, AUC=0.262, status=weak_or_uninformative
- `arith_even` (atomic): final=0.250, delta=-0.016, AUC=0.246, status=weak_or_uninformative
### `mean_correct_margin`
- `arith_compare_gt` (atomic): final=-0.311, delta=0.178, AUC=-0.589, status=usable_or_near_usable
- `arith_min2` (atomic): final=-0.336, delta=0.089, AUC=-0.585, status=usable_or_near_usable
- `comp_min_then_compare_lt` (composite): final=-0.366, delta=-0.071, AUC=-0.496, status=usable_or_near_usable
- `arith_odd` (atomic): final=-0.379, delta=0.033, AUC=-0.662, status=usable_or_near_usable
- `comp_sub_then_compare_gt` (composite): final=-0.380, delta=0.057, AUC=-0.689, status=usable_or_near_usable
- `arith_compare_lt` (atomic): final=-0.408, delta=0.034, AUC=-0.815, status=usable_or_near_usable
- `arith_even` (atomic): final=-0.466, delta=-0.059, AUC=-0.666, status=usable_or_near_usable
- `comp_add_then_compare_gt` (composite): final=-0.471, delta=-0.038, AUC=-0.734, status=usable_or_near_usable
### `mean_correct_mrr`
- `arith_min2` (atomic): final=0.577, delta=0.105, AUC=0.546, status=usable_or_near_usable
- `arith_absdiff` (atomic): final=0.568, delta=0.078, AUC=0.549, status=usable_or_near_usable
- `arith_max2` (atomic): final=0.543, delta=0.025, AUC=0.535, status=usable_or_near_usable
- `comp_min_then_compare_lt` (composite): final=0.539, delta=-0.003, AUC=0.550, status=usable_or_near_usable
- `arith_sub_small` (atomic): final=0.535, delta=0.061, AUC=0.524, status=usable_or_near_usable
- `comp_add_then_equals` (composite): final=0.526, delta=-0.016, AUC=0.539, status=usable_or_near_usable
- `arith_compare_gt` (atomic): final=0.523, delta=0.030, AUC=0.533, status=usable_or_near_usable
- `arith_double` (atomic): final=0.520, delta=-0.038, AUC=0.524, status=usable_or_near_usable
### `mean_logprob_correct`
- `arith_min2` (atomic): final=-2.009, delta=9.040, AUC=-4.719, status=usable_or_near_usable
- `ctrl_arith_digit_surface` (surface_control): final=-2.043, delta=9.120, AUC=-4.813, status=usable_or_near_usable
- `ctrl_arith_word_surface` (surface_control): final=-2.055, delta=8.784, AUC=-4.678, status=usable_or_near_usable
- `arith_compare_gt` (atomic): final=-2.091, delta=9.069, AUC=-4.977, status=usable_or_near_usable
- `arith_compare_lt` (atomic): final=-2.145, delta=8.959, AUC=-5.129, status=usable_or_near_usable
- `comp_sub_then_compare_gt` (composite): final=-2.149, delta=9.036, AUC=-5.025, status=usable_or_near_usable
- `comp_double_then_compare_gt` (composite): final=-2.164, delta=8.934, AUC=-5.007, status=usable_or_near_usable
- `comp_min_then_compare_lt` (composite): final=-2.170, delta=8.970, AUC=-5.044, status=usable_or_near_usable
### `mean_logprob_margin`
- `arith_double` (atomic): final=1.761, delta=1.688, AUC=1.256, status=usable_or_near_usable
- `arith_add_small` (atomic): final=1.581, delta=1.499, AUC=1.114, status=usable_or_near_usable
- `arith_add_large` (atomic): final=1.544, delta=1.444, AUC=1.192, status=usable_or_near_usable
- `arith_absdiff` (atomic): final=1.384, delta=1.110, AUC=1.176, status=usable_or_near_usable
- `arith_sub_small` (atomic): final=1.228, delta=1.031, AUC=1.061, status=usable_or_near_usable
- `ctrl_arith_word_surface` (surface_control): final=1.139, delta=0.566, AUC=1.123, status=usable_or_near_usable
- `comp_add_then_even` (composite): final=0.819, delta=0.486, AUC=0.791, status=usable_or_near_usable
- `comp_add_then_equals` (composite): final=0.811, delta=0.611, AUC=0.825, status=usable_or_near_usable

## H1-like continuous signatures
- `EleutherAI/pythia-1b` / `accuracy`: mean_final=0.245, mean_delta=-0.003, rho(freq, final)=-0.024, rho(learn, final)=0.077, rho(freq, delta)=0.192, rho(learn, delta)=-0.136
- `EleutherAI/pythia-1b` / `mean_correct_margin`: mean_final=-0.579, mean_delta=-0.184, rho(freq, final)=-0.080, rho(learn, final)=0.061, rho(freq, delta)=0.035, rho(learn, delta)=-0.071
- `EleutherAI/pythia-1b` / `mean_correct_mrr`: mean_final=0.509, mean_delta=-0.013, rho(freq, final)=0.015, rho(learn, final)=0.032, rho(freq, delta)=0.188, rho(learn, delta)=-0.132
- `EleutherAI/pythia-1b` / `mean_logprob_correct`: mean_final=-2.359, mean_delta=8.725, rho(freq, final)=-0.034, rho(learn, final)=-0.009, rho(freq, delta)=-0.076, rho(learn, delta)=0.035
- `EleutherAI/pythia-1b` / `mean_logprob_margin`: mean_final=0.799, mean_delta=0.606, rho(freq, final)=0.066, rho(learn, final)=-0.047, rho(freq, delta)=-0.006, rho(learn, delta)=0.050

## H2-like continuous residuals
- `accuracy`: n=10, mean residual=-0.123
  - underperforming composite `comp_add_then_even`: residual=-0.146, observed=0.203, predicted=0.349
  - underperforming composite `comp_absdiff_then_even`: residual=-0.144, observed=0.234, predicted=0.378
  - underperforming composite `comp_add_then_compare_lt`: residual=-0.137, observed=0.203, predicted=0.340
- `mean_correct_margin`: n=10, mean residual=-0.785
  - underperforming composite `comp_add_then_even`: residual=-1.066, observed=-0.688, predicted=0.378
  - underperforming composite `comp_add_then_compare_lt`: residual=-0.892, observed=-0.554, predicted=0.338
  - underperforming composite `comp_double_then_compare_gt`: residual=-0.855, observed=-0.525, predicted=0.330
- `mean_correct_mrr`: n=10, mean residual=-0.197
  - underperforming composite `comp_absdiff_then_even`: residual=-0.233, observed=0.486, predicted=0.719
  - underperforming composite `comp_add_then_even`: residual=-0.227, observed=0.458, predicted=0.685
  - underperforming composite `comp_sub_then_odd`: residual=-0.203, observed=0.499, predicted=0.702
- `mean_logprob_correct`: n=10, mean residual=-0.833
  - underperforming composite `comp_add_then_even`: residual=-1.231, observed=-2.502, predicted=-1.270
  - underperforming composite `comp_add_then_compare_gt`: residual=-0.979, observed=-2.246, predicted=-1.267
  - underperforming composite `comp_add_then_compare_lt`: residual=-0.939, observed=-2.257, predicted=-1.317
- `mean_logprob_margin`: n=10, mean residual=1.283
  - underperforming composite `comp_absdiff_then_even`: residual=0.923, observed=0.519, predicted=-0.404
  - underperforming composite `comp_sub_then_compare_gt`: residual=0.985, observed=0.399, predicted=-0.585
  - underperforming composite `comp_sub_then_odd`: residual=1.117, observed=0.537, predicted=-0.580

## Component coupling
Component coupling compares composite continuous scores to the mean of its listed primitive slices. It is descriptive only.
- `accuracy` / `comp_absdiff_then_even`: composite_final=0.234, component_mean_final=0.273, diff=-0.039
- `accuracy` / `comp_add_then_compare_gt`: composite_final=0.219, component_mean_final=0.266, diff=-0.047
- `accuracy` / `comp_add_then_compare_lt`: composite_final=0.203, component_mean_final=0.203, diff=0.000
- `accuracy` / `comp_add_then_equals`: composite_final=0.266, component_mean_final=0.219, diff=0.047
- `accuracy` / `comp_add_then_even`: composite_final=0.203, component_mean_final=0.242, diff=-0.039
- `accuracy` / `comp_double_then_compare_gt`: composite_final=0.234, component_mean_final=0.266, diff=-0.031
- `accuracy` / `comp_max_then_compare_gt`: composite_final=0.234, component_mean_final=0.281, diff=-0.047
- `accuracy` / `comp_min_then_compare_lt`: composite_final=0.297, component_mean_final=0.250, diff=0.047
- `accuracy` / `comp_sub_then_compare_gt`: composite_final=0.234, component_mean_final=0.289, diff=-0.055
- `accuracy` / `comp_sub_then_odd`: composite_final=0.234, component_mean_final=0.258, diff=-0.023

## Claim boundary
Use continuous-score outputs as calibration and observational bridge evidence only. They can show that a slice moves below top-1 accuracy, but they cannot establish causal dependency without interventions.
