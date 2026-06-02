# B1 mediator diagnostics analysis

This analysis tests whether H3-positive component-composite pairs show stronger leading-indicator gradient/representation coupling than controls.
It is mechanistic corroboration, not a standalone causal test.

Early window: checkpoint_fraction <= `0.2`

## Pair-role summary
- `different_operation_control` `U01_unrelated_substitute` → `C03_reverse_then_substitute_07_02`: grad_cos=0.261, CKA=0.753
- `exact_component` `A07_reverse` → `C03_reverse_then_substitute_07_02`: grad_cos=0.230, CKA=0.747
- `fake_component_control` `K02_shortcut_for_A03_copy` → `C03_reverse_then_substitute_07_02`: grad_cos=0.089, CKA=0.749
- `same_operation_control` `A01_reverse` → `C03_reverse_then_substitute_07_02`: grad_cos=0.250, CKA=0.751
- `surface_control` `S00_surface_rotate` → `C03_reverse_then_substitute_07_02`: grad_cos=0.238, CKA=0.744
- `different_operation_control` `A03_copy` → `C03_reverse_then_substitute_07_02`: grad_cos=0.120, CKA=0.749
- `exact_component` `A02_substitute` → `C03_reverse_then_substitute_07_02`: grad_cos=0.459, CKA=0.752
- `fake_component_control` `K01_shortcut_for_A05_substitute` → `C03_reverse_then_substitute_07_02`: grad_cos=0.121, CKA=0.749
- `same_operation_control` `U00_unrelated_substitute` → `C03_reverse_then_substitute_07_02`: grad_cos=0.211, CKA=0.754
- `surface_control` `S01_surface_rotate` → `C03_reverse_then_substitute_07_02`: grad_cos=0.215, CKA=0.749
- `different_operation_control` `A04_reverse` → `C06_reverse_then_substitute_05_07`: grad_cos=0.218, CKA=0.751
- `exact_component` `A05_substitute` → `C06_reverse_then_substitute_05_07`: grad_cos=0.458, CKA=0.753
- `fake_component_control` `K00_shortcut_for_A02_substitute` → `C06_reverse_then_substitute_05_07`: grad_cos=0.085, CKA=0.749
- `same_operation_control` `U01_unrelated_substitute` → `C06_reverse_then_substitute_05_07`: grad_cos=0.230, CKA=0.753
- `surface_control` `S02_surface_rotate` → `C06_reverse_then_substitute_05_07`: grad_cos=0.275, CKA=0.746
- `different_operation_control` `U01_unrelated_substitute` → `C06_reverse_then_substitute_05_07`: grad_cos=0.230, CKA=0.753
- `exact_component` `A07_reverse` → `C06_reverse_then_substitute_05_07`: grad_cos=0.198, CKA=0.747
- `fake_component_control` `K02_shortcut_for_A03_copy` → `C06_reverse_then_substitute_05_07`: grad_cos=0.119, CKA=0.747
- `same_operation_control` `A01_reverse` → `C06_reverse_then_substitute_05_07`: grad_cos=0.238, CKA=0.749
- `surface_control` `S00_surface_rotate` → `C06_reverse_then_substitute_05_07`: grad_cos=0.250, CKA=0.743

## Exact-vs-control contrasts
- `A07_reverse` → `C03_reverse_then_substitute_07_02` / `exact_minus_different_operation_control`: Δgrad_cos=-0.031, ΔCKA=-0.005
- `A07_reverse` → `C03_reverse_then_substitute_07_02` / `exact_minus_fake_component_control`: Δgrad_cos=0.141, ΔCKA=-0.002
- `A07_reverse` → `C03_reverse_then_substitute_07_02` / `exact_minus_same_operation_control`: Δgrad_cos=-0.021, ΔCKA=-0.004
- `A07_reverse` → `C03_reverse_then_substitute_07_02` / `exact_minus_surface_control`: Δgrad_cos=-0.008, ΔCKA=0.003
- `A02_substitute` → `C03_reverse_then_substitute_07_02` / `exact_minus_different_operation_control`: Δgrad_cos=0.339, ΔCKA=0.003
- `A02_substitute` → `C03_reverse_then_substitute_07_02` / `exact_minus_fake_component_control`: Δgrad_cos=0.338, ΔCKA=0.003
- `A02_substitute` → `C03_reverse_then_substitute_07_02` / `exact_minus_same_operation_control`: Δgrad_cos=0.248, ΔCKA=-0.002
- `A02_substitute` → `C03_reverse_then_substitute_07_02` / `exact_minus_surface_control`: Δgrad_cos=0.244, ΔCKA=0.002
- `A05_substitute` → `C06_reverse_then_substitute_05_07` / `exact_minus_different_operation_control`: Δgrad_cos=0.240, ΔCKA=0.003
- `A05_substitute` → `C06_reverse_then_substitute_05_07` / `exact_minus_fake_component_control`: Δgrad_cos=0.372, ΔCKA=0.004
- `A05_substitute` → `C06_reverse_then_substitute_05_07` / `exact_minus_same_operation_control`: Δgrad_cos=0.227, ΔCKA=0.001
- `A05_substitute` → `C06_reverse_then_substitute_05_07` / `exact_minus_surface_control`: Δgrad_cos=0.183, ΔCKA=0.007
- `A07_reverse` → `C06_reverse_then_substitute_05_07` / `exact_minus_different_operation_control`: Δgrad_cos=-0.032, ΔCKA=-0.006
- `A07_reverse` → `C06_reverse_then_substitute_05_07` / `exact_minus_fake_component_control`: Δgrad_cos=0.079, ΔCKA=-0.001
- `A07_reverse` → `C06_reverse_then_substitute_05_07` / `exact_minus_same_operation_control`: Δgrad_cos=-0.040, ΔCKA=-0.002
- `A07_reverse` → `C06_reverse_then_substitute_05_07` / `exact_minus_surface_control`: Δgrad_cos=-0.052, ΔCKA=0.004

## Interpretation rule
Mediator support for exact-component dependency requires the exact component to show higher early gradient cosine and/or representation CKA with the composite than same-operation and different-operation controls. If same-operation controls match the exact component, interpret the pattern as operation-family transfer rather than exact-component reuse.