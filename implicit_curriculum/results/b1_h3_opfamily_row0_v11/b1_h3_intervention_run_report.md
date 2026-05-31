# B1 H3 intervention run report

This is the training output for pair-specific B1 H3 interventions. It is not the final H3 verdict; run `analyze_b1_h3_interventions` on this directory.

## Pair
- component: `A02_substitute`
- composite: `C06_reverse_then_substitute_02_00`
- unrelated_control: `U00_unrelated_substitute`
- same_operation_control: `U00_unrelated_substitute`
- different_operation_control: `A07_reverse`
- fake_component_control: `K01_shortcut_for_A07_reverse`
- surface_control: `S00_surface_rotate`

## Run summary
- conditions: `baseline, upweight_component, upweight_same_operation_unrelated, upweight_different_operation_matched, upweight_fake_component, upweight_surface_control, delay_component, delay_same_operation_unrelated, delay_different_operation_matched, corrupt_component, corrupt_same_operation_unrelated, corrupt_different_operation_matched`
- seeds: `0, 1, 2, 3, 4, 5, 6, 7, 8, 9`
- max_data_seen: `250000`
- eval rows: `303000`
- quick composite acquisition rate across conditions/seeds: `0.575`