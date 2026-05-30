# Simulated recovery gate report

This gate checks whether the analysis pipeline can recover known synthetic worlds before expensive neural training.

## Design diagnostics

- `n_rows`: 20.0
- `design_condition_number`: 1.913532906714058
- `vif_frequency`: 1.4833933219045805
- `vif_reference_learnability`: 1.0047164099805368
- `vif_formal_utility`: 1.4777644194754413
- `pearson_frequency__reference_learnability`: -0.06318999282510171
- `spearman_frequency__reference_learnability`: -0.06165413533834586
- `binned_mi_frequency__reference_learnability`: 0.26205947507775207
- `pearson_frequency__formal_utility`: 0.5681772178234942
- `spearman_frequency__formal_utility`: 0.4616541353383458
- `binned_mi_frequency__formal_utility`: 0.3143842894542067
- `pearson_reference_learnability__formal_utility`: -0.01411093721361206
- `spearman_reference_learnability__formal_utility`: -0.010526315789473682
- `binned_mi_reference_learnability__formal_utility`: 0.4791761327544231
- `attempts_used`: 1.0
- `passed`: True

## Recovery verdict

| true_mechanism | n_replicates | selected_frequency_only_rate | selected_learnability_only_rate | selected_freq_learn_rate | selected_three_factor_rate | mean_composite_residual | positive_residual_rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| dependency_gated | 10 | 0.2 | 0 | 0 | 0.8 | 2.027 | 1 |
| frequency_only | 10 | 0.9 | 0 | 0 | 0.1 | 0.009352 | 0.6 |
| learnability_only | 10 | 0 | 1 | 0 | 0 | 0.003314 | 0.5 |
| three_factor | 10 | 0 | 0 | 0.3 | 0.7 | -0.04061 | 0.4 |
