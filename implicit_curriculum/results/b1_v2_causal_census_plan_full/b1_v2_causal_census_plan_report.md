# B1 v2 causal-census plan

This file upgrades the earlier H3 pair intervention workflow into the v2 census unit: every row is a pre-registered component→composite causal test with the full matched-control battery.

- structure table: `results/b1_v2_h1_shared_sweep/structure_table.csv`
- readiness/pair source: `results/b1_v2_h3_ready/h3_ready_pair_selection.csv`
- planned rows: `4`
- control-battery complete rows: `4`
- condition set for generated commands: `full`

## Planned pairs
- row `0` `A07_reverse` → `C03_reverse_then_substitute_07_02`; ready=False, score=2.229, same-op=`A01_reverse`, diff-op=`U01_unrelated_substitute`, fake=`K02_shortcut_for_A03_copy`, surface=`S00_surface_rotate`, battery_complete=True
- row `1` `A02_substitute` → `C03_reverse_then_substitute_07_02`; ready=False, score=2.229, same-op=`U00_unrelated_substitute`, diff-op=`A03_copy`, fake=`K01_shortcut_for_A05_substitute`, surface=`S01_surface_rotate`, battery_complete=True
- row `2` `A05_substitute` → `C06_reverse_then_substitute_05_07`; ready=False, score=2.221, same-op=`U01_unrelated_substitute`, diff-op=`A04_reverse`, fake=`K00_shortcut_for_A02_substitute`, surface=`S02_surface_rotate`, battery_complete=True
- row `3` `A07_reverse` → `C06_reverse_then_substitute_05_07`; ready=False, score=2.221, same-op=`A01_reverse`, diff-op=`U01_unrelated_substitute`, fake=`K02_shortcut_for_A03_copy`, surface=`S00_surface_rotate`, battery_complete=True

## Verdict rule
A row is exact-dependent only if the exact component separates from same-operation, different-operation, fake-component, and surface controls. If same-operation controls match the exact component, the row is operation-family transfer. If no exact manipulation moves the composite beyond matched controls, the row is difficulty/parallel. Rows without measurable composite acquisition are excluded as hard-composite/non-learning and counted in coverage.