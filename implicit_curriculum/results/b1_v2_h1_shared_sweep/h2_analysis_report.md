# B1 H2 predictor-ladder and atomic parallel-null analysis

This analysis reuses the B1 H1 shared-sweep outputs. It fits predictor ladders on atomic structures, then predicts composite acquisition under an atomic parallel-rate null.

Primary metric: `token_accuracy` threshold `0.7`.

## Acquisition table

- rows: `750`
- configs: `6`
- tasks: `25`
- atomic acquisition rate: `0.758`
- composite acquisition rate: `0.942`

## Selected predictor by config

- `base`: selected `learnability_only` (CV RMSE log-time=1.051; best=`learnability_only`)
- `batch_large`: selected `learnability_only` (CV RMSE log-time=0.839; best=`learnability_only`)
- `batch_small`: selected `learnability_only` (CV RMSE log-time=1.217; best=`learnability_only`)
- `lr_high`: selected `learnability_only` (CV RMSE log-time=1.240; best=`learnability_only`)
- `lr_low`: selected `learnability_only` (CV RMSE log-time=0.784; best=`learnability_only`)
- `wd_zero`: selected `learnability_only` (CV RMSE log-time=1.048; best=`learnability_only`)

## Composite residuals

- composite rows: `240`
- mean residual log-time: `-2.362`
- positive residual rate: `0.000`

Top delayed composites under the atomic parallel null:
- `batch_large` / `C06_reverse_then_substitute_05_07`: mean residual log-time=-1.250, positive-rate=0.000
- `batch_large` / `C03_reverse_then_substitute_07_02`: mean residual log-time=-1.250, positive-rate=0.000
- `base` / `C03_reverse_then_substitute_07_02`: mean residual log-time=-1.277, positive-rate=0.000
- `base` / `C06_reverse_then_substitute_05_07`: mean residual log-time=-1.277, positive-rate=0.000
- `wd_zero` / `C06_reverse_then_substitute_05_07`: mean residual log-time=-1.295, positive-rate=0.000

## Pair selection for future H3

- `batch_large`: `A07_reverse` → `C03_reverse_then_substitute_07_02` residual=-1.250, positive-rate=0.000
- `batch_large`: `A02_substitute` → `C03_reverse_then_substitute_07_02` residual=-1.250, positive-rate=0.000
- `batch_large`: `A05_substitute` → `C06_reverse_then_substitute_05_07` residual=-1.250, positive-rate=0.000
- `batch_large`: `A07_reverse` → `C06_reverse_then_substitute_05_07` residual=-1.250, positive-rate=0.000
- `base`: `A07_reverse` → `C03_reverse_then_substitute_07_02` residual=-1.277, positive-rate=0.000
- `base`: `A02_substitute` → `C03_reverse_then_substitute_07_02` residual=-1.277, positive-rate=0.000
- `base`: `A05_substitute` → `C06_reverse_then_substitute_05_07` residual=-1.277, positive-rate=0.000
- `base`: `A07_reverse` → `C06_reverse_then_substitute_05_07` residual=-1.277, positive-rate=0.000
- `wd_zero`: `A07_reverse` → `C03_reverse_then_substitute_07_02` residual=-1.295, positive-rate=0.000
- `wd_zero`: `A02_substitute` → `C03_reverse_then_substitute_07_02` residual=-1.295, positive-rate=0.000

## Permutation null

- `base` / `learnability_only`: true-beats-permutation rate=0.960
- `batch_large` / `learnability_only`: true-beats-permutation rate=0.950
- `batch_small` / `learnability_only`: true-beats-permutation rate=0.960
- `lr_high` / `learnability_only`: true-beats-permutation rate=0.880
- `lr_low` / `learnability_only`: true-beats-permutation rate=0.960
- `wd_zero` / `learnability_only`: true-beats-permutation rate=0.830

## Interpretation rule

A clean H2 result requires a simple predictor to beat richer alternatives under cross-validation and permutation, while composites either follow the atomic parallel prediction or show structured residuals. Residuals are observational only; they select pairs for later H3 interventions but do not establish dependency.
