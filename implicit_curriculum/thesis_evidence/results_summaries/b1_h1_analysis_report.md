# B1 H1 shared-sweep analysis report

This report analyzes ordering and sign-stability across B1 sequence-DSL transformer configs/seeds. It is an H1 analysis only; it does not test H2 mediation or H3 causal dependency.

Primary analysis metric: `token_accuracy` threshold `0.7`.

## Threshold sensitivity, base config/all tasks

- exact_match threshold `0.2`: acq=0.608, freq=-0.040, learn=0.665, utility=-0.132
- exact_match threshold `0.5`: acq=0.280, freq=0.078, learn=-0.033, utility=0.064
- token_accuracy threshold `0.5`: acq=0.852, freq=-0.070, learn=0.383, utility=-0.215
- token_accuracy threshold `0.7`: acq=0.736, freq=-0.065, learn=0.521, utility=-0.160
- token_accuracy threshold `0.85`: acq=0.444, freq=-0.076, learn=0.652, utility=-0.107

## Sign stability

- all / frequency: sign-rate=1.000, mean-rho=-0.066, n_configs=6
- all / reference_learnability: sign-rate=1.000, mean-rho=0.537, n_configs=6
- all / formal_utility: sign-rate=1.000, mean-rho=-0.154, n_configs=6
- true_tasks_atomic_composite / frequency: sign-rate=1.000, mean-rho=-0.083, n_configs=6
- true_tasks_atomic_composite / reference_learnability: sign-rate=1.000, mean-rho=0.366, n_configs=6
- true_tasks_atomic_composite / formal_utility: sign-rate=1.000, mean-rho=-0.333, n_configs=6
- kind=atomic / frequency: sign-rate=1.000, mean-rho=-0.318, n_configs=6
- kind=atomic / reference_learnability: sign-rate=1.000, mean-rho=0.731, n_configs=6
- kind=atomic / formal_utility: sign-rate=1.000, mean-rho=-0.327, n_configs=6
- kind=composite / frequency: sign-rate=0.000, mean-rho=0.367, n_configs=6
- kind=composite / reference_learnability: sign-rate=nan, mean-rho=nan, n_configs=0
- kind=composite / formal_utility: sign-rate=nan, mean-rho=nan, n_configs=0

## Config summary, primary metric

- base: acq=0.912, freq=-0.097, learn=0.343, utility=-0.336
- batch_large: acq=0.812, freq=-0.034, learn=0.474, utility=-0.309
- batch_small: acq=0.963, freq=-0.123, learn=0.280, utility=-0.340
- lr_high: acq=0.988, freq=-0.109, learn=0.285, utility=-0.371
- lr_low: acq=0.812, freq=-0.022, learn=0.475, utility=-0.314
- wd_zero: acq=0.906, freq=-0.110, learn=0.342, utility=-0.328

## Frequency realization

- base seed `0`: Spearman=1.000, MAE=0.000
- base seed `1`: Spearman=1.000, MAE=0.000
- base seed `2`: Spearman=1.000, MAE=0.000
- base seed `3`: Spearman=0.999, MAE=0.000
- base seed `4`: Spearman=1.000, MAE=0.000
- base seed `5`: Spearman=0.999, MAE=0.000
- base seed `6`: Spearman=0.999, MAE=0.000
- base seed `7`: Spearman=1.000, MAE=0.000
- base seed `8`: Spearman=0.999, MAE=0.000
- base seed `9`: Spearman=0.999, MAE=0.000

## Decision rule

GREEN for H1 requires nonzero/non-saturated acquisition across configs and stable expected signs, especially learnability positive and frequency negative within true-task/atomic strata. Utility can remain exploratory until the task graph has deeper downstream structure.