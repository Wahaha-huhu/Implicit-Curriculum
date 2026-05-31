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
- `baseline`: acq=0.333, mean censored time=229802.7, final=0.691
- `corrupt_component_strong`: acq=0.000, mean censored time=250112.0, final=0.664
- `corrupt_different_operation_matched_strong`: acq=0.667, mean censored time=224170.7, final=0.717
- `corrupt_same_operation_unrelated_strong`: acq=0.667, mean censored time=218965.3, final=0.745
- `delay_component_strong`: acq=0.000, mean censored time=250112.0, final=0.677
- `delay_different_operation_matched_strong`: acq=0.000, mean censored time=250112.0, final=0.691
- `delay_same_operation_unrelated_strong`: acq=0.333, mean censored time=225536.0, final=0.705
- `pretrain_component`: acq=1.000, mean censored time=0.0, final=0.726
- `pretrain_different_operation_matched`: acq=0.333, mean censored time=244480.0, final=0.706
- `pretrain_same_operation_unrelated`: acq=0.000, mean censored time=250112.0, final=0.569

## Intervention contrasts
- `exact_pretrain_vs_same_operation`: `pretrain_component` vs `pretrain_same_operation_unrelated` (earlier): strict Δ=nan (n=0), censored Δ=-250112.000, censored-rate=1.000, Δfinal=0.157
- `exact_pretrain_vs_different_operation`: `pretrain_component` vs `pretrain_different_operation_matched` (earlier): strict Δ=-233216.000 (n=1), censored Δ=-244480.000, censored-rate=1.000, Δfinal=0.020
- `operation_family_pretrain_vs_different_operation`: `pretrain_same_operation_unrelated` vs `pretrain_different_operation_matched` (earlier): strict Δ=nan (n=0), censored Δ=5632.000, censored-rate=0.000, Δfinal=-0.137
- `exact_strong_corrupt_vs_same_operation`: `corrupt_component_strong` vs `corrupt_same_operation_unrelated_strong` (later): strict Δ=nan (n=0), censored Δ=31146.667, censored-rate=0.667, Δfinal=-0.081
- `exact_strong_corrupt_vs_different_operation`: `corrupt_component_strong` vs `corrupt_different_operation_matched_strong` (later): strict Δ=nan (n=0), censored Δ=25941.333, censored-rate=0.667, Δfinal=-0.053
- `exact_strong_delay_vs_same_operation`: `delay_component_strong` vs `delay_same_operation_unrelated_strong` (later): strict Δ=nan (n=0), censored Δ=24576.000, censored-rate=0.333, Δfinal=-0.028
- `exact_strong_delay_vs_different_operation`: `delay_component_strong` vs `delay_different_operation_matched_strong` (later): strict Δ=nan (n=0), censored Δ=0.000, censored-rate=0.000, Δfinal=-0.014

## Decision aid
- mean censored expected-direction rate: `0.524`
- mean final-metric expected-direction rate: `0.714`
- exact-vs-same-operation censored expected-direction rate: `0.667`
- exact/different-operation censored expected-direction rate: `0.417`

GREEN for exact-component dependency requires exact-component interventions to beat same-operation, different-operation, fake, and surface controls. If component and same-operation controls both help similarly, interpret the result as operation-family transfer rather than exact dependency.