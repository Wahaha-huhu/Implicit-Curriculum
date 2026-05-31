# B1 H3 pair-specific intervention analysis

This is an H3 pilot analysis. It tests whether component interventions move the selected composite beyond matched control interventions. It is causal only within this controlled training setup and remains a pilot until replicated across more pairs/families.

Primary metric: `token_accuracy` threshold `0.7`.

## Pair
- component: `A03_copy`
- composite: `C07_substitute_then_reverse_04_03`
- unrelated_control: `A06_copy`
- same_operation_control: `A06_copy`
- different_operation_control: `U01_unrelated_substitute`
- fake_component_control: `K02_shortcut_for_A04_reverse`
- surface_control: `S01_surface_rotate`

## Composite acquisition by condition
- `baseline`: acq=1.000, mean censored time=64332.8, final=0.843
- `corrupt_component_strong`: acq=1.000, mean censored time=63078.4, final=0.870
- `corrupt_different_operation_matched_strong`: acq=1.000, mean censored time=62617.6, final=0.846
- `corrupt_same_operation_unrelated_strong`: acq=1.000, mean censored time=63539.2, final=0.855
- `delay_component_strong`: acq=1.000, mean censored time=15513.6, final=0.847
- `delay_different_operation_matched_strong`: acq=1.000, mean censored time=61696.0, final=0.843
- `delay_same_operation_unrelated_strong`: acq=1.000, mean censored time=56780.8, final=0.844
- `pretrain_component`: acq=1.000, mean censored time=85427.2, final=0.831
- `pretrain_different_operation_matched`: acq=1.000, mean censored time=86579.2, final=0.849
- `pretrain_same_operation_unrelated`: acq=1.000, mean censored time=85427.2, final=0.831

## Intervention contrasts
- `exact_pretrain_vs_same_operation`: `pretrain_component` vs `pretrain_same_operation_unrelated` (earlier): strict Δ=0.000 (n=10), censored Δ=0.000, censored-rate=0.000, Δfinal=0.000
- `exact_pretrain_vs_different_operation`: `pretrain_component` vs `pretrain_different_operation_matched` (earlier): strict Δ=-1152.000 (n=10), censored Δ=-1152.000, censored-rate=0.400, Δfinal=-0.018
- `operation_family_pretrain_vs_different_operation`: `pretrain_same_operation_unrelated` vs `pretrain_different_operation_matched` (earlier): strict Δ=-1152.000 (n=10), censored Δ=-1152.000, censored-rate=0.400, Δfinal=-0.018
- `exact_strong_corrupt_vs_same_operation`: `corrupt_component_strong` vs `corrupt_same_operation_unrelated_strong` (later): strict Δ=-460.800 (n=10), censored Δ=-460.800, censored-rate=0.000, Δfinal=0.015
- `exact_strong_corrupt_vs_different_operation`: `corrupt_component_strong` vs `corrupt_different_operation_matched_strong` (later): strict Δ=460.800 (n=10), censored Δ=460.800, censored-rate=0.300, Δfinal=0.024
- `exact_strong_delay_vs_same_operation`: `delay_component_strong` vs `delay_same_operation_unrelated_strong` (later): strict Δ=-41267.200 (n=10), censored Δ=-41267.200, censored-rate=0.000, Δfinal=0.002
- `exact_strong_delay_vs_different_operation`: `delay_component_strong` vs `delay_different_operation_matched_strong` (later): strict Δ=-46182.400 (n=10), censored Δ=-46182.400, censored-rate=0.000, Δfinal=0.004

## Decision aid
- mean censored expected-direction rate: `0.157`
- mean final-metric expected-direction rate: `0.214`
- exact-vs-same-operation censored expected-direction rate: `0.000`
- exact/different-operation censored expected-direction rate: `0.275`

GREEN for exact-component dependency requires exact-component interventions to beat same-operation, different-operation, fake, and surface controls. If component and same-operation controls both help similarly, interpret the result as operation-family transfer rather than exact dependency.