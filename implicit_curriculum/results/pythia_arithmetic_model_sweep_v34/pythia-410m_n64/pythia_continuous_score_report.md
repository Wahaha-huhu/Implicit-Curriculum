# Pythia observational continuous-score analysis

This analysis is observational. Continuous scores can reveal subthreshold movement, but they do not establish causal dependency.

- metrics analyzed: `accuracy, mean_logprob_correct, mean_correct_margin, mean_correct_mrr, mean_logprob_margin`
- H2 target summary: `final_metric`
- slices: `24`
- models: `1`

## Best final slices by metric
### `accuracy`
- `arith_min2` (atomic): final=0.328, delta=0.000, AUC=0.328, status=usable_or_near_usable
- `arith_absdiff` (atomic): final=0.297, delta=-0.031, AUC=0.305, status=usable_or_near_usable
- `comp_min_then_compare_lt` (composite): final=0.297, delta=-0.047, AUC=0.312, status=usable_or_near_usable
- `arith_compare_gt` (atomic): final=0.297, delta=0.016, AUC=0.285, status=weak_or_uninformative
- `arith_sub_small` (atomic): final=0.281, delta=0.000, AUC=0.281, status=weak_or_uninformative
- `arith_max2` (atomic): final=0.266, delta=0.000, AUC=0.258, status=weak_or_uninformative
- `comp_add_then_equals` (composite): final=0.266, delta=0.000, AUC=0.254, status=weak_or_uninformative
- `comp_absdiff_then_even` (composite): final=0.250, delta=-0.109, AUC=0.258, status=usable_or_near_usable
### `mean_correct_margin`
- `arith_min2` (atomic): final=-0.413, delta=-0.017, AUC=-0.540, status=usable_or_near_usable
- `ctrl_arith_digit_surface` (surface_control): final=-0.531, delta=-0.117, AUC=-0.763, status=usable_or_near_usable
- `comp_min_then_compare_lt` (composite): final=-0.620, delta=-0.325, AUC=-0.580, status=usable_or_near_usable
- `arith_even` (atomic): final=-0.650, delta=-0.266, AUC=-0.745, status=usable_or_near_usable
- `arith_compare_gt` (atomic): final=-0.663, delta=-0.312, AUC=-0.634, status=usable_or_near_usable
- `comp_add_then_equals` (composite): final=-0.723, delta=-0.347, AUC=-0.729, status=usable_or_near_usable
- `arith_max2` (atomic): final=-0.765, delta=-0.277, AUC=-0.782, status=usable_or_near_usable
- `arith_sub_small` (atomic): final=-0.796, delta=-0.480, AUC=-0.723, status=usable_or_near_usable
### `mean_correct_mrr`
- `arith_min2` (atomic): final=0.578, delta=0.003, AUC=0.570, status=usable_or_near_usable
- `comp_min_then_compare_lt` (composite): final=0.557, delta=-0.033, AUC=0.562, status=usable_or_near_usable
- `arith_compare_gt` (atomic): final=0.552, delta=0.001, AUC=0.545, status=usable_or_near_usable
- `arith_sub_small` (atomic): final=0.544, delta=0.005, AUC=0.540, status=usable_or_near_usable
- `arith_absdiff` (atomic): final=0.540, delta=-0.012, AUC=0.549, status=usable_or_near_usable
- `arith_max2` (atomic): final=0.533, delta=0.007, AUC=0.521, status=usable_or_near_usable
- `comp_add_then_equals` (composite): final=0.533, delta=-0.016, AUC=0.526, status=usable_or_near_usable
- `arith_odd` (atomic): final=0.522, delta=0.000, AUC=0.519, status=usable_or_near_usable
### `mean_logprob_correct`
- `arith_min2` (atomic): final=-1.683, delta=9.202, AUC=-5.320, status=usable_or_near_usable
- `ctrl_arith_digit_surface` (surface_control): final=-1.899, delta=9.016, AUC=-5.467, status=usable_or_near_usable
- `arith_max2` (atomic): final=-2.095, delta=8.834, AUC=-5.542, status=usable_or_near_usable
- `comp_min_then_compare_lt` (composite): final=-2.168, delta=8.761, AUC=-5.381, status=usable_or_near_usable
- `arith_compare_gt` (atomic): final=-2.215, delta=8.793, AUC=-5.386, status=usable_or_near_usable
- `ctrl_arith_word_surface` (surface_control): final=-2.253, delta=8.711, AUC=-5.382, status=usable_or_near_usable
- `arith_double` (atomic): final=-2.329, delta=8.587, AUC=-5.507, status=usable_or_near_usable
- `arith_equals` (atomic): final=-2.367, delta=8.623, AUC=-5.444, status=usable_or_near_usable
### `mean_logprob_margin`
- `arith_absdiff` (atomic): final=1.990, delta=1.870, AUC=1.370, status=usable_or_near_usable
- `arith_add_small` (atomic): final=1.688, delta=1.471, AUC=1.292, status=usable_or_near_usable
- `comp_add_then_compare_gt` (composite): final=1.558, delta=1.293, AUC=0.971, status=usable_or_near_usable
- `arith_odd` (atomic): final=1.485, delta=1.385, AUC=0.938, status=usable_or_near_usable
- `comp_absdiff_then_even` (composite): final=1.476, delta=1.406, AUC=0.879, status=usable_or_near_usable
- `comp_max_then_compare_gt` (composite): final=1.431, delta=1.324, AUC=0.934, status=usable_or_near_usable
- `arith_compare_gt` (atomic): final=1.342, delta=1.186, AUC=0.963, status=usable_or_near_usable
- `comp_add_then_compare_lt` (composite): final=1.324, delta=0.945, AUC=0.939, status=usable_or_near_usable

## H1-like continuous signatures
- `EleutherAI/pythia-410m` / `accuracy`: mean_final=0.245, mean_delta=-0.012, rho(freq, final)=-0.150, rho(learn, final)=0.206, rho(freq, delta)=0.273, rho(learn, delta)=-0.305
- `EleutherAI/pythia-410m` / `mean_correct_margin`: mean_final=-0.898, mean_delta=-0.474, rho(freq, final)=-0.130, rho(learn, final)=0.098, rho(freq, delta)=-0.140, rho(learn, delta)=0.094
- `EleutherAI/pythia-410m` / `mean_correct_mrr`: mean_final=0.514, mean_delta=-0.011, rho(freq, final)=-0.090, rho(learn, final)=0.137, rho(freq, delta)=0.016, rho(learn, delta)=-0.027
- `EleutherAI/pythia-410m` / `mean_logprob_correct`: mean_final=-2.472, mean_delta=8.510, rho(freq, final)=0.173, rho(learn, final)=-0.235, rho(freq, delta)=0.088, rho(learn, delta)=-0.150
- `EleutherAI/pythia-410m` / `mean_logprob_margin`: mean_final=1.292, mean_delta=1.124, rho(freq, final)=-0.104, rho(learn, final)=0.138, rho(freq, delta)=-0.249, rho(learn, delta)=0.289

## H2-like continuous residuals
- `accuracy`: n=10, mean residual=-0.102
  - underperforming composite `comp_add_then_even`: residual=-0.128, observed=0.203, predicted=0.331
  - underperforming composite `comp_add_then_compare_lt`: residual=-0.119, observed=0.203, predicted=0.322
  - underperforming composite `comp_max_then_compare_gt`: residual=-0.118, observed=0.234, predicted=0.352
- `mean_correct_margin`: n=10, mean residual=-1.183
  - underperforming composite `comp_add_then_compare_gt`: residual=-1.399, observed=-1.067, predicted=0.332
  - underperforming composite `comp_add_then_compare_lt`: residual=-1.384, observed=-1.067, predicted=0.317
  - underperforming composite `comp_add_then_even`: residual=-1.360, observed=-0.969, predicted=0.391
- `mean_correct_mrr`: n=10, mean residual=-0.225
  - underperforming composite `comp_add_then_even`: residual=-0.249, observed=0.478, predicted=0.727
  - underperforming composite `comp_add_then_compare_lt`: residual=-0.246, observed=0.473, predicted=0.719
  - underperforming composite `comp_double_then_compare_gt`: residual=-0.237, observed=0.497, predicted=0.734
- `mean_logprob_correct`: n=10, mean residual=-2.258
  - underperforming composite `comp_add_then_even`: residual=-2.856, observed=-2.947, predicted=-0.092
  - underperforming composite `comp_absdiff_then_even`: residual=-2.427, observed=-2.922, predicted=-0.495
  - underperforming composite `comp_add_then_compare_gt`: residual=-2.367, observed=-2.542, predicted=-0.175
- `mean_logprob_margin`: n=10, mean residual=1.750
  - underperforming composite `comp_min_then_compare_lt`: residual=1.534, observed=1.167, predicted=-0.368
  - underperforming composite `comp_sub_then_compare_gt`: residual=1.605, observed=1.282, predicted=-0.323
  - underperforming composite `comp_add_then_equals`: residual=1.653, observed=1.285, predicted=-0.368

## Component coupling
Component coupling compares composite continuous scores to the mean of its listed primitive slices. It is descriptive only.
- `accuracy` / `comp_absdiff_then_even`: composite_final=0.250, component_mean_final=0.266, diff=-0.016
- `accuracy` / `comp_add_then_compare_gt`: composite_final=0.219, component_mean_final=0.266, diff=-0.047
- `accuracy` / `comp_add_then_compare_lt`: composite_final=0.203, component_mean_final=0.203, diff=0.000
- `accuracy` / `comp_add_then_equals`: composite_final=0.266, component_mean_final=0.219, diff=0.047
- `accuracy` / `comp_add_then_even`: composite_final=0.203, component_mean_final=0.234, diff=-0.031
- `accuracy` / `comp_double_then_compare_gt`: composite_final=0.234, component_mean_final=0.266, diff=-0.031
- `accuracy` / `comp_max_then_compare_gt`: composite_final=0.234, component_mean_final=0.281, diff=-0.047
- `accuracy` / `comp_min_then_compare_lt`: composite_final=0.297, component_mean_final=0.250, diff=0.047
- `accuracy` / `comp_sub_then_compare_gt`: composite_final=0.250, component_mean_final=0.289, diff=-0.039
- `accuracy` / `comp_sub_then_odd`: composite_final=0.234, component_mean_final=0.250, diff=-0.016

## Claim boundary
Use continuous-score outputs as calibration and observational bridge evidence only. They can show that a slice moves below top-1 accuracy, but they cannot establish causal dependency without interventions.
