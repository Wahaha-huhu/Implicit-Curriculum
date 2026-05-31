# Pythia observational continuous-score analysis

This analysis is observational. Continuous scores can reveal subthreshold movement, but they do not establish causal dependency.

- metrics analyzed: `accuracy, mean_logprob_correct, mean_correct_margin, mean_correct_mrr, mean_logprob_margin`
- H2 target summary: `final_metric`
- slices: `29`
- models: `1`

## Best final slices by metric
### `accuracy`
- `comp_reverse_then_first` (composite): final=0.312, delta=0.000, AUC=0.312, status=usable_or_near_usable
- `word_reverse2` (atomic): final=0.312, delta=0.000, AUC=0.289, status=usable_or_near_usable
- `arith_compare` (atomic): final=0.297, delta=-0.016, AUC=0.293, status=usable_or_near_usable
- `ctrl_word_surface` (surface_control): final=0.297, delta=0.031, AUC=0.293, status=usable_or_near_usable
- `word_first` (atomic): final=0.297, delta=0.000, AUC=0.301, status=usable_or_near_usable
- `comp_retrieve_then_compare` (composite): final=0.281, delta=0.000, AUC=0.277, status=weak_or_uninformative
- `comp_max_then_compare` (composite): final=0.281, delta=-0.016, AUC=0.285, status=weak_or_uninformative
- `comp_reverse_then_same` (composite): final=0.266, delta=-0.031, AUC=0.297, status=usable_or_near_usable
### `mean_correct_margin`
- `comp_reverse_then_same` (composite): final=-0.456, delta=-0.097, AUC=-0.531, status=usable_or_near_usable
- `comp_retrieve_then_color` (composite): final=-0.542, delta=-0.165, AUC=-0.634, status=usable_or_near_usable
- `word_reverse2` (atomic): final=-0.577, delta=-0.153, AUC=-0.660, status=usable_or_near_usable
- `comp_reverse_then_first` (composite): final=-0.602, delta=-0.283, AUC=-0.578, status=usable_or_near_usable
- `comp_reverse_then_last` (composite): final=-0.603, delta=-0.259, AUC=-0.626, status=usable_or_near_usable
- `comp_retrieve_then_compare` (composite): final=-0.648, delta=-0.266, AUC=-0.491, status=usable_or_near_usable
- `comp_first_then_same` (composite): final=-0.649, delta=-0.160, AUC=-0.672, status=usable_or_near_usable
- `arith_min2` (atomic): final=-0.712, delta=-0.299, AUC=-0.752, status=usable_or_near_usable
### `mean_correct_mrr`
- `comp_reverse_then_first` (composite): final=0.565, delta=0.003, AUC=0.564, status=usable_or_near_usable
- `word_reverse2` (atomic): final=0.555, delta=0.010, AUC=0.546, status=usable_or_near_usable
- `comp_reverse_then_last` (composite): final=0.551, delta=0.009, AUC=0.551, status=usable_or_near_usable
- `comp_reverse_then_same` (composite): final=0.551, delta=-0.007, AUC=0.556, status=usable_or_near_usable
- `ctrl_word_surface` (surface_control): final=0.547, delta=0.012, AUC=0.544, status=usable_or_near_usable
- `word_first` (atomic): final=0.547, delta=0.005, AUC=0.552, status=usable_or_near_usable
- `comp_max_then_compare` (composite): final=0.543, delta=-0.013, AUC=0.543, status=usable_or_near_usable
- `comp_retrieve_then_compare` (composite): final=0.531, delta=-0.010, AUC=0.537, status=usable_or_near_usable
### `mean_logprob_correct`
- `comp_retrieve_then_compare` (composite): final=-1.829, delta=9.312, AUC=-5.106, status=usable_or_near_usable
- `comp_retrieve_then_color` (composite): final=-1.852, delta=9.215, AUC=-5.205, status=usable_or_near_usable
- `arith_min2` (atomic): final=-1.965, delta=8.971, AUC=-5.519, status=usable_or_near_usable
- `word_reverse2` (atomic): final=-1.972, delta=8.941, AUC=-5.345, status=usable_or_near_usable
- `retrieval_number` (atomic): final=-2.025, delta=9.078, AUC=-5.391, status=usable_or_near_usable
- `retrieval_object` (atomic): final=-2.062, delta=9.227, AUC=-5.335, status=usable_or_near_usable
- `comp_reverse_then_last` (composite): final=-2.089, delta=8.859, AUC=-5.357, status=usable_or_near_usable
- `comp_reverse_then_first` (composite): final=-2.102, delta=8.844, AUC=-5.319, status=usable_or_near_usable
### `mean_logprob_margin`
- `arith_add_small` (atomic): final=1.647, delta=1.446, AUC=1.292, status=usable_or_near_usable
- `comp_max_then_compare` (composite): final=1.559, delta=1.448, AUC=0.989, status=usable_or_near_usable
- `comp_add_then_compare` (composite): final=1.544, delta=1.305, AUC=0.993, status=usable_or_near_usable
- `semantic_animal_class` (atomic): final=1.500, delta=1.374, AUC=1.140, status=usable_or_near_usable
- `arith_compare` (atomic): final=1.471, delta=1.352, AUC=0.992, status=usable_or_near_usable
- `ctrl_word_surface` (surface_control): final=1.357, delta=1.070, AUC=0.915, status=usable_or_near_usable
- `word_same` (atomic): final=1.345, delta=1.064, AUC=0.889, status=usable_or_near_usable
- `comp_add_then_even` (composite): final=1.329, delta=1.168, AUC=0.939, status=usable_or_near_usable

## H1-like continuous signatures
- `EleutherAI/pythia-410m` / `accuracy`: mean_final=0.239, mean_delta=-0.005, rho(freq, final)=-0.265, rho(learn, final)=0.232, rho(freq, delta)=-0.010, rho(learn, delta)=0.010
- `EleutherAI/pythia-410m` / `mean_correct_margin`: mean_final=-0.818, mean_delta=-0.415, rho(freq, final)=-0.503, rho(learn, final)=0.496, rho(freq, delta)=-0.524, rho(learn, delta)=0.487
- `EleutherAI/pythia-410m` / `mean_correct_mrr`: mean_final=0.510, mean_delta=-0.006, rho(freq, final)=-0.391, rho(learn, final)=0.348, rho(freq, delta)=-0.139, rho(learn, delta)=0.137
- `EleutherAI/pythia-410m` / `mean_logprob_correct`: mean_final=-2.352, mean_delta=8.665, rho(freq, final)=-0.386, rho(learn, final)=0.422, rho(freq, delta)=-0.347, rho(learn, delta)=0.392
- `EleutherAI/pythia-410m` / `mean_logprob_margin`: mean_final=1.094, mean_delta=0.890, rho(freq, final)=0.125, rho(learn, final)=-0.181, rho(freq, delta)=0.198, rho(learn, delta)=-0.224

## H2-like continuous residuals
- `accuracy`: n=10, mean residual=-0.068
  - underperforming composite `comp_add_then_compare`: residual=-0.125, observed=0.203, predicted=0.328
  - underperforming composite `comp_add_then_even`: residual=-0.124, observed=0.203, predicted=0.327
  - underperforming composite `comp_sub_then_compare`: residual=-0.109, observed=0.203, predicted=0.312
- `mean_correct_margin`: n=10, mean residual=0.164
  - underperforming composite `comp_sub_then_compare`: residual=-0.108, observed=-1.026, predicted=-0.919
  - underperforming composite `comp_add_then_compare`: residual=-0.084, observed=-1.052, predicted=-0.968
  - underperforming composite `comp_add_then_even`: residual=-0.052, observed=-0.972, predicted=-0.921
- `mean_correct_mrr`: n=10, mean residual=-0.136
  - underperforming composite `comp_add_then_even`: residual=-0.188, observed=0.477, predicted=0.664
  - underperforming composite `comp_sub_then_compare`: residual=-0.175, observed=0.482, predicted=0.657
  - underperforming composite `comp_add_then_compare`: residual=-0.165, observed=0.500, predicted=0.665
- `mean_logprob_correct`: n=10, mean residual=0.139
  - underperforming composite `comp_add_then_even`: residual=-0.475, observed=-2.953, predicted=-2.478
  - underperforming composite `comp_max_then_compare`: residual=-0.149, observed=-2.553, predicted=-2.404
  - underperforming composite `comp_sub_then_compare`: residual=-0.035, observed=-2.533, predicted=-2.498
- `mean_logprob_margin`: n=10, mean residual=-0.552
  - underperforming composite `comp_reverse_then_same`: residual=-0.987, observed=0.550, predicted=1.537
  - underperforming composite `comp_retrieve_then_color`: residual=-0.912, observed=0.708, predicted=1.620
  - underperforming composite `comp_reverse_then_last`: residual=-0.896, observed=0.761, predicted=1.657

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
