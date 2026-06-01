# Pythia observational continuous-score analysis

This analysis is observational. Continuous scores can reveal subthreshold movement, but they do not establish causal dependency.

- metrics analyzed: `accuracy, mean_logprob_correct, mean_correct_margin, mean_correct_mrr, mean_logprob_margin`
- H2 target summary: `final_metric`
- slices: `24`
- models: `1`

## Best final slices by metric
### `accuracy`
- `arith_min2` (atomic): final=0.328, delta=0.000, AUC=0.328, status=usable_or_near_usable
- `arith_absdiff` (atomic): final=0.297, delta=0.000, AUC=0.297, status=weak_or_uninformative
- `comp_min_then_compare_lt` (composite): final=0.297, delta=0.000, AUC=0.297, status=weak_or_uninformative
- `arith_compare_gt` (atomic): final=0.297, delta=0.078, AUC=0.277, status=weak_or_uninformative
- `arith_sub_small` (atomic): final=0.281, delta=0.000, AUC=0.281, status=weak_or_uninformative
- `arith_max2` (atomic): final=0.266, delta=0.016, AUC=0.262, status=weak_or_uninformative
- `comp_add_then_equals` (composite): final=0.266, delta=0.094, AUC=0.242, status=weak_or_uninformative
- `comp_absdiff_then_even` (composite): final=0.250, delta=0.000, AUC=0.250, status=weak_or_uninformative
### `mean_correct_margin`
- `arith_absdiff` (atomic): final=-1.146, delta=-0.752, AUC=-0.762, status=usable_or_near_usable
- `ctrl_arith_word_surface` (surface_control): final=-1.207, delta=-0.538, AUC=-1.002, status=usable_or_near_usable
- `arith_min2` (atomic): final=-1.246, delta=-0.883, AUC=-0.772, status=usable_or_near_usable
- `comp_absdiff_then_even` (composite): final=-1.345, delta=-0.665, AUC=-0.916, status=usable_or_near_usable
- `arith_max2` (atomic): final=-1.409, delta=-0.958, AUC=-0.920, status=usable_or_near_usable
- `arith_double` (atomic): final=-1.457, delta=-1.038, AUC=-0.943, status=usable_or_near_usable
- `comp_min_then_compare_lt` (composite): final=-1.490, delta=-0.892, AUC=-0.856, status=usable_or_near_usable
- `arith_compare_gt` (atomic): final=-1.496, delta=-1.040, AUC=-0.829, status=usable_or_near_usable
### `mean_correct_mrr`
- `arith_min2` (atomic): final=0.568, delta=-0.010, AUC=0.573, status=usable_or_near_usable
- `arith_absdiff` (atomic): final=0.559, delta=-0.009, AUC=0.565, status=usable_or_near_usable
- `arith_compare_gt` (atomic): final=0.553, delta=0.049, AUC=0.544, status=usable_or_near_usable
- `comp_min_then_compare_lt` (composite): final=0.543, delta=0.008, AUC=0.548, status=usable_or_near_usable
- `arith_sub_small` (atomic): final=0.539, delta=-0.014, AUC=0.544, status=usable_or_near_usable
- `comp_add_then_equals` (composite): final=0.539, delta=0.078, AUC=0.517, status=usable_or_near_usable
- `arith_max2` (atomic): final=0.535, delta=0.007, AUC=0.531, status=usable_or_near_usable
- `comp_sub_then_compare_gt` (composite): final=0.526, delta=-0.064, AUC=0.542, status=usable_or_near_usable
### `mean_logprob_correct`
- `ctrl_arith_word_surface` (surface_control): final=-3.337, delta=8.233, AUC=-5.718, status=usable_or_near_usable
- `ctrl_arith_digit_surface` (surface_control): final=-3.561, delta=7.843, AUC=-6.061, status=usable_or_near_usable
- `arith_min2` (atomic): final=-3.582, delta=7.665, AUC=-5.933, status=usable_or_near_usable
- `comp_max_then_compare_gt` (composite): final=-3.768, delta=7.471, AUC=-6.194, status=usable_or_near_usable
- `comp_min_then_compare_lt` (composite): final=-3.799, delta=7.551, AUC=-6.164, status=usable_or_near_usable
- `comp_double_then_compare_gt` (composite): final=-3.879, delta=7.335, AUC=-6.122, status=usable_or_near_usable
- `comp_absdiff_then_even` (composite): final=-3.927, delta=7.588, AUC=-6.237, status=usable_or_near_usable
- `arith_compare_gt` (atomic): final=-3.941, delta=7.381, AUC=-6.214, status=usable_or_near_usable
### `mean_logprob_margin`
- `arith_add_small` (atomic): final=2.759, delta=2.515, AUC=1.305, status=usable_or_near_usable
- `arith_sub_small` (atomic): final=2.638, delta=2.324, AUC=1.230, status=usable_or_near_usable
- `arith_add_large` (atomic): final=2.555, delta=2.195, AUC=1.293, status=usable_or_near_usable
- `arith_double` (atomic): final=2.286, delta=2.060, AUC=1.249, status=usable_or_near_usable
- `arith_min2` (atomic): final=2.161, delta=1.878, AUC=1.170, status=usable_or_near_usable
- `comp_add_then_equals` (composite): final=2.093, delta=2.040, AUC=0.992, status=usable_or_near_usable
- `arith_odd` (atomic): final=2.061, delta=2.014, AUC=0.969, status=usable_or_near_usable
- `comp_add_then_compare_lt` (composite): final=1.952, delta=1.882, AUC=0.886, status=usable_or_near_usable

## H1-like continuous signatures
- `EleutherAI/pythia-160m` / `accuracy`: mean_final=0.245, mean_delta=-0.010, rho(freq, final)=-0.150, rho(learn, final)=0.206, rho(freq, delta)=-0.005, rho(learn, delta)=-0.010
- `EleutherAI/pythia-160m` / `mean_correct_margin`: mean_final=-1.633, mean_delta=-1.186, rho(freq, final)=-0.118, rho(learn, final)=0.150, rho(freq, delta)=-0.219, rho(learn, delta)=0.254
- `EleutherAI/pythia-160m` / `mean_correct_mrr`: mean_final=0.521, mean_delta=-0.004, rho(freq, final)=-0.232, rho(learn, final)=0.288, rho(freq, delta)=-0.141, rho(learn, delta)=0.106
- `EleutherAI/pythia-160m` / `mean_logprob_correct`: mean_final=-4.157, mean_delta=7.165, rho(freq, final)=-0.568, rho(learn, final)=0.530, rho(freq, delta)=-0.526, rho(learn, delta)=0.490
- `EleutherAI/pythia-160m` / `mean_logprob_margin`: mean_final=1.996, mean_delta=1.829, rho(freq, final)=0.308, rho(learn, final)=-0.302, rho(freq, delta)=0.350, rho(learn, delta)=-0.365

## H2-like continuous residuals
- `accuracy`: n=10, mean residual=-0.102
  - underperforming composite `comp_add_then_even`: residual=-0.128, observed=0.203, predicted=0.331
  - underperforming composite `comp_add_then_compare_lt`: residual=-0.119, observed=0.203, predicted=0.322
  - underperforming composite `comp_max_then_compare_gt`: residual=-0.118, observed=0.234, predicted=0.352
- `mean_correct_margin`: n=10, mean residual=-0.152
  - underperforming composite `comp_add_then_equals`: residual=-0.329, observed=-1.789, predicted=-1.460
  - underperforming composite `comp_add_then_compare_lt`: residual=-0.270, observed=-1.947, predicted=-1.677
  - underperforming composite `comp_max_then_compare_gt`: residual=-0.198, observed=-1.658, predicted=-1.460
- `mean_correct_mrr`: n=10, mean residual=-0.209
  - underperforming composite `comp_add_then_compare_lt`: residual=-0.226, observed=0.488, predicted=0.714
  - underperforming composite `comp_absdiff_then_even`: residual=-0.222, observed=0.518, predicted=0.741
  - underperforming composite `comp_add_then_even`: residual=-0.219, observed=0.503, predicted=0.721
- `mean_logprob_correct`: n=10, mean residual=-0.833
  - underperforming composite `comp_add_then_even`: residual=-1.228, observed=-4.345, predicted=-3.117
  - underperforming composite `comp_add_then_compare_lt`: residual=-1.088, observed=-4.312, predicted=-3.224
  - underperforming composite `comp_add_then_compare_gt`: residual=-0.964, observed=-4.189, predicted=-3.226
- `mean_logprob_margin`: n=10, mean residual=1.793
  - underperforming composite `comp_absdiff_then_even`: residual=1.236, observed=1.493, predicted=0.256
  - underperforming composite `comp_max_then_compare_gt`: residual=1.496, observed=1.603, predicted=0.107
  - underperforming composite `comp_min_then_compare_lt`: residual=1.671, observed=1.778, predicted=0.107

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
