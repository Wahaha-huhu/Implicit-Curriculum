# B1 H3 pair-specific intervention analysis

This is an H3 pilot analysis. It tests whether component interventions move the selected composite beyond matched control interventions. It is causal only within this controlled training setup and remains a pilot until replicated across more pairs/families.

Primary metric: `token_accuracy` threshold `0.5`.

## Pair
- component: `A01_reverse`
- composite: `C06_reverse_then_substitute_01_05`
- unrelated_control: `A07_reverse`
- same_operation_control: `A07_reverse`
- different_operation_control: `U00_unrelated_substitute`
- fake_component_control: `K01_shortcut_for_A03_copy`
- surface_control: `S00_surface_rotate`

## Composite acquisition by condition
- `baseline`: acq=0.100, mean censored time=246860.8, final=0.418
- `corrupt_component_strong`: acq=0.000, mean censored time=250112.0, final=0.292
- `corrupt_different_operation_matched_strong`: acq=0.100, mean censored time=248422.4, final=0.424
- `corrupt_same_operation_unrelated_strong`: acq=0.000, mean censored time=250112.0, final=0.425
- `delay_component_strong`: acq=0.200, mean censored time=239308.8, final=0.470
- `delay_different_operation_matched_strong`: acq=0.200, mean censored time=245171.2, final=0.404
- `delay_same_operation_unrelated_strong`: acq=0.200, mean censored time=246732.8, final=0.407
- `pretrain_component`: acq=0.200, mean censored time=246732.8, final=0.445
- `pretrain_different_operation_matched`: acq=0.000, mean censored time=250112.0, final=0.236
- `pretrain_same_operation_unrelated`: acq=0.200, mean censored time=246732.8, final=0.445

## Intervention contrasts
- `exact_pretrain_vs_same_operation`: `pretrain_component` vs `pretrain_same_operation_unrelated` (earlier): strict Δ=0.000 (n=2), censored Δ=0.000, censored-rate=0.000, Δfinal=0.000
- `exact_pretrain_vs_different_operation`: `pretrain_component` vs `pretrain_different_operation_matched` (earlier): strict Δ=nan (n=0), censored Δ=-3379.200, censored-rate=0.200, Δfinal=0.209
- `operation_family_pretrain_vs_different_operation`: `pretrain_same_operation_unrelated` vs `pretrain_different_operation_matched` (earlier): strict Δ=nan (n=0), censored Δ=-3379.200, censored-rate=0.200, Δfinal=0.209
- `exact_strong_corrupt_vs_same_operation`: `corrupt_component_strong` vs `corrupt_same_operation_unrelated_strong` (later): strict Δ=nan (n=0), censored Δ=0.000, censored-rate=0.000, Δfinal=-0.133
- `exact_strong_corrupt_vs_different_operation`: `corrupt_component_strong` vs `corrupt_different_operation_matched_strong` (later): strict Δ=nan (n=0), censored Δ=1689.600, censored-rate=0.100, Δfinal=-0.132
- `exact_strong_delay_vs_same_operation`: `delay_component_strong` vs `delay_same_operation_unrelated_strong` (later): strict Δ=-44032.000 (n=1), censored Δ=-7424.000, censored-rate=0.100, Δfinal=0.062
- `exact_strong_delay_vs_different_operation`: `delay_component_strong` vs `delay_different_operation_matched_strong` (later): strict Δ=-28416.000 (n=1), censored Δ=-5862.400, censored-rate=0.100, Δfinal=0.066

## Decision aid
- mean censored expected-direction rate: `0.100`
- mean final-metric expected-direction rate: `0.529`
- exact-vs-same-operation censored expected-direction rate: `0.033`
- exact/different-operation censored expected-direction rate: `0.150`

GREEN for exact-component dependency requires exact-component interventions to beat same-operation, different-operation, fake, and surface controls. If component and same-operation controls both help similarly, interpret the result as operation-family transfer rather than exact dependency.