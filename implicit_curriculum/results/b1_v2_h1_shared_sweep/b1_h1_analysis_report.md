# B1 H1 shared-sweep analysis report

This report analyzes ordering and sign-stability across B1 sequence-DSL transformer configs/seeds. It is an H1 analysis only; it does not test H2 mediation or H3 causal dependency.

Primary analysis metric: `token_accuracy` threshold `0.7`.

## Threshold sensitivity, base config/all tasks

- exact_match threshold `0.2`: acq=0.328, freq=0.161, learn=0.052, utility=0.078
- exact_match threshold `0.5`: acq=0.320, freq=-0.065, learn=0.054, utility=-0.014
- token_accuracy threshold `0.5`: acq=0.752, freq=0.197, learn=0.505, utility=-0.009
- token_accuracy threshold `0.7`: acq=0.696, freq=0.272, learn=0.597, utility=-0.031
- token_accuracy threshold `0.85`: acq=0.320, freq=0.038, learn=-0.011, utility=-0.018

## Sign stability

- all / frequency: sign-rate=0.000, mean-rho=0.253, n_configs=6
- all / reference_learnability: sign-rate=1.000, mean-rho=0.564, n_configs=6
- all / formal_utility: sign-rate=0.500, mean-rho=0.016, n_configs=6
- true_tasks_atomic_composite / frequency: sign-rate=0.000, mean-rho=0.105, n_configs=6
- true_tasks_atomic_composite / reference_learnability: sign-rate=1.000, mean-rho=0.423, n_configs=6
- true_tasks_atomic_composite / formal_utility: sign-rate=1.000, mean-rho=-0.114, n_configs=6
- kind=atomic / frequency: sign-rate=0.000, mean-rho=0.244, n_configs=6
- kind=atomic / reference_learnability: sign-rate=1.000, mean-rho=0.900, n_configs=6
- kind=atomic / formal_utility: sign-rate=0.000, mean-rho=0.272, n_configs=6
- kind=composite / frequency: sign-rate=1.000, mean-rho=-0.121, n_configs=6
- kind=composite / reference_learnability: sign-rate=nan, mean-rho=nan, n_configs=0
- kind=composite / formal_utility: sign-rate=nan, mean-rho=nan, n_configs=0

## Config summary, primary metric

- base: acq=0.875, freq=0.130, learn=0.460, utility=-0.172
- batch_large: acq=0.800, freq=0.103, learn=0.408, utility=-0.061
- batch_small: acq=0.900, freq=0.070, learn=0.358, utility=-0.079
- lr_high: acq=0.875, freq=0.119, learn=0.478, utility=-0.183
- lr_low: acq=0.775, freq=0.076, learn=0.378, utility=-0.017
- wd_zero: acq=0.875, freq=0.131, learn=0.457, utility=-0.171

## Frequency realization

- base seed `0`: Spearman=1.000, MAE=0.000
- base seed `1`: Spearman=1.000, MAE=0.000
- base seed `2`: Spearman=1.000, MAE=0.000
- base seed `3`: Spearman=1.000, MAE=0.000
- base seed `4`: Spearman=0.999, MAE=0.000
- batch_large seed `0`: Spearman=1.000, MAE=0.000
- batch_large seed `1`: Spearman=1.000, MAE=0.000
- batch_large seed `2`: Spearman=0.999, MAE=0.000
- batch_large seed `3`: Spearman=1.000, MAE=0.000
- batch_large seed `4`: Spearman=1.000, MAE=0.000

## Decision rule

GREEN for H1 requires nonzero/non-saturated acquisition across configs and stable expected signs, especially learnability positive and frequency negative within true-task/atomic strata. Utility can remain exploratory until the task graph has deeper downstream structure.