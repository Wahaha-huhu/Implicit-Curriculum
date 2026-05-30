# Simulated recovery gate report

This gate checks whether the analysis pipeline can recover known synthetic worlds before expensive neural training.

## Design diagnostics

- `n_rows`: 32.0
- `design_condition_number`: 1.4306720446004844
- `vif_frequency`: 1.1327234757689515
- `vif_reference_learnability`: 1.1338413344193539
- `vif_formal_utility`: 1.0011787708369944
- `pearson_frequency__reference_learnability`: -0.3420622958177775
- `spearman_frequency__reference_learnability`: -0.36180351906158353
- `binned_mi_frequency__reference_learnability`: 0.2572074885107579
- `pearson_frequency__formal_utility`: -0.002089706519837345
- `spearman_frequency__formal_utility`: 0.014662756598240468
- `binned_mi_frequency__formal_utility`: 0.22234130861791268
- `pearson_reference_learnability__formal_utility`: -0.031468500411231295
- `spearman_reference_learnability__formal_utility`: 0.006964809384164223
- `binned_mi_reference_learnability__formal_utility`: 0.3168806917883967
- `attempts_used`: 1.0
- `passed`: True

## Recovery verdict

| true_mechanism | n_replicates | selected_frequency_only_rate | selected_learnability_only_rate | selected_freq_learn_rate | selected_three_factor_rate | mean_composite_residual | positive_residual_rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| dependency_gated | 100 | 0.03 | 0.02 | 0.05 | 0.9 | 1.358 | 1 |
| frequency_only | 100 | 1 | 0 | 0 | 0 | 0.003987 | 0.5 |
| learnability_only | 100 | 0 | 1 | 0 | 0 | -0.005731 | 0.48 |
| three_factor | 100 | 0 | 0 | 0 | 1 | -0.005015 | 0.44 |
