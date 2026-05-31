# Pythia observational continuous-score analysis

This analysis is observational. Continuous scores can reveal subthreshold movement, but they do not establish causal dependency.

- metrics analyzed: `accuracy, mean_logprob_correct, mean_correct_margin, mean_correct_mrr, mean_logprob_margin`
- H2 target summary: `final_metric`
- slices: `29`
- models: `1`

## Best final slices by metric
### `accuracy`
- `comp_retrieve_then_compare` (composite): final=0.344, delta=0.094, AUC=0.289, status=usable_or_near_usable
- `comp_reverse_then_first` (composite): final=0.312, delta=-0.016, AUC=0.316, status=usable_or_near_usable
- `arith_compare` (atomic): final=0.312, delta=0.047, AUC=0.293, status=usable_or_near_usable
- `word_reverse2` (atomic): final=0.312, delta=0.109, AUC=0.285, status=usable_or_near_usable
- `ctrl_word_surface` (surface_control): final=0.297, delta=0.031, AUC=0.289, status=weak_or_uninformative
- `word_first` (atomic): final=0.297, delta=0.047, AUC=0.285, status=weak_or_uninformative
- `retrieval_number` (atomic): final=0.281, delta=0.000, AUC=0.266, status=weak_or_uninformative
- `comp_max_then_compare` (composite): final=0.281, delta=0.078, AUC=0.262, status=weak_or_uninformative
### `mean_correct_margin`
- `comp_add_then_even` (composite): final=-0.302, delta=0.421, AUC=-0.905, status=usable_or_near_usable
- `arith_compare` (atomic): final=-0.347, delta=0.373, AUC=-0.809, status=usable_or_near_usable
- `comp_max_then_compare` (composite): final=-0.365, delta=0.423, AUC=-0.840, status=usable_or_near_usable
- `comp_sub_then_compare` (composite): final=-0.406, delta=0.136, AUC=-0.884, status=usable_or_near_usable
- `comp_retrieve_then_compare` (composite): final=-0.412, delta=0.123, AUC=-0.699, status=usable_or_near_usable
- `comp_first_then_same` (composite): final=-0.468, delta=0.081, AUC=-0.812, status=usable_or_near_usable
- `comp_add_then_compare` (composite): final=-0.483, delta=0.025, AUC=-0.918, status=usable_or_near_usable
- `arith_even` (atomic): final=-0.502, delta=0.024, AUC=-0.994, status=usable_or_near_usable
### `mean_correct_mrr`
- `comp_retrieve_then_compare` (composite): final=0.591, delta=0.065, AUC=0.556, status=usable_or_near_usable
- `comp_max_then_compare` (composite): final=0.556, delta=0.069, AUC=0.539, status=usable_or_near_usable
- `arith_compare` (atomic): final=0.555, delta=0.035, AUC=0.543, status=usable_or_near_usable
- `word_first` (atomic): final=0.552, delta=0.043, AUC=0.540, status=usable_or_near_usable
- `word_reverse2` (atomic): final=0.552, delta=0.062, AUC=0.542, status=usable_or_near_usable
- `comp_first_then_same` (composite): final=0.548, delta=0.012, AUC=0.530, status=usable_or_near_usable
- `comp_reverse_then_first` (composite): final=0.548, delta=-0.012, AUC=0.555, status=usable_or_near_usable
- `ctrl_word_surface` (surface_control): final=0.542, delta=0.022, AUC=0.538, status=usable_or_near_usable
### `mean_logprob_correct`
- `semantic_animal_class` (atomic): final=-3.014, delta=7.883, AUC=-5.594, status=usable_or_near_usable
- `syntax_is_are` (atomic): final=-3.819, delta=7.145, AUC=-5.794, status=usable_or_near_usable
- `comp_retrieve_then_compare` (composite): final=-4.069, delta=6.701, AUC=-5.679, status=usable_or_near_usable
- `comp_reverse_then_same` (composite): final=-4.164, delta=6.933, AUC=-5.892, status=usable_or_near_usable
- `ctrl_retrieval_surface` (surface_control): final=-4.408, delta=6.626, AUC=-6.009, status=usable_or_near_usable
- `arith_even` (atomic): final=-4.436, delta=6.553, AUC=-6.074, status=usable_or_near_usable
- `comp_add_then_even` (composite): final=-4.469, delta=6.619, AUC=-6.049, status=usable_or_near_usable
- `retrieval_number` (atomic): final=-4.477, delta=6.229, AUC=-5.741, status=usable_or_near_usable
### `mean_logprob_margin`
- `retrieval_object` (atomic): final=1.581, delta=1.396, AUC=1.258, status=usable_or_near_usable
- `ctrl_retrieval_surface` (surface_control): final=1.561, delta=1.045, AUC=1.367, status=usable_or_near_usable
- `ctrl_word_surface` (surface_control): final=1.465, delta=0.892, AUC=1.290, status=usable_or_near_usable
- `comp_retrieve_then_color` (composite): final=1.420, delta=1.226, AUC=1.229, status=usable_or_near_usable
- `word_first` (atomic): final=1.313, delta=0.765, AUC=1.299, status=usable_or_near_usable
- `semantic_color_lookup` (atomic): final=1.287, delta=0.990, AUC=1.339, status=usable_or_near_usable
- `ctrl_number_surface` (surface_control): final=1.193, delta=0.975, AUC=1.234, status=usable_or_near_usable
- `word_last` (atomic): final=1.146, delta=0.655, AUC=1.215, status=usable_or_near_usable

## H1-like continuous signatures
- `EleutherAI/pythia-70m` / `accuracy`: mean_final=0.243, mean_delta=-0.010, rho(freq, final)=-0.267, rho(learn, final)=0.255, rho(freq, delta)=-0.112, rho(learn, delta)=0.099
- `EleutherAI/pythia-70m` / `mean_correct_margin`: mean_final=-0.771, mean_delta=-0.163, rho(freq, final)=-0.331, rho(learn, final)=0.349, rho(freq, delta)=-0.263, rho(learn, delta)=0.257
- `EleutherAI/pythia-70m` / `mean_correct_mrr`: mean_final=0.518, mean_delta=-0.006, rho(freq, final)=-0.292, rho(learn, final)=0.282, rho(freq, delta)=-0.132, rho(learn, delta)=0.111
- `EleutherAI/pythia-70m` / `mean_logprob_correct`: mean_final=-4.662, mean_delta=6.345, rho(freq, final)=-0.022, rho(learn, final)=0.103, rho(freq, delta)=0.026, rho(learn, delta)=0.007
- `EleutherAI/pythia-70m` / `mean_logprob_margin`: mean_final=0.669, mean_delta=0.201, rho(freq, final)=-0.040, rho(learn, final)=0.030, rho(freq, delta)=-0.129, rho(learn, delta)=0.134

## H2-like continuous residuals
- `accuracy`: n=10, mean residual=-0.032
  - underperforming composite `comp_add_then_compare`: residual=-0.107, observed=0.203, predicted=0.310
  - underperforming composite `comp_add_then_even`: residual=-0.072, observed=0.234, predicted=0.307
  - underperforming composite `comp_sub_then_compare`: residual=-0.071, observed=0.219, predicted=0.289
- `mean_correct_margin`: n=10, mean residual=0.480
  - underperforming composite `comp_retrieve_then_color`: residual=0.059, observed=-1.054, predicted=-1.113
  - underperforming composite `comp_reverse_then_first`: residual=0.096, observed=-0.987, predicted=-1.083
  - underperforming composite `comp_reverse_then_last`: residual=0.109, observed=-0.974, predicted=-1.083
- `mean_correct_mrr`: n=10, mean residual=-0.153
  - underperforming composite `comp_add_then_compare`: residual=-0.214, observed=0.484, predicted=0.698
  - underperforming composite `comp_sub_then_compare`: residual=-0.180, observed=0.503, predicted=0.683
  - underperforming composite `comp_add_then_even`: residual=-0.169, observed=0.529, predicted=0.697
- `mean_logprob_correct`: n=10, mean residual=2.703
  - underperforming composite `comp_reverse_then_first`: residual=2.074, observed=-5.339, predicted=-7.413
  - underperforming composite `comp_reverse_then_last`: residual=2.074, observed=-5.339, predicted=-7.413
  - underperforming composite `comp_add_then_compare`: residual=2.626, observed=-4.549, predicted=-7.175
- `mean_logprob_margin`: n=10, mean residual=-0.451
  - underperforming composite `comp_add_then_even`: residual=-0.922, observed=0.206, predicted=1.129
  - underperforming composite `comp_add_then_compare`: residual=-0.853, observed=0.256, predicted=1.108
  - underperforming composite `comp_sub_then_compare`: residual=-0.716, observed=0.344, predicted=1.060

## Component coupling
Component coupling compares composite continuous scores to the mean of its listed primitive slices. It is descriptive only.
- `accuracy` / `comp_add_then_compare`: composite_final=0.203, component_mean_final=0.242, diff=-0.039
- `accuracy` / `comp_add_then_even`: composite_final=0.234, component_mean_final=0.164, diff=0.070
- `accuracy` / `comp_first_then_same`: composite_final=0.266, component_mean_final=0.258, diff=0.008
- `accuracy` / `comp_max_then_compare`: composite_final=0.281, component_mean_final=0.234, diff=0.047
- `accuracy` / `comp_retrieve_then_color`: composite_final=0.250, component_mean_final=0.195, diff=0.055
- `accuracy` / `comp_retrieve_then_compare`: composite_final=0.344, component_mean_final=0.297, diff=0.047
- `accuracy` / `comp_reverse_then_first`: composite_final=0.312, component_mean_final=0.305, diff=0.008
- `accuracy` / `comp_reverse_then_last`: composite_final=0.250, component_mean_final=0.281, diff=-0.031
- `accuracy` / `comp_reverse_then_same`: composite_final=0.266, component_mean_final=0.266, diff=0.000
- `accuracy` / `comp_sub_then_compare`: composite_final=0.219, component_mean_final=0.273, diff=-0.055

## Claim boundary
Use continuous-score outputs as calibration and observational bridge evidence only. They can show that a slice moves below top-1 accuracy, but they cannot establish causal dependency without interventions.
