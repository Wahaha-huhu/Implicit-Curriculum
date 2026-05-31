# B1 H2 predictor-ladder and atomic parallel-null analysis

This analysis reuses the B1 H1 shared-sweep outputs. It fits predictor ladders on atomic structures, then predicts composite acquisition under an atomic parallel-rate null.

Primary metric: `token_accuracy` threshold `0.7`.

## Acquisition table

- rows: `1500`
- configs: `6`
- tasks: `25`
- atomic acquisition rate: `0.694`
- composite acquisition rate: `0.742`

## Selected predictor by config

- `base`: selected `learnability_only` (CV RMSE log-time=0.919; best=`learnability_only`)
- `batch_large`: selected `learnability_only` (CV RMSE log-time=0.725; best=`learnability_only`)
- `batch_small`: selected `learnability_only` (CV RMSE log-time=1.145; best=`learnability_only`)
- `lr_high`: selected `learnability_only` (CV RMSE log-time=1.137; best=`learnability_only`)
- `lr_low`: selected `learnability_only` (CV RMSE log-time=0.747; best=`learnability_only`)
- `wd_zero`: selected `learnability_only` (CV RMSE log-time=0.930; best=`learnability_only`)

## Composite residuals

- composite rows: `480`
- mean residual log-time: `2.904`
- positive residual rate: `1.000`

Top delayed composites under the atomic parallel null:
- `lr_high` / `C00_reverse_then_substitute_02_05`: mean residual log-time=5.001, positive-rate=1.000
- `lr_high` / `C06_reverse_then_substitute_01_05`: mean residual log-time=4.960, positive-rate=1.000
- `batch_small` / `C00_reverse_then_substitute_02_05`: mean residual log-time=4.921, positive-rate=1.000
- `base` / `C00_reverse_then_substitute_02_05`: mean residual log-time=4.913, positive-rate=1.000
- `base` / `C06_reverse_then_substitute_01_05`: mean residual log-time=4.913, positive-rate=1.000

## Pair selection for future H3

- `lr_high`: `A02_substitute` → `C00_reverse_then_substitute_02_05` residual=5.001, positive-rate=1.000
- `lr_high`: `A05_substitute` → `C00_reverse_then_substitute_02_05` residual=5.001, positive-rate=1.000
- `lr_high`: `A01_reverse` → `C06_reverse_then_substitute_01_05` residual=4.960, positive-rate=1.000
- `lr_high`: `A05_substitute` → `C06_reverse_then_substitute_01_05` residual=4.960, positive-rate=1.000
- `batch_small`: `A02_substitute` → `C00_reverse_then_substitute_02_05` residual=4.921, positive-rate=1.000
- `batch_small`: `A05_substitute` → `C00_reverse_then_substitute_02_05` residual=4.921, positive-rate=1.000
- `base`: `A02_substitute` → `C00_reverse_then_substitute_02_05` residual=4.913, positive-rate=1.000
- `base`: `A05_substitute` → `C00_reverse_then_substitute_02_05` residual=4.913, positive-rate=1.000
- `base`: `A01_reverse` → `C06_reverse_then_substitute_01_05` residual=4.913, positive-rate=1.000
- `base`: `A05_substitute` → `C06_reverse_then_substitute_01_05` residual=4.913, positive-rate=1.000

## Permutation null

- `base` / `learnability_only`: true-beats-permutation rate=0.980
- `batch_large` / `learnability_only`: true-beats-permutation rate=0.960
- `batch_small` / `learnability_only`: true-beats-permutation rate=0.970
- `lr_high` / `learnability_only`: true-beats-permutation rate=0.940
- `lr_low` / `learnability_only`: true-beats-permutation rate=1.000
- `wd_zero` / `learnability_only`: true-beats-permutation rate=0.990

## Interpretation rule

A clean H2 result requires a simple predictor to beat richer alternatives under cross-validation and permutation, while composites either follow the atomic parallel prediction or show structured residuals. Residuals are observational only; they select pairs for later H3 interventions but do not establish dependency.
