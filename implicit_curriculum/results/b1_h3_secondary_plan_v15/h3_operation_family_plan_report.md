# B1 H3 operation-family control plan

This plan sharpens H3 by separating exact-component effects from operation-family transfer.
Each row can be passed to `run_b1_h3_interventions` using `--plan-file ... --plan-index N`.

- source pair_selection: `results/b1_h1_shared_sweep_v08/h2_pair_selection.csv`
- n planned pairs: `2`
- include_composites: `None`
- exclude_composites: `['C06_reverse_then_substitute_02_00']`
- condition_set_for_script: `strong`

## Planned pairs
- row `0`: `A04_reverse` → `C07_substitute_then_reverse_04_03`; same-op=`A07_reverse`, diff-op=`U02_unrelated_substitute`, fake=`K00_shortcut_for_A00_copy`, surface=`S02_surface_rotate`, source residual=0.952, positive-rate=1.000
- row `1`: `A03_copy` → `C07_substitute_then_reverse_04_03`; same-op=`A06_copy`, diff-op=`U01_unrelated_substitute`, fake=`K02_shortcut_for_A04_reverse`, surface=`S01_surface_rotate`, source residual=0.952, positive-rate=1.000

## Recommended standard condition set
`baseline upweight_component upweight_same_operation_unrelated upweight_different_operation_matched upweight_fake_component upweight_surface_control delay_component delay_same_operation_unrelated delay_different_operation_matched corrupt_component corrupt_same_operation_unrelated corrupt_different_operation_matched`

## Recommended strong condition set
`baseline pretrain_component pretrain_same_operation_unrelated pretrain_different_operation_matched corrupt_component_strong corrupt_same_operation_unrelated_strong corrupt_different_operation_matched_strong delay_component_strong delay_same_operation_unrelated_strong delay_different_operation_matched_strong`

## Interpretation rule
Exact-component dependency requires the exact component to beat same-operation and different-operation controls. If exact and same-operation controls move the composite similarly, interpret the effect as operation-family transfer rather than exact dependency.