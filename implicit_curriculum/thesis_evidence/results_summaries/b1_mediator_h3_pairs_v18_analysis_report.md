# B1 mediator diagnostics analysis

This analysis tests whether H3-positive component-composite pairs show stronger leading-indicator gradient/representation coupling than controls.
It is mechanistic corroboration, not a standalone causal test.

Early window: checkpoint_fraction <= `0.2`

## Pair-role summary
- `different_operation_control` `A07_reverse` → `C06_reverse_then_substitute_02_00`: grad_cos=0.223, CKA=0.713
- `exact_component` `A02_substitute` → `C06_reverse_then_substitute_02_00`: grad_cos=0.533, CKA=0.714
- `fake_component_control` `K01_shortcut_for_A07_reverse` → `C06_reverse_then_substitute_02_00`: grad_cos=0.112, CKA=0.714
- `same_operation_control` `U00_unrelated_substitute` → `C06_reverse_then_substitute_02_00`: grad_cos=0.210, CKA=0.715
- `surface_control` `S00_surface_rotate` → `C06_reverse_then_substitute_02_00`: grad_cos=0.216, CKA=0.711
- `different_operation_control` `U02_unrelated_substitute` → `C06_reverse_then_substitute_02_00`: grad_cos=0.205, CKA=0.715
- `exact_component` `A00_copy` → `C06_reverse_then_substitute_02_00`: grad_cos=0.146, CKA=0.712
- `fake_component_control` `K00_shortcut_for_A00_copy` → `C06_reverse_then_substitute_02_00`: grad_cos=0.122, CKA=0.710
- `same_operation_control` `A06_copy` → `C06_reverse_then_substitute_02_00`: grad_cos=0.159, CKA=0.710
- `surface_control` `S02_surface_rotate` → `C06_reverse_then_substitute_02_00`: grad_cos=0.261, CKA=0.711
- `different_operation_control` `U02_unrelated_substitute` → `C07_substitute_then_reverse_04_03`: grad_cos=0.217, CKA=0.713
- `exact_component` `A04_reverse` → `C07_substitute_then_reverse_04_03`: grad_cos=0.465, CKA=0.708
- `fake_component_control` `K00_shortcut_for_A00_copy` → `C07_substitute_then_reverse_04_03`: grad_cos=0.269, CKA=0.708
- `same_operation_control` `A07_reverse` → `C07_substitute_then_reverse_04_03`: grad_cos=0.441, CKA=0.709
- `surface_control` `S02_surface_rotate` → `C07_substitute_then_reverse_04_03`: grad_cos=0.279, CKA=0.708
- `different_operation_control` `U01_unrelated_substitute` → `C07_substitute_then_reverse_04_03`: grad_cos=0.192, CKA=0.712
- `exact_component` `A03_copy` → `C07_substitute_then_reverse_04_03`: grad_cos=0.230, CKA=0.709
- `fake_component_control` `K02_shortcut_for_A04_reverse` → `C07_substitute_then_reverse_04_03`: grad_cos=0.252, CKA=0.708
- `same_operation_control` `A06_copy` → `C07_substitute_then_reverse_04_03`: grad_cos=0.273, CKA=0.708
- `surface_control` `S01_surface_rotate` → `C07_substitute_then_reverse_04_03`: grad_cos=0.291, CKA=0.701

## Exact-vs-control contrasts
- `A02_substitute` → `C06_reverse_then_substitute_02_00` / `exact_minus_different_operation_control`: Δgrad_cos=0.310, ΔCKA=0.001
- `A02_substitute` → `C06_reverse_then_substitute_02_00` / `exact_minus_fake_component_control`: Δgrad_cos=0.421, ΔCKA=0.001
- `A02_substitute` → `C06_reverse_then_substitute_02_00` / `exact_minus_same_operation_control`: Δgrad_cos=0.323, ΔCKA=-0.000
- `A02_substitute` → `C06_reverse_then_substitute_02_00` / `exact_minus_surface_control`: Δgrad_cos=0.317, ΔCKA=0.004
- `A00_copy` → `C06_reverse_then_substitute_02_00` / `exact_minus_different_operation_control`: Δgrad_cos=-0.059, ΔCKA=-0.003
- `A00_copy` → `C06_reverse_then_substitute_02_00` / `exact_minus_fake_component_control`: Δgrad_cos=0.025, ΔCKA=0.002
- `A00_copy` → `C06_reverse_then_substitute_02_00` / `exact_minus_same_operation_control`: Δgrad_cos=-0.013, ΔCKA=0.002
- `A00_copy` → `C06_reverse_then_substitute_02_00` / `exact_minus_surface_control`: Δgrad_cos=-0.115, ΔCKA=0.002
- `A04_reverse` → `C07_substitute_then_reverse_04_03` / `exact_minus_different_operation_control`: Δgrad_cos=0.248, ΔCKA=-0.005
- `A04_reverse` → `C07_substitute_then_reverse_04_03` / `exact_minus_fake_component_control`: Δgrad_cos=0.197, ΔCKA=-0.000
- `A04_reverse` → `C07_substitute_then_reverse_04_03` / `exact_minus_same_operation_control`: Δgrad_cos=0.024, ΔCKA=-0.001
- `A04_reverse` → `C07_substitute_then_reverse_04_03` / `exact_minus_surface_control`: Δgrad_cos=0.186, ΔCKA=-0.000
- `A03_copy` → `C07_substitute_then_reverse_04_03` / `exact_minus_different_operation_control`: Δgrad_cos=0.038, ΔCKA=-0.003
- `A03_copy` → `C07_substitute_then_reverse_04_03` / `exact_minus_fake_component_control`: Δgrad_cos=-0.023, ΔCKA=0.001
- `A03_copy` → `C07_substitute_then_reverse_04_03` / `exact_minus_same_operation_control`: Δgrad_cos=-0.043, ΔCKA=0.001
- `A03_copy` → `C07_substitute_then_reverse_04_03` / `exact_minus_surface_control`: Δgrad_cos=-0.061, ΔCKA=0.008

## Interpretation rule
Mediator support for exact-component dependency requires the exact component to show higher early gradient cosine and/or representation CKA with the composite than same-operation and different-operation controls. If same-operation controls match the exact component, interpret the pattern as operation-family transfer rather than exact-component reuse.