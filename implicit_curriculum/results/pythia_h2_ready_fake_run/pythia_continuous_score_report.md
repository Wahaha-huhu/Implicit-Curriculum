# Pythia observational continuous-score analysis

This analysis is observational. Continuous scores can reveal subthreshold movement, but they do not establish causal dependency.

- metrics analyzed: `accuracy, mean_logprob_correct, mean_correct_margin, mean_correct_mrr, mean_logprob_margin`
- H2 target summary: `final_metric`
- slices: `29`
- models: `1`

## Best final slices by metric
### `accuracy`
- `arith_add_small` (atomic): final=0.260, delta=0.060, AUC=0.230, status=weak_or_uninformative
- `arith_compare` (atomic): final=0.260, delta=0.060, AUC=0.230, status=weak_or_uninformative
- `arith_even` (atomic): final=0.260, delta=0.060, AUC=0.230, status=weak_or_uninformative
- `arith_max2` (atomic): final=0.260, delta=0.060, AUC=0.230, status=weak_or_uninformative
- `arith_min2` (atomic): final=0.260, delta=0.060, AUC=0.230, status=weak_or_uninformative
- `arith_sub_small` (atomic): final=0.260, delta=0.060, AUC=0.230, status=weak_or_uninformative
- `semantic_color_lookup` (atomic): final=0.260, delta=0.060, AUC=0.230, status=weak_or_uninformative
- `syntax_is_are` (atomic): final=0.260, delta=0.060, AUC=0.230, status=weak_or_uninformative
### `mean_correct_margin`
- `arith_add_small` (atomic): final=-0.360, delta=0.140, AUC=-0.430, status=usable_or_near_usable
- `arith_compare` (atomic): final=-0.360, delta=0.140, AUC=-0.430, status=usable_or_near_usable
- `arith_even` (atomic): final=-0.360, delta=0.140, AUC=-0.430, status=usable_or_near_usable
- `arith_max2` (atomic): final=-0.360, delta=0.140, AUC=-0.430, status=usable_or_near_usable
- `arith_min2` (atomic): final=-0.360, delta=0.140, AUC=-0.430, status=usable_or_near_usable
- `arith_sub_small` (atomic): final=-0.360, delta=0.140, AUC=-0.430, status=usable_or_near_usable
- `semantic_color_lookup` (atomic): final=-0.360, delta=0.140, AUC=-0.430, status=usable_or_near_usable
- `syntax_is_are` (atomic): final=-0.360, delta=0.140, AUC=-0.430, status=usable_or_near_usable
### `mean_correct_mrr`
- `arith_add_small` (atomic): final=0.540, delta=0.040, AUC=0.520, status=usable_or_near_usable
- `arith_compare` (atomic): final=0.540, delta=0.040, AUC=0.520, status=usable_or_near_usable
- `arith_even` (atomic): final=0.540, delta=0.040, AUC=0.520, status=usable_or_near_usable
- `arith_max2` (atomic): final=0.540, delta=0.040, AUC=0.520, status=usable_or_near_usable
- `arith_min2` (atomic): final=0.540, delta=0.040, AUC=0.520, status=usable_or_near_usable
- `arith_sub_small` (atomic): final=0.540, delta=0.040, AUC=0.520, status=usable_or_near_usable
- `comp_add_then_compare` (composite): final=0.540, delta=0.040, AUC=0.520, status=usable_or_near_usable
- `comp_add_then_even` (composite): final=0.540, delta=0.040, AUC=0.520, status=usable_or_near_usable
### `mean_logprob_correct`
- `arith_add_small` (atomic): final=-3.960, delta=1.040, AUC=-4.480, status=usable_or_near_usable
- `arith_compare` (atomic): final=-3.960, delta=1.040, AUC=-4.480, status=usable_or_near_usable
- `arith_even` (atomic): final=-3.960, delta=1.040, AUC=-4.480, status=usable_or_near_usable
- `arith_max2` (atomic): final=-3.960, delta=1.040, AUC=-4.480, status=usable_or_near_usable
- `arith_min2` (atomic): final=-3.960, delta=1.040, AUC=-4.480, status=usable_or_near_usable
- `arith_sub_small` (atomic): final=-3.960, delta=1.040, AUC=-4.480, status=usable_or_near_usable
- `semantic_color_lookup` (atomic): final=-3.960, delta=1.040, AUC=-4.480, status=usable_or_near_usable
- `syntax_is_are` (atomic): final=-3.960, delta=1.040, AUC=-4.480, status=usable_or_near_usable
### `mean_logprob_margin`
- `arith_add_small` (atomic): final=0.240, delta=0.240, AUC=0.120, status=usable_or_near_usable
- `arith_compare` (atomic): final=0.240, delta=0.240, AUC=0.120, status=usable_or_near_usable
- `arith_even` (atomic): final=0.240, delta=0.240, AUC=0.120, status=usable_or_near_usable
- `arith_max2` (atomic): final=0.240, delta=0.240, AUC=0.120, status=usable_or_near_usable
- `arith_min2` (atomic): final=0.240, delta=0.240, AUC=0.120, status=usable_or_near_usable
- `arith_sub_small` (atomic): final=0.240, delta=0.240, AUC=0.120, status=usable_or_near_usable
- `semantic_color_lookup` (atomic): final=0.240, delta=0.240, AUC=0.120, status=usable_or_near_usable
- `syntax_is_are` (atomic): final=0.240, delta=0.240, AUC=0.120, status=usable_or_near_usable

## H1-like continuous signatures
- `fake` / `accuracy`: mean_final=0.256, mean_delta=0.056, rho(freq, final)=0.849, rho(learn, final)=-0.836, rho(freq, delta)=0.849, rho(learn, delta)=-0.836
- `fake` / `mean_correct_margin`: mean_final=-0.364, mean_delta=0.136, rho(freq, final)=0.849, rho(learn, final)=-0.836, rho(freq, delta)=0.849, rho(learn, delta)=-0.836
- `fake` / `mean_correct_mrr`: mean_final=0.540, mean_delta=0.040, rho(freq, final)=nan, rho(learn, final)=nan, rho(freq, delta)=nan, rho(learn, delta)=nan
- `fake` / `mean_logprob_correct`: mean_final=-3.964, mean_delta=1.036, rho(freq, final)=0.849, rho(learn, final)=-0.836, rho(freq, delta)=0.849, rho(learn, delta)=-0.836
- `fake` / `mean_logprob_margin`: mean_final=0.236, mean_delta=0.236, rho(freq, final)=0.849, rho(learn, final)=-0.836, rho(freq, delta)=0.849, rho(learn, delta)=-0.836

## H2-like continuous residuals
- `accuracy`: n=10, mean residual=-0.097
  - underperforming composite `comp_add_then_compare`: residual=-0.097, observed=0.250, predicted=0.347
  - underperforming composite `comp_add_then_even`: residual=-0.097, observed=0.250, predicted=0.347
  - underperforming composite `comp_first_then_same`: residual=-0.097, observed=0.250, predicted=0.347
- `mean_correct_margin`: n=10, mean residual=0.110
  - underperforming composite `comp_add_then_even`: residual=0.110, observed=-0.370, predicted=-0.480
  - underperforming composite `comp_first_then_same`: residual=0.110, observed=-0.370, predicted=-0.480
  - underperforming composite `comp_max_then_compare`: residual=0.110, observed=-0.370, predicted=-0.480
- `mean_correct_mrr`: n=10, mean residual=-0.180
  - underperforming composite `comp_add_then_compare`: residual=-0.180, observed=0.540, predicted=0.720
  - underperforming composite `comp_add_then_even`: residual=-0.180, observed=0.540, predicted=0.720
  - underperforming composite `comp_first_then_same`: residual=-0.180, observed=0.540, predicted=0.720
- `mean_logprob_correct`: n=10, mean residual=1.310
  - underperforming composite `comp_reverse_then_same`: residual=1.310, observed=-3.970, predicted=-5.280
  - underperforming composite `comp_add_then_compare`: residual=1.310, observed=-3.970, predicted=-5.280
  - underperforming composite `comp_first_then_same`: residual=1.310, observed=-3.970, predicted=-5.280
- `mean_logprob_margin`: n=10, mean residual=-0.090
  - underperforming composite `comp_sub_then_compare`: residual=-0.090, observed=0.230, predicted=0.320
  - underperforming composite `comp_reverse_then_same`: residual=-0.090, observed=0.230, predicted=0.320
  - underperforming composite `comp_add_then_compare`: residual=-0.090, observed=0.230, predicted=0.320

## Component coupling
Component coupling compares composite continuous scores to the mean of its listed primitive slices. It is descriptive only.
- `accuracy` / `comp_add_then_compare`: composite_final=0.250, component_mean_final=0.260, diff=-0.010
- `accuracy` / `comp_add_then_even`: composite_final=0.250, component_mean_final=0.260, diff=-0.010
- `accuracy` / `comp_first_then_same`: composite_final=0.250, component_mean_final=0.260, diff=-0.010
- `accuracy` / `comp_max_then_compare`: composite_final=0.250, component_mean_final=0.260, diff=-0.010
- `accuracy` / `comp_retrieve_then_color`: composite_final=0.250, component_mean_final=0.260, diff=-0.010
- `accuracy` / `comp_retrieve_then_compare`: composite_final=0.250, component_mean_final=0.260, diff=-0.010
- `accuracy` / `comp_reverse_then_first`: composite_final=0.250, component_mean_final=0.260, diff=-0.010
- `accuracy` / `comp_reverse_then_last`: composite_final=0.250, component_mean_final=0.260, diff=-0.010
- `accuracy` / `comp_reverse_then_same`: composite_final=0.250, component_mean_final=0.260, diff=-0.010
- `accuracy` / `comp_sub_then_compare`: composite_final=0.250, component_mean_final=0.260, diff=-0.010

## Claim boundary
Use continuous-score outputs as calibration and observational bridge evidence only. They can show that a slice moves below top-1 accuracy, but they cannot establish causal dependency without interventions.
