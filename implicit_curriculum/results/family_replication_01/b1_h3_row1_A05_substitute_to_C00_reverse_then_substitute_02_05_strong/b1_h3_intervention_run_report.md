# B1 H3 intervention run report

This is the training output for pair-specific B1 H3 interventions. It is not the final H3 verdict; run `analyze_b1_h3_interventions` on this directory.

## Pair
- component: `A05_substitute`
- composite: `C00_reverse_then_substitute_02_05`
- unrelated_control: `U01_unrelated_substitute`
- same_operation_control: `U01_unrelated_substitute`
- different_operation_control: `A03_copy`
- fake_component_control: `K02_shortcut_for_A00_copy`
- surface_control: `S01_surface_rotate`

## Run summary
- conditions: `baseline, pretrain_component, pretrain_same_operation_unrelated, pretrain_different_operation_matched, corrupt_component_strong, corrupt_same_operation_unrelated_strong, corrupt_different_operation_matched_strong, delay_component_strong, delay_same_operation_unrelated_strong, delay_different_operation_matched_strong`
- seeds: `0, 1, 2, 3, 4, 5, 6, 7, 8, 9`
- max_data_seen: `250000`
- pretrain_data_seen: `50000`
- eval rows: `252500`
- quick composite acquisition rate across conditions/seeds: `0.000`