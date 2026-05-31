# Pythia observational threshold-sensitivity analysis

This analysis is observational. Thresholds diagnose whether the pilot is in a measurable regime; they do not create causal evidence.

- metric: `accuracy`
- thresholds: `0.2, 0.3, 0.4, 0.5`
- slices: `8`
- models: `1`

## Slice calibration
- `easy_add_then_compare` (composite): final=0.312, max=0.312, AUC=0.289, status=usable_or_near_usable
- `easy_add_1d` (atomic): final=0.281, max=0.281, AUC=0.246, status=too_hard_or_uninformative
- `easy_copy_word` (atomic): final=0.281, max=0.281, AUC=0.203, status=too_hard_or_uninformative
- `easy_reverse_two_words` (atomic): final=0.250, max=0.328, AUC=0.270, status=usable_or_near_usable
- `easy_color_surface` (surface_control): final=0.234, max=0.234, AUC=0.234, status=too_hard_or_uninformative
- `easy_animals_surface` (surface_control): final=0.203, max=0.203, AUC=0.203, status=too_hard_or_uninformative
- `easy_reverse_then_copy` (composite): final=0.156, max=0.281, AUC=0.188, status=too_hard_or_uninformative
- `easy_compare_1d` (atomic): final=0.125, max=0.281, AUC=0.156, status=too_hard_or_uninformative

## Threshold acquisition summary
- `EleutherAI/pythia-70m` threshold `0.2`: acq=1.000, freq-rho=0.541, learn-rho=-0.463
- `EleutherAI/pythia-70m` threshold `0.3`: acq=0.333, freq-rho=nan, learn-rho=nan
- `EleutherAI/pythia-70m` threshold `0.4`: acq=0.000, freq-rho=nan, learn-rho=nan
- `EleutherAI/pythia-70m` threshold `0.5`: acq=0.000, freq-rho=nan, learn-rho=nan

## H2 residual availability
- threshold `0.2`: composite rows=2, valid residual rows=2
  - `easy_reverse_then_copy` residual=-10.397, final=0.156
  - `easy_add_then_compare` residual=-11.090, final=0.312
- threshold `0.3`: composite rows=2, valid residual rows=0
- threshold `0.4`: composite rows=2, valid residual rows=0
- threshold `0.5`: composite rows=2, valid residual rows=0

## Claim boundary
Use this as calibration for a Pythia-style bridge. If acquisition appears only at low thresholds or only in final/AUC, describe it as subthreshold observational signal, not acquisition evidence and never causal evidence.
