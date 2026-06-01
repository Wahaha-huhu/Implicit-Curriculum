# B1 H3 pair-specific intervention analysis

This is an H3 pilot analysis. It tests whether component interventions move the selected composite beyond matched control interventions. It is causal only within this controlled training setup and remains a pilot until replicated across more pairs/families.

Primary metric: `token_accuracy` threshold `0.7`.

## Pair
- component: `A02_substitute`
- composite: `C03_reverse_then_substitute_07_02`
- unrelated_control: `U00_unrelated_substitute`
- same_operation_control: `U00_unrelated_substitute`
- different_operation_control: `A03_copy`
- fake_component_control: `K01_shortcut_for_A05_substitute`
- surface_control: `S01_surface_rotate`

## Composite acquisition by condition
- `baseline`: acq=1.000, mean censored time=181760.0, final=0.785
- `corrupt_component`: acq=0.900, mean censored time=182988.8, final=0.788
- `corrupt_component_strong`: acq=1.000, mean censored time=178201.6, final=0.796
- `corrupt_different_operation_matched`: acq=1.000, mean censored time=172518.4, final=0.794
- `corrupt_different_operation_matched_strong`: acq=1.000, mean censored time=180377.6, final=0.788
- `corrupt_same_operation_unrelated`: acq=1.000, mean censored time=180966.4, final=0.792
- `corrupt_same_operation_unrelated_strong`: acq=1.000, mean censored time=173516.8, final=0.788
- `delay_component`: acq=1.000, mean censored time=175462.4, final=0.790
- `delay_component_strong`: acq=1.000, mean censored time=173004.8, final=0.791
- `delay_different_operation_matched`: acq=1.000, mean censored time=180198.4, final=0.787
- `delay_different_operation_matched_strong`: acq=1.000, mean censored time=180198.4, final=0.786
- `delay_same_operation_unrelated`: acq=0.900, mean censored time=182169.6, final=0.778
- `delay_same_operation_unrelated_strong`: acq=0.900, mean censored time=183731.2, final=0.781
- `pretrain_component`: acq=0.500, mean censored time=228377.6, final=0.765
- `pretrain_different_operation_matched`: acq=0.600, mean censored time=222003.2, final=0.719
- `pretrain_same_operation_unrelated`: acq=0.500, mean censored time=238540.8, final=0.674
- `upweight_component`: acq=0.900, mean censored time=184345.6, final=0.772
- `upweight_different_operation_matched`: acq=0.900, mean censored time=184371.2, final=0.776
- `upweight_fake_component`: acq=1.000, mean censored time=180070.4, final=0.786
- `upweight_same_operation_unrelated`: acq=1.000, mean censored time=186035.2, final=0.780
- `upweight_surface_control`: acq=1.000, mean censored time=174694.4, final=0.781

## Intervention contrasts
- `exact_vs_same_operation`: `upweight_component` vs `upweight_same_operation_unrelated` (earlier): strict Δ=-7111.111 (n=9), censored Δ=-1689.600, censored-rate=0.500, Δfinal=-0.008
- `exact_vs_different_operation`: `upweight_component` vs `upweight_different_operation_matched` (earlier): strict Δ=-1856.000 (n=8), censored Δ=-25.600, censored-rate=0.300, Δfinal=-0.004
- `exact_vs_fake_component`: `upweight_component` vs `upweight_fake_component` (earlier): strict Δ=-483.556 (n=9), censored Δ=4275.200, censored-rate=0.400, Δfinal=-0.014
- `exact_vs_surface`: `upweight_component` vs `upweight_surface_control` (earlier): strict Δ=3953.778 (n=9), censored Δ=9651.200, censored-rate=0.100, Δfinal=-0.009
- `operation_family_vs_different_operation`: `upweight_same_operation_unrelated` vs `upweight_different_operation_matched` (earlier): strict Δ=3726.222 (n=9), censored Δ=1664.000, censored-rate=0.200, Δfinal=0.004
- `exact_corrupt_vs_same_operation`: `corrupt_component` vs `corrupt_same_operation_unrelated` (later): strict Δ=-4522.667 (n=9), censored Δ=2022.400, censored-rate=0.300, Δfinal=-0.004
- `exact_corrupt_vs_different_operation`: `corrupt_component` vs `corrupt_different_operation_matched` (later): strict Δ=2133.333 (n=9), censored Δ=10470.400, censored-rate=0.300, Δfinal=-0.006
- `exact_delay_vs_same_operation`: `delay_component` vs `delay_same_operation_unrelated` (later): strict Δ=-3840.000 (n=9), censored Δ=-6707.200, censored-rate=0.200, Δfinal=0.012
- `exact_delay_vs_different_operation`: `delay_component` vs `delay_different_operation_matched` (later): strict Δ=-4736.000 (n=10), censored Δ=-4736.000, censored-rate=0.100, Δfinal=0.003
- `exact_pretrain_vs_same_operation`: `pretrain_component` vs `pretrain_same_operation_unrelated` (earlier): strict Δ=-35712.000 (n=2), censored Δ=-10163.200, censored-rate=0.500, Δfinal=0.091
- `exact_pretrain_vs_different_operation`: `pretrain_component` vs `pretrain_different_operation_matched` (earlier): strict Δ=-7296.000 (n=2), censored Δ=6374.400, censored-rate=0.400, Δfinal=0.047
- `operation_family_pretrain_vs_different_operation`: `pretrain_same_operation_unrelated` vs `pretrain_different_operation_matched` (earlier): strict Δ=25920.000 (n=4), censored Δ=16537.600, censored-rate=0.100, Δfinal=-0.045
- `exact_strong_corrupt_vs_same_operation`: `corrupt_component_strong` vs `corrupt_same_operation_unrelated_strong` (later): strict Δ=4684.800 (n=10), censored Δ=4684.800, censored-rate=0.500, Δfinal=0.008
- `exact_strong_corrupt_vs_different_operation`: `corrupt_component_strong` vs `corrupt_different_operation_matched_strong` (later): strict Δ=-2176.000 (n=10), censored Δ=-2176.000, censored-rate=0.200, Δfinal=0.008
- `exact_strong_delay_vs_same_operation`: `delay_component_strong` vs `delay_same_operation_unrelated_strong` (later): strict Δ=-8305.778 (n=9), censored Δ=-10726.400, censored-rate=0.200, Δfinal=0.010
- `exact_strong_delay_vs_different_operation`: `delay_component_strong` vs `delay_different_operation_matched_strong` (later): strict Δ=-7193.600 (n=10), censored Δ=-7193.600, censored-rate=0.100, Δfinal=0.006

## Decision aid
- mean censored expected-direction rate: `0.275`
- mean final-metric expected-direction rate: `0.406`
- exact-vs-same-operation censored expected-direction rate: `0.367`
- exact/different-operation censored expected-direction rate: `0.213`

GREEN for exact-component dependency requires exact-component interventions to beat same-operation, different-operation, fake, and surface controls. If component and same-operation controls both help similarly, interpret the result as operation-family transfer rather than exact dependency.