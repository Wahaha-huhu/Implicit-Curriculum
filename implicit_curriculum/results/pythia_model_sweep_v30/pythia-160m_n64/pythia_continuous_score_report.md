# Pythia observational continuous-score analysis

This analysis is observational. Continuous scores can reveal subthreshold movement, but they do not establish causal dependency.

- metrics analyzed: `accuracy, mean_logprob_correct, mean_correct_margin, mean_correct_mrr, mean_logprob_margin`
- H2 target summary: `final_metric`
- slices: `29`
- models: `1`

## Best final slices by metric
### `accuracy`
- `comp_reverse_then_first` (composite): final=0.312, delta=0.156, AUC=0.270, status=usable_or_near_usable
- `word_reverse2` (atomic): final=0.312, delta=0.000, AUC=0.309, status=usable_or_near_usable
- `arith_compare` (atomic): final=0.297, delta=0.062, AUC=0.281, status=weak_or_uninformative
- `ctrl_word_surface` (surface_control): final=0.297, delta=0.000, AUC=0.297, status=weak_or_uninformative
- `word_first` (atomic): final=0.297, delta=0.000, AUC=0.305, status=usable_or_near_usable
- `comp_retrieve_then_compare` (composite): final=0.281, delta=0.000, AUC=0.281, status=weak_or_uninformative
- `comp_max_then_compare` (composite): final=0.281, delta=-0.016, AUC=0.285, status=weak_or_uninformative
- `comp_reverse_then_same` (composite): final=0.266, delta=0.000, AUC=0.262, status=weak_or_uninformative
### `mean_correct_margin`
- `word_reverse2` (atomic): final=-0.867, delta=-0.568, AUC=-0.558, status=usable_or_near_usable
- `comp_reverse_then_first` (composite): final=-0.876, delta=-0.385, AUC=-0.680, status=usable_or_near_usable
- `comp_reverse_then_same` (composite): final=-0.964, delta=-0.410, AUC=-0.724, status=usable_or_near_usable
- `comp_reverse_then_last` (composite): final=-1.027, delta=-0.447, AUC=-0.738, status=usable_or_near_usable
- `word_first` (atomic): final=-1.049, delta=-0.655, AUC=-0.708, status=usable_or_near_usable
- `word_copy` (atomic): final=-1.086, delta=-0.665, AUC=-0.697, status=usable_or_near_usable
- `word_last` (atomic): final=-1.178, delta=-0.731, AUC=-0.810, status=usable_or_near_usable
- `ctrl_word_surface` (surface_control): final=-1.204, delta=-0.808, AUC=-0.907, status=usable_or_near_usable
### `mean_correct_mrr`
- `word_first` (atomic): final=0.553, delta=-0.003, AUC=0.556, status=usable_or_near_usable
- `ctrl_word_surface` (surface_control): final=0.552, delta=-0.001, AUC=0.554, status=usable_or_near_usable
- `arith_compare` (atomic): final=0.548, delta=0.022, AUC=0.542, status=usable_or_near_usable
- `arith_min2` (atomic): final=0.546, delta=0.016, AUC=0.532, status=usable_or_near_usable
- `comp_retrieve_then_compare` (composite): final=0.546, delta=-0.003, AUC=0.550, status=usable_or_near_usable
- `comp_reverse_then_first` (composite): final=0.544, delta=0.072, AUC=0.528, status=usable_or_near_usable
- `comp_max_then_compare` (composite): final=0.543, delta=-0.001, AUC=0.546, status=usable_or_near_usable
- `word_reverse2` (atomic): final=0.542, delta=-0.033, AUC=0.558, status=usable_or_near_usable
### `mean_logprob_correct`
- `semantic_animal_class` (atomic): final=-2.697, delta=8.537, AUC=-5.198, status=usable_or_near_usable
- `syntax_is_are` (atomic): final=-3.256, delta=7.995, AUC=-5.761, status=usable_or_near_usable
- `comp_max_then_compare` (composite): final=-3.625, delta=7.675, AUC=-6.149, status=usable_or_near_usable
- `ctrl_word_surface` (surface_control): final=-3.643, delta=7.614, AUC=-5.775, status=usable_or_near_usable
- `ctrl_retrieval_surface` (surface_control): final=-3.804, delta=7.743, AUC=-5.672, status=usable_or_near_usable
- `arith_min2` (atomic): final=-3.839, delta=7.507, AUC=-6.117, status=usable_or_near_usable
- `semantic_color_lookup` (atomic): final=-3.852, delta=7.421, AUC=-6.080, status=usable_or_near_usable
- `comp_retrieve_then_color` (composite): final=-3.855, delta=7.436, AUC=-5.976, status=usable_or_near_usable
### `mean_logprob_margin`
- `retrieval_object` (atomic): final=2.874, delta=2.729, AUC=1.632, status=usable_or_near_usable
- `arith_add_small` (atomic): final=2.803, delta=2.598, AUC=1.342, status=usable_or_near_usable
- `arith_sub_small` (atomic): final=2.644, delta=2.412, AUC=1.232, status=usable_or_near_usable
- `retrieval_number` (atomic): final=2.381, delta=2.227, AUC=1.495, status=usable_or_near_usable
- `arith_min2` (atomic): final=2.370, delta=2.130, AUC=1.166, status=usable_or_near_usable
- `comp_retrieve_then_color` (composite): final=2.156, delta=1.568, AUC=1.511, status=usable_or_near_usable
- `comp_add_then_even` (composite): final=2.105, delta=2.034, AUC=1.012, status=usable_or_near_usable
- `ctrl_retrieval_surface` (surface_control): final=2.079, delta=1.853, AUC=1.079, status=usable_or_near_usable

## H1-like continuous signatures
- `EleutherAI/pythia-160m` / `accuracy`: mean_final=0.239, mean_delta=0.001, rho(freq, final)=-0.265, rho(learn, final)=0.232, rho(freq, delta)=-0.149, rho(learn, delta)=0.108
- `EleutherAI/pythia-160m` / `mean_correct_margin`: mean_final=-1.500, mean_delta=-1.023, rho(freq, final)=-0.150, rho(learn, final)=0.062, rho(freq, delta)=-0.214, rho(learn, delta)=0.100
- `EleutherAI/pythia-160m` / `mean_correct_mrr`: mean_final=0.511, mean_delta=-0.003, rho(freq, final)=-0.146, rho(learn, final)=0.130, rho(freq, delta)=-0.167, rho(learn, delta)=0.063
- `EleutherAI/pythia-160m` / `mean_logprob_correct`: mean_final=-4.210, mean_delta=7.069, rho(freq, final)=-0.063, rho(learn, final)=0.019, rho(freq, delta)=-0.067, rho(learn, delta)=0.005
- `EleutherAI/pythia-160m` / `mean_logprob_margin`: mean_final=1.866, mean_delta=1.666, rho(freq, final)=0.095, rho(learn, final)=-0.018, rho(freq, delta)=0.054, rho(learn, delta)=0.032

## H2-like continuous residuals
- `accuracy`: n=10, mean residual=-0.068
  - underperforming composite `comp_add_then_compare`: residual=-0.125, observed=0.203, predicted=0.328
  - underperforming composite `comp_add_then_even`: residual=-0.124, observed=0.203, predicted=0.327
  - underperforming composite `comp_sub_then_compare`: residual=-0.109, observed=0.203, predicted=0.312
- `mean_correct_margin`: n=10, mean residual=-0.249
  - underperforming composite `comp_add_then_compare`: residual=-0.969, observed=-2.043, predicted=-1.073
  - underperforming composite `comp_sub_then_compare`: residual=-0.698, observed=-1.959, predicted=-1.261
  - underperforming composite `comp_add_then_even`: residual=-0.695, observed=-1.792, predicted=-1.096
- `mean_correct_mrr`: n=10, mean residual=-0.196
  - underperforming composite `comp_add_then_compare`: residual=-0.244, observed=0.474, predicted=0.718
  - underperforming composite `comp_first_then_same`: residual=-0.219, observed=0.510, predicted=0.729
  - underperforming composite `comp_reverse_then_last`: residual=-0.216, observed=0.503, predicted=0.719
- `mean_logprob_correct`: n=10, mean residual=0.056
  - underperforming composite `comp_reverse_then_last`: residual=-0.532, observed=-4.777, predicted=-4.245
  - underperforming composite `comp_reverse_then_first`: residual=-0.385, observed=-4.631, predicted=-4.245
  - underperforming composite `comp_add_then_compare`: residual=-0.257, observed=-4.367, predicted=-4.110
- `mean_logprob_margin`: n=10, mean residual=0.171
  - underperforming composite `comp_reverse_then_same`: residual=-0.490, observed=1.248, predicted=1.738
  - underperforming composite `comp_reverse_then_last`: residual=-0.107, observed=1.408, predicted=1.515
  - underperforming composite `comp_retrieve_then_compare`: residual=-0.079, observed=1.972, predicted=2.051

## Component coupling
Component coupling compares composite continuous scores to the mean of its listed primitive slices. It is descriptive only.
- `accuracy` / `comp_add_then_compare`: composite_final=0.203, component_mean_final=0.234, diff=-0.031
- `accuracy` / `comp_add_then_even`: composite_final=0.203, component_mean_final=0.180, diff=0.023
- `accuracy` / `comp_first_then_same`: composite_final=0.250, component_mean_final=0.258, diff=-0.008
- `accuracy` / `comp_max_then_compare`: composite_final=0.281, component_mean_final=0.219, diff=0.062
- `accuracy` / `comp_retrieve_then_color`: composite_final=0.250, component_mean_final=0.195, diff=0.055
- `accuracy` / `comp_retrieve_then_compare`: composite_final=0.281, component_mean_final=0.273, diff=0.008
- `accuracy` / `comp_reverse_then_first`: composite_final=0.312, component_mean_final=0.305, diff=0.008
- `accuracy` / `comp_reverse_then_last`: composite_final=0.250, component_mean_final=0.281, diff=-0.031
- `accuracy` / `comp_reverse_then_same`: composite_final=0.266, component_mean_final=0.266, diff=0.000
- `accuracy` / `comp_sub_then_compare`: composite_final=0.203, component_mean_final=0.266, diff=-0.062

## Claim boundary
Use continuous-score outputs as calibration and observational bridge evidence only. They can show that a slice moves below top-1 accuracy, but they cannot establish causal dependency without interventions.
