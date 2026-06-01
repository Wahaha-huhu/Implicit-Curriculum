# B1 H3 pair-specific intervention analysis

This is an H3 pilot analysis. It tests whether component interventions move the selected composite beyond matched control interventions. It is causal only within this controlled training setup and remains a pilot until replicated across more pairs/families.

Primary metric: `token_accuracy` threshold `0.7`.

## Pair
- component: `A07_reverse`
- composite: `C03_reverse_then_substitute_07_02`
- unrelated_control: `A01_reverse`
- same_operation_control: `A01_reverse`
- different_operation_control: `U01_unrelated_substitute`
- fake_component_control: `K02_shortcut_for_A03_copy`
- surface_control: `S00_surface_rotate`

## Composite acquisition by condition
- `baseline`: acq=1.000, mean censored time=181760.0, final=0.785
- `corrupt_component`: acq=1.000, mean censored time=176998.4, final=0.789
- `corrupt_component_strong`: acq=0.900, mean censored time=179046.4, final=0.782
- `corrupt_different_operation_matched`: acq=0.900, mean censored time=176793.6, final=0.779
- `corrupt_different_operation_matched_strong`: acq=1.000, mean censored time=182681.6, final=0.784
- `corrupt_same_operation_unrelated`: acq=1.000, mean censored time=172928.0, final=0.792
- `corrupt_same_operation_unrelated_strong`: acq=0.900, mean censored time=178995.2, final=0.781
- `delay_component`: acq=1.000, mean censored time=173824.0, final=0.785
- `delay_component_strong`: acq=1.000, mean censored time=175001.6, final=0.788
- `delay_different_operation_matched`: acq=1.000, mean censored time=179020.8, final=0.786
- `delay_different_operation_matched_strong`: acq=1.000, mean censored time=180761.6, final=0.787
- `delay_same_operation_unrelated`: acq=1.000, mean censored time=173568.0, final=0.788
- `delay_same_operation_unrelated_strong`: acq=1.000, mean censored time=175462.4, final=0.788
- `pretrain_component`: acq=1.000, mean censored time=194048.0, final=0.787
- `pretrain_different_operation_matched`: acq=0.500, mean censored time=238540.8, final=0.674
- `pretrain_same_operation_unrelated`: acq=1.000, mean censored time=194048.0, final=0.787
- `upweight_component`: acq=1.000, mean censored time=175257.6, final=0.784
- `upweight_different_operation_matched`: acq=1.000, mean censored time=185472.0, final=0.776
- `upweight_fake_component`: acq=1.000, mean censored time=174950.4, final=0.782
- `upweight_same_operation_unrelated`: acq=1.000, mean censored time=168985.6, final=0.789
- `upweight_surface_control`: acq=1.000, mean censored time=157875.2, final=0.787

## Intervention contrasts
- `exact_vs_same_operation`: `upweight_component` vs `upweight_same_operation_unrelated` (earlier): strict Δ=6272.000 (n=10), censored Δ=6272.000, censored-rate=0.200, Δfinal=-0.005
- `exact_vs_different_operation`: `upweight_component` vs `upweight_different_operation_matched` (earlier): strict Δ=-10214.400 (n=10), censored Δ=-10214.400, censored-rate=0.500, Δfinal=0.008
- `exact_vs_fake_component`: `upweight_component` vs `upweight_fake_component` (earlier): strict Δ=307.200 (n=10), censored Δ=307.200, censored-rate=0.200, Δfinal=0.002
- `exact_vs_surface`: `upweight_component` vs `upweight_surface_control` (earlier): strict Δ=17382.400 (n=10), censored Δ=17382.400, censored-rate=0.100, Δfinal=-0.003
- `operation_family_vs_different_operation`: `upweight_same_operation_unrelated` vs `upweight_different_operation_matched` (earlier): strict Δ=-16486.400 (n=10), censored Δ=-16486.400, censored-rate=0.600, Δfinal=0.013
- `exact_corrupt_vs_same_operation`: `corrupt_component` vs `corrupt_same_operation_unrelated` (later): strict Δ=4070.400 (n=10), censored Δ=4070.400, censored-rate=0.300, Δfinal=-0.003
- `exact_corrupt_vs_different_operation`: `corrupt_component` vs `corrupt_different_operation_matched` (later): strict Δ=3840.000 (n=9), censored Δ=204.800, censored-rate=0.300, Δfinal=0.010
- `exact_delay_vs_same_operation`: `delay_component` vs `delay_same_operation_unrelated` (later): strict Δ=256.000 (n=10), censored Δ=256.000, censored-rate=0.400, Δfinal=-0.004
- `exact_delay_vs_different_operation`: `delay_component` vs `delay_different_operation_matched` (later): strict Δ=-5196.800 (n=10), censored Δ=-5196.800, censored-rate=0.300, Δfinal=-0.002
- `exact_pretrain_vs_same_operation`: `pretrain_component` vs `pretrain_same_operation_unrelated` (earlier): strict Δ=0.000 (n=10), censored Δ=0.000, censored-rate=0.000, Δfinal=0.000
- `exact_pretrain_vs_different_operation`: `pretrain_component` vs `pretrain_different_operation_matched` (earlier): strict Δ=-32870.400 (n=5), censored Δ=-44492.800, censored-rate=0.900, Δfinal=0.113
- `operation_family_pretrain_vs_different_operation`: `pretrain_same_operation_unrelated` vs `pretrain_different_operation_matched` (earlier): strict Δ=-32870.400 (n=5), censored Δ=-44492.800, censored-rate=0.900, Δfinal=0.113
- `exact_strong_corrupt_vs_same_operation`: `corrupt_component_strong` vs `corrupt_same_operation_unrelated_strong` (later): strict Δ=56.889 (n=9), censored Δ=51.200, censored-rate=0.300, Δfinal=0.001
- `exact_strong_corrupt_vs_different_operation`: `corrupt_component_strong` vs `corrupt_different_operation_matched_strong` (later): strict Δ=-7651.556 (n=9), censored Δ=-3635.200, censored-rate=0.400, Δfinal=-0.002
- `exact_strong_delay_vs_same_operation`: `delay_component_strong` vs `delay_same_operation_unrelated_strong` (later): strict Δ=-460.800 (n=10), censored Δ=-460.800, censored-rate=0.300, Δfinal=0.001
- `exact_strong_delay_vs_different_operation`: `delay_component_strong` vs `delay_different_operation_matched_strong` (later): strict Δ=-5760.000 (n=10), censored Δ=-5760.000, censored-rate=0.200, Δfinal=0.001

## Decision aid
- mean censored expected-direction rate: `0.369`
- mean final-metric expected-direction rate: `0.550`
- exact-vs-same-operation censored expected-direction rate: `0.250`
- exact/different-operation censored expected-direction rate: `0.513`

GREEN for exact-component dependency requires exact-component interventions to beat same-operation, different-operation, fake, and surface controls. If component and same-operation controls both help similarly, interpret the result as operation-family transfer rather than exact dependency.