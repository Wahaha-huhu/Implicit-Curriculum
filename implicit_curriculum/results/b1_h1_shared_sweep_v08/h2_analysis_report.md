# B1 H2 predictor-ladder and atomic parallel-null analysis

This analysis reuses the B1 H1 shared-sweep outputs. It fits predictor ladders on atomic structures, then predicts composite acquisition under an atomic parallel-rate null.

Primary metric: `token_accuracy` threshold `0.7`.

## Acquisition table

- rows: `1500`
- configs: `6`
- tasks: `25`
- atomic acquisition rate: `0.863`
- composite acquisition rate: `0.935`

## Selected predictor by config

- `base`: selected `frequency_only` (CV RMSE log-time=1.036; best=`frequency_only`)
- `batch_large`: selected `learnability_only` (CV RMSE log-time=0.881; best=`learnability_only`)
- `batch_small`: selected `frequency_only` (CV RMSE log-time=1.077; best=`frequency_only`)
- `lr_high`: selected `frequency_only` (CV RMSE log-time=1.016; best=`frequency_only`)
- `lr_low`: selected `learnability_only` (CV RMSE log-time=0.881; best=`learnability_only`)
- `wd_zero`: selected `frequency_only` (CV RMSE log-time=1.028; best=`frequency_only`)

## Composite residuals

- composite rows: `480`
- mean residual log-time: `-0.526`
- positive residual rate: `0.419`

Top delayed composites under the atomic parallel null:
- `batch_small` / `C06_reverse_then_substitute_02_00`: mean residual log-time=1.858, positive-rate=1.000
- `wd_zero` / `C06_reverse_then_substitute_02_00`: mean residual log-time=1.743, positive-rate=1.000
- `lr_high` / `C06_reverse_then_substitute_02_00`: mean residual log-time=1.737, positive-rate=1.000
- `base` / `C06_reverse_then_substitute_02_00`: mean residual log-time=1.727, positive-rate=1.000
- `base` / `C07_substitute_then_reverse_04_03`: mean residual log-time=0.952, positive-rate=1.000

## Pair selection for future H3

- `batch_small`: `A02_substitute` → `C06_reverse_then_substitute_02_00` residual=1.858, positive-rate=1.000
- `batch_small`: `A00_copy` → `C06_reverse_then_substitute_02_00` residual=1.858, positive-rate=1.000
- `wd_zero`: `A02_substitute` → `C06_reverse_then_substitute_02_00` residual=1.743, positive-rate=1.000
- `wd_zero`: `A00_copy` → `C06_reverse_then_substitute_02_00` residual=1.743, positive-rate=1.000
- `lr_high`: `A02_substitute` → `C06_reverse_then_substitute_02_00` residual=1.737, positive-rate=1.000
- `lr_high`: `A00_copy` → `C06_reverse_then_substitute_02_00` residual=1.737, positive-rate=1.000
- `base`: `A02_substitute` → `C06_reverse_then_substitute_02_00` residual=1.727, positive-rate=1.000
- `base`: `A00_copy` → `C06_reverse_then_substitute_02_00` residual=1.727, positive-rate=1.000
- `base`: `A04_reverse` → `C07_substitute_then_reverse_04_03` residual=0.952, positive-rate=1.000
- `base`: `A03_copy` → `C07_substitute_then_reverse_04_03` residual=0.952, positive-rate=1.000

## Permutation null

- `base` / `frequency_only`: true-beats-permutation rate=0.900
- `batch_large` / `learnability_only`: true-beats-permutation rate=0.950
- `batch_small` / `frequency_only`: true-beats-permutation rate=0.830
- `lr_high` / `frequency_only`: true-beats-permutation rate=0.890
- `lr_low` / `learnability_only`: true-beats-permutation rate=0.960
- `wd_zero` / `frequency_only`: true-beats-permutation rate=0.870

## Interpretation rule

A clean H2 result requires a simple predictor to beat richer alternatives under cross-validation and permutation, while composites either follow the atomic parallel prediction or show structured residuals. Residuals are observational only; they select pairs for later H3 interventions but do not establish dependency.
