# N1 Cross-Task Coupling Pilot

This layer implements the positive-mechanism pivot: instead of assuming ordered learning,
quanta, or composition, it directly measures whether changing task **A**'s training
presence changes task **B**'s learning, then tests whether early gradient/representation
coupling predicts that effect.

## Scientific target

For each ordered pair `A -> B`, the pilot estimates a directional interaction effect:

```text
I(A -> B) = slope of B's learning outcome as A's training mixture weight is varied
```

The source task `A` is assigned dose multipliers such as `0, 0.5, 1, 2`. The total
sampling budget remains fixed. When A is removed or reduced, probability mass is sent
to a matched filler; when A is increased, that filler is displaced first. This makes
the outcome closer to an A-specific transfer/interference measurement than a generic
budget effect.

The leading predictors are measured early:

- gradient cosine between A and B,
- gradient inner product,
- magnitude-weighted first-order transfer score,
- gradient SNR,
- linear CKA between A/B representations.

The primary pilot question is whether these predictors have non-degenerate variance and
track the measured dose-response interaction enough to justify a larger N1 run.

## Files added

```text
src/ic_experiments/coupling.py
src/ic_experiments/experiments/make_b1_coupling_pilot_plan.py
src/ic_experiments/experiments/run_b1_coupling_pilot.py
src/ic_experiments/experiments/analyze_b1_coupling_pilot.py
tests/n1_coupling_import_test.py
tests/n1_coupling_unit_test.py
```

## Minimal commands

Run from `Implicit-Curriculum/implicit_curriculum`:

```bash
export PYTHONPATH="$(pwd)/src"
export CUDA_VISIBLE_DEVICES=0
```

Generate a small heterogeneous pair plan from an existing B1 structure table:

```bash
python -m ic_experiments.experiments.make_b1_coupling_pilot_plan \
  --structure-table results/b1_v2_h1_shared_sweep/structure_table.csv \
  --output-dir results/n1_b1_coupling_pilot_plan \
  --max-pairs 12 \
  --seeds 0 1 2 \
  --dose-multipliers 0 0.5 1 2 \
  --write-run-script \
  --device cuda \
  --max-data-seen 120000 \
  --batch-size 256 \
  --n-checkpoints 60 \
  --eval-examples-per-task 256
```

If you do not trust the existing upstream artefacts, generate a fresh B1 family instead:

```bash
python -m ic_experiments.experiments.make_b1_coupling_pilot_plan \
  --output-dir results/n1_b1_coupling_pilot_plan \
  --family-seed 0 \
  --max-pairs 12 \
  --seeds 0 1 2 \
  --dose-multipliers 0 0.5 1 2 \
  --write-run-script \
  --device cuda
```

Run the pilot:

```bash
python -m ic_experiments.experiments.run_b1_coupling_pilot \
  --structure-table results/n1_b1_coupling_pilot_plan/structure_table.csv \
  --pair-plan results/n1_b1_coupling_pilot_plan/b1_coupling_pair_plan.csv \
  --output-dir results/n1_b1_coupling_pilot \
  --seeds 0 1 2 \
  --dose-multipliers 0 0.5 1 2 \
  --device cuda \
  --max-data-seen 120000 \
  --batch-size 256 \
  --n-checkpoints 60 \
  --eval-examples-per-task 256 \
  --early-probe-fraction 0.05 \
  --probe-examples 128 \
  --probe-microbatch 32 \
  --skip-existing 2>&1 | tee logs/n1_b1_coupling_pilot.log
```

Analyze:

```bash
python -m ic_experiments.experiments.analyze_b1_coupling_pilot \
  --result-dir results/n1_b1_coupling_pilot \
  --output-dir results/n1_b1_coupling_pilot_analysis
```

## Outputs to inspect

```text
results/n1_b1_coupling_pilot/target_outcomes.csv
results/n1_b1_coupling_pilot/early_coupling_predictors.csv
results/n1_b1_coupling_pilot_analysis/b1_coupling_seed_interaction_effects.csv
results/n1_b1_coupling_pilot_analysis/b1_coupling_pair_interaction_summary.csv
results/n1_b1_coupling_pilot_analysis/b1_coupling_predictor_vs_interaction.csv
results/n1_b1_coupling_pilot_analysis/b1_coupling_predictor_correlations.csv
results/n1_b1_coupling_pilot_analysis/b1_coupling_pilot_analysis_report.md
```

## Go/no-go criterion

Proceed to a larger N1 run only if:

1. target interaction slopes have nontrivial variance across pairs;
2. multiple pair types are represented;
3. the dose-response is not dominated by failed targets;
4. early predictors are non-degenerate;
5. gradient/first-order predictors show at least weak sign or rank signal beyond pure noise.

A failure here is useful: it means the task family or dose-response design needs repair
before a 4090-scale run.
