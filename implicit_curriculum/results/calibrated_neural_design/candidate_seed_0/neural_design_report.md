# Neural design gate report

This gate generates an actual trainable Boolean task family and checks whether realized structural properties are identifiable enough for H1/H2-style neural experiments.

Passed: **True**
Attempts used: `1`

## Key diagnostics

- n_tasks: `34`
- design_condition_number: `1.253`
- vif_frequency: `1.036`
- vif_reference_learnability: `1.051`
- vif_formal_utility: `1.017`
- max_abs_pearson: `0.1848`
- max_abs_spearman: `0.3089`

## Interpretation

If this gate passes, the generated neural family is suitable for a first ordering pilot. It does not yet prove that neural acquisition follows the intended structural predictors; it only licenses fitting them without obvious collinearity failure.