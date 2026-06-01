# Pythia observational continuous-score analysis

This analysis is observational. Continuous scores can reveal subthreshold movement, but they do not establish causal dependency.

- metrics analyzed: `accuracy, mean_logprob_correct, mean_correct_margin, mean_correct_mrr, mean_logprob_margin`
- H2 target summary: `final_metric`
- slices: `29`
- models: `1`

## Best final slices by metric
### `accuracy`
- `ctrl_number_surface` (surface_control): final=0.562, delta=0.000, AUC=0.562, status=usable_or_near_usable
- `arith_even` (atomic): final=0.438, delta=0.000, AUC=0.438, status=usable_or_near_usable
- `comp_add_then_compare` (composite): final=0.438, delta=0.000, AUC=0.438, status=usable_or_near_usable
- `comp_reverse_then_first` (composite): final=0.375, delta=0.000, AUC=0.375, status=usable_or_near_usable
- `word_first` (atomic): final=0.375, delta=0.000, AUC=0.375, status=usable_or_near_usable
- `comp_sub_then_compare` (composite): final=0.375, delta=0.000, AUC=0.375, status=usable_or_near_usable
- `comp_add_then_even` (composite): final=0.375, delta=0.000, AUC=0.375, status=usable_or_near_usable
- `comp_reverse_then_last` (composite): final=0.375, delta=0.000, AUC=0.375, status=usable_or_near_usable
### `mean_correct_margin`
- `ctrl_number_surface` (surface_control): final=0.011, delta=0.000, AUC=0.011, status=weak_or_uninformative
- `comp_add_then_compare` (composite): final=0.006, delta=0.000, AUC=0.006, status=weak_or_uninformative
- `arith_compare` (atomic): final=-0.060, delta=0.000, AUC=-0.060, status=weak_or_uninformative
- `arith_even` (atomic): final=-0.068, delta=0.000, AUC=-0.068, status=weak_or_uninformative
- `comp_add_then_even` (composite): final=-0.071, delta=0.000, AUC=-0.071, status=weak_or_uninformative
- `comp_max_then_compare` (composite): final=-0.088, delta=0.000, AUC=-0.088, status=weak_or_uninformative
- `comp_retrieve_then_color` (composite): final=-0.091, delta=0.000, AUC=-0.091, status=weak_or_uninformative
- `comp_sub_then_compare` (composite): final=-0.101, delta=0.000, AUC=-0.101, status=weak_or_uninformative
### `mean_correct_mrr`
- `ctrl_number_surface` (surface_control): final=0.734, delta=0.000, AUC=0.734, status=usable_or_near_usable
- `comp_add_then_compare` (composite): final=0.667, delta=0.000, AUC=0.667, status=usable_or_near_usable
- `arith_even` (atomic): final=0.630, delta=0.000, AUC=0.630, status=usable_or_near_usable
- `semantic_animal_class` (atomic): final=0.625, delta=0.000, AUC=0.625, status=usable_or_near_usable
- `comp_add_then_even` (composite): final=0.615, delta=0.000, AUC=0.615, status=usable_or_near_usable
- `comp_reverse_then_last` (composite): final=0.615, delta=0.000, AUC=0.615, status=usable_or_near_usable
- `arith_compare` (atomic): final=0.615, delta=0.000, AUC=0.615, status=usable_or_near_usable
- `comp_sub_then_compare` (composite): final=0.609, delta=0.000, AUC=0.609, status=usable_or_near_usable
### `mean_logprob_correct`
- `semantic_animal_class` (atomic): final=-1.623, delta=0.000, AUC=-1.623, status=weak_or_uninformative
- `ctrl_retrieval_surface` (surface_control): final=-1.709, delta=0.000, AUC=-1.709, status=weak_or_uninformative
- `retrieval_object` (atomic): final=-1.729, delta=0.000, AUC=-1.729, status=weak_or_uninformative
- `ctrl_number_surface` (surface_control): final=-1.734, delta=0.000, AUC=-1.734, status=weak_or_uninformative
- `comp_retrieve_then_color` (composite): final=-1.768, delta=0.000, AUC=-1.768, status=weak_or_uninformative
- `word_reverse2` (atomic): final=-1.813, delta=0.000, AUC=-1.813, status=weak_or_uninformative
- `word_same` (atomic): final=-1.866, delta=0.000, AUC=-1.866, status=weak_or_uninformative
- `retrieval_number` (atomic): final=-1.890, delta=0.000, AUC=-1.890, status=weak_or_uninformative
### `mean_logprob_margin`
- `semantic_animal_class` (atomic): final=0.568, delta=0.000, AUC=0.568, status=weak_or_uninformative
- `ctrl_number_surface` (surface_control): final=0.331, delta=0.000, AUC=0.331, status=weak_or_uninformative
- `syntax_is_are` (atomic): final=0.322, delta=0.000, AUC=0.322, status=weak_or_uninformative
- `retrieval_number` (atomic): final=0.284, delta=0.000, AUC=0.284, status=weak_or_uninformative
- `arith_sub_small` (atomic): final=0.260, delta=0.000, AUC=0.260, status=weak_or_uninformative
- `comp_reverse_then_same` (composite): final=0.244, delta=0.000, AUC=0.244, status=weak_or_uninformative
- `word_reverse2` (atomic): final=0.239, delta=0.000, AUC=0.239, status=weak_or_uninformative
- `arith_max2` (atomic): final=0.221, delta=0.000, AUC=0.221, status=weak_or_uninformative

## H1-like continuous signatures
- `EleutherAI/pythia-2.8b` / `accuracy`: mean_final=0.291, mean_delta=0.000, rho(freq, final)=-0.209, rho(learn, final)=0.200, rho(freq, delta)=nan, rho(learn, delta)=nan
- `EleutherAI/pythia-2.8b` / `mean_correct_margin`: mean_final=-0.205, mean_delta=0.000, rho(freq, final)=-0.470, rho(learn, final)=0.440, rho(freq, delta)=nan, rho(learn, delta)=nan
- `EleutherAI/pythia-2.8b` / `mean_correct_mrr`: mean_final=0.553, mean_delta=0.000, rho(freq, final)=-0.172, rho(learn, final)=0.148, rho(freq, delta)=nan, rho(learn, delta)=nan
- `EleutherAI/pythia-2.8b` / `mean_logprob_correct`: mean_final=-1.973, mean_delta=0.000, rho(freq, final)=0.229, rho(learn, final)=-0.228, rho(freq, delta)=nan, rho(learn, delta)=nan
- `EleutherAI/pythia-2.8b` / `mean_logprob_margin`: mean_final=0.196, mean_delta=0.000, rho(freq, final)=0.257, rho(learn, final)=-0.196, rho(freq, delta)=nan, rho(learn, delta)=nan

## H2-like continuous residuals
- `accuracy`: n=10, mean residual=-0.119
  - underperforming composite `comp_first_then_same`: residual=-0.270, observed=0.188, predicted=0.458
  - underperforming composite `comp_retrieve_then_color`: residual=-0.256, observed=0.188, predicted=0.444
  - underperforming composite `comp_max_then_compare`: residual=-0.189, observed=0.250, predicted=0.439
- `mean_correct_margin`: n=10, mean residual=-0.175
  - underperforming composite `comp_first_then_same`: residual=-0.391, observed=-0.248, predicted=0.143
  - underperforming composite `comp_reverse_then_first`: residual=-0.277, observed=-0.188, predicted=0.090
  - underperforming composite `comp_reverse_then_same`: residual=-0.224, observed=-0.187, predicted=0.037
- `mean_correct_mrr`: n=10, mean residual=-0.223
  - underperforming composite `comp_first_then_same`: residual=-0.315, observed=0.505, predicted=0.820
  - underperforming composite `comp_retrieve_then_color`: residual=-0.279, observed=0.521, predicted=0.800
  - underperforming composite `comp_max_then_compare`: residual=-0.267, observed=0.531, predicted=0.798
- `mean_logprob_correct`: n=10, mean residual=0.031
  - underperforming composite `comp_max_then_compare`: residual=-0.206, observed=-2.278, predicted=-2.072
  - underperforming composite `comp_reverse_then_last`: residual=-0.135, observed=-2.179, predicted=-2.044
  - underperforming composite `comp_reverse_then_first`: residual=-0.037, observed=-2.080, predicted=-2.044
- `mean_logprob_margin`: n=10, mean residual=-0.103
  - underperforming composite `comp_retrieve_then_color`: residual=-0.178, observed=0.095, predicted=0.273
  - underperforming composite `comp_max_then_compare`: residual=-0.148, observed=0.119, predicted=0.267
  - underperforming composite `comp_reverse_then_last`: residual=-0.135, observed=0.114, predicted=0.249

## Component coupling
Component coupling compares composite continuous scores to the mean of its listed primitive slices. It is descriptive only.
- `accuracy` / `comp_add_then_compare`: composite_final=0.438, component_mean_final=0.219, diff=0.219
- `accuracy` / `comp_add_then_even`: composite_final=0.375, component_mean_final=0.281, diff=0.094
- `accuracy` / `comp_first_then_same`: composite_final=0.188, component_mean_final=0.312, diff=-0.125
- `accuracy` / `comp_max_then_compare`: composite_final=0.250, component_mean_final=0.281, diff=-0.031
- `accuracy` / `comp_retrieve_then_color`: composite_final=0.188, component_mean_final=0.219, diff=-0.031
- `accuracy` / `comp_retrieve_then_compare`: composite_final=0.375, component_mean_final=0.344, diff=0.031
- `accuracy` / `comp_reverse_then_first`: composite_final=0.375, component_mean_final=0.281, diff=0.094
- `accuracy` / `comp_reverse_then_last`: composite_final=0.375, component_mean_final=0.188, diff=0.188
- `accuracy` / `comp_reverse_then_same`: composite_final=0.312, component_mean_final=0.219, diff=0.094
- `accuracy` / `comp_sub_then_compare`: composite_final=0.375, component_mean_final=0.281, diff=0.094

## Claim boundary
Use continuous-score outputs as calibration and observational bridge evidence only. They can show that a slice moves below top-1 accuracy, but they cannot establish causal dependency without interventions.
