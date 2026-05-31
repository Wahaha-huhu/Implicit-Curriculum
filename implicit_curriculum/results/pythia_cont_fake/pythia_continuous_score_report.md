# Pythia observational continuous-score analysis

This analysis is observational. Continuous scores can reveal subthreshold movement, but they do not establish causal dependency.

- metrics analyzed: `accuracy, mean_logprob_correct, mean_correct_margin, mean_correct_mrr, mean_logprob_margin`
- H2 target summary: `final_metric`
- slices: `8`
- models: `1`

## Best final slices by metric
### `accuracy`
- `easy_add_1d` (atomic): final=0.360, delta=0.160, AUC=0.280, status=usable_or_near_usable
- `easy_reverse_two_words` (atomic): final=0.360, delta=0.160, AUC=0.280, status=usable_or_near_usable
- `easy_copy_word` (atomic): final=0.360, delta=0.160, AUC=0.280, status=usable_or_near_usable
- `easy_compare_1d` (atomic): final=0.360, delta=0.160, AUC=0.280, status=usable_or_near_usable
- `easy_add_then_compare` (composite): final=0.300, delta=0.100, AUC=0.250, status=usable_or_near_usable
- `easy_reverse_then_copy` (composite): final=0.300, delta=0.100, AUC=0.250, status=usable_or_near_usable
- `easy_color_surface` (surface_control): final=0.260, delta=0.060, AUC=0.230, status=weak_or_uninformative
- `easy_animals_surface` (surface_control): final=0.260, delta=0.060, AUC=0.230, status=weak_or_uninformative
### `mean_correct_margin`
- `easy_add_1d` (atomic): final=-0.140, delta=0.160, AUC=-0.220, status=usable_or_near_usable
- `easy_reverse_two_words` (atomic): final=-0.140, delta=0.160, AUC=-0.220, status=usable_or_near_usable
- `easy_copy_word` (atomic): final=-0.140, delta=0.160, AUC=-0.220, status=usable_or_near_usable
- `easy_compare_1d` (atomic): final=-0.140, delta=0.160, AUC=-0.220, status=usable_or_near_usable
- `easy_add_then_compare` (composite): final=-0.200, delta=0.100, AUC=-0.250, status=usable_or_near_usable
- `easy_reverse_then_copy` (composite): final=-0.200, delta=0.100, AUC=-0.250, status=usable_or_near_usable
- `easy_color_surface` (surface_control): final=-0.240, delta=0.060, AUC=-0.270, status=usable_or_near_usable
- `easy_animals_surface` (surface_control): final=-0.240, delta=0.060, AUC=-0.270, status=usable_or_near_usable
### `mean_correct_mrr`
- `easy_add_1d` (atomic): final=0.340, delta=0.040, AUC=0.320, status=usable_or_near_usable
- `easy_reverse_two_words` (atomic): final=0.340, delta=0.040, AUC=0.320, status=usable_or_near_usable
- `easy_copy_word` (atomic): final=0.340, delta=0.040, AUC=0.320, status=usable_or_near_usable
- `easy_compare_1d` (atomic): final=0.340, delta=0.040, AUC=0.320, status=usable_or_near_usable
- `easy_add_then_compare` (composite): final=0.325, delta=0.025, AUC=0.312, status=usable_or_near_usable
- `easy_reverse_then_copy` (composite): final=0.325, delta=0.025, AUC=0.312, status=usable_or_near_usable
- `easy_color_surface` (surface_control): final=0.315, delta=0.015, AUC=0.307, status=weak_or_uninformative
- `easy_animals_surface` (surface_control): final=0.315, delta=0.015, AUC=0.307, status=weak_or_uninformative
### `mean_logprob_correct`
- `easy_add_1d` (atomic): final=-2.640, delta=0.160, AUC=-2.720, status=usable_or_near_usable
- `easy_reverse_two_words` (atomic): final=-2.640, delta=0.160, AUC=-2.720, status=usable_or_near_usable
- `easy_copy_word` (atomic): final=-2.640, delta=0.160, AUC=-2.720, status=usable_or_near_usable
- `easy_compare_1d` (atomic): final=-2.640, delta=0.160, AUC=-2.720, status=usable_or_near_usable
- `easy_add_then_compare` (composite): final=-2.700, delta=0.100, AUC=-2.750, status=usable_or_near_usable
- `easy_reverse_then_copy` (composite): final=-2.700, delta=0.100, AUC=-2.750, status=usable_or_near_usable
- `easy_color_surface` (surface_control): final=-2.740, delta=0.060, AUC=-2.770, status=usable_or_near_usable
- `easy_animals_surface` (surface_control): final=-2.740, delta=0.060, AUC=-2.770, status=usable_or_near_usable
### `mean_logprob_margin`
- `easy_add_1d` (atomic): final=0.200, delta=0.200, AUC=0.100, status=usable_or_near_usable
- `easy_add_then_compare` (composite): final=0.200, delta=0.200, AUC=0.100, status=usable_or_near_usable
- `easy_animals_surface` (surface_control): final=0.200, delta=0.200, AUC=0.100, status=usable_or_near_usable
- `easy_color_surface` (surface_control): final=0.200, delta=0.200, AUC=0.100, status=usable_or_near_usable
- `easy_compare_1d` (atomic): final=0.200, delta=0.200, AUC=0.100, status=usable_or_near_usable
- `easy_copy_word` (atomic): final=0.200, delta=0.200, AUC=0.100, status=usable_or_near_usable
- `easy_reverse_then_copy` (composite): final=0.200, delta=0.200, AUC=0.100, status=usable_or_near_usable
- `easy_reverse_two_words` (atomic): final=0.200, delta=0.200, AUC=0.100, status=usable_or_near_usable

## H1-like continuous signatures
- `fake` / `accuracy`: mean_final=0.340, mean_delta=0.140, rho(freq, final)=0.828, rho(learn, final)=-0.840, rho(freq, delta)=0.828, rho(learn, delta)=-0.840
- `fake` / `mean_correct_margin`: mean_final=-0.160, mean_delta=0.140, rho(freq, final)=0.828, rho(learn, final)=-0.840, rho(freq, delta)=0.828, rho(learn, delta)=-0.840
- `fake` / `mean_correct_mrr`: mean_final=0.335, mean_delta=0.035, rho(freq, final)=0.828, rho(learn, final)=-0.840, rho(freq, delta)=0.828, rho(learn, delta)=-0.840
- `fake` / `mean_logprob_correct`: mean_final=-2.660, mean_delta=0.140, rho(freq, final)=0.828, rho(learn, final)=-0.840, rho(freq, delta)=0.828, rho(learn, delta)=-0.840
- `fake` / `mean_logprob_margin`: mean_final=0.200, mean_delta=0.200, rho(freq, final)=nan, rho(learn, final)=nan, rho(freq, delta)=nan, rho(learn, delta)=nan

## H2-like continuous residuals
- No valid H2 continuous residuals; likely too few atomic slices or missing features.

## Component coupling
Component coupling compares composite continuous scores to the mean of its listed primitive slices. It is descriptive only.
- `accuracy` / `easy_add_then_compare`: composite_final=0.300, component_mean_final=0.360, diff=-0.060
- `accuracy` / `easy_reverse_then_copy`: composite_final=0.300, component_mean_final=0.360, diff=-0.060
- `mean_logprob_correct` / `easy_add_then_compare`: composite_final=-2.700, component_mean_final=-2.640, diff=-0.060
- `mean_logprob_correct` / `easy_reverse_then_copy`: composite_final=-2.700, component_mean_final=-2.640, diff=-0.060
- `mean_correct_margin` / `easy_add_then_compare`: composite_final=-0.200, component_mean_final=-0.140, diff=-0.060
- `mean_correct_margin` / `easy_reverse_then_copy`: composite_final=-0.200, component_mean_final=-0.140, diff=-0.060
- `mean_correct_mrr` / `easy_add_then_compare`: composite_final=0.325, component_mean_final=0.340, diff=-0.015
- `mean_correct_mrr` / `easy_reverse_then_copy`: composite_final=0.325, component_mean_final=0.340, diff=-0.015
- `mean_logprob_margin` / `easy_add_then_compare`: composite_final=0.200, component_mean_final=0.200, diff=0.000
- `mean_logprob_margin` / `easy_reverse_then_copy`: composite_final=0.200, component_mean_final=0.200, diff=0.000

## Claim boundary
Use continuous-score outputs as calibration and observational bridge evidence only. They can show that a slice moves below top-1 accuracy, but they cannot establish causal dependency without interventions.
