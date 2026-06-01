# Pythia observational continuous-score analysis

This analysis is observational. Continuous scores can reveal subthreshold movement, but they do not establish causal dependency.

- metrics analyzed: `accuracy, mean_logprob_correct, mean_correct_margin, mean_correct_mrr, mean_logprob_margin`
- H2 target summary: `final_metric`
- slices: `24`
- models: `1`

## Best final slices by metric
### `accuracy`
- `arith_compare_gt` (atomic): final=0.312, delta=0.078, AUC=0.285, status=usable_or_near_usable
- `comp_min_then_compare_lt` (composite): final=0.312, delta=0.078, AUC=0.285, status=usable_or_near_usable
- `comp_add_then_equals` (composite): final=0.297, delta=0.141, AUC=0.246, status=weak_or_uninformative
- `arith_absdiff` (atomic): final=0.297, delta=0.094, AUC=0.273, status=weak_or_uninformative
- `arith_sub_small` (atomic): final=0.281, delta=0.016, AUC=0.277, status=weak_or_uninformative
- `arith_max2` (atomic): final=0.266, delta=0.062, AUC=0.250, status=weak_or_uninformative
- `comp_sub_then_odd` (composite): final=0.250, delta=0.000, AUC=0.242, status=weak_or_uninformative
- `comp_add_then_compare_lt` (composite): final=0.250, delta=-0.016, AUC=0.230, status=weak_or_uninformative
### `mean_correct_margin`
- `comp_add_then_equals` (composite): final=-0.253, delta=0.501, AUC=-0.828, status=usable_or_near_usable
- `comp_double_then_compare_gt` (composite): final=-0.276, delta=0.390, AUC=-0.818, status=usable_or_near_usable
- `comp_min_then_compare_lt` (composite): final=-0.309, delta=0.427, AUC=-0.823, status=usable_or_near_usable
- `comp_add_then_even` (composite): final=-0.330, delta=0.405, AUC=-0.943, status=usable_or_near_usable
- `comp_sub_then_odd` (composite): final=-0.380, delta=0.212, AUC=-0.818, status=usable_or_near_usable
- `arith_compare_gt` (atomic): final=-0.416, delta=0.378, AUC=-0.806, status=usable_or_near_usable
- `arith_even` (atomic): final=-0.426, delta=0.330, AUC=-0.922, status=usable_or_near_usable
- `comp_add_then_compare_gt` (composite): final=-0.457, delta=0.136, AUC=-0.886, status=usable_or_near_usable
### `mean_correct_mrr`
- `comp_add_then_equals` (composite): final=0.565, delta=0.111, AUC=0.525, status=usable_or_near_usable
- `arith_compare_gt` (atomic): final=0.561, delta=0.065, AUC=0.542, status=usable_or_near_usable
- `comp_min_then_compare_lt` (composite): final=0.557, delta=0.066, AUC=0.541, status=usable_or_near_usable
- `arith_absdiff` (atomic): final=0.552, delta=0.077, AUC=0.540, status=usable_or_near_usable
- `arith_max2` (atomic): final=0.548, delta=0.052, AUC=0.532, status=usable_or_near_usable
- `comp_double_then_compare_gt` (composite): final=0.543, delta=0.013, AUC=0.530, status=usable_or_near_usable
- `arith_sub_small` (atomic): final=0.540, delta=0.009, AUC=0.539, status=usable_or_near_usable
- `comp_absdiff_then_even` (composite): final=0.533, delta=0.033, AUC=0.520, status=usable_or_near_usable
### `mean_logprob_correct`
- `ctrl_arith_word_surface` (surface_control): final=-3.812, delta=7.225, AUC=-5.633, status=usable_or_near_usable
- `comp_double_then_compare_gt` (composite): final=-4.265, delta=6.759, AUC=-5.924, status=usable_or_near_usable
- `arith_double` (atomic): final=-4.383, delta=6.634, AUC=-5.794, status=usable_or_near_usable
- `arith_even` (atomic): final=-4.415, delta=6.723, AUC=-6.042, status=usable_or_near_usable
- `arith_odd` (atomic): final=-4.423, delta=6.649, AUC=-6.058, status=usable_or_near_usable
- `comp_add_then_equals` (composite): final=-4.510, delta=6.635, AUC=-6.044, status=usable_or_near_usable
- `comp_sub_then_odd` (composite): final=-4.549, delta=6.558, AUC=-6.037, status=usable_or_near_usable
- `comp_add_then_even` (composite): final=-4.569, delta=6.544, AUC=-6.112, status=usable_or_near_usable
### `mean_logprob_margin`
- `ctrl_arith_digit_surface` (surface_control): final=1.287, delta=0.888, AUC=1.200, status=usable_or_near_usable
- `arith_absdiff` (atomic): final=0.958, delta=0.535, AUC=1.303, status=usable_or_near_usable
- `arith_add_large` (atomic): final=0.817, delta=0.246, AUC=1.353, status=usable_or_near_usable
- `arith_double` (atomic): final=0.773, delta=0.191, AUC=1.344, status=usable_or_near_usable
- `arith_sub_small` (atomic): final=0.771, delta=0.261, AUC=1.387, status=usable_or_near_usable
- `comp_absdiff_then_even` (composite): final=0.646, delta=0.153, AUC=1.090, status=usable_or_near_usable
- `arith_add_small` (atomic): final=0.620, delta=0.047, AUC=1.323, status=usable_or_near_usable
- `comp_max_then_compare_gt` (composite): final=0.530, delta=-0.074, AUC=1.082, status=usable_or_near_usable

## H1-like continuous signatures
- `EleutherAI/pythia-70m` / `accuracy`: mean_final=0.241, mean_delta=0.001, rho(freq, final)=-0.256, rho(learn, final)=0.315, rho(freq, delta)=-0.363, rho(learn, delta)=0.419
- `EleutherAI/pythia-70m` / `mean_correct_margin`: mean_final=-0.532, mean_delta=0.173, rho(freq, final)=-0.590, rho(learn, final)=0.529, rho(freq, delta)=-0.568, rho(learn, delta)=0.489
- `EleutherAI/pythia-70m` / `mean_correct_mrr`: mean_final=0.519, mean_delta=0.003, rho(freq, final)=-0.450, rho(learn, final)=0.465, rho(freq, delta)=-0.479, rho(learn, delta)=0.512
- `EleutherAI/pythia-70m` / `mean_logprob_correct`: mean_final=-4.744, mean_delta=6.359, rho(freq, final)=-0.307, rho(learn, final)=0.226, rho(freq, delta)=-0.362, rho(learn, delta)=0.312
- `EleutherAI/pythia-70m` / `mean_logprob_margin`: mean_final=0.479, mean_delta=-0.046, rho(freq, final)=0.109, rho(learn, final)=-0.022, rho(freq, delta)=-0.028, rho(learn, delta)=0.111

## H2-like continuous residuals
- `accuracy`: n=10, mean residual=0.142
  - underperforming composite `comp_add_then_even`: residual=0.110, observed=0.203, predicted=0.093
  - underperforming composite `comp_max_then_compare_gt`: residual=0.116, observed=0.234, predicted=0.118
  - underperforming composite `comp_absdiff_then_even`: residual=0.118, observed=0.250, predicted=0.132
- `mean_correct_margin`: n=10, mean residual=-1.143
  - underperforming composite `comp_add_then_compare_gt`: residual=-1.330, observed=-0.457, predicted=0.873
  - underperforming composite `comp_add_then_compare_lt`: residual=-1.312, observed=-0.473, predicted=0.839
  - underperforming composite `comp_add_then_even`: residual=-1.223, observed=-0.330, predicted=0.893
- `mean_correct_mrr`: n=10, mean residual=-0.087
  - underperforming composite `comp_sub_then_compare_gt`: residual=-0.103, observed=0.510, predicted=0.614
  - underperforming composite `comp_max_then_compare_gt`: residual=-0.102, observed=0.521, predicted=0.623
  - underperforming composite `comp_add_then_even`: residual=-0.102, observed=0.508, predicted=0.609
- `mean_logprob_correct`: n=10, mean residual=1.746
  - underperforming composite `comp_add_then_compare_lt`: residual=1.482, observed=-4.730, predicted=-6.212
  - underperforming composite `comp_add_then_compare_gt`: residual=1.537, observed=-4.621, predicted=-6.158
  - underperforming composite `comp_sub_then_compare_gt`: residual=1.603, observed=-4.721, predicted=-6.323
- `mean_logprob_margin`: n=10, mean residual=1.103
  - underperforming composite `comp_add_then_equals`: residual=1.006, observed=0.362, predicted=-0.644
  - underperforming composite `comp_sub_then_compare_gt`: residual=1.027, observed=0.388, predicted=-0.639
  - underperforming composite `comp_sub_then_odd`: residual=1.047, observed=0.405, predicted=-0.642

## Component coupling
Component coupling compares composite continuous scores to the mean of its listed primitive slices. It is descriptive only.
- `accuracy` / `comp_absdiff_then_even`: composite_final=0.250, component_mean_final=0.258, diff=-0.008
- `accuracy` / `comp_add_then_compare_gt`: composite_final=0.219, component_mean_final=0.273, diff=-0.055
- `accuracy` / `comp_add_then_compare_lt`: composite_final=0.250, component_mean_final=0.227, diff=0.023
- `accuracy` / `comp_add_then_equals`: composite_final=0.297, component_mean_final=0.195, diff=0.102
- `accuracy` / `comp_add_then_even`: composite_final=0.203, component_mean_final=0.227, diff=-0.023
- `accuracy` / `comp_double_then_compare_gt`: composite_final=0.234, component_mean_final=0.273, diff=-0.039
- `accuracy` / `comp_max_then_compare_gt`: composite_final=0.234, component_mean_final=0.289, diff=-0.055
- `accuracy` / `comp_min_then_compare_lt`: composite_final=0.312, component_mean_final=0.172, diff=0.141
- `accuracy` / `comp_sub_then_compare_gt`: composite_final=0.250, component_mean_final=0.297, diff=-0.047
- `accuracy` / `comp_sub_then_odd`: composite_final=0.250, component_mean_final=0.250, diff=0.000

## Claim boundary
Use continuous-score outputs as calibration and observational bridge evidence only. They can show that a slice moves below top-1 accuracy, but they cannot establish causal dependency without interventions.
