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

## Durable thesis evidence record

From v1.0.1 onward, every serious result that may support a thesis claim should be summarized under `thesis_evidence/`. Active `results/` directories may be overwritten, but `thesis_evidence/` should be append-only except for documented corrections.

After each major run:

1. Copy compact reports/CSVs into `thesis_evidence/results_summaries/`.
2. Add a row to `thesis_evidence/RESULTS_REGISTRY.csv`.
3. Update `thesis_evidence/EXPERIMENT_LOG.md` with the verdict and caveats.
4. Update `thesis_evidence/CLAIMS_AND_EVIDENCE.md` only if the result changes what can be safely claimed.
5. Add or update figure/table plans in `thesis_evidence/FIGURES_TABLES_TODO.md`.


## v1.1 — H3 operation-family controls

Adds a sharper H3 intervention design after the first C06 test showed mixed results: the exact component improved the composite relative to fake/surface controls, but not relative to a same-operation unrelated control. The new goal is to distinguish exact-component dependency from operation-family transfer.

New commands:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.make_b1_h3_operation_family_plan \
  --structure-table results/b1_h1_shared_sweep_v08/structure_table.csv \
  --pair-selection results/b1_h1_shared_sweep_v08/h2_pair_selection.csv \
  --output-dir results/b1_h3_operation_family_plan_v11 \
  --top-composites 1 \
  --components-per-composite 2
```

Then run `run_b1_h3_interventions` with `--plan-file` and `--plan-index`. The runner now supports same-operation and different-operation controls and intervention conditions such as `upweight_same_operation_unrelated`, `upweight_different_operation_matched`, `delay_same_operation_unrelated`, and `corrupt_same_operation_unrelated`.


## v1.2 — H3 consolidation and stronger component-specific tests

Status: implemented.

Adds:
- `analyze_b1_h3_multirow` to combine multiple H3 row analyses into a thesis-ready component-level summary.
- Optional stronger H3 intervention conditions:
  - `pretrain_component`, `pretrain_same_operation_unrelated`, `pretrain_different_operation_matched`
  - `delay_component_strong`, `delay_same_operation_unrelated_strong`, `delay_different_operation_matched_strong`
  - `corrupt_component_strong`, `corrupt_same_operation_unrelated_strong`, `corrupt_different_operation_matched_strong`
- Updated thesis evidence notes to record the row-0/row-1 mixed H3 interpretation.

Scientific status:
- Row 0 (`A02_substitute → C06`) gives a promising exact-component upweight signal.
- Row 1 (`A00_copy → C06`) is weak/mixed.
- Current H3 evidence is component-specific and not yet sufficient for a broad developmental-dependency claim.

Next recommended run:
- Combine row 0 and row 1 with `analyze_b1_h3_multirow`.
- Run stronger/model-state intervention test on row 0 using pretraining and strong corruption/delay variants.

## v1.3 — Hypothesis audit and claim boundary

This version adds a thesis-evidence audit before further experiments. The audit concludes:

- H1 ordering is supported in B1 mainly through reference learnability; frequency is weaker and stratum-dependent.
- H2 simple predictor/residual analysis is supported as a controlled pilot.
- H3 exact dependency is supported only for one pair-specific case so far: `A02_substitute -> C06_reverse_then_substitute_02_00`.
- The original broad claim that composites generally depend on all formal components is too strong.
- No causal claim about real LLM training is supported yet.

Future work should replicate the pair-specific H3 result across another family/composite and add mediator/probe evidence before making stronger dependency claims.

## v1.4 — Evidence consolidation and comprehensive experiment plan

Purpose: consolidate the current evidence into a thesis-safe portfolio and plan the next experiments needed for a comprehensive picture.

Added commands:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.analyze_thesis_portfolio \
  --evidence-dir thesis_evidence \
  --output-dir thesis_evidence/portfolio \
  --code-version v1.4
```

```bash
PYTHONPATH=src python -m ic_experiments.experiments.make_b1_comprehensive_experiment_plan \
  --output-dir results/comprehensive_experiment_plan_v14 \
  --base-structure-table results/b1_h1_shared_sweep_v08/structure_table.csv \
  --base-h2-dir results/b1_h1_shared_sweep_v08 \
  --code-version v1.4
```

Main outputs:

- `thesis_evidence/portfolio/portfolio_summary.md`
- `thesis_evidence/portfolio/claim_status_dashboard.csv`
- `results/comprehensive_experiment_plan_v14/comprehensive_experiment_plan.md`
- `results/comprehensive_experiment_plan_v14/comprehensive_experiment_plan.csv`
- `results/comprehensive_experiment_plan_v14/recommended_commands.sh`

Current claim boundary: H1/H2 are strong controlled-pilot results; H3 is pair-specific positive for `A02_substitute → C06`, mixed for `A00_copy → C06`, and should be replicated before broad dependency claims.

## v1.5 — Targeted H3 follow-up planning

Status: implemented.

Purpose: after the strong 10-seed row-0 result, the next evidence need is replication/generalization. v1.5 extends the H3 operation-family planner so we can target secondary composites, exclude already-tested composites, and generate ready-to-run strong-intervention commands.

New planner features:

- `--include-composites`: explicitly target one or more composites.
- `--exclude-composites`: exclude already-tested composites such as `C06_reverse_then_substitute_02_00`.
- `--min-positive-rate` and `--min-residual`: filter H2-selected pairs.
- `--write-run-script`: emit `recommended_h3_commands.sh`.
- `--condition-set {standard,strong}`: choose standard upweight/delay/corrupt or strong pretrain/corrupt/delay interventions.

Recommended next command:

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

Then run:

```bash
bash results/b1_h3_secondary_plan_v15/recommended_h3_commands.sh
```

Decision rule:

- If a secondary composite shows exact-component effects under pretraining and strong corruption, the H3 result becomes a replicated controlled phenomenon.
- If only C06/A02 works, the thesis claim remains localized/pair-specific.
- If the secondary composite is negative, use it as evidence that H2 residuals are candidate selectors, not sufficient evidence of dependency.

## v1.6 — Comprehensive H3 evidence synthesis

Added a synthesis layer for all current B1 H3 pair-specific intervention results.

New command:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.analyze_b1_h3_evidence_matrix \
  --row-dirs <h3_result_dir_1> <h3_result_dir_2> ... \
  --output-dir results/b1_h3_evidence_matrix_v16 \
  --code-version v1.6 \
  --archive-root results/archive \
  --thesis-use candidate
```

Expected outputs:

- `H3_SYNTHESIS.md`
- `h3_pair_evidence_matrix.csv`
- `h3_all_intervention_contrasts.csv`
- `h3_composite_level_summary.csv`
- `h3_claim_boundary_table.csv`
- `run_manifest.json`

The durable thesis archive now includes:

- `thesis_evidence/H3_SYNTHESIS.md`
- `thesis_evidence/tables/h3_pair_evidence_matrix.csv`
- `thesis_evidence/tables/h3_claim_boundary_table.csv`

Current interpretation: H3 evidence supports heterogeneous causal structure. `A02_substitute → C06` is positive pair-specific evidence; `A00_copy → C06` is weak/mixed; C07 pairs support operation-family/negative boundary evidence rather than exact-component dependency.

## v1.7 — Task-design validity and Pythia bridge planning

Added durable thesis-design documents that justify the controlled task design and clarify how the work can become a credible contribution:

1. `thesis_evidence/TASK_DESIGN_JUSTIFICATION.md` — validity argument for B0/B1/B2/Pythia and control classes.
2. `thesis_evidence/PYTHIA_BRIDGE_EXPERIMENT_DESIGN.md` — observational bridge from controlled signatures to Pythia-like checkpointed LLMs.
3. `thesis_evidence/TOP_CONFERENCE_POSITIONING.md` — contribution framing and reviewer-risk matrix.
4. `thesis_evidence/tables/task_design_validity_matrix.csv` — what each task/control rules out.
5. `thesis_evidence/tables/contribution_claim_map.csv` — evidence-to-claim map.
6. `thesis_evidence/tables/pythia_bridge_slice_design.csv` — candidate Pythia slice families.

Next recommended experiments remain: mediator diagnostics for positive vs negative B1 pairs; second-family B1 replication; B2 coverage strengthening; small Pythia observational pilot.


## v1.8 — Mediator diagnostics

Adds `run_b1_mediator_diagnostics` and `analyze_b1_mediator_diagnostics`.

Purpose: test whether H3-positive pairs show stronger early gradient/representation coupling than weak/negative or operation-family pairs.

Outputs:

- `mediator_task_stats.csv`
- `mediator_pair_stats.csv`
- `mediator_pair_role_summary.csv`
- `mediator_contrast_summary.csv`
- `mediator_analysis_report.md`

Interpretation: mechanistic corroboration only; causal claims still require H3 interventions.

## v1.9 — Final evidence consolidation after mediator diagnostics

Purpose: consolidate H1/H2/H3/mediator results into durable thesis artifacts.

New command:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.make_final_thesis_evidence_package \
  --evidence-dir thesis_evidence \
  --output-dir thesis_evidence/final_evidence_package \
  --code-version v1.9
```

New or updated evidence artifacts:

- `thesis_evidence/FINAL_RESULTS_SYNTHESIS.md`
- `thesis_evidence/MEDIATOR_DIAGNOSTIC_SYNTHESIS.md`
- `thesis_evidence/tables/final_claim_evidence_matrix.csv`
- `thesis_evidence/tables/mediator_pair_evidence_matrix.csv`
- `thesis_evidence/tables/figure_source_map.csv`

Current claim boundary: localized exact-component dependency is supported for one controlled pair and gradient-corroborated; universal dependency and causal LLM generalization are not supported.

## v2.0 — Second B1-family replication workflow

Added:

- `make_b1_replication_plan`: generates a full calibration → H1 → H2 → H3 command script for an independently generated B1 family.
- `analyze_b1_cross_family_synthesis`: aggregates H1/H2/H3 evidence across generated B1 families using a registry CSV.
- `thesis_evidence/SECOND_FAMILY_REPLICATION_PLAN.md`
- `thesis_evidence/CROSS_FAMILY_SYNTHESIS_PLAN.md`
- `thesis_evidence/tables/b1_family_registry_template.csv`

Scientific purpose: test whether the localized dependency result found in the first B1 family recurs in a second generated family. This is the next key credibility step before claiming a robust controlled phenomenon.

## v2.1 — H3 threshold/readiness and learnability-proxy audit

Family 2 exposed a methodological failure mode: the largest H2 residuals can select composites that are too hard for H3 intervention analysis at the default token-accuracy threshold. v2.1 adds:

- `analyze_b1_h3_threshold_sensitivity`: reanalyzes H3 runs across multiple thresholds and reports AUC/final metrics.
- `select_b1_h3_ready_candidates`: ranks H2 residual candidates by residual size plus measurable H1 readiness.
- `audit_b1_learnability_proxy`: checks whether `reference_learnability` behaves like difficulty or is confounded/reversed in a given B1 family.

Use these before spending more GPU time on family-2 H3 interventions.

## v2.2 — Readiness-aware H3 planning and family diagnostic synthesis

v2.2 adds two utilities after the family-2 H3 failure mode exposed by v2.1:

1. `make_b1_h3_readiness_aware_plan`
   - consumes `h3_ready_pair_selection.csv` from the readiness selector;
   - filters to H3-ready pairs by default;
   - writes a normal `h3_operation_family_plan.csv` so existing H3 runners can be used;
   - optionally writes `recommended_h3_commands.sh`.

2. `summarize_b1_family_diagnostics`
   - combines H1, H2, readiness, threshold-sensitivity, and learnability-audit outputs;
   - writes a family-level claim-boundary report;
   - helps decide whether a family supports H3 replication or only H1/H2 regime contrast.

Recommended family-2 flow:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.select_b1_h3_ready_candidates \
  --h1-result-dir results/family_replication_01/b1_h1_shared_sweep \
  --pair-selection results/family_replication_01/b1_h1_shared_sweep/h2_pair_selection.csv \
  --output-dir results/family_replication_01/h3_readiness_v21 \
  --metric-family token_accuracy \
  --thresholds 0.3 0.4 0.5 0.6 0.7 \
  --target-threshold 0.5 \
  --min-final 0.15 \
  --max-final 0.90 \
  --min-acq-rate 0.05 \
  --min-residual 0.0 \
  --code-version v2.2 \
  --archive-root results/archive \
  --thesis-use diagnostic
```

If this finds ready candidates:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.make_b1_h3_readiness_aware_plan \
  --structure-table results/family_replication_01/b1_h1_shared_sweep/structure_table.csv \
  --ready-pair-selection results/family_replication_01/h3_readiness_v21/h3_ready_pair_selection.csv \
  --output-dir results/family_replication_01/b1_h3_readiness_aware_plan_v22 \
  --ready-only \
  --allow-not-ready \
  --top-composites 1 \
  --components-per-composite 2 \
  --write-run-script \
  --condition-set strong \
  --run-output-prefix results/family_replication_01/b1_h3_ready_v22 \
  --code-version v2.2 \
  --archive-root results/archive \
  --thesis-use candidate
```

Then inspect the plan before running `recommended_h3_commands.sh`.

To summarize a family after diagnostics:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.summarize_b1_family_diagnostics \
  --family-id family_replication_01 \
  --h1-dir results/family_replication_01/b1_h1_shared_sweep \
  --h2-dir results/family_replication_01/b1_h1_shared_sweep \
  --readiness-dir results/family_replication_01/h3_readiness_v21 \
  --threshold-sensitivity-dir results/family_replication_01/b1_h3_exclude_c00_row1_A05_substitute_to_C06_reverse_then_substitute_01_05_strong \
  --output-dir results/family_replication_01/family_diagnostic_synthesis_v22 \
  --code-version v2.2 \
  --archive-root results/archive \
  --thesis-use diagnostic
```

## v2.3 — Cross-family controlled synthesis

Purpose: consolidate family 1 and family 2 evidence so thesis claims distinguish replicated patterns from one-family/localized results.

Run after family 2 readiness/H3 diagnostics:

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

Send back:

```text
results/b1_cross_family_claim_synthesis_v23/CROSS_FAMILY_CONTROLLED_SYNTHESIS.md
results/b1_cross_family_claim_synthesis_v23/cross_family_stage_summary.csv
results/b1_cross_family_claim_synthesis_v23/cross_family_h3_diagnostics.csv
results/b1_cross_family_claim_synthesis_v23/cross_family_claim_matrix.csv
```

Decision rule:

- If exact positive H3 appears in two families, strengthen the controlled dependency claim.
- If only family 1 remains positive, keep exact dependency localized and pair-specific.
- If family 2 shows hard/subthreshold candidates, treat it as evidence for H3-readiness selection, not a failed universal theory.

## v2.4 — Pythia-style observational pilot

Purpose: start the bridge from controlled B1 to checkpointed LMs while preserving the claim boundary. The new Pythia scripts evaluate behavioral slices across checkpoints and run H1/H2-style observational analyses. They do not establish causal dependency.

Commands:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.make_pythia_observational_slice_suite \
  --output-dir results/pythia_slice_suite_v24 \
  --n-per-slice 64 \
  --code-version v2.4
```

```bash
PYTHONPATH=src python -m ic_experiments.experiments.run_pythia_observational_pilot \
  --slice-table results/pythia_slice_suite_v24/pythia_slice_table.csv \
  --examples results/pythia_slice_suite_v24/pythia_slice_examples.jsonl \
  --output-dir results/pythia_observational_pilot_v24 \
  --model-name EleutherAI/pythia-70m \
  --revisions step0 step1000 step10000 step143000 \
  --device cuda
```

```bash
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_observational_pilot \
  --result-dir results/pythia_observational_pilot_v24 \
  --metric accuracy \
  --threshold 0.5 \
  --code-version v2.4
```

Files to inspect:

- `pythia_slice_suite_report.md`
- `pythia_observational_pilot_report.md`
- `pythia_observational_analysis_report.md`
- `pythia_h1_ordering_summary.csv`
- `pythia_h2_composite_residuals.csv`

Decision rule: if the slice suite is too noisy or models remain near random, redesign slices before scaling. If slices produce interpretable checkpoint curves, expand the suite and compare signatures against the B1 cross-family synthesis.


## v2.5 — Pythia observational calibration

If the Pythia observational pilot has zero acquisition at threshold 0.5, run:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_threshold_sensitivity \
  --result-dir results/pythia_observational_pilot_v24 \
  --metric accuracy \
  --thresholds 0.2 0.3 0.4 0.5 \
  --code-version v2.5
```

Generate an easier calibration suite with:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.make_pythia_easy_slice_suite \
  --output-dir results/pythia_easy_slice_suite_v25 \
  --n-per-slice 64 \
  --code-version v2.5
```

Then evaluate it with `run_pythia_observational_pilot` and analyze with the threshold-sensitivity command.

## v2.6 — Pythia continuous-score bridge

The v2.6 milestone addresses the fact that Pythia-70M pilots may not cross top-1 accuracy thresholds even when the correct option becomes more competitive.

Run on an existing Pythia result directory:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_continuous_scores \
  --result-dir results/pythia_easy_observational_pilot_v25 \
  --code-version v2.6 \
  --archive-root results/archive \
  --thesis-use diagnostic
```

Send back:

```text
pythia_continuous_score_report.md
pythia_continuous_slice_summary.csv
pythia_continuous_h1_summary.csv
pythia_continuous_h2_residuals.csv
pythia_continuous_component_coupling.csv
```

For future Pythia runs, rerun `run_pythia_observational_pilot` with v2.6 to record correct-option margin, rank, and reciprocal rank. Existing outputs remain compatible but will only expose metrics already present.

## v2.7 — Pythia H2-ready observational suite

Added:

- `make_pythia_h2_ready_slice_suite`
- `analyze_pythia_h2_readiness`
- expanded Pythia slice metadata with `answer_entropy_proxy`
- `thesis_evidence/PYTHIA_H2_READY_SLICE_PLAN.md`

Purpose: expand the Pythia bridge from calibration-only to an H2-ready observational suite, if the larger slice set produces enough non-flat primitive and composite signals. This remains observational and cannot establish causal dependency.

## v2.8 — First-stage experiment summary package

Status: implemented.

Purpose:

The first controlled evidence arc and the first Pythia observational bridge are now mature enough to summarize for thesis writing. v2.8 creates a durable package corresponding to the Methodology & Implementation and Results & Discussion sections.

Implemented components:

- `make_first_stage_experiment_summary` command;
- top-level thesis evidence notes:
  - `FIRST_STAGE_EXPERIMENT_SUMMARY.md`,
  - `METHODOLOGY_IMPLEMENTATION_DRAFT.md`,
  - `RESULTS_DISCUSSION_DRAFT.md`;
- tables:
  - `first_stage_claim_table.csv`,
  - `first_stage_experiment_map.csv`,
  - `first_stage_figure_table_plan.csv`.

Scientific boundary:

This stage consolidates evidence. It does not add new causal evidence. It records that exact-component dependency is localized in the controlled B1 family-1 positive pair, not yet replicated as a broad cross-family phenomenon, and that Pythia results remain observational.

Next possible stages:

1. create thesis figures/tables from the first-stage package;
2. strengthen B2 sparse-parity frequency baseline;
3. run Pythia v2.7 suite on a larger model or more checkpoints;
4. generate a third B1 family with H3-readiness built into calibration.

## v2.9 — Pythia residual refinement

Purpose: decide whether the Pythia H2-style residuals from v2.7 are stable across metrics and composite families.

Run after continuous-score analysis:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_residual_refinement \
  --result-dir results/pythia_h2_ready_observational_pilot_v27 \
  --code-version v2.9 \
  --archive-root results/archive \
  --thesis-use diagnostic
```

Send back:

```text
pythia_residual_refinement_report.md
pythia_residual_agreement_by_composite.csv
pythia_residual_family_summary.csv
pythia_component_coupling_agreement.csv
pythia_residual_metric_matrix.csv
```

Interpretation:

- GREEN: several composites show residual agreement across metrics and component coupling supports the same direction.
- YELLOW: residuals exist but are metric-dependent.
- RED: residuals are degenerate or dominated by controls.

Claim boundary: observational bridge only; no causal dependency claim.
