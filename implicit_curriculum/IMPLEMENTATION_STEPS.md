# Step-by-step implementation plan

This repository should grow through gated milestones. Each milestone must produce runnable code, a small result artifact, and a decision about whether the next milestone is scientifically justified.

## Step 0 — Minimum decisive pilot infrastructure

Status: implemented.

Implemented components:

- controlled Boolean atomic/composite/control tasks;
- task-conditioned MLP;
- per-task held-out evaluation;
- acquisition-time extraction by sustained balanced-accuracy threshold;
- gradient diagnostics;
- representation CKA diagnostics;
- first-pass data interventions and matched unrelated controls.

Gate decision: passed as infrastructure, not yet as scientific evidence.

## Step 1 — Simulated recovery and decorrelated property design

Status: implemented in this version.

Purpose:

Before interpreting neural training, check whether the analysis pipeline can recover known synthetic worlds.

Implemented components:

- `ic_experiments.design`: decorrelated synthetic property table generator;
- VIF, Pearson, Spearman, standardized condition-number, and binned mutual-information diagnostics;
- `ic_experiments.recovery`: synthetic acquisition-time worlds;
- predictor ladder with cross-validated selection;
- atomic-fit/composite-residual dependency recovery check;
- CLI: `python -m ic_experiments.experiments.run_recovery_gate`.

Current smoke result:

- decorrelated design passed;
- frequency-only world usually selects frequency-only;
- learnability-only world selects learnability-only;
- three-factor world often selects three-factor, sometimes simpler `freq_learn` under parsimony;
- dependency-gated world shows strong positive composite residual.

Gate decision: passed as a recovery/infrastructure gate. The next step is to map the same property-design discipline into actual neural task families.

## Step 2 — VIF-targeted neural task generator

Next to implement.

Goal:

Construct actual trainable task families whose realized `frequency`, `reference_learnability`, and `formal_utility` pass the same diagnostics as the synthetic design.

Required outputs:

- generated task family metadata;
- frozen property table;
- diagnostics report;
- baseline trainability smoke run.

Gate to proceed:

- labels correct;
- frequencies match target mixture;
- property diagnostics pass or failed factors are declared non-identifiable;
- atomics and composites are learnable in isolation.

## Step 3 — H1 pilot: ordering and sign-stability

Goal:

Run the smallest real H1 experiment before the full grid.

Minimal version:

- 12–20 structures;
- one MLP and one tiny transformer;
- 5–10 seeds;
- two frequency regimes;
- two learning rates.

Gate to proceed:

- acquisition order is not random;
- structural predictors beat exposure-only baseline;
- effect signs are mostly stable.

## Step 4 — H2 within-configuration predictor ladder

Goal:

Fit the full predictor ladder on atomics and characterize whether frequency-only, learnability-only, multi-factor, or no scalar predictor is sufficient.

Required additions:

- cross-validated collapse metric;
- permutation null;
- coefficient intervals;
- threshold sensitivity analysis.

## Step 5 — H3 dependency-vs-parallelism pilot

Goal:

Test whether composite residuals move under component-specific interventions beyond controls.

Required additions:

- stronger surface/no-reuse controls;
- gradient-matched controls;
- model-state intervention, e.g. component pretraining or representation transplant;
- composite residual analysis fit on atomics only.

## Step 6 — Regime robustness

Goal:

Sweep one axis at a time toward LLM-like regimes.

Axes:

- multi-epoch to near-single-pass;
- clean to noisy labels;
- few structures to power-law tail;
- MLP to tiny transformer sequence tasks;
- weight decay/optimizer changes.

## Step 7 — Observational Pythia rung

Goal:

Run only after controlled signatures survive relevant regime shifts.

Allowed claim:

Observational consistency or inconsistency with the controlled account, not causality.
