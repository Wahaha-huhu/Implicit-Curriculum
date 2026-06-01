# Pythia observational continuous-score analysis

This analysis is observational. Continuous scores can reveal subthreshold movement, but they do not establish causal dependency.

- metrics analyzed: `accuracy, mean_logprob_correct, mean_correct_margin, mean_correct_mrr, mean_logprob_margin`
- H2 target summary: `final_metric`
- slices: `29`
- models: `1`

## Best final slices by metric
### `accuracy`
- `arith_compare` (atomic): final=0.438, delta=0.312, AUC=0.354, status=usable_or_near_usable
- `ctrl_number_surface` (surface_control): final=0.438, delta=0.250, AUC=0.229, status=usable_or_near_usable
- `comp_reverse_then_first` (composite): final=0.375, delta=0.125, AUC=0.333, status=usable_or_near_usable
- `comp_reverse_then_same` (composite): final=0.375, delta=0.062, AUC=0.333, status=usable_or_near_usable
- `comp_first_then_same` (composite): final=0.375, delta=0.125, AUC=0.333, status=usable_or_near_usable
- `semantic_animal_class` (atomic): final=0.375, delta=0.062, AUC=0.354, status=usable_or_near_usable
- `word_same` (atomic): final=0.375, delta=0.062, AUC=0.271, status=usable_or_near_usable
- `word_last` (atomic): final=0.312, delta=0.062, AUC=0.312, status=usable_or_near_usable
### `mean_correct_margin`
- `ctrl_number_surface` (surface_control): final=-0.091, delta=0.414, AUC=-0.508, status=usable_or_near_usable
- `word_last` (atomic): final=-0.158, delta=0.439, AUC=-0.345, status=usable_or_near_usable
- `comp_retrieve_then_compare` (composite): final=-0.181, delta=0.453, AUC=-0.420, status=usable_or_near_usable
- `arith_even` (atomic): final=-0.198, delta=0.362, AUC=-0.392, status=usable_or_near_usable
- `arith_compare` (atomic): final=-0.215, delta=0.720, AUC=-0.435, status=usable_or_near_usable
- `word_reverse2` (atomic): final=-0.221, delta=0.806, AUC=-0.555, status=usable_or_near_usable
- `semantic_color_lookup` (atomic): final=-0.243, delta=0.425, AUC=-0.548, status=usable_or_near_usable
- `retrieval_object` (atomic): final=-0.249, delta=0.269, AUC=-0.373, status=usable_or_near_usable
### `mean_correct_mrr`
- `arith_compare` (atomic): final=0.641, delta=0.234, AUC=0.578, status=usable_or_near_usable
- `ctrl_number_surface` (surface_control): final=0.641, delta=0.104, AUC=0.542, status=usable_or_near_usable
- `comp_reverse_then_same` (composite): final=0.615, delta=0.089, AUC=0.550, status=usable_or_near_usable
- `word_copy` (atomic): final=0.599, delta=0.094, AUC=0.549, status=usable_or_near_usable
- `comp_reverse_then_first` (composite): final=0.594, delta=0.062, AUC=0.580, status=usable_or_near_usable
- `word_same` (atomic): final=0.589, delta=0.026, AUC=0.524, status=usable_or_near_usable
- `word_reverse2` (atomic): final=0.589, delta=0.146, AUC=0.533, status=usable_or_near_usable
- `comp_first_then_same` (composite): final=0.578, delta=0.068, AUC=0.556, status=usable_or_near_usable
### `mean_logprob_correct`
- `ctrl_number_surface` (surface_control): final=-1.697, delta=9.043, AUC=-5.062, status=usable_or_near_usable
- `word_reverse2` (atomic): final=-1.700, delta=9.510, AUC=-5.063, status=usable_or_near_usable
- `retrieval_object` (atomic): final=-1.746, delta=9.295, AUC=-5.176, status=usable_or_near_usable
- `retrieval_number` (atomic): final=-1.775, delta=9.206, AUC=-5.432, status=usable_or_near_usable
- `comp_retrieve_then_compare` (composite): final=-1.786, delta=9.210, AUC=-5.184, status=usable_or_near_usable
- `comp_retrieve_then_color` (composite): final=-1.811, delta=9.167, AUC=-5.361, status=usable_or_near_usable
- `semantic_color_lookup` (atomic): final=-1.816, delta=9.257, AUC=-5.421, status=usable_or_near_usable
- `ctrl_word_surface` (surface_control): final=-1.838, delta=9.121, AUC=-5.187, status=usable_or_near_usable
### `mean_logprob_margin`
- `semantic_animal_class` (atomic): final=0.861, delta=0.596, AUC=0.818, status=usable_or_near_usable
- `ctrl_word_surface` (surface_control): final=0.831, delta=0.788, AUC=0.398, status=usable_or_near_usable
- `word_first` (atomic): final=0.647, delta=0.414, AUC=0.520, status=usable_or_near_usable
- `comp_reverse_then_first` (composite): final=0.587, delta=0.174, AUC=0.481, status=usable_or_near_usable
- `word_copy` (atomic): final=0.575, delta=0.194, AUC=0.464, status=usable_or_near_usable
- `comp_reverse_then_last` (composite): final=0.544, delta=0.112, AUC=0.557, status=usable_or_near_usable
- `ctrl_retrieval_surface` (surface_control): final=0.491, delta=0.349, AUC=0.327, status=usable_or_near_usable
- `syntax_is_are` (atomic): final=0.466, delta=-0.068, AUC=0.421, status=usable_or_near_usable

## H1-like continuous signatures
- `EleutherAI/pythia-1.4b` / `accuracy`: mean_final=0.264, mean_delta=-0.005, rho(freq, final)=0.083, rho(learn, final)=-0.186, rho(freq, delta)=0.038, rho(learn, delta)=-0.091
- `EleutherAI/pythia-1.4b` / `mean_correct_margin`: mean_final=-0.341, mean_delta=0.268, rho(freq, final)=-0.119, rho(learn, final)=0.092, rho(freq, delta)=-0.166, rho(learn, delta)=0.149
- `EleutherAI/pythia-1.4b` / `mean_correct_mrr`: mean_final=0.526, mean_delta=-0.000, rho(freq, final)=-0.009, rho(learn, final)=-0.067, rho(freq, delta)=-0.058, rho(learn, delta)=0.017
- `EleutherAI/pythia-1.4b` / `mean_logprob_correct`: mean_final=-2.021, mean_delta=8.991, rho(freq, final)=-0.244, rho(learn, final)=0.215, rho(freq, delta)=-0.109, rho(learn, delta)=0.070
- `EleutherAI/pythia-1.4b` / `mean_logprob_margin`: mean_final=0.314, mean_delta=-0.048, rho(freq, final)=0.182, rho(learn, final)=-0.208, rho(freq, delta)=0.233, rho(learn, delta)=-0.240

## H2-like continuous residuals
- `accuracy`: n=10, mean residual=-0.375
  - underperforming composite `comp_add_then_even`: residual=-0.512, observed=0.125, predicted=0.637
  - underperforming composite `comp_add_then_compare`: residual=-0.509, observed=0.125, predicted=0.634
  - underperforming composite `comp_retrieve_then_color`: residual=-0.469, observed=0.125, predicted=0.594
- `mean_correct_margin`: n=10, mean residual=-0.596
  - underperforming composite `comp_reverse_then_last`: residual=-0.852, observed=-0.529, predicted=0.323
  - underperforming composite `comp_first_then_same`: residual=-0.781, observed=-0.412, predicted=0.369
  - underperforming composite `comp_add_then_compare`: residual=-0.671, observed=-0.421, predicted=0.250
- `mean_correct_mrr`: n=10, mean residual=-0.356
  - underperforming composite `comp_add_then_compare`: residual=-0.462, observed=0.422, predicted=0.884
  - underperforming composite `comp_reverse_then_last`: residual=-0.433, observed=0.458, predicted=0.892
  - underperforming composite `comp_retrieve_then_color`: residual=-0.417, observed=0.438, predicted=0.855
- `mean_logprob_correct`: n=10, mean residual=-0.498
  - underperforming composite `comp_first_then_same`: residual=-0.778, observed=-2.138, predicted=-1.361
  - underperforming composite `comp_reverse_then_last`: residual=-0.680, observed=-2.088, predicted=-1.408
  - underperforming composite `comp_max_then_compare`: residual=-0.608, observed=-2.133, predicted=-1.524
- `mean_logprob_margin`: n=10, mean residual=0.132
  - underperforming composite `comp_add_then_compare`: residual=-0.056, observed=0.165, predicted=0.221
  - underperforming composite `comp_max_then_compare`: residual=-0.040, observed=0.103, predicted=0.143
  - underperforming composite `comp_retrieve_then_color`: residual=-0.017, observed=0.168, predicted=0.186

## Component coupling
Component coupling compares composite continuous scores to the mean of its listed primitive slices. It is descriptive only.
- `accuracy` / `comp_add_then_compare`: composite_final=0.125, component_mean_final=0.281, diff=-0.156
- `accuracy` / `comp_add_then_even`: composite_final=0.125, component_mean_final=0.188, diff=-0.062
- `accuracy` / `comp_first_then_same`: composite_final=0.375, component_mean_final=0.312, diff=0.062
- `accuracy` / `comp_max_then_compare`: composite_final=0.250, component_mean_final=0.344, diff=-0.094
- `accuracy` / `comp_retrieve_then_color`: composite_final=0.125, component_mean_final=0.250, diff=-0.125
- `accuracy` / `comp_retrieve_then_compare`: composite_final=0.188, component_mean_final=0.344, diff=-0.156
- `accuracy` / `comp_reverse_then_first`: composite_final=0.375, component_mean_final=0.281, diff=0.094
- `accuracy` / `comp_reverse_then_last`: composite_final=0.188, component_mean_final=0.312, diff=-0.125
- `accuracy` / `comp_reverse_then_same`: composite_final=0.375, component_mean_final=0.344, diff=0.031
- `accuracy` / `comp_sub_then_compare`: composite_final=0.250, component_mean_final=0.312, diff=-0.062

## Claim boundary
Use continuous-score outputs as calibration and observational bridge evidence only. They can show that a slice moves below top-1 accuracy, but they cannot establish causal dependency without interventions.
