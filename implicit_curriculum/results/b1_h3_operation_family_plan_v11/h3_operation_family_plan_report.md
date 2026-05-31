# B1 H3 operation-family control plan

This plan sharpens H3 by separating exact-component effects from operation-family transfer.
Each row can be passed to `run_b1_h3_interventions` using `--plan-file ... --plan-index N`.

- source pair_selection: `results/b1_h1_shared_sweep_v08/h2_pair_selection.csv`
- n planned pairs: `2`

## Planned pairs
- row `0`: `A02_substitute` → `C06_reverse_then_substitute_02_00`; same-op=`U00_unrelated_substitute`, diff-op=`A07_reverse`, fake=`K01_shortcut_for_A07_reverse`, surface=`S00_surface_rotate`
- row `1`: `A00_copy` → `C06_reverse_then_substitute_02_00`; same-op=`A06_copy`, diff-op=`U02_unrelated_substitute`, fake=`K00_shortcut_for_A00_copy`, surface=`S02_surface_rotate`

## Recommended condition set
`baseline upweight_component upweight_same_operation_unrelated upweight_different_operation_matched upweight_fake_component upweight_surface_control delay_component delay_same_operation_unrelated delay_different_operation_matched corrupt_component corrupt_same_operation_unrelated corrupt_different_operation_matched`