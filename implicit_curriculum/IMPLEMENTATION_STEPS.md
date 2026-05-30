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

Status: implemented in v0.3.

Goal:

Construct actual trainable task families whose realized `frequency`, `reference_learnability`, and `formal_utility` pass the same diagnostics as the synthetic design.

Implemented components:

- `ic_experiments.neural_design`: generated Boolean task families with atomics, composites, shortcut/no-reuse controls, surface controls, and unrelated controls;
- VIF/correlation/condition-number diagnostics on realized neural task properties;
- component/control selection for intervention pilots;
- CLIs: `run_neural_design_gate`, `run_h1_ordering_pilot`, and `analyze_h1_pilot`;
- stronger diagnostics comparing component→composite gradient/CKA against fake, surface, and unrelated controls.

Gate to proceed:

- design diagnostics pass;
- generated-family baseline has nontrivial acquisition coverage;
- ordering summary has interpretable signs or final-metric fallback;
- intervention contrasts beat fake/surface/unrelated controls before scaling.

## Step 3 — H1 pilot: ordering and sign-stability

Status: partially implemented in v0.3 via the generated-family pilot runner. Full sign-stability across configurations is not implemented yet.

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

## v0.4 — calibrated neural family gate

v0.4 adds a calibration layer between design-identifiable generated families and GPU-heavy H1/H2/H3 runs.

New commands:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.run_calibrated_neural_design \
  --output-dir results/calibrated_neural_design \
  --candidate-seeds 0 1 2 3 4 \
  --calibration-seeds 0 1 \
  --n-atomic 12 \
  --n-composite 10 \
  --n-shortcut-controls 4 \
  --n-surface-controls 4 \
  --n-unrelated-controls 4 \
  --n-bits 48 \
  --max-data-seen 120000 \
  --checkpoint-every 2000 \
  --batch-size 512 \
  --hidden-dim 256 \
  --depth 2 \
  --device cuda
```

Key outputs:

- `results/calibrated_neural_design/calibrated_neural_design_report.md`
- `results/calibrated_neural_design/candidate_calibration_summary.csv`
- `results/calibrated_neural_design/structure_table.csv`
- `results/calibrated_neural_design/chosen_component_and_controls.json`
- `results/calibrated_neural_design/calibration_acquisition_summary.csv`

Use the calibrated family in the H1 pilot:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.run_h1_ordering_pilot \
  --output-dir results/h1_calibrated_interventions \
  --structure-table results/calibrated_neural_design/structure_table.csv \
  --chosen-component-file results/calibrated_neural_design/chosen_component_and_controls.json \
  --seeds 0 1 2 3 4 \
  --conditions baseline upweight_component upweight_unrelated_matched upweight_fake_component upweight_surface_control corrupt_component corrupt_unrelated_matched delay_component delay_unrelated_matched \
  --n-bits 48 \
  --max-data-seen 120000 \
  --checkpoint-every 2000 \
  --batch-size 512 \
  --hidden-dim 256 \
  --depth 2 \
  --grad-stats-every 20000 \
  --device cuda
```

Then analyze:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.analyze_h1_pilot \
  --result-dir results/h1_calibrated_interventions
```

v0.4 analysis reports both strict threshold-crossing contrasts and right-censored contrasts for non-acquired paired seeds.

## v0.5 — backend realignment toward the operational design

This version starts the refactor from a Boolean-only sandbox toward the stronger experiment spine.

### Backends

- **B0 Boolean sandbox**: existing `TaskSpec`/MLP path. Use this for fast debugging only.
- **B2 sparse parity**: quanta-comparable baseline. Generate with `run_sparse_parity_design`, then train with the existing `run_h1_ordering_pilot --model mlp` path.
- **B1 sequence DSL**: smoke-testable sequence/decoder-only-transformer substrate. Generate with `run_sequence_dsl_design`, train a small pilot with `run_sequence_dsl_pilot`.

### New outputs

- `generic_structure_table.csv`: backend-agnostic structure metadata.
- `backend_manifest.json` or `summary.json`: backend/config metadata.
- `checkpoint_fraction`: added to Boolean/MLP eval/gradient/CKA outputs where relevant, so later Exp 2 mediation can enforce the leading-indicator rule.

### What remains to implement before the full shared sweep

- Full B1 calibration with richer operations and mandatory control packets per composite.
- Shared-sweep directory layout for Exp 1/2/3.
- Leading-indicator mediation analysis tables.
- Model-state interventions for Exp 4.

## v0.6 — Backend-specific calibration and analysis

This version adds the first calibration layer for the stronger operational design.

### New B2 sparse-parity commands

Generate/train/analyze with B2-appropriate assumptions. B2 has no composites and no formal utility by default, so do not use component/control diagnostics for this backend.

```bash
PYTHONPATH=src python -m ic_experiments.experiments.run_sparse_parity_pilot \
  --output-dir results/sparse_parity_pilot_v06 \
  --seeds 0 1 2 3 4 \
  --n-bits 40 \
  --n-tasks 24 \
  --degrees 2 3 \
  --max-data-seen 500000 \
  --checkpoint-every 5000 \
  --batch-size 1024 \
  --hidden-dim 512 \
  --depth 3 \
  --device cuda

PYTHONPATH=src python -m ic_experiments.experiments.analyze_sparse_parity_pilot \
  --result-dir results/sparse_parity_pilot_v06
```

Key outputs:

- `sparse_parity_analysis_report.md`
- `sparse_parity_ordering_summary.csv`
- `sparse_parity_acquisition_times.csv`
- `sparse_parity_degree_summary.csv`
- `sparse_parity_auc.csv`

### New B1 sequence-DSL calibration commands

Calibrate several sequence-DSL families before running larger transformer pilots.

```bash
PYTHONPATH=src python -m ic_experiments.experiments.run_sequence_dsl_calibration \
  --output-dir results/sequence_dsl_calibration_v06 \
  --candidate-seeds 0 1 2 3 4 \
  --calibration-seeds 0 1 \
  --vocab-content 32 \
  --input-len 6 \
  --max-data-seen 120000 \
  --batch-size 256 \
  --learning-rate 5e-4 \
  --device cuda
```

Key outputs:

- `sequence_dsl_calibration_report.md`
- `candidate_calibration_summary.csv`
- `structure_table.csv` for the selected family
- `selected_eval_curves.csv`
- `selected_acquisition_times.csv`

Then run a larger pilot on the selected family:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.run_sequence_dsl_pilot \
  --output-dir results/sequence_dsl_pilot_v06 \
  --structure-table results/sequence_dsl_calibration_v06/structure_table.csv \
  --seeds 0 1 2 3 4 \
  --max-data-seen 200000 \
  --batch-size 256 \
  --n-checkpoints 80 \
  --eval-examples-per-task 512 \
  --d-model 128 \
  --n-layers 2 \
  --n-heads 4 \
  --d-mlp 512 \
  --vocab-content 32 \
  --input-len 6 \
  --device cuda

PYTHONPATH=src python -m ic_experiments.experiments.analyze_sequence_dsl_pilot \
  --result-dir results/sequence_dsl_pilot_v06
```

Key outputs:

- `sequence_dsl_analysis_report.md`
- `sequence_ordering_summary.csv`
- `sequence_acquisition_times_multi_metric.csv`
- `sequence_final_by_kind.csv`
- `sequence_auc.csv`

### Implementation note

True sequence composites are now actual compositions of their listed component operations. Shortcut controls still list a component but bypass it by returning an identity target, preserving the formal-dependency/no-reuse negative control.

## v0.9 — Run archival + H2 predictor ladder

This version adds two thesis-readiness pieces:

1. **Run management / archival**
   - `ic_experiments.run_management`
   - `python -m ic_experiments.experiments.archive_result`
   - Writes `run_manifest.json`, `command.txt`, and `git_commit.txt`.
   - Supports archiving result directories into `results/archive/<version>/<experiment>/<run_id>/`.

2. **B1 H2 predictor ladder + atomic parallel-null residual analysis**
   - `python -m ic_experiments.experiments.analyze_b1_h2_predictor_ladder`
   - Reuses B1 H1 shared-sweep outputs.
   - Fits predictor ladders on atomic structures only.
   - Selects a simplest sufficient predictor by leave-one-structure-out CV and a one-standard-error rule.
   - Predicts composite acquisition under the atomic parallel-rate null.
   - Writes residuals and pair-selection tables for future H3 intervention candidates.

Main outputs:

```text
h2_analysis_report.md
h2_acquisition_table.csv
h2_predictor_ladder_cv.csv
h2_selected_models.csv
h2_model_coefficients.csv
h2_atomic_parallel_predictions.csv
h2_composite_residuals.csv
h2_composite_residual_summary_by_task.csv
h2_pair_selection.csv
h2_permutation_null.csv
run_manifest.json
```

Recommended next command:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.analyze_b1_h2_predictor_ladder \
  --result-dir results/b1_h1_shared_sweep_v08 \
  --metric-family token_accuracy \
  --threshold 0.7 \
  --n-permutations 100 \
  --code-version v0.9 \
  --archive-root results/archive \
  --thesis-use candidate
```

Archive an existing thesis-candidate run:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.archive_result \
  --source-dir results/b1_h1_shared_sweep_v08 \
  --archive-root results/archive \
  --experiment B1_H1_shared_sweep \
  --code-version v0.8.1 \
  --run-id b1_h1_seed0-9_base-grid \
  --thesis-use candidate
```

## v1.0 — B1 H3 pair-specific intervention runner

Adds the first H3 causal-intervention layer for H2-selected component-composite pairs.

New commands:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.run_b1_h3_interventions \
  --output-dir results/b1_h3_c06_v10 \
  --structure-table results/b1_h1_shared_sweep_v08/structure_table.csv \
  --pair-selection results/b1_h1_shared_sweep_v08/h2_pair_selection.csv \
  --seeds 0 1 2 3 4 5 6 7 8 9 \
  --conditions baseline upweight_component upweight_unrelated_matched upweight_fake_component upweight_surface_control delay_component delay_unrelated_matched corrupt_component corrupt_unrelated_matched \
  --max-data-seen 250000 \
  --batch-size 256 \
  --n-checkpoints 100 \
  --eval-examples-per-task 512 \
  --d-model 128 --n-layers 2 --n-heads 4 --d-mlp 512 \
  --vocab-content 32 --input-len 6 \
  --device cuda \
  --code-version v1.0 \
  --archive-root results/archive \
  --thesis-use candidate

PYTHONPATH=src python -m ic_experiments.experiments.analyze_b1_h3_interventions \
  --result-dir results/b1_h3_c06_v10 \
  --metric-family token_accuracy \
  --threshold 0.7 \
  --code-version v1.0 \
  --archive-root results/archive \
  --thesis-use candidate
```

Primary outputs:

- `h3_analysis_report.md`
- `h3_intervention_contrasts.csv`
- `h3_pair_summary.csv`
- `h3_acquisition_times.csv`
- `h3_final_metrics.csv`
- `h3_pair_config.csv`
- `run_manifest.json`

Decision rule: GREEN requires component upweighting to move the selected composite earlier than unrelated/fake/surface upweighting, and component delay/corruption to move it later or reduce final metric more than matched unrelated interventions. Residual evidence remains observational; this is the first controlled causal test.
