# B1 H3 C06 row-0 / row-1 interpretation

This summary records the current H3 evidence for the delayed composite `C06_reverse_then_substitute_02_00`.

## Row 0: `A02_substitute → C06`

Status: promising partial positive.

Key evidence:
- `upweight_component` beats same-operation unrelated, different-operation, fake, and surface controls.
- Exact-vs-same-operation upweight censored delta ≈ `-53,248`; expected-direction rate ≈ `0.900`; final metric delta ≈ `+0.086`.
- Corrupt-component contrast is weak-positive.
- Delay contrast is weak/negative.

Thesis-safe interpretation: exact substitution-component upweighting can accelerate the composite beyond operation-family controls, but full dependency is not established.

## Row 1: `A00_copy → C06`

Status: weak/mixed.

Key evidence:
- Upweight exact-copy component does not robustly beat same-operation/fake/surface controls.
- Corrupt-component contrast is the strongest row-1 signal, but upweight/delay do not confirm it.

Thesis-safe interpretation: C06's residual is not uniformly explained by all listed components; the substitution component appears more causally relevant than the copy component in this pilot.

## Combined conclusion

Current H3 evidence is component-specific and incomplete. It supports further testing of `A02_substitute → C06`, especially with model-state interventions such as component pretraining, but does not yet justify a broad developmental-dependency claim.
