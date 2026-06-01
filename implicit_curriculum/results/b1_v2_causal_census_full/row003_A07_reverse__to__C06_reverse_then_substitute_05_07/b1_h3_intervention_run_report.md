# B1 H3 intervention run report

This is the training output for pair-specific B1 H3 interventions. It is not the final H3 verdict; run `analyze_b1_h3_interventions` on this directory.

## Pair
- component: `A07_reverse`
- composite: `C06_reverse_then_substitute_05_07`
- unrelated_control: `A01_reverse`
- same_operation_control: `A01_reverse`
- different_operation_control: `U01_unrelated_substitute`
- fake_component_control: `K02_shortcut_for_A03_copy`
- surface_control: `S00_surface_rotate`

## Run summary
- conditions: `baseline, upweight_component, upweight_same_operation_unrelated, upweight_different_operation_matched, upweight_fake_component, upweight_surface_control, delay_component, delay_same_operation_unrelated, delay_different_operation_matched, corrupt_component, corrupt_same_operation_unrelated, corrupt_different_operation_matched, pretrain_component, pretrain_same_operation_unrelated, pretrain_different_operation_matched, corrupt_component_strong, corrupt_same_operation_unrelated_strong, corrupt_different_operation_matched_strong, delay_component_strong, delay_same_operation_unrelated_strong, delay_different_operation_matched_strong`
- seeds: `0, 1, 2, 3, 4, 5, 6, 7, 8, 9`
- max_data_seen: `250000`
- pretrain_data_seen: `50000`
- eval rows: `530250`
- quick composite acquisition rate across conditions/seeds: `0.962`