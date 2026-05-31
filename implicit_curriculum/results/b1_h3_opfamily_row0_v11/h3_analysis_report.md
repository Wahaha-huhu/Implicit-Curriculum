# B1 H3 pair-specific intervention analysis

This is an H3 pilot analysis. It tests whether component interventions move the selected composite beyond matched control interventions. It is causal only within this controlled training setup and remains a pilot until replicated across more pairs/families.

Primary metric: `token_accuracy` threshold `0.7`.

## Pair
- component: `A02_substitute`
- composite: `C06_reverse_then_substitute_02_00`
- unrelated_control: `U00_unrelated_substitute`
- same_operation_control: `U00_unrelated_substitute`
- different_operation_control: `A07_reverse`
- fake_component_control: `K01_shortcut_for_A07_reverse`
- surface_control: `S00_surface_rotate`

## Composite acquisition by condition
- `baseline`: acq=0.600, mean censored time=212044.8, final=0.723
- `corrupt_component`: acq=0.400, mean censored time=230246.4, final=0.708
- `corrupt_different_operation_matched`: acq=0.600, mean censored time=219904.0, final=0.721
- `corrupt_same_operation_unrelated`: acq=0.700, mean censored time=209177.6, final=0.736
- `delay_component`: acq=0.500, mean censored time=219315.2, final=0.714
- `delay_different_operation_matched`: acq=0.500, mean censored time=219315.2, final=0.724
- `delay_same_operation_unrelated`: acq=0.600, mean censored time=210201.6, final=0.725
- `upweight_component`: acq=0.900, mean censored time=180147.2, final=0.755
- `upweight_different_operation_matched`: acq=0.600, mean censored time=215705.6, final=0.716
- `upweight_fake_component`: acq=0.500, mean censored time=220492.8, final=0.725
- `upweight_same_operation_unrelated`: acq=0.300, mean censored time=233395.2, final=0.669
- `upweight_surface_control`: acq=0.700, mean censored time=211532.8, final=0.737

## Intervention contrasts
- `exact_vs_same_operation`: `upweight_component` vs `upweight_same_operation_unrelated` (earlier): strict Δ=-40192.000 (n=3), censored Δ=-53248.000, censored-rate=0.900, Δfinal=0.086
- `exact_vs_different_operation`: `upweight_component` vs `upweight_different_operation_matched` (earlier): strict Δ=-27306.667 (n=6), censored Δ=-35558.400, censored-rate=0.900, Δfinal=0.039
- `exact_vs_fake_component`: `upweight_component` vs `upweight_fake_component` (earlier): strict Δ=-27596.800 (n=5), censored Δ=-40345.600, censored-rate=0.900, Δfinal=0.031
- `exact_vs_surface`: `upweight_component` vs `upweight_surface_control` (earlier): strict Δ=-27977.143 (n=7), censored Δ=-31385.600, censored-rate=0.800, Δfinal=0.018
- `operation_family_vs_different_operation`: `upweight_same_operation_unrelated` vs `upweight_different_operation_matched` (earlier): strict Δ=13056.000 (n=3), censored Δ=17689.600, censored-rate=0.000, Δfinal=-0.047
- `exact_corrupt_vs_same_operation`: `corrupt_component` vs `corrupt_same_operation_unrelated` (later): strict Δ=32448.000 (n=4), censored Δ=21068.800, censored-rate=0.700, Δfinal=-0.028
- `exact_corrupt_vs_different_operation`: `corrupt_component` vs `corrupt_different_operation_matched` (later): strict Δ=12800.000 (n=3), censored Δ=10342.400, censored-rate=0.500, Δfinal=-0.013
- `exact_delay_vs_same_operation`: `delay_component` vs `delay_same_operation_unrelated` (later): strict Δ=6041.600 (n=5), censored Δ=9113.600, censored-rate=0.200, Δfinal=-0.011
- `exact_delay_vs_different_operation`: `delay_component` vs `delay_different_operation_matched` (later): strict Δ=0.000 (n=5), censored Δ=0.000, censored-rate=0.000, Δfinal=-0.010

## Decision aid
- mean censored expected-direction rate: `0.544`
- mean final-metric expected-direction rate: `0.756`
- exact-vs-same-operation censored expected-direction rate: `0.600`
- exact/different-operation censored expected-direction rate: `0.350`

GREEN for exact-component dependency requires exact-component interventions to beat same-operation, different-operation, fake, and surface controls. If component and same-operation controls both help similarly, interpret the result as operation-family transfer rather than exact dependency.