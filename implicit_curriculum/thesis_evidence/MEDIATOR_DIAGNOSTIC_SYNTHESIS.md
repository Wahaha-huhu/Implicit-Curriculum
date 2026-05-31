# Mediator diagnostic synthesis: gradient coupling versus representation CKA

This document records the current mediator evidence for the B1 H3 component-composite pairs. The mediator analysis is mechanistic corroboration, not standalone causal evidence. It asks whether the H3-positive pair has stronger early component-composite coupling than weak, negative, or operation-family pairs.

## Main result

The strongest H3-positive pair, `A02_substitute → C06_reverse_then_substitute_02_00`, also has the strongest early exact-component gradient coupling.

| Pair | H3 status | Early exact gradient cosine | Same-operation control | Different-operation control | Interpretation |
|---|---:|---:|---:|---:|---|
| `A02_substitute → C06` | positive exact-component | 0.533 | 0.210 | 0.223 | Exact component separates strongly from controls. |
| `A00_copy → C06` | weak/mixed | 0.146 | 0.159 | 0.205 | No exact-component gradient separation. |
| `A04_reverse → C07` | operation-family transfer | 0.465 | 0.441 | 0.217 | Exact and same-operation reverse are nearly matched. |
| `A03_copy → C07` | negative | 0.230 | 0.273 | 0.192 | No exact-component separation. |

For `A02_substitute → C06`, the exact-minus-control gradient contrasts are large: +0.323 versus same-operation, +0.310 versus different-operation, +0.421 versus fake component, and +0.317 versus surface control. This aligns with the H3 behavioral result: exact pretraining and exact corruption move the composite beyond matched controls.

## CKA limitation

The current representation CKA diagnostic is not discriminative. Most CKA values are approximately 0.708–0.715, and exact-minus-control CKA contrasts are near zero. Therefore, current representation CKA should not be used as evidence for exact-component dependency.

## Thesis-safe interpretation

The mediator result supports a gradient-mediated interpretation of the localized H3 positive pair: the pair that shows exact-component causal sensitivity also shows unusually high early component-composite gradient alignment. Weak/negative pairs do not show this pattern, and the operation-family case shows exact and same-operation gradient alignment nearly matched. This strengthens the controlled mechanism story but does not prove a universal dependency mechanism.

## Claim boundary

Safe claim:

> In the controlled B1 setting, the strongest exact-component H3 pair also shows stronger early gradient alignment with its composite than same-operation, different-operation, fake, and surface controls.

Unsafe claim:

> Representation CKA currently supports exact-component dependency.

Unsafe claim:

> Gradient alignment alone proves causal dependency.
