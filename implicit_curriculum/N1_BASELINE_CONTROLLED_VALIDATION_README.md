# N1 baseline-controlled coupling validation

This patch upgrades the N1 cross-task coupling pilot from a raw-correlation smoke test into the validation run needed before thesis-scale experiments.

The scientific gate is now:

1. the measured source-dose interaction `I(A -> B)` must have nontrivial variance;
2. raw early coupling predictors should show some signal;
3. frequency / learnability / surface baselines are reported explicitly;
4. gradient or first-order predictors must survive residualized or incremental checks before scaling claims.

The primary short-run outcome is `mean_slope_target_auc_token_accuracy`, because the first pilot showed threshold acquisition and exact match were too sparse for reliable use.

## What changed

- `make_b1_coupling_pilot_plan.py`
  - added `--balanced-sampling` and `--balance-bins` to spread pair selection across pair type, source/target frequency, and source/target learnability.
- `analyze_b1_coupling_pilot.py`
  - added baseline correlations for frequency, reference learnability, surface overlap, pair type, formal relation, and operation labels;
  - added residualized predictor tests: predictor vs interaction residual after numeric baselines;
  - added incremental model checks: baseline-only vs baseline+predictor full-sample and leave-one-out R²;
  - added warnings when acquisition is sparse or CKA is nearly degenerate.
- `coupling.py`
  - added balanced pair downsampling helpers.

## Recommended medium validation run on one RTX 4090

Run from `Implicit-Curriculum/implicit_curriculum`:

```bash
source .venv/bin/activate  # if using one
export PYTHONPATH="$(pwd)/src"
export CUDA_VISIBLE_DEVICES=0
mkdir -p results logs

python -m ic_experiments.experiments.make_b1_coupling_pilot_plan \
  --output-dir results/n1_b1_coupling_validation_plan \
  --family-seed 1 \
  --pair-seed 1 \
  --max-pairs 48 \
  --balanced-sampling \
  --balance-bins 3 \
  --seeds 0 1 2 3 4 \
  --dose-multipliers 0 0.5 1 2 \
  --write-run-script \
  --run-output-dir results/n1_b1_coupling_validation \
  --device cuda \
  --max-data-seen 180000 \
  --batch-size 256 \
  --n-checkpoints 80 \
  --eval-examples-per-task 384

python -m ic_experiments.experiments.run_b1_coupling_pilot \
  --structure-table results/n1_b1_coupling_validation_plan/structure_table.csv \
  --pair-plan results/n1_b1_coupling_validation_plan/b1_coupling_pair_plan.csv \
  --output-dir results/n1_b1_coupling_validation \
  --seeds 0 1 2 3 4 \
  --dose-multipliers 0 0.5 1 2 \
  --device cuda \
  --max-data-seen 180000 \
  --batch-size 256 \
  --n-checkpoints 80 \
  --eval-examples-per-task 384 \
  --early-probe-fraction 0.05 \
  --probe-examples 128 \
  --probe-microbatch 32 \
  --skip-existing 2>&1 | tee logs/n1_b1_coupling_validation.log

python -m ic_experiments.experiments.analyze_b1_coupling_pilot \
  --result-dir results/n1_b1_coupling_validation \
  --output-dir results/n1_b1_coupling_validation_analysis \
  --primary-outcome mean_slope_target_auc_token_accuracy
```

If this is too slow, use `--max-pairs 32` and keep 5 seeds. Prefer reducing pairs over reducing seeds, because the validation target is seed-level stability of interaction slopes.

## What to send back

```bash
mkdir -p handoff_n1_validation
cp -r results/n1_b1_coupling_validation_plan handoff_n1_validation/ 2>/dev/null || true
cp -r results/n1_b1_coupling_validation_analysis handoff_n1_validation/ 2>/dev/null || true
mkdir -p handoff_n1_validation/logs
cp logs/n1_b1_coupling_validation.log handoff_n1_validation/logs/ 2>/dev/null || true
mkdir -p handoff_n1_validation/n1_b1_coupling_validation_tables
find results/n1_b1_coupling_validation \
  \( -name "*.csv" -o -name "*.json" -o -name "*.md" -o -name "*.txt" \) \
  -not -path "*/checkpoints/*" \
  -not -path "*/models/*" \
  -not -path "*/state_dicts/*" \
  -print \
  | tar -czf handoff_n1_validation/n1_b1_coupling_validation_tables.tar.gz -T - 2>/dev/null || true
zip -r handoff_n1_validation.zip handoff_n1_validation
```

Upload `handoff_n1_validation.zip`.

## Decision rule

Proceed to a thesis-scale N1 run only if:

- interaction slopes still have nontrivial variance;
- raw gradient/first-order predictors are non-degenerate;
- frequency/learnability baselines do not fully absorb the signal;
- residualized gradient cosine or first-order transfer remains informative, or incremental baseline+predictor models improve over baseline-only out of sample.

If frequency/difficulty dominate and gradient coupling does not survive controls, that is still an informative result: the training-dynamics coupling hypothesis is weaker in this B1 regime than the first pilot suggested.
