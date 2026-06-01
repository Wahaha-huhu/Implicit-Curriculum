# Pythia observational continuous-score analysis

This analysis is observational. Continuous scores can reveal subthreshold movement, but they do not establish causal dependency.

- metrics analyzed: `accuracy, mean_logprob_correct, mean_correct_margin, mean_correct_mrr, mean_logprob_margin`
- H2 target summary: `final_metric`
- slices: `29`
- models: `1`

## Best final slices by metric
### `accuracy`
- `comp_reverse_then_first` (composite): final=0.312, delta=0.156, AUC=0.270, status=usable_or_near_usable
- `word_reverse2` (atomic): final=0.312, delta=0.016, AUC=0.309, status=usable_or_near_usable
- `arith_compare` (atomic): final=0.297, delta=0.047, AUC=0.285, status=weak_or_uninformative
- `ctrl_word_surface` (surface_control): final=0.297, delta=0.094, AUC=0.273, status=weak_or_uninformative
- `word_first` (atomic): final=0.297, delta=0.094, AUC=0.273, status=weak_or_uninformative
- `comp_retrieve_then_compare` (composite): final=0.281, delta=0.109, AUC=0.254, status=weak_or_uninformative
- `comp_max_then_compare` (composite): final=0.281, delta=0.047, AUC=0.270, status=weak_or_uninformative
- `comp_retrieve_then_color` (composite): final=0.266, delta=0.016, AUC=0.254, status=weak_or_uninformative
### `mean_correct_margin`
- `word_reverse2` (atomic): final=-0.210, delta=0.153, AUC=-0.550, status=usable_or_near_usable
- `arith_compare` (atomic): final=-0.308, delta=0.174, AUC=-0.600, status=usable_or_near_usable
- `ctrl_number_surface` (surface_control): final=-0.348, delta=0.062, AUC=-0.719, status=usable_or_near_usable
- `comp_reverse_then_last` (composite): final=-0.411, delta=-0.128, AUC=-0.545, status=usable_or_near_usable
- `comp_retrieve_then_compare` (composite): final=-0.425, delta=0.110, AUC=-0.802, status=usable_or_near_usable
- `comp_add_then_compare` (composite): final=-0.434, delta=0.074, AUC=-0.760, status=usable_or_near_usable
- `comp_reverse_then_first` (composite): final=-0.466, delta=-0.121, AUC=-0.596, status=usable_or_near_usable
- `arith_min2` (atomic): final=-0.476, delta=-0.147, AUC=-0.668, status=usable_or_near_usable
### `mean_correct_mrr`
- `word_reverse2` (atomic): final=0.561, delta=0.020, AUC=0.553, status=usable_or_near_usable
- `comp_reverse_then_first` (composite): final=0.549, delta=0.104, AUC=0.521, status=usable_or_near_usable
- `comp_reverse_then_last` (composite): final=0.548, delta=0.066, AUC=0.527, status=usable_or_near_usable
- `comp_retrieve_then_compare` (composite): final=0.546, delta=0.074, AUC=0.530, status=usable_or_near_usable
- `ctrl_word_surface` (surface_control): final=0.544, delta=0.059, AUC=0.527, status=usable_or_near_usable
- `arith_compare` (atomic): final=0.544, delta=0.035, AUC=0.538, status=usable_or_near_usable
- `word_first` (atomic): final=0.543, delta=0.055, AUC=0.531, status=usable_or_near_usable
- `word_copy` (atomic): final=0.538, delta=-0.014, AUC=0.538, status=usable_or_near_usable
### `mean_logprob_correct`
- `word_reverse2` (atomic): final=-1.738, delta=9.208, AUC=-4.548, status=usable_or_near_usable
- `word_copy` (atomic): final=-1.957, delta=9.039, AUC=-4.717, status=usable_or_near_usable
- `arith_compare` (atomic): final=-2.043, delta=9.158, AUC=-4.976, status=usable_or_near_usable
- `arith_min2` (atomic): final=-2.143, delta=8.850, AUC=-4.758, status=usable_or_near_usable
- `comp_add_then_compare` (composite): final=-2.160, delta=9.033, AUC=-5.041, status=usable_or_near_usable
- `ctrl_number_surface` (surface_control): final=-2.177, delta=8.842, AUC=-4.945, status=usable_or_near_usable
- `comp_reverse_then_last` (composite): final=-2.192, delta=8.860, AUC=-4.795, status=usable_or_near_usable
- `comp_sub_then_compare` (composite): final=-2.202, delta=8.936, AUC=-5.063, status=usable_or_near_usable
### `mean_logprob_margin`
- `arith_add_small` (atomic): final=1.557, delta=1.457, AUC=1.115, status=usable_or_near_usable
- `word_first` (atomic): final=1.427, delta=1.248, AUC=1.174, status=usable_or_near_usable
- `arith_sub_small` (atomic): final=1.197, delta=0.992, AUC=1.044, status=usable_or_near_usable
- `semantic_animal_class` (atomic): final=1.152, delta=1.050, AUC=1.230, status=usable_or_near_usable
- `word_copy` (atomic): final=1.024, delta=0.929, AUC=0.757, status=usable_or_near_usable
- `semantic_color_lookup` (atomic): final=1.007, delta=0.623, AUC=1.146, status=usable_or_near_usable
- `word_last` (atomic): final=0.976, delta=0.640, AUC=1.047, status=usable_or_near_usable
- `retrieval_number` (atomic): final=0.944, delta=0.621, AUC=1.230, status=usable_or_near_usable

## H1-like continuous signatures
- `EleutherAI/pythia-1b` / `accuracy`: mean_final=0.240, mean_delta=-0.007, rho(freq, final)=-0.294, rho(learn, final)=0.263, rho(freq, delta)=-0.348, rho(learn, delta)=0.331
- `EleutherAI/pythia-1b` / `mean_correct_margin`: mean_final=-0.648, mean_delta=-0.311, rho(freq, final)=-0.555, rho(learn, final)=0.528, rho(freq, delta)=-0.502, rho(learn, delta)=0.512
- `EleutherAI/pythia-1b` / `mean_correct_mrr`: mean_final=0.508, mean_delta=-0.014, rho(freq, final)=-0.255, rho(learn, final)=0.243, rho(freq, delta)=-0.286, rho(learn, delta)=0.300
- `EleutherAI/pythia-1b` / `mean_logprob_correct`: mean_final=-2.379, mean_delta=8.693, rho(freq, final)=-0.272, rho(learn, final)=0.241, rho(freq, delta)=-0.323, rho(learn, delta)=0.333
- `EleutherAI/pythia-1b` / `mean_logprob_margin`: mean_final=0.810, mean_delta=0.592, rho(freq, final)=0.512, rho(learn, final)=-0.518, rho(freq, delta)=0.469, rho(learn, delta)=-0.467

## H2-like continuous residuals
- `accuracy`: n=10, mean residual=-0.064
  - underperforming composite `comp_add_then_compare`: residual=-0.125, observed=0.203, predicted=0.328
  - underperforming composite `comp_add_then_even`: residual=-0.124, observed=0.203, predicted=0.327
  - underperforming composite `comp_sub_then_compare`: residual=-0.109, observed=0.203, predicted=0.312
- `mean_correct_margin`: n=10, mean residual=-0.182
  - underperforming composite `comp_add_then_even`: residual=-0.368, observed=-0.667, predicted=-0.298
  - underperforming composite `comp_first_then_same`: residual=-0.332, observed=-0.557, predicted=-0.225
  - underperforming composite `comp_reverse_then_same`: residual=-0.275, observed=-0.545, predicted=-0.270
- `mean_correct_mrr`: n=10, mean residual=-0.152
  - underperforming composite `comp_add_then_even`: residual=-0.206, observed=0.465, predicted=0.671
  - underperforming composite `comp_add_then_compare`: residual=-0.187, observed=0.484, predicted=0.671
  - underperforming composite `comp_sub_then_compare`: residual=-0.182, observed=0.479, predicted=0.662
- `mean_logprob_correct`: n=10, mean residual=0.073
  - underperforming composite `comp_reverse_then_same`: residual=-0.204, observed=-2.511, predicted=-2.307
  - underperforming composite `comp_add_then_even`: residual=-0.130, observed=-2.457, predicted=-2.326
  - underperforming composite `comp_first_then_same`: residual=-0.054, observed=-2.286, predicted=-2.232
- `mean_logprob_margin`: n=10, mean residual=0.360
  - underperforming composite `comp_retrieve_then_color`: residual=0.044, observed=0.391, predicted=0.347
  - underperforming composite `comp_sub_then_compare`: residual=0.101, observed=0.448, predicted=0.347
  - underperforming composite `comp_add_then_compare`: residual=0.126, observed=0.506, predicted=0.380

## Component coupling
Component coupling compares composite continuous scores to the mean of its listed primitive slices. It is descriptive only.
- `accuracy` / `comp_add_then_compare`: composite_final=0.203, component_mean_final=0.234, diff=-0.031
- `accuracy` / `comp_add_then_even`: composite_final=0.203, component_mean_final=0.180, diff=0.023
- `accuracy` / `comp_first_then_same`: composite_final=0.250, component_mean_final=0.258, diff=-0.008
- `accuracy` / `comp_max_then_compare`: composite_final=0.281, component_mean_final=0.219, diff=0.062
- `accuracy` / `comp_retrieve_then_color`: composite_final=0.266, component_mean_final=0.195, diff=0.070
- `accuracy` / `comp_retrieve_then_compare`: composite_final=0.281, component_mean_final=0.273, diff=0.008
- `accuracy` / `comp_reverse_then_first`: composite_final=0.312, component_mean_final=0.305, diff=0.008
- `accuracy` / `comp_reverse_then_last`: composite_final=0.266, component_mean_final=0.281, diff=-0.016
- `accuracy` / `comp_reverse_then_same`: composite_final=0.266, component_mean_final=0.266, diff=0.000
- `accuracy` / `comp_sub_then_compare`: composite_final=0.203, component_mean_final=0.266, diff=-0.062

## Claim boundary
Use continuous-score outputs as calibration and observational bridge evidence only. They can show that a slice moves below top-1 accuracy, but they cannot establish causal dependency without interventions.
