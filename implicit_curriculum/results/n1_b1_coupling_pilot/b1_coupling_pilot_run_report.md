# B1 N1 cross-task coupling pilot run

This run estimates directional cross-task interaction I(A→B) by varying A's mixture weight and measuring B's learning, while logging leading-indicator gradient/representation couplings.

## Setup
- pairs: `12`
- dose multipliers: `0.0, 0.5, 1.0, 2.0`
- seeds: `0, 1, 2`
- max_data_seen: `120000`
- early_probe_fraction: `0.05`
- param_subset: `last_block_ln_head`
- outcome rows: `144`
- predictor rows: `288`

## Pair-type coverage
- `component_to_composite`: `3`
- `composite_to_component_reverse`: `2`
- `control_or_surface`: `2`
- `same_operation`: `2`
- `same_operation_reverse`: `2`
- `unrelated_matched`: `1`

## Next analysis
Run `python -m ic_experiments.experiments.analyze_b1_coupling_pilot --result-dir <this-dir> --output-dir <analysis-dir>` to estimate slopes, seed-level uncertainty, and predictor-vs-interaction correlations.