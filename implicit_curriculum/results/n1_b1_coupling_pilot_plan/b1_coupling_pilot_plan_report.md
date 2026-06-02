# B1 N1 cross-task coupling pilot plan

This is the first pilot for the positive-mechanism reframe: measure whether early training-dynamics coupling predicts directly measured cross-task transfer/interference.

## Inputs
- structure table: `results/n1_b1_coupling_pilot_plan/structure_table.csv`
- pairs: `12`
- run rows: `144`
- dose multipliers: `0.0, 0.5, 1.0, 2.0`
- seeds: `0, 1, 2`

## Pair-type coverage
- `component_to_composite`: `3`
- `composite_to_component_reverse`: `2`
- `control_or_surface`: `2`
- `same_operation`: `2`
- `same_operation_reverse`: `2`
- `unrelated_matched`: `1`

## Planned pairs
- `P000_A05_substitute__to__C05_copy_then_substitute_05_07`: `A05_substitute` → `C05_copy_then_substitute_05_07` (component_to_composite), filler=`K00_shortcut_for_A00_copy`
- `P001_C03_reverse_then_substitute_01_06__to__A06_copy`: `C03_reverse_then_substitute_01_06` → `A06_copy` (composite_to_component_reverse), filler=`S00_surface_rotate`
- `P002_U00_unrelated_substitute__to__A02_substitute`: `U00_unrelated_substitute` → `A02_substitute` (control_or_surface), filler=`K01_shortcut_for_A06_copy`
- `P003_A06_copy__to__A00_copy`: `A06_copy` → `A00_copy` (same_operation), filler=`U03_unrelated_substitute`
- `P004_A00_copy__to__A06_copy`: `A00_copy` → `A06_copy` (same_operation_reverse), filler=`U01_unrelated_substitute`
- `P005_U02_unrelated_substitute__to__S00_surface_rotate`: `U02_unrelated_substitute` → `S00_surface_rotate` (unrelated_matched), filler=`K00_shortcut_for_A00_copy`
- `P006_A01_reverse__to__C00_reverse_then_substitute_01_06`: `A01_reverse` → `C00_reverse_then_substitute_01_06` (component_to_composite), filler=`U03_unrelated_substitute`
- `P007_C00_reverse_then_substitute_01_06__to__A01_reverse`: `C00_reverse_then_substitute_01_06` → `A01_reverse` (composite_to_component_reverse), filler=`U01_unrelated_substitute`
- `P008_S00_surface_rotate__to__A04_reverse`: `S00_surface_rotate` → `A04_reverse` (control_or_surface), filler=`U02_unrelated_substitute`
- `P009_A07_reverse__to__A04_reverse`: `A07_reverse` → `A04_reverse` (same_operation), filler=`S01_surface_rotate`
- `P010_A05_substitute__to__A02_substitute`: `A05_substitute` → `A02_substitute` (same_operation_reverse), filler=`K00_shortcut_for_A00_copy`
- `P011_A06_copy__to__C03_reverse_then_substitute_01_06`: `A06_copy` → `C03_reverse_then_substitute_01_06` (component_to_composite), filler=`U03_unrelated_substitute`

## Interpretation discipline
This plan does not assume ordered learning, quanta, or composition. It creates a heterogeneous pair set so that the runner can measure a continuous interaction effect I(A→B) and validate early gradient/representation coupling against that effect.