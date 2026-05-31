# B1 H3 pair-specific intervention analysis

This is an H3 pilot analysis. It tests whether component interventions move the selected composite beyond matched control interventions. It is causal only within this controlled training setup and remains a pilot until replicated across more pairs/families.

Primary metric: `token_accuracy` threshold `0.7`.

## Pair
- component: `A05_substitute`
- composite: `C06_reverse_then_substitute_01_05`
- unrelated_control: `U01_unrelated_substitute`
- same_operation_control: `U01_unrelated_substitute`
- different_operation_control: `A03_copy`
- fake_component_control: `K02_shortcut_for_A00_copy`
- surface_control: `S01_surface_rotate`

## Composite acquisition by condition
- `baseline`: acq=0.000, mean censored time=250112.0, final=0.418
- `corrupt_component_strong`: acq=0.000, mean censored time=250112.0, final=0.410
- `corrupt_different_operation_matched_strong`: acq=0.000, mean censored time=250112.0, final=0.414
- `corrupt_same_operation_unrelated_strong`: acq=0.000, mean censored time=250112.0, final=0.400
- `delay_component_strong`: acq=0.000, mean censored time=250112.0, final=0.430
- `delay_different_operation_matched_strong`: acq=0.000, mean censored time=250112.0, final=0.441
- `delay_same_operation_unrelated_strong`: acq=0.000, mean censored time=250112.0, final=0.451
- `pretrain_component`: acq=0.000, mean censored time=250112.0, final=0.330
- `pretrain_different_operation_matched`: acq=0.000, mean censored time=250112.0, final=0.464
- `pretrain_same_operation_unrelated`: acq=0.000, mean censored time=250112.0, final=0.345

## Intervention contrasts
- `exact_pretrain_vs_same_operation`: `pretrain_component` vs `pretrain_same_operation_unrelated` (earlier): strict Δ=nan (n=0), censored Δ=0.000, censored-rate=0.000, Δfinal=-0.015
- `exact_pretrain_vs_different_operation`: `pretrain_component` vs `pretrain_different_operation_matched` (earlier): strict Δ=nan (n=0), censored Δ=0.000, censored-rate=0.000, Δfinal=-0.135
- `operation_family_pretrain_vs_different_operation`: `pretrain_same_operation_unrelated` vs `pretrain_different_operation_matched` (earlier): strict Δ=nan (n=0), censored Δ=0.000, censored-rate=0.000, Δfinal=-0.119
- `exact_strong_corrupt_vs_same_operation`: `corrupt_component_strong` vs `corrupt_same_operation_unrelated_strong` (later): strict Δ=nan (n=0), censored Δ=0.000, censored-rate=0.000, Δfinal=0.009
- `exact_strong_corrupt_vs_different_operation`: `corrupt_component_strong` vs `corrupt_different_operation_matched_strong` (later): strict Δ=nan (n=0), censored Δ=0.000, censored-rate=0.000, Δfinal=-0.004
- `exact_strong_delay_vs_same_operation`: `delay_component_strong` vs `delay_same_operation_unrelated_strong` (later): strict Δ=nan (n=0), censored Δ=0.000, censored-rate=0.000, Δfinal=-0.021
- `exact_strong_delay_vs_different_operation`: `delay_component_strong` vs `delay_different_operation_matched_strong` (later): strict Δ=nan (n=0), censored Δ=0.000, censored-rate=0.000, Δfinal=-0.011

## Decision aid
- mean censored expected-direction rate: `0.000`
- mean final-metric expected-direction rate: `0.429`
- exact-vs-same-operation censored expected-direction rate: `0.000`
- exact/different-operation censored expected-direction rate: `0.000`

GREEN for exact-component dependency requires exact-component interventions to beat same-operation, different-operation, fake, and surface controls. If component and same-operation controls both help similarly, interpret the result as operation-family transfer rather than exact dependency.