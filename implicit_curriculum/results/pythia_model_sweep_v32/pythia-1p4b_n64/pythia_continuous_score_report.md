# Pythia observational continuous-score analysis

This analysis is observational. Continuous scores can reveal subthreshold movement, but they do not establish causal dependency.

- metrics analyzed: `accuracy, mean_logprob_correct, mean_correct_margin, mean_correct_mrr, mean_logprob_margin`
- H2 target summary: `final_metric`
- slices: `29`
- models: `1`

## Best final slices by metric
### `accuracy`
- `ctrl_number_surface` (surface_control): final=0.344, delta=0.094, AUC=0.258, status=usable_or_near_usable
- `arith_min2` (atomic): final=0.328, delta=0.031, AUC=0.289, status=usable_or_near_usable
- `comp_retrieve_then_color` (composite): final=0.312, delta=0.062, AUC=0.285, status=usable_or_near_usable
- `word_first` (atomic): final=0.312, delta=0.109, AUC=0.285, status=usable_or_near_usable
- `comp_reverse_then_first` (composite): final=0.312, delta=0.109, AUC=0.273, status=usable_or_near_usable
- `ctrl_word_surface` (surface_control): final=0.297, delta=0.016, AUC=0.281, status=weak_or_uninformative
- `retrieval_number` (atomic): final=0.297, delta=0.062, AUC=0.262, status=weak_or_uninformative
- `word_same` (atomic): final=0.297, delta=0.047, AUC=0.258, status=weak_or_uninformative
### `mean_correct_margin`
- `ctrl_number_surface` (surface_control): final=-0.150, delta=0.442, AUC=-0.637, status=usable_or_near_usable
- `comp_retrieve_then_compare` (composite): final=-0.168, delta=0.497, AUC=-0.507, status=usable_or_near_usable
- `retrieval_number` (atomic): final=-0.172, delta=0.340, AUC=-0.594, status=usable_or_near_usable
- `comp_retrieve_then_color` (composite): final=-0.207, delta=0.547, AUC=-0.608, status=usable_or_near_usable
- `semantic_color_lookup` (atomic): final=-0.242, delta=0.393, AUC=-0.697, status=usable_or_near_usable
- `word_reverse2` (atomic): final=-0.260, delta=0.676, AUC=-0.481, status=usable_or_near_usable
- `arith_even` (atomic): final=-0.267, delta=0.302, AUC=-0.589, status=usable_or_near_usable
- `comp_sub_then_compare` (composite): final=-0.281, delta=0.357, AUC=-0.589, status=usable_or_near_usable
### `mean_correct_mrr`
- `ctrl_word_surface` (surface_control): final=0.574, delta=0.042, AUC=0.542, status=usable_or_near_usable
- `ctrl_number_surface` (surface_control): final=0.570, delta=0.039, AUC=0.523, status=usable_or_near_usable
- `word_reverse2` (atomic): final=0.566, delta=0.109, AUC=0.549, status=usable_or_near_usable
- `arith_min2` (atomic): final=0.564, delta=0.027, AUC=0.537, status=usable_or_near_usable
- `word_first` (atomic): final=0.562, delta=0.073, AUC=0.547, status=usable_or_near_usable
- `comp_retrieve_then_color` (composite): final=0.555, delta=0.039, AUC=0.539, status=usable_or_near_usable
- `comp_reverse_then_first` (composite): final=0.547, delta=0.036, AUC=0.539, status=usable_or_near_usable
- `retrieval_number` (atomic): final=0.547, delta=0.031, AUC=0.527, status=usable_or_near_usable
### `mean_logprob_correct`
- `retrieval_number` (atomic): final=-1.706, delta=9.238, AUC=-5.167, status=usable_or_near_usable
- `word_reverse2` (atomic): final=-1.726, delta=9.377, AUC=-4.780, status=usable_or_near_usable
- `ctrl_number_surface` (surface_control): final=-1.747, delta=9.106, AUC=-4.884, status=usable_or_near_usable
- `comp_retrieve_then_color` (composite): final=-1.771, delta=9.240, AUC=-5.037, status=usable_or_near_usable
- `ctrl_word_surface` (surface_control): final=-1.771, delta=9.139, AUC=-4.845, status=usable_or_near_usable
- `comp_retrieve_then_compare` (composite): final=-1.779, delta=9.230, AUC=-4.912, status=usable_or_near_usable
- `semantic_color_lookup` (atomic): final=-1.806, delta=9.205, AUC=-5.167, status=usable_or_near_usable
- `retrieval_object` (atomic): final=-1.850, delta=9.220, AUC=-4.929, status=usable_or_near_usable
### `mean_logprob_margin`
- `ctrl_word_surface` (surface_control): final=0.823, delta=0.768, AUC=0.372, status=usable_or_near_usable
- `semantic_animal_class` (atomic): final=0.813, delta=0.541, AUC=0.818, status=usable_or_near_usable
- `word_first` (atomic): final=0.611, delta=0.402, AUC=0.504, status=usable_or_near_usable
- `word_copy` (atomic): final=0.608, delta=0.225, AUC=0.572, status=usable_or_near_usable
- `comp_reverse_then_first` (composite): final=0.601, delta=0.185, AUC=0.475, status=usable_or_near_usable
- `ctrl_retrieval_surface` (surface_control): final=0.513, delta=0.377, AUC=0.326, status=usable_or_near_usable
- `syntax_is_are` (atomic): final=0.495, delta=-0.046, AUC=0.563, status=usable_or_near_usable
- `comp_reverse_then_last` (composite): final=0.482, delta=0.087, AUC=0.492, status=usable_or_near_usable

## H1-like continuous signatures
- `EleutherAI/pythia-1.4b` / `accuracy`: mean_final=0.252, mean_delta=0.002, rho(freq, final)=-0.363, rho(learn, final)=0.345, rho(freq, delta)=-0.149, rho(learn, delta)=0.197
- `EleutherAI/pythia-1.4b` / `mean_correct_margin`: mean_final=-0.348, mean_delta=0.253, rho(freq, final)=-0.385, rho(learn, final)=0.399, rho(freq, delta)=-0.215, rho(learn, delta)=0.249
- `EleutherAI/pythia-1.4b` / `mean_correct_mrr`: mean_final=0.519, mean_delta=-0.003, rho(freq, final)=-0.326, rho(learn, final)=0.314, rho(freq, delta)=-0.147, rho(learn, delta)=0.202
- `EleutherAI/pythia-1.4b` / `mean_logprob_correct`: mean_final=-2.023, mean_delta=8.978, rho(freq, final)=-0.426, rho(learn, final)=0.391, rho(freq, delta)=-0.162, rho(learn, delta)=0.150
- `EleutherAI/pythia-1.4b` / `mean_logprob_margin`: mean_final=0.311, mean_delta=-0.057, rho(freq, final)=0.242, rho(learn, final)=-0.278, rho(freq, delta)=0.247, rho(learn, delta)=-0.282

## H2-like continuous residuals
- `accuracy`: n=10, mean residual=-0.172
  - underperforming composite `comp_add_then_even`: residual=-0.238, observed=0.203, predicted=0.441
  - underperforming composite `comp_first_then_same`: residual=-0.204, observed=0.250, predicted=0.454
  - underperforming composite `comp_reverse_then_last`: residual=-0.198, observed=0.250, predicted=0.448
- `mean_correct_margin`: n=10, mean residual=-0.200
  - underperforming composite `comp_first_then_same`: residual=-0.395, observed=-0.485, predicted=-0.090
  - underperforming composite `comp_reverse_then_last`: residual=-0.280, observed=-0.368, predicted=-0.088
  - underperforming composite `comp_reverse_then_first`: residual=-0.266, observed=-0.354, predicted=-0.088
- `mean_correct_mrr`: n=10, mean residual=-0.224
  - underperforming composite `comp_reverse_then_last`: residual=-0.257, observed=0.500, predicted=0.757
  - underperforming composite `comp_add_then_even`: residual=-0.252, observed=0.500, predicted=0.752
  - underperforming composite `comp_first_then_same`: residual=-0.249, observed=0.512, predicted=0.761
- `mean_logprob_correct`: n=10, mean residual=-0.153
  - underperforming composite `comp_first_then_same`: residual=-0.404, observed=-2.163, predicted=-1.758
  - underperforming composite `comp_reverse_then_first`: residual=-0.246, observed=-2.018, predicted=-1.771
  - underperforming composite `comp_max_then_compare`: residual=-0.237, observed=-2.082, predicted=-1.845
- `mean_logprob_margin`: n=10, mean residual=0.088
  - underperforming composite `comp_max_then_compare`: residual=-0.069, observed=0.108, predicted=0.177
  - underperforming composite `comp_sub_then_compare`: residual=-0.067, observed=0.148, predicted=0.214
  - underperforming composite `comp_retrieve_then_color`: residual=-0.053, observed=0.162, predicted=0.214

## Component coupling
Component coupling compares composite continuous scores to the mean of its listed primitive slices. It is descriptive only.
- `accuracy` / `comp_add_then_compare`: composite_final=0.250, component_mean_final=0.234, diff=0.016
- `accuracy` / `comp_add_then_even`: composite_final=0.203, component_mean_final=0.211, diff=-0.008
- `accuracy` / `comp_first_then_same`: composite_final=0.250, component_mean_final=0.305, diff=-0.055
- `accuracy` / `comp_max_then_compare`: composite_final=0.281, component_mean_final=0.242, diff=0.039
- `accuracy` / `comp_retrieve_then_color`: composite_final=0.312, component_mean_final=0.188, diff=0.125
- `accuracy` / `comp_retrieve_then_compare`: composite_final=0.250, component_mean_final=0.289, diff=-0.039
- `accuracy` / `comp_reverse_then_first`: composite_final=0.312, component_mean_final=0.305, diff=0.008
- `accuracy` / `comp_reverse_then_last`: composite_final=0.250, component_mean_final=0.250, diff=0.000
- `accuracy` / `comp_reverse_then_same`: composite_final=0.281, component_mean_final=0.297, diff=-0.016
- `accuracy` / `comp_sub_then_compare`: composite_final=0.250, component_mean_final=0.242, diff=0.008

## Claim boundary
Use continuous-score outputs as calibration and observational bridge evidence only. They can show that a slice moves below top-1 accuracy, but they cannot establish causal dependency without interventions.
