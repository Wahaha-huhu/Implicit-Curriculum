# Cross-family controlled evidence synthesis

This document summarizes the controlled B1 evidence after adding the second generated family. It is intentionally conservative: it separates claims that replicate across families from claims that remain localized to one family or one component-composite pair.

## Summary

The controlled experiments now support a stronger methodological claim than a universal-mechanism claim.

- **Family 1** supports a localized exact-component dependency site: `A02_substitute → C06_reverse_then_substitute_02_00`. This pair has intervention evidence and early gradient-alignment support.
- **Family 2** replicates that acquisition is structured and that H2 residuals can identify problematic composites, but it does **not** replicate positive exact-component dependency under the current H3 settings.
- Family 2 exposes an important boundary condition: the largest residual composites can be too hard or only subthreshold-ready for intervention tests.

## Updated thesis-safe conclusion

The thesis should not claim that exact-component dependency is a universal rule of compositional acquisition. The stronger claim is that acquisition order and residuals are not self-interpreting. A controlled pipeline with matched interventions and readiness checks can distinguish at least three mechanisms:

1. exact-component dependency;
2. operation-family transfer;
3. hard-composite or subthreshold residual failure.

## Cross-family interpretation

| Claim | Current status | Evidence | Boundary |
|---|---|---|---|
| B1 acquisition is structured | supported cross-family pilot | Both families show usable H1/H2 structure | Predictor signs are not universal |
| Frequency can predict acquisition | supported but regime-dependent | Stronger in family 2 than family 1 | Not sufficient for H3 dependency |
| Reference learnability universally predicts later acquisition | not supported | Family 2 reverses the proxy sign | Requires proxy audit before broad claims |
| H2 residuals identify candidate sites | supported with readiness caveat | Family 1 selected a positive pair; family 2 exposed hard/subthreshold candidates | Residual magnitude alone is insufficient |
| Exact dependency replicates across families | not yet supported | Positive in family 1 only | Current exact-dependency claim remains localized |
| Operation-family transfer is an alternative mechanism | supported pilot | Reverse-side rows match same-operation controls | Needs broader sampling to estimate prevalence |

## Practical rule for future H3

Use H2 residuals to find candidates, but use H3 readiness before expensive intervention runs. A good H3 candidate should have:

- positive residual under the atomic parallel-null;
- non-near-random final token accuracy;
- some low/moderate-threshold acquisition;
- enough headroom for intervention improvement;
- matched same-operation and different-operation controls.

## Consequence for Pythia-like work

For checkpointed LLMs, acquisition order and residuals should be treated as observational signatures, not causal evidence. The controlled B1 experiments show why: the same residual analysis can lead to exact dependency, operation-family transfer, or hard-composite failure depending on intervention results.
