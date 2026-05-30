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

## v0.3 generated neural design gate

Generate a concrete trainable task family whose realized properties are decorrelated:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.run_neural_design_gate \
  --output-dir results/neural_design_gate \
  --seed 0 \
  --n-atomic 12 \
  --n-composite 8 \
  --n-shortcut-controls 4 \
  --n-surface-controls 4 \
  --n-unrelated-controls 4 \
  --n-bits 48 \
  --max-attempts 10000
```

Expected outputs:

- `structure_table.csv`
- `design_diagnostics.csv`
- `summary.json`
- `neural_design_report.md`

## v0.3 generated-family H1/intervention pilot

Run a baseline-only generated-family pilot:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.run_h1_ordering_pilot \
  --output-dir results/h1_generated_baseline \
  --structure-table results/neural_design_gate/structure_table.csv \
  --seeds 0 1 2 3 4 \
  --conditions baseline \
  --n-bits 48 \
  --max-data-seen 100000 \
  --checkpoint-every 2000 \
  --batch-size 512 \
  --hidden-dim 256 \
  --depth 2 \
  --grad-stats-every 20000 \
  --device cuda

PYTHONPATH=src python -m ic_experiments.experiments.analyze_h1_pilot \
  --result-dir results/h1_generated_baseline
```

Run the generated-family intervention pilot:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.run_h1_ordering_pilot \
  --output-dir results/h1_generated_interventions \
  --structure-table results/neural_design_gate/structure_table.csv \
  --seeds 0 1 2 3 4 \
  --conditions baseline upweight_component upweight_unrelated_matched upweight_fake_component upweight_surface_control corrupt_component corrupt_unrelated_matched delay_component delay_unrelated_matched \
  --n-bits 48 \
  --max-data-seen 100000 \
  --checkpoint-every 2000 \
  --batch-size 512 \
  --hidden-dim 256 \
  --depth 2 \
  --grad-stats-every 20000 \
  --device cuda

PYTHONPATH=src python -m ic_experiments.experiments.analyze_h1_pilot \
  --result-dir results/h1_generated_interventions
```

Key analysis outputs:

- `h1_analysis_report.md`
- `acquisition_summary_by_task.csv`
- `ordering_summary.csv`
- `intervention_pair_tests.csv`
- `component_control_diagnostics.csv`

## v0.4 calibrated neural design workflow

v0.4 adds a calibration gate. The old v0.3 `run_neural_design_gate` only checked whether structural properties were identifiable. The new `run_calibrated_neural_design` also runs short baseline neural training on multiple candidate families and selects one with usable acquisition coverage and multiple measurable composites for the focal component.

Run calibration:

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

Then use the selected family and chosen focal component/control set:

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

Analyze:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.analyze_h1_pilot \
  --result-dir results/h1_calibrated_interventions
```

New analysis columns in `intervention_pair_tests.csv` include strict threshold-crossing deltas and right-censored deltas for non-acquired paired seeds.

## v0.5 backend commands

### B2 sparse parity design

```bash
PYTHONPATH=src python -m ic_experiments.experiments.run_sparse_parity_design \
  --output-dir results/sparse_parity_design \
  --seed 0 \
  --n-bits 40 \
  --n-tasks 24 \
  --degrees 3 5 \
  --frequency-mode zipf
```

Train the sparse-parity baseline through the existing MLP runner:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.run_h1_ordering_pilot \
  --output-dir results/sparse_parity_pilot \
  --structure-table results/sparse_parity_design/structure_table.csv \
  --seeds 0 1 2 \
  --conditions baseline \
  --n-bits 40 \
  --max-data-seen 100000 \
  --checkpoint-every 2000 \
  --batch-size 512 \
  --hidden-dim 512 \
  --depth 2 \
  --grad-stats-every 20000 \
  --device cuda
```

### B1 sequence DSL design and smoke pilot

```bash
PYTHONPATH=src python -m ic_experiments.experiments.run_sequence_dsl_design \
  --output-dir results/sequence_dsl_design \
  --seed 0 \
  --vocab-content 64 \
  --input-len 8 \
  --n-atomic 8 \
  --n-composite 6
```

Small smoke pilot:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.run_sequence_dsl_pilot \
  --output-dir results/sequence_dsl_pilot_smoke \
  --structure-table results/sequence_dsl_design/structure_table.csv \
  --seeds 0 \
  --max-data-seen 20000 \
  --batch-size 128 \
  --n-checkpoints 30 \
  --eval-examples-per-task 256 \
  --d-model 128 \
  --n-layers 2 \
  --n-heads 4 \
  --d-mlp 512 \
  --device cuda
```

The sequence DSL path is currently a smoke/pilot substrate, not the full Exp 1 shared sweep.

## v0.6 backend-specific calibration

v0.6 separates backend analyses:

- **B2 sparse parity**: use `run_sparse_parity_pilot` and `analyze_sparse_parity_pilot`. This backend tests frequency/degree ordering only and intentionally has no component/control dependency logic.
- **B1 sequence DSL**: use `run_sequence_dsl_calibration` before larger transformer pilots. Analyze with `analyze_sequence_dsl_pilot`, which reports token-accuracy, exact-match, AUC, and threshold sensitivity.

Do not interpret B1 exact-match 0.90 as the only acquisition observable during calibration. Use token accuracy, exact match, loss/AUC, and right-censored acquisition together.
