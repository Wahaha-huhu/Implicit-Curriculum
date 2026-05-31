# B1 H3 pair-specific intervention analysis

This is an H3 pilot analysis. It tests whether component interventions move the selected composite beyond matched control interventions. It is causal only within this controlled training setup and remains a pilot until replicated across more pairs/families.

Primary metric: `token_accuracy` threshold `0.7`.

## Pair
- component: `A00_copy`
- composite: `C06_reverse_then_substitute_02_00`
- unrelated_control: `A06_copy`
- same_operation_control: `A06_copy`
- different_operation_control: `U02_unrelated_substitute`
- fake_component_control: `K00_shortcut_for_A00_copy`
- surface_control: `S02_surface_rotate`

## Composite acquisition by condition
- `baseline`: acq=0.600, mean censored time=212044.8, final=0.723
- `corrupt_component`: acq=0.700, mean censored time=221235.2, final=0.720
- `corrupt_different_operation_matched`: acq=0.700, mean censored time=213836.8, final=0.733
- `corrupt_same_operation_unrelated`: acq=0.900, mean censored time=198374.4, final=0.741
- `delay_component`: acq=0.600, mean censored time=219084.8, final=0.713
- `delay_different_operation_matched`: acq=0.700, mean censored time=211353.6, final=0.729
- `delay_same_operation_unrelated`: acq=0.500, mean censored time=219417.6, final=0.721
- `upweight_component`: acq=0.500, mean censored time=219315.2, final=0.715
- `upweight_different_operation_matched`: acq=0.400, mean censored time=230144.0, final=0.696
- `upweight_fake_component`: acq=0.600, mean censored time=220364.8, final=0.724
- `upweight_same_operation_unrelated`: acq=0.400, mean censored time=225945.6, final=0.714
- `upweight_surface_control`: acq=0.600, mean censored time=221184.0, final=0.710

## Intervention contrasts
- `exact_vs_same_operation`: `upweight_component` vs `upweight_same_operation_unrelated` (earlier): strict Δ=-12352.000 (n=4), censored Δ=-6630.400, censored-rate=0.300, Δfinal=0.002
- `exact_vs_different_operation`: `upweight_component` vs `upweight_different_operation_matched` (earlier): strict Δ=-22848.000 (n=4), censored Δ=-10828.800, censored-rate=0.500, Δfinal=0.020
- `exact_vs_fake_component`: `upweight_component` vs `upweight_fake_component` (earlier): strict Δ=-5478.400 (n=5), censored Δ=-1049.600, censored-rate=0.200, Δfinal=-0.008
- `exact_vs_surface`: `upweight_component` vs `upweight_surface_control` (earlier): strict Δ=-13158.400 (n=5), censored Δ=-1868.800, censored-rate=0.300, Δfinal=0.006
- `operation_family_vs_different_operation`: `upweight_same_operation_unrelated` vs `upweight_different_operation_matched` (earlier): strict Δ=-10496.000 (n=4), censored Δ=-4198.400, censored-rate=0.200, Δfinal=0.018
- `exact_corrupt_vs_same_operation`: `corrupt_component` vs `corrupt_same_operation_unrelated` (later): strict Δ=25600.000 (n=7), censored Δ=22860.800, censored-rate=0.700, Δfinal=-0.021
- `exact_corrupt_vs_different_operation`: `corrupt_component` vs `corrupt_different_operation_matched` (later): strict Δ=9728.000 (n=6), censored Δ=7398.400, censored-rate=0.400, Δfinal=-0.014
- `exact_delay_vs_same_operation`: `delay_component` vs `delay_same_operation_unrelated` (later): strict Δ=7296.000 (n=4), censored Δ=-332.800, censored-rate=0.400, Δfinal=-0.007
- `exact_delay_vs_different_operation`: `delay_component` vs `delay_different_operation_matched` (later): strict Δ=7466.667 (n=6), censored Δ=7731.200, censored-rate=0.300, Δfinal=-0.016

## Decision aid
- mean censored expected-direction rate: `0.367`
- mean final-metric expected-direction rate: `0.678`
- exact-vs-same-operation censored expected-direction rate: `0.467`
- exact/different-operation censored expected-direction rate: `0.350`

GREEN for exact-component dependency requires exact-component interventions to beat same-operation, different-operation, fake, and surface controls. If component and same-operation controls both help similarly, interpret the result as operation-family transfer rather than exact dependency.