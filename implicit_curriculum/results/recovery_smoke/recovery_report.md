# Simulated recovery gate report

This gate checks whether the analysis pipeline can recover known synthetic worlds before expensive neural training.

## Design diagnostics

- `n_rows`: 12.0
- `design_condition_number`: 35.059056721005625
- `vif_frequency`: 1.0593087109351824
- `vif_reference_learnability`: 1.0020669507813307
- `vif_formal_utility`: 1.060802537910596
- `pearson_frequency__reference_learnability`: 0.022385336403683655
- `spearman_frequency__reference_learnability`: -0.06993006993006995
- `binned_mi_frequency__reference_learnability`: 0.40320660254510515
- `pearson_frequency__formal_utility`: -0.2363098991716459
- `spearman_frequency__formal_utility`: -0.1328671328671329
- `binned_mi_frequency__formal_utility`: 0.6342556627317535
- `pearson_reference_learnability__formal_utility`: -0.04368755193411096
- `spearman_reference_learnability__formal_utility`: 0.08391608391608392
- `binned_mi_reference_learnability__formal_utility`: 0.5187311326384293
- `attempts_used`: 14.0
- `passed`: True

## Recovery verdict

| true_mechanism | n_replicates | selected_frequency_only_rate | selected_learnability_only_rate | selected_freq_learn_rate | selected_three_factor_rate | mean_composite_residual | positive_residual_rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| dependency_gated | 3 | 0 | 1 | 0 | 0 | 1.059 | 1 |
| frequency_only | 3 | 1 | 0 | 0 | 0 | 0.03957 | 0.6667 |
| learnability_only | 3 | 0 | 0.6667 | 0.3333 | 0 | 0.0166 | 0.6667 |
| three_factor | 3 | 0 | 0 | 0 | 1 | 0.06897 | 0.6667 |
