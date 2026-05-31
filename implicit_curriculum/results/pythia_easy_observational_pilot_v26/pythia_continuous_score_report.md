# Pythia observational continuous-score analysis

This analysis is observational. Continuous scores can reveal subthreshold movement, but they do not establish causal dependency.

- metrics analyzed: `accuracy, mean_logprob_correct, mean_correct_margin, mean_correct_mrr, mean_logprob_margin`
- H2 target summary: `final_metric`
- slices: `8`
- models: `1`

## Best final slices by metric
### `accuracy`
- `easy_add_then_compare` (composite): final=0.312, delta=0.094, AUC=0.289, status=usable_or_near_usable
- `easy_add_1d` (atomic): final=0.281, delta=0.141, AUC=0.246, status=weak_or_uninformative
- `easy_copy_word` (atomic): final=0.281, delta=0.094, AUC=0.203, status=weak_or_uninformative
- `easy_reverse_two_words` (atomic): final=0.250, delta=-0.078, AUC=0.270, status=usable_or_near_usable
- `easy_color_surface` (surface_control): final=0.234, delta=0.000, AUC=0.234, status=weak_or_uninformative
- `easy_animals_surface` (surface_control): final=0.203, delta=0.000, AUC=0.203, status=weak_or_uninformative
- `easy_reverse_then_copy` (composite): final=0.156, delta=-0.125, AUC=0.188, status=weak_or_uninformative
- `easy_compare_1d` (atomic): final=0.125, delta=-0.156, AUC=0.156, status=weak_or_uninformative
### `mean_correct_margin`
- `easy_add_then_compare` (composite): final=-0.318, delta=0.484, AUC=-0.736, status=usable_or_near_usable
- `easy_copy_word` (atomic): final=-0.381, delta=0.177, AUC=-0.964, status=usable_or_near_usable
- `easy_compare_1d` (atomic): final=-0.463, delta=0.006, AUC=-1.037, status=usable_or_near_usable
- `easy_add_1d` (atomic): final=-0.671, delta=0.182, AUC=-1.060, status=usable_or_near_usable
- `easy_animals_surface` (surface_control): final=-1.063, delta=-0.381, AUC=-1.209, status=usable_or_near_usable
- `easy_color_surface` (surface_control): final=-1.124, delta=-0.611, AUC=-1.135, status=usable_or_near_usable
- `easy_reverse_then_copy` (composite): final=-1.125, delta=-0.689, AUC=-1.208, status=usable_or_near_usable
- `easy_reverse_two_words` (atomic): final=-1.307, delta=-0.767, AUC=-1.081, status=usable_or_near_usable
### `mean_correct_mrr`
- `easy_add_then_compare` (composite): final=0.573, delta=0.073, AUC=0.558, status=usable_or_near_usable
- `easy_copy_word` (atomic): final=0.560, delta=0.066, AUC=0.502, status=usable_or_near_usable
- `easy_add_1d` (atomic): final=0.553, delta=0.105, AUC=0.523, status=usable_or_near_usable
- `easy_color_surface` (surface_control): final=0.520, delta=0.013, AUC=0.513, status=usable_or_near_usable
- `easy_reverse_two_words` (atomic): final=0.513, delta=-0.047, AUC=0.527, status=usable_or_near_usable
- `easy_animals_surface` (surface_control): final=0.504, delta=-0.008, AUC=0.502, status=usable_or_near_usable
- `easy_reverse_then_copy` (composite): final=0.469, delta=-0.099, AUC=0.491, status=usable_or_near_usable
- `easy_compare_1d` (atomic): final=0.460, delta=-0.107, AUC=0.481, status=usable_or_near_usable
### `mean_logprob_correct`
- `easy_add_then_compare` (composite): final=-4.425, delta=6.745, AUC=-5.968, status=usable_or_near_usable
- `easy_color_surface` (surface_control): final=-4.471, delta=6.652, AUC=-5.883, status=usable_or_near_usable
- `easy_compare_1d` (atomic): final=-4.507, delta=6.382, AUC=-6.091, status=usable_or_near_usable
- `easy_animals_surface` (surface_control): final=-4.508, delta=6.393, AUC=-5.819, status=usable_or_near_usable
- `easy_add_1d` (atomic): final=-4.535, delta=6.620, AUC=-5.821, status=usable_or_near_usable
- `easy_copy_word` (atomic): final=-4.547, delta=6.455, AUC=-6.125, status=usable_or_near_usable
- `easy_reverse_two_words` (atomic): final=-5.254, delta=5.489, AUC=-6.125, status=usable_or_near_usable
- `easy_reverse_then_copy` (composite): final=-5.416, delta=5.400, AUC=-6.336, status=usable_or_near_usable
### `mean_logprob_margin`
- `easy_color_surface` (surface_control): final=1.564, delta=1.211, AUC=1.424, status=usable_or_near_usable
- `easy_reverse_two_words` (atomic): final=1.177, delta=0.673, AUC=1.189, status=usable_or_near_usable
- `easy_animals_surface` (surface_control): final=1.132, delta=0.490, AUC=1.243, status=usable_or_near_usable
- `easy_reverse_then_copy` (composite): final=0.901, delta=0.454, AUC=1.091, status=usable_or_near_usable
- `easy_add_1d` (atomic): final=0.645, delta=0.083, AUC=1.356, status=usable_or_near_usable
- `easy_compare_1d` (atomic): final=0.316, delta=-0.330, AUC=0.950, status=usable_or_near_usable
- `easy_add_then_compare` (composite): final=0.301, delta=-0.273, AUC=0.967, status=usable_or_near_usable
- `easy_copy_word` (atomic): final=0.279, delta=-0.250, AUC=0.854, status=usable_or_near_usable

## H1-like continuous signatures
- `EleutherAI/pythia-70m` / `accuracy`: mean_final=0.234, mean_delta=-0.005, rho(freq, final)=-0.029, rho(learn, final)=0.132, rho(freq, delta)=0.319, rho(learn, delta)=-0.176
- `EleutherAI/pythia-70m` / `mean_correct_margin`: mean_final=-0.711, mean_delta=-0.101, rho(freq, final)=0.086, rho(learn, final)=-0.116, rho(freq, delta)=0.257, rho(learn, delta)=-0.203
- `EleutherAI/pythia-70m` / `mean_correct_mrr`: mean_final=0.521, mean_delta=-0.001, rho(freq, final)=-0.086, rho(learn, final)=0.174, rho(freq, delta)=0.257, rho(learn, delta)=-0.116
- `EleutherAI/pythia-70m` / `mean_logprob_correct`: mean_final=-4.781, mean_delta=6.182, rho(freq, final)=0.371, rho(learn, final)=-0.406, rho(freq, delta)=0.371, rho(learn, delta)=-0.319
- `EleutherAI/pythia-70m` / `mean_logprob_margin`: mean_final=0.603, mean_delta=0.060, rho(freq, final)=-0.200, rho(learn, final)=0.232, rho(freq, delta)=-0.314, rho(learn, delta)=0.406

## H2-like continuous residuals
- No valid H2 continuous residuals; likely too few atomic slices or missing features.

## Component coupling
Component coupling compares composite continuous scores to the mean of its listed primitive slices. It is descriptive only.
- `accuracy` / `easy_add_then_compare`: composite_final=0.312, component_mean_final=0.203, diff=0.109
- `accuracy` / `easy_reverse_then_copy`: composite_final=0.156, component_mean_final=0.266, diff=-0.109
- `mean_logprob_correct` / `easy_add_then_compare`: composite_final=-4.425, component_mean_final=-4.521, diff=0.096
- `mean_logprob_correct` / `easy_reverse_then_copy`: composite_final=-5.416, component_mean_final=-4.900, diff=-0.515
- `mean_correct_margin` / `easy_add_then_compare`: composite_final=-0.318, component_mean_final=-0.567, diff=0.249
- `mean_correct_margin` / `easy_reverse_then_copy`: composite_final=-1.125, component_mean_final=-0.844, diff=-0.281
- `mean_correct_mrr` / `easy_add_then_compare`: composite_final=0.573, component_mean_final=0.507, diff=0.066
- `mean_correct_mrr` / `easy_reverse_then_copy`: composite_final=0.469, component_mean_final=0.536, diff=-0.068
- `mean_logprob_margin` / `easy_add_then_compare`: composite_final=0.301, component_mean_final=0.480, diff=-0.179
- `mean_logprob_margin` / `easy_reverse_then_copy`: composite_final=0.901, component_mean_final=0.728, diff=0.173

## Claim boundary
Use continuous-score outputs as calibration and observational bridge evidence only. They can show that a slice moves below top-1 accuracy, but they cannot establish causal dependency without interventions.
