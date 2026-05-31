# B1 H3 pair-specific intervention analysis

This is an H3 pilot analysis. It tests whether component interventions move the selected composite beyond matched control interventions. It is causal only within this controlled training setup and remains a pilot until replicated across more pairs/families.

Primary metric: `token_accuracy` threshold `0.7`.

## Pair
- component: `A04_reverse`
- composite: `C07_substitute_then_reverse_04_03`
- unrelated_control: `A07_reverse`
- same_operation_control: `A07_reverse`
- different_operation_control: `U02_unrelated_substitute`
- fake_component_control: `K00_shortcut_for_A00_copy`
- surface_control: `S02_surface_rotate`

## Composite acquisition by condition
- `baseline`: acq=1.000, mean censored time=64332.8, final=0.843
- `corrupt_component_strong`: acq=1.000, mean censored time=64512.0, final=0.838
- `corrupt_different_operation_matched_strong`: acq=1.000, mean censored time=63974.4, final=0.854
- `corrupt_same_operation_unrelated_strong`: acq=1.000, mean censored time=65280.0, final=0.837
- `delay_component_strong`: acq=1.000, mean censored time=65766.4, final=0.843
- `delay_different_operation_matched_strong`: acq=1.000, mean censored time=62566.4, final=0.846
- `delay_same_operation_unrelated_strong`: acq=1.000, mean censored time=65766.4, final=0.846
- `pretrain_component`: acq=1.000, mean censored time=0.0, final=0.852
- `pretrain_different_operation_matched`: acq=1.000, mean censored time=86144.0, final=0.845
- `pretrain_same_operation_unrelated`: acq=1.000, mean censored time=0.0, final=0.852

## Intervention contrasts
- `exact_pretrain_vs_same_operation`: `pretrain_component` vs `pretrain_same_operation_unrelated` (earlier): strict Δ=0.000 (n=10), censored Δ=0.000, censored-rate=0.000, Δfinal=0.000
- `exact_pretrain_vs_different_operation`: `pretrain_component` vs `pretrain_different_operation_matched` (earlier): strict Δ=-86144.000 (n=10), censored Δ=-86144.000, censored-rate=1.000, Δfinal=0.007
- `operation_family_pretrain_vs_different_operation`: `pretrain_same_operation_unrelated` vs `pretrain_different_operation_matched` (earlier): strict Δ=-86144.000 (n=10), censored Δ=-86144.000, censored-rate=1.000, Δfinal=0.007
- `exact_strong_corrupt_vs_same_operation`: `corrupt_component_strong` vs `corrupt_same_operation_unrelated_strong` (later): strict Δ=-768.000 (n=10), censored Δ=-768.000, censored-rate=0.300, Δfinal=0.001
- `exact_strong_corrupt_vs_different_operation`: `corrupt_component_strong` vs `corrupt_different_operation_matched_strong` (later): strict Δ=537.600 (n=10), censored Δ=537.600, censored-rate=0.300, Δfinal=-0.016
- `exact_strong_delay_vs_same_operation`: `delay_component_strong` vs `delay_same_operation_unrelated_strong` (later): strict Δ=0.000 (n=10), censored Δ=0.000, censored-rate=0.000, Δfinal=-0.003
- `exact_strong_delay_vs_different_operation`: `delay_component_strong` vs `delay_different_operation_matched_strong` (later): strict Δ=3200.000 (n=10), censored Δ=3200.000, censored-rate=0.600, Δfinal=-0.003

## Decision aid
- mean censored expected-direction rate: `0.457`
- mean final-metric expected-direction rate: `0.500`
- exact-vs-same-operation censored expected-direction rate: `0.100`
- exact/different-operation censored expected-direction rate: `0.725`

GREEN for exact-component dependency requires exact-component interventions to beat same-operation, different-operation, fake, and surface controls. If component and same-operation controls both help similarly, interpret the result as operation-family transfer rather than exact dependency.