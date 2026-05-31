# H3 synthesis: exact dependency, operation-family transfer, and boundary mapping

This document summarizes the current H3 evidence across B1 sequence-DSL component–composite intervention tests. It is intended for thesis writing and should be updated append-only as more pairs/families are tested.

## Current H3 evidence matrix

| Pair | Composite | Result | Thesis-safe interpretation |
|---|---|---|---|
| `A02_substitute → C06_reverse_then_substitute_02_00` | `C06` | **Positive, pair-specific** | Exact substitution-side component pretraining strongly accelerates C06 and exact corruption delays/degrades it beyond same-operation and different-operation controls. |
| `A00_copy → C06_reverse_then_substitute_02_00` | `C06` | **Weak / mixed** | Copy-side component does not show robust exact-component support; corruption is somewhat supportive but upweight/delay are weak. |
| `A04_reverse → C07_substitute_then_reverse_04_03` | `C07` | **Operation-family transfer** | Exact reverse pretraining and same-operation reverse pretraining are indistinguishable; both beat a different-operation control. |
| `A03_copy → C07_substitute_then_reverse_04_03` | `C07` | **Negative** | Exact copy component does not beat same-operation controls and strong delay is opposite to exact-dependency predictions. |

## Overall H3 interpretation

The current H3 evidence does **not** support a universal component-before-composite dependency mechanism. Instead, it supports a more nuanced and more defensible picture:

> H2 residuals identify candidate sites where the atomic parallel-rate model fails, but H3 interventions reveal heterogeneous causal structure. Some residuals correspond to localized exact-component sensitivity, while others are better explained by operation-family transfer, saturation, or no exact dependency.

The strongest positive evidence is localized to `A02_substitute → C06_reverse_then_substitute_02_00`. This is a controlled-setting, pair-specific causal result, not a general LLM-training mechanism.

## Claim boundary

Safe claims:

1. In the controlled B1 setting, H2 residuals are useful for selecting candidate dependency sites.
2. Exact-component dependency is not automatic: it must be earned through controls against same-operation, different-operation, fake, and surface interventions.
3. One tested pair (`A02_substitute → C06`) shows positive exact-component causal sensitivity under strong interventions.
4. Other tested pairs are weak, negative, or operation-family-level, showing that formal component membership is not enough.

Unsafe claims:

1. “Composite capabilities generally require all formal components to be acquired first.”
2. “The B1 experiments prove the mechanism of real LLM training.”
3. “H2 residuals alone prove dependency.”
4. “Operation-family transfer and exact-component dependency are the same phenomenon.”

## Next evidence needed

The next strongest additions would be:

1. Replicate `A02_substitute → C06` in a second generated B1 family.
2. Add mediator diagnostics for `A02 → C06`, such as early gradient alignment, representation/probe transfer, or activation patching.
3. Improve B2 sparse-parity coverage so the quanta-style frequency baseline is thesis-ready.
4. Eventually run an observational, non-causal Pythia slice check if the controlled story remains coherent.

## Mediator diagnostic addendum

Mediator diagnostics strengthen the interpretation of the H3 evidence. The positive pair `A02_substitute → C06` has early exact-component gradient cosine 0.533, compared with 0.210 for the same-operation control and 0.223 for the different-operation control. By contrast, weak/negative pairs such as `A00_copy → C06` and `A03_copy → C07` do not show exact-component gradient separation. The operation-family case `A04_reverse → C07` shows high exact gradient cosine but a nearly matched same-operation reverse control, consistent with operation-family transfer.

The current CKA diagnostic is not discriminative: values are nearly flat across exact and control pairs. Therefore the H3 mechanism claim should reference early gradient alignment, not CKA-based representation evidence.
