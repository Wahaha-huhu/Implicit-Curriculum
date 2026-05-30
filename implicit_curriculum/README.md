# Gradient-Mediated Implicit Curriculum Experiments

This repository is the first implementation pass for the v7 proposal: a controlled pilot for testing whether structural acquisition order is mediated by gradient alignment and reusable representations, and whether component learning causally shifts composite acquisition beyond matched controls.

## Current scope

The current code implements the **minimum decisive pilot**, not the full H1/H2/H3 grid:

- labeled atomic, composite, shortcut, unrelated, and surface-control Boolean structures;
- configurable mixed training distribution;
- small MLP classifier with task identity conditioning;
- per-structure held-out evaluation;
- sustained-threshold acquisition-time extraction;
- gradient diagnostics: gradient mass, gradient SNR, within-task gradient alignment, and component-composite gradient cosine;
- representation diagnostics: hidden-state linear CKA across tasks;
- data interventions: component upweighting, component delay, component label corruption;
- matched controls using an unrelated task with similar data-budget displacement;
- CSV/JSON result outputs for downstream analysis.

The goal of this pilot is to validate infrastructure and expose failure modes before scaling to the full decorrelated factorial design.

## Quick start

```bash
cd implicit_curriculum_impl
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src python -m ic_experiments.experiments.run_pilot --output-dir results/pilot_smoke --seeds 0 --max-data-seen 2048 --checkpoint-every 512 --batch-size 64 --hidden-dim 64
```

For a slightly more meaningful local run:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.run_pilot \
  --output-dir results/pilot_fuller \
  --seeds 0 1 2 \
  --max-data-seen 20000 \
  --checkpoint-every 1000 \
  --batch-size 128 \
  --hidden-dim 128 \
  --grad-stats-every 5000 \
  --conditions baseline upweight_A upweight_U_matched corrupt_A corrupt_U_matched delay_A delay_U_matched
```

## Output files

A pilot run writes:

- `eval_curves.csv`: per-condition, per-seed, per-task loss/accuracy over training;
- `acquisition_times.csv`: first sustained threshold crossing for each task;
- `grad_stats.csv`: per-task gradient norm/SNR/within-alignment and cross-task gradient cosine;
- `representation_cka.csv`: hidden-representation similarity between task-conditioned inputs;
- `structure_table.csv`: task metadata, including frequency, reference learnability, and formal utility;
- `summary.json`: compact metadata and paths.

## Scientific caution

This pilot is an infrastructure and diagnostic step. Its Boolean task family is intentionally controlled but not yet enough to support broad claims about LLM training. The next implementation steps are:

1. add VIF-targeted structure generation and simulated recovery tests;
2. add tiny transformer sequence tasks;
3. add gradient-matched controls more explicitly;
4. implement the H1/H2 full grid;
5. add model-state interventions for H3.

## Step 1 gate: simulated recovery + decorrelated property design

Before scaling neural training, run the simulated recovery gate:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.run_recovery_gate \
  --output-dir results/recovery_gate \
  --seed 0 \
  --n-atomic 12 \
  --n-composite 8 \
  --n-replicates 30
```

This writes:

- `design.csv`: a synthetic decorrelated property table;
- `summary.json`: VIF, Pearson/Spearman correlation, condition-number, and binned-MI diagnostics;
- `synthetic_worlds.csv`: acquisition times sampled from known synthetic mechanisms;
- `cv_folds.csv` and `cv_summary.csv`: cross-validated predictor-ladder scores;
- `dependency_residuals.csv`: composite residuals after fitting atomics;
- `verdict.csv`: compact recovery rates by true synthetic mechanism;
- `recovery_report.md`: human-readable report.

This gate should pass before H1/H2 scaling. If the analysis cannot recover frequency-only, three-factor, and dependency-gated synthetic worlds, the neural experiments should not be interpreted mechanistically.
