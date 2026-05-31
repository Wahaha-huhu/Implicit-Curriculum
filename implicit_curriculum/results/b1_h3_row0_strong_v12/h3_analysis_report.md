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
- `corrupt_component_strong`: acq=0.300, mean censored time=234598.4, final=0.690
- `corrupt_different_operation_matched_strong`: acq=0.800, mean censored time=203980.8, final=0.734
- `corrupt_same_operation_unrelated_strong`: acq=0.800, mean censored time=194995.2, final=0.751
- `delay_component_strong`: acq=0.400, mean censored time=224665.6, final=0.711
- `delay_different_operation_matched_strong`: acq=0.500, mean censored time=219315.2, final=0.724
- `delay_same_operation_unrelated_strong`: acq=0.600, mean censored time=204211.2, final=0.730
- `pretrain_component`: acq=1.000, mean censored time=0.0, final=0.706
- `pretrain_different_operation_matched`: acq=0.400, mean censored time=238771.2, final=0.707
- `pretrain_same_operation_unrelated`: acq=0.200, mean censored time=243712.0, final=0.657

## Intervention contrasts
- `exact_pretrain_vs_same_operation`: `pretrain_component` vs `pretrain_same_operation_unrelated` (earlier): strict Δ=-218112.000 (n=2), censored Δ=-243712.000, censored-rate=1.000, Δfinal=0.048
- `exact_pretrain_vs_different_operation`: `pretrain_component` vs `pretrain_different_operation_matched` (earlier): strict Δ=-221760.000 (n=4), censored Δ=-238771.200, censored-rate=1.000, Δfinal=-0.001
- `operation_family_pretrain_vs_different_operation`: `pretrain_same_operation_unrelated` vs `pretrain_different_operation_matched` (earlier): strict Δ=nan (n=0), censored Δ=4940.800, censored-rate=0.200, Δfinal=-0.050
- `exact_strong_corrupt_vs_same_operation`: `corrupt_component_strong` vs `corrupt_same_operation_unrelated_strong` (later): strict Δ=33792.000 (n=3), censored Δ=39603.200, censored-rate=0.800, Δfinal=-0.061
- `exact_strong_corrupt_vs_different_operation`: `corrupt_component_strong` vs `corrupt_different_operation_matched_strong` (later): strict Δ=29866.667 (n=3), censored Δ=30617.600, censored-rate=0.800, Δfinal=-0.044
- `exact_strong_delay_vs_same_operation`: `delay_component_strong` vs `delay_same_operation_unrelated_strong` (later): strict Δ=17472.000 (n=4), censored Δ=20454.400, censored-rate=0.500, Δfinal=-0.019
- `exact_strong_delay_vs_different_operation`: `delay_component_strong` vs `delay_different_operation_matched_strong` (later): strict Δ=9152.000 (n=4), censored Δ=5350.400, censored-rate=0.400, Δfinal=-0.013

## Decision aid
- mean censored expected-direction rate: `0.671`
- mean final-metric expected-direction rate: `0.686`
- exact-vs-same-operation censored expected-direction rate: `0.767`
- exact/different-operation censored expected-direction rate: `0.600`

GREEN for exact-component dependency requires exact-component interventions to beat same-operation, different-operation, fake, and surface controls. If component and same-operation controls both help similarly, interpret the result as operation-family transfer rather than exact dependency.