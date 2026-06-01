# Pythia observational continuous-score analysis

This analysis is observational. Continuous scores can reveal subthreshold movement, but they do not establish causal dependency.

- metrics analyzed: `accuracy, mean_logprob_correct, mean_correct_margin, mean_correct_mrr, mean_logprob_margin`
- H2 target summary: `final_metric`
- slices: `29`
- models: `1`

## Best final slices by metric
### `accuracy`
- `arith_compare` (atomic): final=0.500, delta=0.312, AUC=0.396, status=usable_or_near_usable
- `comp_reverse_then_first` (composite): final=0.375, delta=0.250, AUC=0.292, status=usable_or_near_usable
- `comp_first_then_same` (composite): final=0.375, delta=0.188, AUC=0.312, status=usable_or_near_usable
- `word_reverse2` (atomic): final=0.375, delta=0.062, AUC=0.354, status=usable_or_near_usable
- `word_last` (atomic): final=0.375, delta=0.125, AUC=0.333, status=usable_or_near_usable
- `semantic_animal_class` (atomic): final=0.375, delta=0.375, AUC=0.250, status=usable_or_near_usable
- `comp_reverse_then_same` (composite): final=0.312, delta=0.000, AUC=0.312, status=usable_or_near_usable
- `retrieval_object` (atomic): final=0.312, delta=0.062, AUC=0.292, status=usable_or_near_usable
### `mean_correct_margin`
- `arith_compare` (atomic): final=-0.015, delta=0.529, AUC=-0.266, status=usable_or_near_usable
- `word_reverse2` (atomic): final=-0.130, delta=0.166, AUC=-0.327, status=usable_or_near_usable
- `comp_first_then_same` (composite): final=-0.323, delta=-0.123, AUC=-0.368, status=usable_or_near_usable
- `comp_retrieve_then_compare` (composite): final=-0.436, delta=0.038, AUC=-0.615, status=usable_or_near_usable
- `comp_reverse_then_first` (composite): final=-0.437, delta=-0.089, AUC=-0.461, status=usable_or_near_usable
- `ctrl_number_surface` (surface_control): final=-0.451, delta=0.064, AUC=-0.874, status=usable_or_near_usable
- `word_copy` (atomic): final=-0.457, delta=-0.249, AUC=-0.415, status=usable_or_near_usable
- `comp_reverse_then_same` (composite): final=-0.461, delta=-0.288, AUC=-0.395, status=usable_or_near_usable
### `mean_correct_mrr`
- `arith_compare` (atomic): final=0.693, delta=0.229, AUC=0.613, status=usable_or_near_usable
- `word_reverse2` (atomic): final=0.641, delta=0.068, AUC=0.602, status=usable_or_near_usable
- `word_last` (atomic): final=0.609, delta=0.120, AUC=0.569, status=usable_or_near_usable
- `comp_reverse_then_first` (composite): final=0.589, delta=0.161, AUC=0.531, status=usable_or_near_usable
- `comp_first_then_same` (composite): final=0.578, delta=0.120, AUC=0.540, status=usable_or_near_usable
- `word_copy` (atomic): final=0.562, delta=0.005, AUC=0.561, status=usable_or_near_usable
- `retrieval_object` (atomic): final=0.562, delta=0.057, AUC=0.538, status=usable_or_near_usable
- `comp_retrieve_then_compare` (composite): final=0.562, delta=0.047, AUC=0.543, status=usable_or_near_usable
### `mean_logprob_correct`
- `word_reverse2` (atomic): final=-1.669, delta=9.229, AUC=-4.993, status=usable_or_near_usable
- `arith_compare` (atomic): final=-1.869, delta=9.367, AUC=-5.320, status=usable_or_near_usable
- `word_copy` (atomic): final=-1.913, delta=9.100, AUC=-5.297, status=usable_or_near_usable
- `comp_sub_then_compare` (composite): final=-2.167, delta=9.055, AUC=-5.573, status=usable_or_near_usable
- `comp_add_then_compare` (composite): final=-2.200, delta=8.948, AUC=-5.556, status=usable_or_near_usable
- `arith_min2` (atomic): final=-2.205, delta=8.677, AUC=-5.184, status=usable_or_near_usable
- `comp_first_then_same` (composite): final=-2.221, delta=8.921, AUC=-5.387, status=usable_or_near_usable
- `ctrl_number_surface` (surface_control): final=-2.223, delta=8.895, AUC=-5.698, status=usable_or_near_usable
### `mean_logprob_margin`
- `arith_add_small` (atomic): final=1.568, delta=1.489, AUC=1.015, status=usable_or_near_usable
- `word_first` (atomic): final=1.354, delta=1.182, AUC=1.154, status=usable_or_near_usable
- `arith_sub_small` (atomic): final=1.244, delta=1.044, AUC=0.908, status=usable_or_near_usable
- `semantic_animal_class` (atomic): final=1.183, delta=1.077, AUC=1.124, status=usable_or_near_usable
- `semantic_color_lookup` (atomic): final=1.047, delta=0.655, AUC=1.107, status=usable_or_near_usable
- `word_copy` (atomic): final=1.013, delta=0.903, AUC=0.737, status=usable_or_near_usable
- `word_last` (atomic): final=0.964, delta=0.665, AUC=0.991, status=usable_or_near_usable
- `retrieval_number` (atomic): final=0.958, delta=0.650, AUC=1.010, status=usable_or_near_usable

## H1-like continuous signatures
- `EleutherAI/pythia-1b` / `accuracy`: mean_final=0.260, mean_delta=-0.002, rho(freq, final)=0.047, rho(learn, final)=-0.102, rho(freq, delta)=0.031, rho(learn, delta)=-0.078
- `EleutherAI/pythia-1b` / `mean_correct_margin`: mean_final=-0.640, mean_delta=-0.323, rho(freq, final)=-0.431, rho(learn, final)=0.389, rho(freq, delta)=-0.340, rho(learn, delta)=0.352
- `EleutherAI/pythia-1b` / `mean_correct_mrr`: mean_final=0.520, mean_delta=-0.012, rho(freq, final)=-0.012, rho(learn, final)=-0.031, rho(freq, delta)=0.049, rho(learn, delta)=-0.075
- `EleutherAI/pythia-1b` / `mean_logprob_correct`: mean_final=-2.375, mean_delta=8.682, rho(freq, final)=-0.326, rho(learn, final)=0.285, rho(freq, delta)=-0.323, rho(learn, delta)=0.307
- `EleutherAI/pythia-1b` / `mean_logprob_margin`: mean_final=0.821, mean_delta=0.599, rho(freq, final)=0.488, rho(learn, final)=-0.493, rho(freq, delta)=0.464, rho(learn, delta)=-0.465

## H2-like continuous residuals
- `accuracy`: n=10, mean residual=-0.202
  - underperforming composite `comp_add_then_compare`: residual=-0.344, observed=0.125, predicted=0.469
  - underperforming composite `comp_add_then_even`: residual=-0.343, observed=0.125, predicted=0.468
  - underperforming composite `comp_reverse_then_last`: residual=-0.279, observed=0.188, predicted=0.466
- `mean_correct_margin`: n=10, mean residual=-0.362
  - underperforming composite `comp_add_then_even`: residual=-0.603, observed=-0.731, predicted=-0.128
  - underperforming composite `comp_max_then_compare`: residual=-0.534, observed=-0.727, predicted=-0.193
  - underperforming composite `comp_retrieve_then_color`: residual=-0.508, observed=-0.749, predicted=-0.241
- `mean_correct_mrr`: n=10, mean residual=-0.213
  - underperforming composite `comp_add_then_compare`: residual=-0.306, observed=0.432, predicted=0.738
  - underperforming composite `comp_add_then_even`: residual=-0.295, observed=0.443, predicted=0.738
  - underperforming composite `comp_retrieve_then_color`: residual=-0.253, observed=0.458, predicted=0.711
- `mean_logprob_correct`: n=10, mean residual=0.086
  - underperforming composite `comp_add_then_even`: residual=-0.092, observed=-2.433, predicted=-2.342
  - underperforming composite `comp_reverse_then_same`: residual=-0.076, observed=-2.422, predicted=-2.346
  - underperforming composite `comp_first_then_same`: residual=0.007, observed=-2.221, predicted=-2.228
- `mean_logprob_margin`: n=10, mean residual=0.304
  - underperforming composite `comp_retrieve_then_color`: residual=0.026, observed=0.444, predicted=0.418
  - underperforming composite `comp_sub_then_compare`: residual=0.026, observed=0.444, predicted=0.418
  - underperforming composite `comp_add_then_compare`: residual=0.039, observed=0.486, predicted=0.447

## Component coupling
Component coupling compares composite continuous scores to the mean of its listed primitive slices. It is descriptive only.
- `accuracy` / `comp_add_then_compare`: composite_final=0.125, component_mean_final=0.281, diff=-0.156
- `accuracy` / `comp_add_then_even`: composite_final=0.125, component_mean_final=0.125, diff=0.000
- `accuracy` / `comp_first_then_same`: composite_final=0.375, component_mean_final=0.188, diff=0.188
- `accuracy` / `comp_max_then_compare`: composite_final=0.188, component_mean_final=0.375, diff=-0.188
- `accuracy` / `comp_retrieve_then_color`: composite_final=0.188, component_mean_final=0.281, diff=-0.094
- `accuracy` / `comp_retrieve_then_compare`: composite_final=0.312, component_mean_final=0.375, diff=-0.062
- `accuracy` / `comp_reverse_then_first`: composite_final=0.375, component_mean_final=0.312, diff=0.062
- `accuracy` / `comp_reverse_then_last`: composite_final=0.188, component_mean_final=0.375, diff=-0.188
- `accuracy` / `comp_reverse_then_same`: composite_final=0.312, component_mean_final=0.250, diff=0.062
- `accuracy` / `comp_sub_then_compare`: composite_final=0.250, component_mean_final=0.344, diff=-0.094

## Claim boundary
Use continuous-score outputs as calibration and observational bridge evidence only. They can show that a slice moves below top-1 accuracy, but they cannot establish causal dependency without interventions.
