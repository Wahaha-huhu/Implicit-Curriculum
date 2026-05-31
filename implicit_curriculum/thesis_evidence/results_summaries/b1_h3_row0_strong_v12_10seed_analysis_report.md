# B1 H3 pair-specific intervention analysis

This is an H3 pilot analysis. It tests whether component interventions move the selected composite beyond matched control interventions. It is causal only within this controlled training setup and remains a pilot until replicated across more pairs/families.

Primary metric: `token_accuracy` threshold `0.7`.

## Pair
- component: `A02_substitute`
- composite: `C06_reverse_then_substitute_02_00`
- unrelated_control: `U01_unrelated_substitute`
- fake_component_control: `K01_shortcut_for_A07_reverse`
- surface_control: `S00_surface_rotate`

## Composite acquisition by condition
- `baseline`: acq=0.600, mean censored time=212044.8, final=0.723
- `corrupt_component`: acq=0.400, mean censored time=230246.4, final=0.708
- `corrupt_unrelated_matched`: acq=0.400, mean censored time=224460.8, final=0.706
- `delay_component`: acq=0.500, mean censored time=219315.2, final=0.714
- `delay_unrelated_matched`: acq=0.600, mean censored time=219622.4, final=0.720
- `upweight_component`: acq=0.900, mean censored time=180147.2, final=0.755
- `upweight_fake_component`: acq=0.500, mean censored time=220492.8, final=0.725
- `upweight_surface_control`: acq=0.700, mean censored time=211532.8, final=0.737
- `upweight_unrelated_matched`: acq=0.800, mean censored time=183014.4, final=0.757

## Intervention contrasts
- `upweight_component` vs `upweight_unrelated_matched` (earlier): strict Δ=7104.000 (n=8), censored Δ=-2867.200, censored-rate=0.100, Δfinal=-0.001
- `upweight_component` vs `upweight_fake_component` (earlier): strict Δ=-27596.800 (n=5), censored Δ=-40345.600, censored-rate=0.900, Δfinal=0.031
- `upweight_component` vs `upweight_surface_control` (earlier): strict Δ=-27977.143 (n=7), censored Δ=-31385.600, censored-rate=0.800, Δfinal=0.018
- `corrupt_component` vs `corrupt_unrelated_matched` (later): strict Δ=14464.000 (n=4), censored Δ=5785.600, censored-rate=0.300, Δfinal=0.003
- `delay_component` vs `delay_unrelated_matched` (later): strict Δ=-10035.200 (n=5), censored Δ=-307.200, censored-rate=0.100, Δfinal=-0.006

## Decision aid
- mean censored expected-direction rate: `0.440`
- mean final-metric expected-direction rate: `0.640`

GREEN requires most contrasts to move in the expected direction versus unrelated/fake/surface controls, with nontrivial paired coverage. YELLOW means intervention signal is mixed or coverage is weak; RED means matched controls move similarly or opposite.