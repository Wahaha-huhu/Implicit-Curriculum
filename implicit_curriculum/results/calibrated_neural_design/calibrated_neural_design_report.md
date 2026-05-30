# Calibrated neural design report

This gate runs brief baseline neural training on generated families and selects a family whose tasks are identifiable *and* measurably trainable.

## Criteria

- target_min_mean_acquisition_rate: `0.45`
- target_max_mean_acquisition_rate: `0.85`
- min_atomic_composite_acquisition_rate: `0.35`
- max_atomic_composite_acquisition_rate: `0.9`
- usable_composite_min_rate: `0.3`
- usable_composite_max_rate: `0.95`
- min_usable_composites_for_component: `3`
- min_component_acquisition_rate: `0.5`
- target_composite_rate: `0.65`

## Selected family

- passed: `False`
- reason: `insufficient_usable_composites_or_component_coverage`
- mean_acquisition_rate: `0.23529411764705882`
- atomic_composite_acquisition_rate: `0.2727272727272727`
- composite_acquisition_rate: `0.15`
- n_tasks: `34`
- chosen_component: `A07_bit_10`
- n_usable_composites: `1`
- component_acquisition_rate: `1.0`
- mean_downstream_composite_acquisition_rate: `0.5`
- candidate_seed: `2`
- component: `A07_bit_10`
- composites: `C05_and_07_05`
- unrelated_control: `U03_and_bits_37_42`
- fake_component_control: `K01_shortcut_for_02_bit46`
- surface_control: `S02_surface_xor_8_39`
- calibration_passed: `False`

## Candidate summary

|   candidate_seed | passed   |   mean_acquisition_rate |   atomic_composite_acquisition_rate |   composite_acquisition_rate | chosen_component   |   n_usable_composites |
|-----------------:|:---------|------------------------:|------------------------------------:|-----------------------------:|:-------------------|----------------------:|
|                0 | False    |                0.191176 |                            0.25     |                         0.15 | A00_not_bit_26     |                     1 |
|                1 | False    |                0.220588 |                            0.227273 |                         0.15 | A05_not_bit_2      |                     1 |
|                2 | False    |                0.235294 |                            0.272727 |                         0.15 | A07_bit_10         |                     1 |
|                3 | False    |                0.308824 |                            0.340909 |                         0.3  | A09_bit_4          |                     0 |
|                4 | False    |                0.205882 |                            0.227273 |                         0.1  | A11_not_bit_12     |                     0 |