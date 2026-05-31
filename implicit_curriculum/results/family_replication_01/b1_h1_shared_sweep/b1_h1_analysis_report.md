# B1 H1 shared-sweep analysis report

This report analyzes ordering and sign-stability across B1 sequence-DSL transformer configs/seeds. It is an H1 analysis only; it does not test H2 mediation or H3 causal dependency.

Primary analysis metric: `token_accuracy` threshold `0.7`.

## Threshold sensitivity, base config/all tasks

- exact_match threshold `0.2`: acq=0.320, freq=0.049, learn=0.041, utility=-0.024
- exact_match threshold `0.5`: acq=0.320, freq=-0.033, learn=0.004, utility=-0.012
- token_accuracy threshold `0.5`: acq=0.612, freq=-0.391, learn=-0.638, utility=-0.066
- token_accuracy threshold `0.7`: acq=0.572, freq=-0.431, learn=-0.672, utility=-0.027
- token_accuracy threshold `0.85`: acq=0.320, freq=0.000, learn=0.000, utility=0.000

## Sign stability

- all / frequency: sign-rate=1.000, mean-rho=-0.395, n_configs=6
- all / reference_learnability: sign-rate=0.000, mean-rho=-0.635, n_configs=6
- all / formal_utility: sign-rate=1.000, mean-rho=-0.053, n_configs=6
- true_tasks_atomic_composite / frequency: sign-rate=1.000, mean-rho=-0.319, n_configs=6
- true_tasks_atomic_composite / reference_learnability: sign-rate=0.000, mean-rho=-0.466, n_configs=6
- true_tasks_atomic_composite / formal_utility: sign-rate=0.000, mean-rho=0.143, n_configs=6
- kind=atomic / frequency: sign-rate=1.000, mean-rho=-0.433, n_configs=6
- kind=atomic / reference_learnability: sign-rate=0.000, mean-rho=-0.889, n_configs=6
- kind=atomic / formal_utility: sign-rate=1.000, mean-rho=-0.070, n_configs=6
- kind=composite / frequency: sign-rate=1.000, mean-rho=-0.237, n_configs=6
- kind=composite / reference_learnability: sign-rate=nan, mean-rho=nan, n_configs=0
- kind=composite / formal_utility: sign-rate=nan, mean-rho=nan, n_configs=0

## Config summary, primary metric

- base: acq=0.725, freq=-0.352, learn=-0.517, utility=0.165
- batch_large: acq=0.675, freq=-0.297, learn=-0.428, utility=0.119
- batch_small: acq=0.762, freq=-0.338, learn=-0.486, utility=0.149
- lr_high: acq=0.762, freq=-0.318, learn=-0.463, utility=0.134
- lr_low: acq=0.650, freq=-0.243, learn=-0.410, utility=0.125
- wd_zero: acq=0.731, freq=-0.363, learn=-0.494, utility=0.165

## Frequency realization

- base seed `0`: Spearman=1.000, MAE=0.000
- base seed `1`: Spearman=0.999, MAE=0.000
- base seed `2`: Spearman=1.000, MAE=0.000
- base seed `3`: Spearman=1.000, MAE=0.000
- base seed `4`: Spearman=1.000, MAE=0.000
- base seed `5`: Spearman=1.000, MAE=0.000
- base seed `6`: Spearman=1.000, MAE=0.000
- base seed `7`: Spearman=1.000, MAE=0.000
- base seed `8`: Spearman=1.000, MAE=0.000
- base seed `9`: Spearman=0.999, MAE=0.000

## Decision rule

GREEN for H1 requires nonzero/non-saturated acquisition across configs and stable expected signs, especially learnability positive and frequency negative within true-task/atomic strata. Utility can remain exploratory until the task graph has deeper downstream structure.