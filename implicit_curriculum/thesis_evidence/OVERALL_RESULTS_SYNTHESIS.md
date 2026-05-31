# Overall Results Synthesis after v1.4

This file summarizes the current state of evidence for thesis writing. It should be updated as new results are added.

## Current defensible thesis story

The evidence supports a **scoped controlled-mechanism map**, not a universal mechanism of LLM training.

1. **Synthetic recovery gate:** the analysis pipeline can recover known synthetic mechanisms before neural experiments.
2. **B2 sparse parity baseline:** sparse parity behaves like a frequency/difficulty-dominated regime, giving a quanta-style contrast, though acquisition coverage should be improved before final quantitative claims.
3. **B1 sequence-DSL transformer substrate:** the controlled sequence task family is trainable, non-saturated, and suitable for ordering/predictability analyses.
4. **H1 ordering:** reference learnability robustly predicts later acquisition across the B1 pilot configuration grid; frequency has weaker expected-direction effects, strongest in atomics and not universal within composites.
5. **H2 predictability/residuals:** atomic acquisition is captured by simple one-factor predictors, with the selected factor drifting by configuration; residuals under the atomic parallel-null identify composite candidates for intervention.
6. **H3 interventions:** the strongest pair-specific result is `A02_substitute → C06_reverse_then_substitute_02_00`. Exact component pretraining accelerates the composite beyond same-operation and different-operation controls, and exact strong corruption hurts the composite beyond those controls. The `A00_copy → C06` row is weak/mixed, so dependency is component-specific rather than uniform.

## Strongest current positive result

For `A02_substitute → C06_reverse_then_substitute_02_00`:

- exact pretraining vs same-operation pretraining: censored acquisition shift ≈ `-243,712`, expected-direction rate `1.000`;
- exact pretraining vs different-operation pretraining: censored acquisition shift ≈ `-238,771`, expected-direction rate `1.000`;
- exact strong corruption vs same-operation corruption: censored shift ≈ `+39,603`, expected-direction rate `0.800`;
- exact strong corruption vs different-operation corruption: censored shift ≈ `+30,618`, expected-direction rate `0.800`.

This supports **pair-specific causal sensitivity** in the controlled B1 setting.

## Main negative/mixed result

For `A00_copy → C06_reverse_then_substitute_02_00`, upweight and delay were weak/mixed, with only corruption giving partial support. This prevents any claim that all formal components causally enable the composite.

## Claim boundary

Safe:

- structural properties, especially reference learnability, predict acquisition order in controlled B1 pilots;
- simple atomic predictors work within configurations, with coefficient/predictor drift;
- residuals are useful for selecting intervention targets;
- one exact component-composite pair shows causal sensitivity under stronger interventions.

Unsafe:

- universal closed-form acquisition law;
- frequency-only explanation for sequence-transformer tasks;
- uniform component dependency;
- causal claims about real LLM training.

## Next evidence needed

1. Test another delayed composite, such as C07.
2. Replicate the A02→C06 result on a second generated B1 family.
3. Add mediator diagnostics: early gradient alignment, representation/probe transfer, or activation patching.
4. Improve B2 sparse-parity acquisition coverage for a cleaner frequency baseline.
