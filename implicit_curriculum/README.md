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

## Result archival convention

From v0.9 onward, potential thesis-source results should be archived rather than overwritten.

```bash
PYTHONPATH=src python -m ic_experiments.experiments.archive_result \
  --source-dir results/b1_h1_shared_sweep_v08 \
  --archive-root results/archive \
  --experiment B1_H1_shared_sweep \
  --code-version v0.8.1 \
  --run-id b1_h1_seed0-9_base-grid \
  --thesis-use candidate
```

Each archive writes `run_manifest.json`, `command.txt`, `git_commit.txt`, and updates `results/archive/results_registry.csv`.

## B1 H2 predictor ladder

After a B1 H1 shared sweep has run, reuse its outputs for H2:

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

This writes the predictor ladder, selected atomic parallel-null model, composite residuals, and pair-selection candidates for later H3 interventions.

### v1.0 H3 pair-specific interventions

After running H2 and obtaining `h2_pair_selection.csv`, run the first H3 pilot on the top selected pair:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.run_b1_h3_interventions \
  --output-dir results/b1_h3_c06_v10 \
  --structure-table results/b1_h1_shared_sweep_v08/structure_table.csv \
  --pair-selection results/b1_h1_shared_sweep_v08/h2_pair_selection.csv \
  --seeds 0 1 2 3 4 5 6 7 8 9 \
  --conditions baseline upweight_component upweight_unrelated_matched upweight_fake_component upweight_surface_control delay_component delay_unrelated_matched corrupt_component corrupt_unrelated_matched \
  --max-data-seen 250000 --batch-size 256 --n-checkpoints 100 \
  --eval-examples-per-task 512 --d-model 128 --n-layers 2 --n-heads 4 --d-mlp 512 \
  --vocab-content 32 --input-len 6 --device cuda

PYTHONPATH=src python -m ic_experiments.experiments.analyze_b1_h3_interventions \
  --result-dir results/b1_h3_c06_v10 --metric-family token_accuracy --threshold 0.7
```

## Thesis evidence archive

The repository includes `thesis_evidence/`, an append-only folder for cumulative experiment summaries, claim/evidence mapping, and figure/table planning. Use this folder for thesis-writing source material rather than overwriteable `results/` directories.

Key files:

- `thesis_evidence/EXPERIMENT_LOG.md`
- `thesis_evidence/CLAIMS_AND_EVIDENCE.md`
- `thesis_evidence/RESULTS_REGISTRY.csv`
- `thesis_evidence/FIGURES_TABLES_TODO.md`


### v1.1 H3 operation-family control layer

The first H3 C06 pilot was mixed: exact-component upweighting helped relative to fake/surface controls, but not relative to a same-operation unrelated control. v1.1 therefore adds an operation-family control plan and conditions that distinguish:

- exact component dependency;
- operation-family transfer;
- generic data-budget/distribution effects.

Use `make_b1_h3_operation_family_plan` to create a plan from `h2_pair_selection.csv`, then run `run_b1_h3_interventions --plan-file ... --plan-index N` for each planned component-composite row.


### v1.2 H3 multi-row summary and stronger intervention conditions

Combine previously analyzed H3 rows:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.analyze_b1_h3_multirow   --row-dirs results/b1_h3_opfamily_row0_v11 results/b1_h3_opfamily_row1_v11   --output-dir results/b1_h3_c06_multirow_v12   --code-version v1.2   --archive-root results/archive   --thesis-use candidate
```

Run a stronger row-0 intervention suite:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.run_b1_h3_interventions   --output-dir results/b1_h3_row0_strong_v12   --structure-table results/b1_h1_shared_sweep_v08/structure_table.csv   --plan-file results/b1_h3_operation_family_plan_v11/h3_operation_family_plan.csv   --plan-index 0   --seeds 0 1 2 3 4 5 6 7 8 9   --conditions baseline pretrain_component pretrain_same_operation_unrelated pretrain_different_operation_matched corrupt_component_strong corrupt_same_operation_unrelated_strong corrupt_different_operation_matched_strong delay_component_strong delay_same_operation_unrelated_strong delay_different_operation_matched_strong   --pretrain-data-seen 50000   --strong-corrupt-prob 0.50   --strong-delay-fraction 0.60   --max-data-seen 250000   --batch-size 256   --n-checkpoints 100   --eval-examples-per-task 512   --d-model 128   --n-layers 2   --n-heads 4   --d-mlp 512   --vocab-content 32   --input-len 6   --device cuda   --code-version v1.2   --archive-root results/archive   --thesis-use candidate
```

## v1.3 thesis claim audit

v1.3 adds a durable hypothesis audit under `thesis_evidence/`:

- `HYPOTHESIS_AUDIT.md`
- `THESIS_CLAIM_RULES.md`
- `tables/hypothesis_status.csv`

The main conclusion is that the original broad dependency hypothesis is too strong. Current evidence supports controlled ordering/predictability claims and one pair-specific H3 causal result (`A02_substitute -> C06`), but not a universal developmental-dependency mechanism or any causal claim about real LLM training.

### v1.4 evidence portfolio

From v1.4 onward, the repository includes a thesis-evidence portfolio generator. Use it after adding new result summaries to `thesis_evidence/results_summaries/`:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.analyze_thesis_portfolio \
  --evidence-dir thesis_evidence \
  --output-dir thesis_evidence/portfolio \
  --code-version v1.4
```

To create the next-experiment plan for broadening the evidence base:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.make_b1_comprehensive_experiment_plan \
  --output-dir results/comprehensive_experiment_plan_v14 \
  --base-structure-table results/b1_h1_shared_sweep_v08/structure_table.csv \
  --base-h2-dir results/b1_h1_shared_sweep_v08 \
  --code-version v1.4
```

The current thesis-safe conclusion is scoped: B1 H1/H2 are promising controlled-pilot results; H3 provides pair-specific evidence for `A02_substitute → C06`, but not a universal dependency mechanism.

## v1.5: targeted H3 follow-up planning

v1.5 extends the H3 operation-family planner so follow-up experiments can target secondary composites or exclude already-tested composites without editing CSVs by hand.

New planner options:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.make_b1_h3_operation_family_plan \
  --structure-table results/b1_h1_shared_sweep_v08/structure_table.csv \
  --pair-selection results/b1_h1_shared_sweep_v08/h2_pair_selection.csv \
  --output-dir results/b1_h3_secondary_plan_v15 \
  --exclude-composites C06_reverse_then_substitute_02_00 \
  --top-composites 1 \
  --components-per-composite 2 \
  --write-run-script \
  --condition-set strong \
  --run-output-prefix results/b1_h3_secondary_v15 \
  --code-version v1.5 \
  --thesis-use candidate
```

This writes:

```text
h3_operation_family_plan.csv
h3_operation_family_plan_report.md
recommended_h3_commands.sh
```

Run the generated script to execute and analyze the selected secondary H3 rows:

```bash
bash results/b1_h3_secondary_plan_v15/recommended_h3_commands.sh
```

Use this for the next comprehensive test: whether the pair-specific `A02_substitute -> C06` causal signal generalizes to another delayed composite, rather than only one C06 component.

### v1.6 H3 evidence synthesis

Use `analyze_b1_h3_evidence_matrix` to combine multiple H3 pair-specific intervention runs into thesis-ready evidence tables. This is now the preferred summary layer before updating claims.

Example:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.analyze_b1_h3_evidence_matrix \
  --row-dirs \
    results/b1_h3_row0_strong_v12 \
    results/b1_h3_opfamily_row1_v11 \
    results/b1_h3_secondary_v15_row0_A04_reverse_to_C07_substitute_then_reverse_04_03_strong \
    results/b1_h3_secondary_v15_row1_A03_copy_to_C07_substitute_then_reverse_04_03_strong \
  --output-dir results/b1_h3_evidence_matrix_v16 \
  --code-version v1.6 \
  --archive-root results/archive \
  --thesis-use candidate
```

## v1.7 thesis-design validity additions

The repository now includes durable thesis-design documents under `thesis_evidence/`:

- `TASK_DESIGN_JUSTIFICATION.md`: why B0/B1/B2/Pythia exist, what each control rules out, and what claims the task design can support.
- `PYTHIA_BRIDGE_EXPERIMENT_DESIGN.md`: observational bridge plan for Pythia-like checkpointed LLMs.
- `TOP_CONFERENCE_POSITIONING.md`: contribution framing, reviewer concerns, and claim boundaries.
- `tables/task_design_validity_matrix.csv`: task-design elements and validity threats.
- `tables/contribution_claim_map.csv`: contribution-to-evidence mapping.
- `tables/pythia_bridge_slice_design.csv`: first-pass Pythia slice families.

These files are append-only thesis evidence. They should be updated whenever new experiments change the claim boundary.


### v1.8 mediator diagnostics

Use `run_b1_mediator_diagnostics` to probe early gradient and representation coupling for selected H3 pairs, then `analyze_b1_mediator_diagnostics` to compare exact components against same-operation, different-operation, fake, and surface controls. These diagnostics support the gradient-mediated mechanism but do not by themselves establish causality.

## v1.9 final evidence consolidation

The `thesis_evidence/` folder now includes mediator diagnostics and a final claim/evidence matrix. To build an index of thesis evidence artifacts:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.make_final_thesis_evidence_package \
  --evidence-dir thesis_evidence \
  --output-dir thesis_evidence/final_evidence_package \
  --code-version v1.9
```

Key files:

- `thesis_evidence/FINAL_RESULTS_SYNTHESIS.md`
- `thesis_evidence/MEDIATOR_DIAGNOSTIC_SYNTHESIS.md`
- `thesis_evidence/tables/final_claim_evidence_matrix.csv`
- `thesis_evidence/tables/mediator_pair_evidence_matrix.csv`
- `thesis_evidence/tables/figure_source_map.csv`

### v2.0 second-family replication workflow

Generate a second-family replication plan:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.make_b1_replication_plan \
  --output-dir results/b1_replication_plan_v20 \
  --family-id family_replication_01 \
  --candidate-seeds 20 21 22 23 24 25 26 27 28 29 \
  --code-version v2.0
```

Then run the generated script section by section:

```bash
bash results/b1_replication_plan_v20/recommended_replication_commands.sh
```

After a replication family has H1/H2/H3 outputs, aggregate families with:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.analyze_b1_cross_family_synthesis \
  --family-registry thesis_evidence/tables/b1_family_registry.csv \
  --output-dir results/b1_cross_family_synthesis_v20 \
  --code-version v2.0
```

### v2.1 H3 readiness and threshold sensitivity

New diagnostic commands:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.analyze_b1_h3_threshold_sensitivity --help
PYTHONPATH=src python -m ic_experiments.experiments.select_b1_h3_ready_candidates --help
PYTHONPATH=src python -m ic_experiments.experiments.audit_b1_learnability_proxy --help
```

These commands diagnose whether an H3 candidate is truly negative, too hard at the default acquisition threshold, or a better candidate for final/AUC-based analysis.

### v2.2 readiness-aware H3 planning

v2.2 adds a readiness-aware H3 planner so the largest H2 residuals are not blindly used for intervention when they are too hard to acquire. The key command is:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.make_b1_h3_readiness_aware_plan --help
```

It consumes `h3_ready_pair_selection.csv` from `select_b1_h3_ready_candidates` and writes an H3 plan compatible with the existing `run_b1_h3_interventions` runner.

v2.2 also adds:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.summarize_b1_family_diagnostics --help
```

This writes a family-level synthesis stating whether a B1 family supports H1/H2 regime claims, H3 replication claims, or only diagnostic/boundary claims.

## v2.3 Cross-family controlled synthesis

v2.3 adds a thesis-oriented cross-family synthesis command:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.analyze_b1_cross_family_claims \
  --family1-h1-dir results/b1_h1_shared_sweep_v08 \
  --family1-h2-dir results/b1_h1_shared_sweep_v08 \
  --family1-h3-matrix results/b1_h3_evidence_matrix_v16/h3_pair_evidence_matrix.csv \
  --family1-mediator-dir results/b1_mediator_h3_pairs_v18 \
  --family2-h1-dir results/family_replication_01/b1_h1_shared_sweep \
  --family2-h2-dir results/family_replication_01/b1_h1_shared_sweep \
  --family2-readiness-dir results/family_replication_01/h3_readiness_v21 \
  --family2-h3-dirs \
    results/family_replication_01/b1_h3_row0_A02_substitute_to_C00_reverse_then_substitute_02_05_strong \
    results/family_replication_01/b1_h3_exclude_c00_row1_A05_substitute_to_C06_reverse_then_substitute_01_05_strong \
    results/family_replication_01/b1_h3_ready_v22_row0_A01_reverse_to_C06_reverse_then_substitute_01_05_strong \
  --family2-threshold-dirs \
    results/family_replication_01/b1_h3_exclude_c00_row1_A05_substitute_to_C06_reverse_then_substitute_01_05_strong \
    results/family_replication_01/b1_h3_ready_v22_row0_A01_reverse_to_C06_reverse_then_substitute_01_05_strong \
  --output-dir results/b1_cross_family_claim_synthesis_v23 \
  --code-version v2.3 \
  --archive-root results/archive \
  --thesis-use candidate
```

This writes `CROSS_FAMILY_CONTROLLED_SYNTHESIS.md`, `cross_family_stage_summary.csv`, `cross_family_h3_diagnostics.csv`, and `cross_family_claim_matrix.csv`.

The intended interpretation is conservative: family 1 supports a localized exact-component dependency site, while family 2 is a regime/stress test showing stable H1/H2 structure but no positive H3 replication under the tested settings.

## v2.4 Pythia-style observational bridge

v2.4 adds a lightweight observational pilot for checkpointed causal language models. This bridge is intentionally weaker than B1 H3: it can test H1/H2-like signatures across checkpoints, but it cannot establish causal dependency.

Create the slice suite:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.make_pythia_observational_slice_suite \
  --output-dir results/pythia_slice_suite_v24 \
  --n-per-slice 64 \
  --code-version v2.4
```

Evaluate a checkpointed model if `torch` and `transformers` are installed and model checkpoints are available:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.run_pythia_observational_pilot \
  --slice-table results/pythia_slice_suite_v24/pythia_slice_table.csv \
  --examples results/pythia_slice_suite_v24/pythia_slice_examples.jsonl \
  --output-dir results/pythia_observational_pilot_v24 \
  --model-name EleutherAI/pythia-70m \
  --revisions step0 step1000 step10000 step143000 \
  --device cuda
```

Analyze the observational signatures:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_observational_pilot \
  --result-dir results/pythia_observational_pilot_v24 \
  --metric accuracy \
  --threshold 0.5 \
  --code-version v2.4
```

Interpret these outputs as observational bridge evidence only. Do not use them as H3 causal evidence.


### v2.5 Pythia calibration

Pythia observational bridge calibration adds:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_threshold_sensitivity
PYTHONPATH=src python -m ic_experiments.experiments.make_pythia_easy_slice_suite
```

Use these when the initial Pythia pilot has no acquired slices at the default threshold. Threshold-sensitivity and easy-slice calibration are diagnostic only and do not support causal claims.

## v2.6 Pythia continuous-score calibration

Pythia observational bridge v2.6 adds continuous-score analysis so that subthreshold learning can be diagnosed without relying only on top-1 accuracy thresholds.

New command:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_continuous_scores \
  --result-dir results/pythia_easy_observational_pilot_v25 \
  --code-version v2.6 \
  --archive-root results/archive \
  --thesis-use diagnostic
```

Future `run_pythia_observational_pilot` outputs also include correct-option margin, correct-option rank, and reciprocal rank. Existing v2.4/v2.5 outputs can still be analyzed for available metrics such as accuracy and correct log probability.

Outputs:

```text
pythia_continuous_score_report.md
pythia_continuous_slice_summary.csv
pythia_continuous_h1_summary.csv
pythia_continuous_h2_residuals.csv
pythia_continuous_component_coupling.csv
```

These outputs are observational calibration only. They can identify slice/checkpoint regimes where Pythia shows subthreshold movement, but they do not establish causal dependency.

## v2.7 Pythia H2-ready observational suite

v2.7 adds a larger Pythia observational slice suite and H2-readiness diagnostics. This is an observational bridge only: it can test whether checkpointed LMs show H1/H2-like signatures, but it cannot support causal dependency claims.

Commands:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.make_pythia_h2_ready_slice_suite \
  --output-dir results/pythia_h2_ready_slice_suite_v27 \
  --n-per-slice 64 \
  --code-version v2.7

PYTHONPATH=src python -m ic_experiments.experiments.run_pythia_observational_pilot \
  --slice-table results/pythia_h2_ready_slice_suite_v27/pythia_slice_table.csv \
  --examples results/pythia_h2_ready_slice_suite_v27/pythia_slice_examples.jsonl \
  --output-dir results/pythia_h2_ready_observational_pilot_v27 \
  --model-name EleutherAI/pythia-70m \
  --revisions step0 step1000 step10000 step143000 \
  --max-examples-per-slice 64 \
  --device cuda \
  --code-version v2.7

PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_h2_readiness \
  --result-dir results/pythia_h2_ready_observational_pilot_v27 \
  --code-version v2.7

PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_continuous_scores \
  --result-dir results/pythia_h2_ready_observational_pilot_v27 \
  --code-version v2.7
```

## v2.8 first-stage experiment summary

v2.8 adds a durable first-stage summary package for thesis writing. It gathers the controlled B1/B2 evidence, cross-family synthesis, mediator diagnostics, and the first Pythia observational bridge into a claim-bounded summary.

Generate the package with:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.make_first_stage_experiment_summary \
  --evidence-dir thesis_evidence \
  --output-dir thesis_evidence/first_stage_summary \
  --code-version v2.8 \
  --archive-root results/archive \
  --thesis-use candidate
```

Expected outputs:

- `thesis_evidence/first_stage_summary/FIRST_STAGE_EXPERIMENT_SUMMARY.md`
- `thesis_evidence/first_stage_summary/METHODOLOGY_IMPLEMENTATION_DRAFT.md`
- `thesis_evidence/first_stage_summary/RESULTS_DISCUSSION_DRAFT.md`
- `thesis_evidence/first_stage_summary/first_stage_claim_table.csv`
- `thesis_evidence/first_stage_summary/first_stage_experiment_map.csv`
- `thesis_evidence/first_stage_summary/first_stage_figure_table_plan.csv`

This package should be treated as the first stable thesis-writing checkpoint. It supports controlled-methodology and localized-dependency claims, not universal causal claims about LLM pretraining.
