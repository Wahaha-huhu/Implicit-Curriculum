# B1 H3 pair-specific intervention analysis

This is an H3 pilot analysis. It tests whether component interventions move the selected composite beyond matched control interventions. It is causal only within this controlled training setup and remains a pilot until replicated across more pairs/families.

Primary metric: `token_accuracy` threshold `0.7`.

## Pair
- component: `A05_substitute`
- composite: `C06_reverse_then_substitute_05_07`
- unrelated_control: `U01_unrelated_substitute`
- same_operation_control: `U01_unrelated_substitute`
- different_operation_control: `A04_reverse`
- fake_component_control: `K00_shortcut_for_A02_substitute`
- surface_control: `S02_surface_rotate`

## Composite acquisition by condition
- `baseline`: acq=1.000, mean censored time=180480.0, final=0.787
- `corrupt_component`: acq=1.000, mean censored time=171059.2, final=0.791
- `corrupt_component_strong`: acq=1.000, mean censored time=169497.6, final=0.796
- `corrupt_different_operation_matched`: acq=0.900, mean censored time=181017.6, final=0.782
- `corrupt_different_operation_matched_strong`: acq=0.900, mean censored time=183424.0, final=0.785
- `corrupt_same_operation_unrelated`: acq=0.900, mean censored time=175616.0, final=0.779
- `corrupt_same_operation_unrelated_strong`: acq=1.000, mean censored time=182681.6, final=0.786
- `delay_component`: acq=1.000, mean censored time=172953.6, final=0.786
- `delay_component_strong`: acq=1.000, mean censored time=170649.6, final=0.786
- `delay_different_operation_matched`: acq=1.000, mean censored time=173900.8, final=0.790
- `delay_different_operation_matched_strong`: acq=1.000, mean censored time=173900.8, final=0.790
- `delay_same_operation_unrelated`: acq=1.000, mean censored time=177740.8, final=0.788
- `delay_same_operation_unrelated_strong`: acq=1.000, mean censored time=180761.6, final=0.789
- `pretrain_component`: acq=0.500, mean censored time=228556.8, final=0.763
- `pretrain_different_operation_matched`: acq=1.000, mean censored time=194048.0, final=0.787
- `pretrain_same_operation_unrelated`: acq=0.500, mean censored time=238540.8, final=0.670
- `upweight_component`: acq=1.000, mean censored time=187289.6, final=0.786
- `upweight_different_operation_matched`: acq=1.000, mean censored time=183500.8, final=0.780
- `upweight_fake_component`: acq=1.000, mean censored time=176640.0, final=0.785
- `upweight_same_operation_unrelated`: acq=1.000, mean censored time=183526.4, final=0.778
- `upweight_surface_control`: acq=0.900, mean censored time=180582.4, final=0.768

## Intervention contrasts
- `exact_vs_same_operation`: `upweight_component` vs `upweight_same_operation_unrelated` (earlier): strict Δ=3763.200 (n=10), censored Δ=3763.200, censored-rate=0.300, Δfinal=0.008
- `exact_vs_different_operation`: `upweight_component` vs `upweight_different_operation_matched` (earlier): strict Δ=3788.800 (n=10), censored Δ=3788.800, censored-rate=0.100, Δfinal=0.006
- `exact_vs_fake_component`: `upweight_component` vs `upweight_fake_component` (earlier): strict Δ=10649.600 (n=10), censored Δ=10649.600, censored-rate=0.100, Δfinal=0.001
- `exact_vs_surface`: `upweight_component` vs `upweight_surface_control` (earlier): strict Δ=12686.222 (n=9), censored Δ=6707.200, censored-rate=0.100, Δfinal=0.018
- `operation_family_vs_different_operation`: `upweight_same_operation_unrelated` vs `upweight_different_operation_matched` (earlier): strict Δ=25.600 (n=10), censored Δ=25.600, censored-rate=0.300, Δfinal=-0.001
- `exact_corrupt_vs_same_operation`: `corrupt_component` vs `corrupt_same_operation_unrelated` (later): strict Δ=3128.889 (n=9), censored Δ=-4556.800, censored-rate=0.300, Δfinal=0.012
- `exact_corrupt_vs_different_operation`: `corrupt_component` vs `corrupt_different_operation_matched` (later): strict Δ=-1564.444 (n=9), censored Δ=-9958.400, censored-rate=0.300, Δfinal=0.009
- `exact_delay_vs_same_operation`: `delay_component` vs `delay_same_operation_unrelated` (later): strict Δ=-4787.200 (n=10), censored Δ=-4787.200, censored-rate=0.200, Δfinal=-0.002
- `exact_delay_vs_different_operation`: `delay_component` vs `delay_different_operation_matched` (later): strict Δ=-947.200 (n=10), censored Δ=-947.200, censored-rate=0.000, Δfinal=-0.003
- `exact_pretrain_vs_same_operation`: `pretrain_component` vs `pretrain_same_operation_unrelated` (earlier): strict Δ=-42624.000 (n=2), censored Δ=-9984.000, censored-rate=0.500, Δfinal=0.093
- `exact_pretrain_vs_different_operation`: `pretrain_component` vs `pretrain_different_operation_matched` (earlier): strict Δ=204.800 (n=5), censored Δ=34508.800, censored-rate=0.200, Δfinal=-0.024
- `operation_family_pretrain_vs_different_operation`: `pretrain_same_operation_unrelated` vs `pretrain_different_operation_matched` (earlier): strict Δ=32870.400 (n=5), censored Δ=44492.800, censored-rate=0.000, Δfinal=-0.117
- `exact_strong_corrupt_vs_same_operation`: `corrupt_component_strong` vs `corrupt_same_operation_unrelated_strong` (later): strict Δ=-13184.000 (n=10), censored Δ=-13184.000, censored-rate=0.200, Δfinal=0.010
- `exact_strong_corrupt_vs_different_operation`: `corrupt_component_strong` vs `corrupt_different_operation_matched_strong` (later): strict Δ=-7281.778 (n=9), censored Δ=-13926.400, censored-rate=0.200, Δfinal=0.012
- `exact_strong_delay_vs_same_operation`: `delay_component_strong` vs `delay_same_operation_unrelated_strong` (later): strict Δ=-10112.000 (n=10), censored Δ=-10112.000, censored-rate=0.100, Δfinal=-0.003
- `exact_strong_delay_vs_different_operation`: `delay_component_strong` vs `delay_different_operation_matched_strong` (later): strict Δ=-3251.200 (n=10), censored Δ=-3251.200, censored-rate=0.000, Δfinal=-0.004

## Decision aid
- mean censored expected-direction rate: `0.181`
- mean final-metric expected-direction rate: `0.431`
- exact-vs-same-operation censored expected-direction rate: `0.267`
- exact/different-operation censored expected-direction rate: `0.138`

GREEN for exact-component dependency requires exact-component interventions to beat same-operation, different-operation, fake, and surface controls. If component and same-operation controls both help similarly, interpret the result as operation-family transfer rather than exact dependency.