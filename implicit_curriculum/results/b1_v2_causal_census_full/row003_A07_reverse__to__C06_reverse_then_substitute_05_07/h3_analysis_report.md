# B1 H3 pair-specific intervention analysis

This is an H3 pilot analysis. It tests whether component interventions move the selected composite beyond matched control interventions. It is causal only within this controlled training setup and remains a pilot until replicated across more pairs/families.

Primary metric: `token_accuracy` threshold `0.7`.

## Pair
- component: `A07_reverse`
- composite: `C06_reverse_then_substitute_05_07`
- unrelated_control: `A01_reverse`
- same_operation_control: `A01_reverse`
- different_operation_control: `U01_unrelated_substitute`
- fake_component_control: `K02_shortcut_for_A03_copy`
- surface_control: `S00_surface_rotate`

## Composite acquisition by condition
- `baseline`: acq=1.000, mean censored time=180480.0, final=0.787
- `corrupt_component`: acq=1.000, mean censored time=178048.0, final=0.789
- `corrupt_component_strong`: acq=0.900, mean censored time=178688.0, final=0.782
- `corrupt_different_operation_matched`: acq=0.900, mean censored time=175616.0, final=0.779
- `corrupt_different_operation_matched_strong`: acq=1.000, mean censored time=182681.6, final=0.786
- `corrupt_same_operation_unrelated`: acq=1.000, mean censored time=172979.2, final=0.789
- `corrupt_same_operation_unrelated_strong`: acq=0.900, mean censored time=181222.4, final=0.781
- `delay_component`: acq=1.000, mean censored time=173824.0, final=0.785
- `delay_component_strong`: acq=1.000, mean censored time=173542.4, final=0.790
- `delay_different_operation_matched`: acq=1.000, mean censored time=177740.8, final=0.788
- `delay_different_operation_matched_strong`: acq=1.000, mean censored time=180761.6, final=0.789
- `delay_same_operation_unrelated`: acq=1.000, mean censored time=170342.4, final=0.789
- `delay_same_operation_unrelated_strong`: acq=1.000, mean censored time=173516.8, final=0.788
- `pretrain_component`: acq=1.000, mean censored time=194048.0, final=0.787
- `pretrain_different_operation_matched`: acq=0.500, mean censored time=238540.8, final=0.670
- `pretrain_same_operation_unrelated`: acq=1.000, mean censored time=194048.0, final=0.787
- `upweight_component`: acq=1.000, mean censored time=174336.0, final=0.784
- `upweight_different_operation_matched`: acq=1.000, mean censored time=183526.4, final=0.778
- `upweight_fake_component`: acq=1.000, mean censored time=173004.8, final=0.784
- `upweight_same_operation_unrelated`: acq=1.000, mean censored time=168985.6, final=0.789
- `upweight_surface_control`: acq=1.000, mean censored time=156774.4, final=0.788

## Intervention contrasts
- `exact_vs_same_operation`: `upweight_component` vs `upweight_same_operation_unrelated` (earlier): strict Δ=5350.400 (n=10), censored Δ=5350.400, censored-rate=0.300, Δfinal=-0.005
- `exact_vs_different_operation`: `upweight_component` vs `upweight_different_operation_matched` (earlier): strict Δ=-9190.400 (n=10), censored Δ=-9190.400, censored-rate=0.500, Δfinal=0.006
- `exact_vs_fake_component`: `upweight_component` vs `upweight_fake_component` (earlier): strict Δ=1331.200 (n=10), censored Δ=1331.200, censored-rate=0.300, Δfinal=0.001
- `exact_vs_surface`: `upweight_component` vs `upweight_surface_control` (earlier): strict Δ=17561.600 (n=10), censored Δ=17561.600, censored-rate=0.100, Δfinal=-0.003
- `operation_family_vs_different_operation`: `upweight_same_operation_unrelated` vs `upweight_different_operation_matched` (earlier): strict Δ=-14540.800 (n=10), censored Δ=-14540.800, censored-rate=0.600, Δfinal=0.010
- `exact_corrupt_vs_same_operation`: `corrupt_component` vs `corrupt_same_operation_unrelated` (later): strict Δ=5068.800 (n=10), censored Δ=5068.800, censored-rate=0.300, Δfinal=0.001
- `exact_corrupt_vs_different_operation`: `corrupt_component` vs `corrupt_different_operation_matched` (later): strict Δ=6314.667 (n=9), censored Δ=2432.000, censored-rate=0.300, Δfinal=0.011
- `exact_delay_vs_same_operation`: `delay_component` vs `delay_same_operation_unrelated` (later): strict Δ=3481.600 (n=10), censored Δ=3481.600, censored-rate=0.400, Δfinal=-0.003
- `exact_delay_vs_different_operation`: `delay_component` vs `delay_different_operation_matched` (later): strict Δ=-3916.800 (n=10), censored Δ=-3916.800, censored-rate=0.300, Δfinal=-0.003
- `exact_pretrain_vs_same_operation`: `pretrain_component` vs `pretrain_same_operation_unrelated` (earlier): strict Δ=0.000 (n=10), censored Δ=0.000, censored-rate=0.000, Δfinal=0.000
- `exact_pretrain_vs_different_operation`: `pretrain_component` vs `pretrain_different_operation_matched` (earlier): strict Δ=-32870.400 (n=5), censored Δ=-44492.800, censored-rate=0.900, Δfinal=0.117
- `operation_family_pretrain_vs_different_operation`: `pretrain_same_operation_unrelated` vs `pretrain_different_operation_matched` (earlier): strict Δ=-32870.400 (n=5), censored Δ=-44492.800, censored-rate=0.900, Δfinal=0.117
- `exact_strong_corrupt_vs_same_operation`: `corrupt_component_strong` vs `corrupt_same_operation_unrelated_strong` (later): strict Δ=-2816.000 (n=9), censored Δ=-2534.400, censored-rate=0.100, Δfinal=0.001
- `exact_strong_corrupt_vs_different_operation`: `corrupt_component_strong` vs `corrupt_different_operation_matched_strong` (later): strict Δ=-8049.778 (n=9), censored Δ=-3993.600, censored-rate=0.300, Δfinal=-0.005
- `exact_strong_delay_vs_same_operation`: `delay_component_strong` vs `delay_same_operation_unrelated_strong` (later): strict Δ=25.600 (n=10), censored Δ=25.600, censored-rate=0.300, Δfinal=0.002
- `exact_strong_delay_vs_different_operation`: `delay_component_strong` vs `delay_different_operation_matched_strong` (later): strict Δ=-7219.200 (n=10), censored Δ=-7219.200, censored-rate=0.200, Δfinal=0.001

## Decision aid
- mean censored expected-direction rate: `0.363`
- mean final-metric expected-direction rate: `0.537`
- exact-vs-same-operation censored expected-direction rate: `0.233`
- exact/different-operation censored expected-direction rate: `0.500`

GREEN for exact-component dependency requires exact-component interventions to beat same-operation, different-operation, fake, and surface controls. If component and same-operation controls both help similarly, interpret the result as operation-family transfer rather than exact dependency.