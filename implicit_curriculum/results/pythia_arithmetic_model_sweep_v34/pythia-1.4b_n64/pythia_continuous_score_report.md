# Pythia observational continuous-score analysis

This analysis is observational. Continuous scores can reveal subthreshold movement, but they do not establish causal dependency.

- metrics analyzed: `accuracy, mean_logprob_correct, mean_correct_margin, mean_correct_mrr, mean_logprob_margin`
- H2 target summary: `final_metric`
- slices: `24`
- models: `1`

## Best final slices by metric
### `accuracy`
- `comp_sub_then_compare_gt` (composite): final=0.406, delta=0.203, AUC=0.277, status=usable_or_near_usable
- `ctrl_arith_digit_surface` (surface_control): final=0.391, delta=0.156, AUC=0.258, status=usable_or_near_usable
- `arith_min2` (atomic): final=0.359, delta=0.172, AUC=0.301, status=usable_or_near_usable
- `arith_compare_gt` (atomic): final=0.312, delta=0.047, AUC=0.297, status=usable_or_near_usable
- `comp_add_then_compare_lt` (composite): final=0.312, delta=0.016, AUC=0.254, status=usable_or_near_usable
- `arith_absdiff` (atomic): final=0.297, delta=0.109, AUC=0.270, status=weak_or_uninformative
- `arith_max2` (atomic): final=0.281, delta=0.031, AUC=0.266, status=weak_or_uninformative
- `comp_add_then_compare_gt` (composite): final=0.266, delta=0.062, AUC=0.227, status=weak_or_uninformative
### `mean_correct_margin`
- `ctrl_arith_word_surface` (surface_control): final=-0.125, delta=0.315, AUC=-0.672, status=usable_or_near_usable
- `arith_min2` (atomic): final=-0.195, delta=0.427, AUC=-0.591, status=usable_or_near_usable
- `ctrl_arith_digit_surface` (surface_control): final=-0.216, delta=0.577, AUC=-0.675, status=usable_or_near_usable
- `comp_absdiff_then_even` (composite): final=-0.223, delta=0.265, AUC=-0.522, status=usable_or_near_usable
- `arith_even` (atomic): final=-0.256, delta=0.322, AUC=-0.542, status=usable_or_near_usable
- `arith_compare_gt` (atomic): final=-0.261, delta=0.381, AUC=-0.521, status=usable_or_near_usable
- `comp_sub_then_odd` (composite): final=-0.265, delta=0.425, AUC=-0.498, status=usable_or_near_usable
- `comp_sub_then_compare_gt` (composite): final=-0.277, delta=0.400, AUC=-0.559, status=usable_or_near_usable
### `mean_correct_mrr`
- `ctrl_arith_digit_surface` (surface_control): final=0.609, delta=0.091, AUC=0.532, status=usable_or_near_usable
- `comp_sub_then_compare_gt` (composite): final=0.602, delta=0.105, AUC=0.534, status=usable_or_near_usable
- `arith_min2` (atomic): final=0.591, delta=0.116, AUC=0.555, status=usable_or_near_usable
- `arith_absdiff` (atomic): final=0.553, delta=0.085, AUC=0.539, status=usable_or_near_usable
- `arith_compare_gt` (atomic): final=0.552, delta=0.030, AUC=0.545, status=usable_or_near_usable
- `arith_add_small` (atomic): final=0.542, delta=0.043, AUC=0.517, status=usable_or_near_usable
- `comp_sub_then_odd` (composite): final=0.540, delta=0.066, AUC=0.517, status=usable_or_near_usable
- `comp_add_then_compare_lt` (composite): final=0.539, delta=-0.016, AUC=0.515, status=usable_or_near_usable
### `mean_logprob_correct`
- `ctrl_arith_word_surface` (surface_control): final=-1.716, delta=9.106, AUC=-4.707, status=usable_or_near_usable
- `ctrl_arith_digit_surface` (surface_control): final=-1.855, delta=9.081, AUC=-5.070, status=usable_or_near_usable
- `arith_min2` (atomic): final=-1.881, delta=9.233, AUC=-5.146, status=usable_or_near_usable
- `comp_sub_then_odd` (composite): final=-1.943, delta=9.051, AUC=-5.009, status=usable_or_near_usable
- `arith_max2` (atomic): final=-2.009, delta=9.077, AUC=-5.269, status=usable_or_near_usable
- `comp_sub_then_compare_gt` (composite): final=-2.061, delta=8.886, AUC=-5.126, status=usable_or_near_usable
- `comp_absdiff_then_even` (composite): final=-2.069, delta=8.866, AUC=-5.169, status=usable_or_near_usable
- `comp_double_then_compare_gt` (composite): final=-2.077, delta=8.958, AUC=-5.153, status=usable_or_near_usable
### `mean_logprob_margin`
- `arith_absdiff` (atomic): final=0.714, delta=0.401, AUC=0.692, status=usable_or_near_usable
- `arith_odd` (atomic): final=0.438, delta=0.107, AUC=0.366, status=usable_or_near_usable
- `arith_double` (atomic): final=0.405, delta=-0.020, AUC=0.635, status=usable_or_near_usable
- `arith_add_small` (atomic): final=0.330, delta=0.013, AUC=0.708, status=usable_or_near_usable
- `comp_add_then_even` (composite): final=0.325, delta=0.019, AUC=0.402, status=usable_or_near_usable
- `arith_sub_small` (atomic): final=0.308, delta=-0.033, AUC=0.668, status=usable_or_near_usable
- `comp_sub_then_odd` (composite): final=0.306, delta=-0.023, AUC=0.341, status=usable_or_near_usable
- `arith_max2` (atomic): final=0.259, delta=-0.011, AUC=0.804, status=usable_or_near_usable

## H1-like continuous signatures
- `EleutherAI/pythia-1.4b` / `accuracy`: mean_final=0.257, mean_delta=0.006, rho(freq, final)=0.091, rho(learn, final)=-0.086, rho(freq, delta)=0.066, rho(learn, delta)=-0.047
- `EleutherAI/pythia-1.4b` / `mean_correct_margin`: mean_final=-0.344, mean_delta=0.227, rho(freq, final)=-0.360, rho(learn, final)=0.327, rho(freq, delta)=-0.298, rho(learn, delta)=0.288
- `EleutherAI/pythia-1.4b` / `mean_correct_mrr`: mean_final=0.525, mean_delta=0.005, rho(freq, final)=0.014, rho(learn, final)=0.004, rho(freq, delta)=-0.003, rho(learn, delta)=0.039
- `EleutherAI/pythia-1.4b` / `mean_logprob_correct`: mean_final=-2.138, mean_delta=8.852, rho(freq, final)=-0.585, rho(learn, final)=0.513, rho(freq, delta)=-0.531, rho(learn, delta)=0.492
- `EleutherAI/pythia-1.4b` / `mean_logprob_margin`: mean_final=0.246, mean_delta=-0.080, rho(freq, final)=0.358, rho(learn, final)=-0.335, rho(freq, delta)=0.142, rho(learn, delta)=-0.144

## H2-like continuous residuals
- `accuracy`: n=10, mean residual=-0.179
  - underperforming composite `comp_absdiff_then_even`: residual=-0.240, observed=0.203, predicted=0.444
  - underperforming composite `comp_add_then_even`: residual=-0.234, observed=0.203, predicted=0.437
  - underperforming composite `comp_max_then_compare_gt`: residual=-0.224, observed=0.219, predicted=0.443
- `mean_correct_margin`: n=10, mean residual=-0.157
  - underperforming composite `comp_add_then_equals`: residual=-0.237, observed=-0.383, predicted=-0.146
  - underperforming composite `comp_add_then_even`: residual=-0.216, observed=-0.320, predicted=-0.103
  - underperforming composite `comp_add_then_compare_gt`: residual=-0.199, observed=-0.323, predicted=-0.124
- `mean_correct_mrr`: n=10, mean residual=-0.190
  - underperforming composite `comp_absdiff_then_even`: residual=-0.238, observed=0.487, predicted=0.725
  - underperforming composite `comp_add_then_even`: residual=-0.222, observed=0.492, predicted=0.714
  - underperforming composite `comp_min_then_compare_lt`: residual=-0.216, observed=0.505, predicted=0.722
- `mean_logprob_correct`: n=10, mean residual=-0.305
  - underperforming composite `comp_add_then_even`: residual=-0.391, observed=-2.082, predicted=-1.692
  - underperforming composite `comp_add_then_equals`: residual=-0.371, observed=-2.153, predicted=-1.782
  - underperforming composite `comp_add_then_compare_lt`: residual=-0.366, observed=-2.110, predicted=-1.744
- `mean_logprob_margin`: n=10, mean residual=-0.003
  - underperforming composite `comp_absdiff_then_even`: residual=-0.202, observed=0.084, predicted=0.286
  - underperforming composite `comp_max_then_compare_gt`: residual=-0.133, observed=0.089, predicted=0.222
  - underperforming composite `comp_min_then_compare_lt`: residual=-0.132, observed=0.090, predicted=0.222

## Component coupling
Component coupling compares composite continuous scores to the mean of its listed primitive slices. It is descriptive only.
- `accuracy` / `comp_absdiff_then_even`: composite_final=0.203, component_mean_final=0.266, diff=-0.062
- `accuracy` / `comp_add_then_compare_gt`: composite_final=0.266, component_mean_final=0.281, diff=-0.016
- `accuracy` / `comp_add_then_compare_lt`: composite_final=0.312, component_mean_final=0.234, diff=0.078
- `accuracy` / `comp_add_then_equals`: composite_final=0.266, component_mean_final=0.234, diff=0.031
- `accuracy` / `comp_add_then_even`: composite_final=0.203, component_mean_final=0.242, diff=-0.039
- `accuracy` / `comp_double_then_compare_gt`: composite_final=0.234, component_mean_final=0.273, diff=-0.039
- `accuracy` / `comp_max_then_compare_gt`: composite_final=0.219, component_mean_final=0.297, diff=-0.078
- `accuracy` / `comp_min_then_compare_lt`: composite_final=0.234, component_mean_final=0.289, diff=-0.055
- `accuracy` / `comp_sub_then_compare_gt`: composite_final=0.406, component_mean_final=0.281, diff=0.125
- `accuracy` / `comp_sub_then_odd`: composite_final=0.234, component_mean_final=0.234, diff=0.000

## Claim boundary
Use continuous-score outputs as calibration and observational bridge evidence only. They can show that a slice moves below top-1 accuracy, but they cannot establish causal dependency without interventions.
