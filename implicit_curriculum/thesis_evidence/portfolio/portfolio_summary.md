# Thesis Evidence Portfolio Summary

This report is generated from `thesis_evidence/` and is intentionally conservative. It distinguishes supported controlled-pilot claims from unsupported broad mechanism claims.

## Current overall conclusion

The evidence now supports a scoped controlled-mechanism story: structural properties predict acquisition order in the B1 sequence-transformer substrate, especially reference learnability; atomic timing is captured by simple configuration-dependent predictors; atomic-parallel residuals identify candidate composite dependency sites; and one component-composite pair (`A02_substitute → C06`) shows pair-specific causal sensitivity under stronger interventions. The evidence does not support a universal law of LLM training or uniform dependency across all formal components.

## Claim dashboard

| Experiment | Status | Supported claim | Caveat |
|---|---|---|---|
| Exp0 synthetic recovery | green | Analysis pipeline recovers known synthetic worlds sufficiently for downstream pilots. | Synthetic validation only; not a neural result. |
| B2 sparse parity | yellow-green | Quanta-style baseline: frequency effect is strong when learnable (e.g. threshold .85 rho≈-0.71). | Acquisition coverage remains modest (≈0.242); final use should improve coverage. |
| B1 H1 ordering/sign stability | green-pilot | Reference learnability robustly predicts later acquisition across configs (mean rho≈0.537); atomic frequency is expected-direction but weaker (rho≈-0.318). | Pilot grid only; frequency is weak/reversed inside composites. |
| B1 H2 predictor ladder/residuals | green-pilot | Atomic acquisition is explained by simple one-factor predictors with config drift; composite residuals select intervention candidates. | Residuals are observational and do not prove dependency. |
| B1 H3 C06 interventions | green-yellow pair-specific | A02_substitute → C06 shows pair-specific causal evidence under exact pretraining and strong corruption beyond same/different-operation controls. | A00_copy → C06 is weak/mixed; result is not a universal component-dependency claim. |

## Claims currently safe to write

1. The analysis pipeline passes synthetic recovery before neural use.
2. Sparse parity provides a contrasting frequency-dominated/quanta-style regime, but should be strengthened for final quantitative claims.
3. In B1, reference learnability robustly predicts later acquisition across the pilot configuration grid; frequency is weaker and stratum-dependent.
4. Atomic acquisition is captured by simple one-factor predictors whose selected factor drifts by configuration.
5. Composite residuals are useful for selecting causal intervention targets but do not themselves prove dependency.
6. Strong H3 interventions give pair-specific causal evidence for `A02_substitute → C06`, while `A00_copy → C06` is weak/mixed.

## Claims not yet safe

- A universal closed-form law of acquisition timing.
- Frequency universally determining ordering in sequence-transformer tasks.
- Uniform component-to-composite developmental dependency.
- Any causal claim about real LLM training.
