# Thesis Figures and Tables To Build Later

This file lists figure/table candidates and the source artifacts to use. Do not generate final figures from overwriteable `results/latest` folders; use archived runs or files copied into `thesis_evidence/results_summaries/`.

## Figure 1 — Experimental ladder and claim tiers

Purpose: show B0/B1/B2/Exp0/H1/H2/H3 ladder and which claims each supports.

Source: `EXPERIMENT_LOG.md`, proposal design.

## Figure 2 — Synthetic recovery gate

Purpose: show that the analysis pipeline recovers known worlds.

Source files:

- `results_summaries/exp0_recovery_verdict.csv`
- `results_summaries/exp0_recovery_report.md`

Possible panels:

- selected predictor rate by synthetic world;
- dependency-gated residual vs non-dependency worlds.

## Figure 3 — B2 sparse parity baseline

Purpose: frequency-dominated baseline.

Source files:

- `results_summaries/b2_sparse_parity_analysis_report.md`
- `results_summaries/b2_sparse_parity_ordering_summary.csv`
- `results_summaries/b2_sparse_parity_degree_summary.csv`

Possible panels:

- acquisition time vs log frequency;
- final accuracy by parity degree.

## Figure 4 — B1 H1 sign-stability across configurations

Purpose: show stable learnability/frequency signs across B1 configs.

Source files:

- `results_summaries/b1_h1_sign_stability.csv`
- `results_summaries/b1_h1_config_summary.csv`
- `results_summaries/b1_h1_threshold_sensitivity.csv`

Possible panels:

- bar plot of Spearman rho by predictor/config;
- threshold sensitivity plot;
- frequency realization inset.

## Figure 5 — H2 predictor ladder and config drift

Purpose: show simple predictors selected, but dominant predictor drifts by config.

Source files:

- `results_summaries/b1_h2_selected_models.csv`
- `results_summaries/b1_h2_model_coefficients.csv` if available in archive;
- `results_summaries/b1_h2_analysis_report.md`.

Possible panels:

- selected predictor by config;
- CV RMSE by model rung;
- permutation-beat rates.

## Figure 6 — Composite residuals under atomic parallel null

Purpose: show that composites are not uniformly explained by atomic parallel-rate model.

Source files:

- `results_summaries/b1_h2_composite_residual_summary_by_task.csv`
- `results_summaries/b1_h2_pair_selection.csv`

Possible panels:

- residual distribution;
- top delayed composites across configs;
- C06 residual heatmap by config.

## Figure 7 — H3 C06 intervention result: mixed/negative exact-dependency test

Purpose: show why the first H3 result points to operation-family transfer rather than exact component dependency.

Source files:

- `results_summaries/b1_h3_c06_analysis_report.md`
- `results_summaries/b1_h3_c06_intervention_contrasts.csv`
- `results_summaries/b1_h3_c06_pair_summary.csv`

Possible panels:

- acquisition rate and censored time by condition;
- contrasts: component vs unrelated/fake/surface;
- final metric by condition.

## Table 1 — Key claims, evidence, and caveats

Source: `CLAIMS_AND_EVIDENCE.md`.

## Table 2 — Experiment versions and status

Source: `RESULTS_REGISTRY.csv`.

---

## New thesis figures/tables after strong H3 row-0

### Table: Hypothesis status audit

Source: `tables/hypothesis_status.csv`.

Purpose: show which hypotheses are supported, partially supported, unsupported, or future-only.

### Figure/Table: H3 exact-component intervention contrast for A02 -> C06

Source:

- `results_summaries/b1_h3_row0_strong_v12_intervention_contrasts.csv`
- `results_summaries/b1_h3_row0_strong_v12_pair_summary.csv`

Plot candidates:

- censored acquisition time by condition;
- final token accuracy by condition;
- exact pretrain vs same/different-operation controls;
- exact strong corruption vs same/different-operation controls.

Caption message:

> Exact component pretraining and corruption move the delayed composite beyond operation-matched controls, but the result is pair-specific and should not be generalized to all components.

## Figure 8 — H3 evidence matrix across tested pairs

Purpose: show that dependency is heterogeneous rather than universal.

Source files:

- `tables/h3_pair_evidence_matrix.csv`
- `H3_SYNTHESIS.md`

Possible panels:

- pair-by-pair heatmap with verdict categories;
- composite-level summary: C06 localized exact site, C07 operation-family/saturation.

## Figure 9 — Mediator diagnostics: gradient alignment separates the positive pair

Purpose: show that the H3-positive pair has stronger early gradient coupling than controls and weak/negative pairs.

Source files:

- `tables/mediator_pair_evidence_matrix.csv`
- `results_summaries/b1_mediator_h3_pairs_v18_analysis_report.md`
- `results_summaries/b1_mediator_h3_pairs_v18_contrast_summary.csv`

Possible panels:

- bar plot: exact vs same-operation vs different-operation gradient cosine for each pair;
- exact-minus-control gradient cosine by pair;
- CKA flatness panel or appendix table showing CKA is not discriminative.

## Table 3 — Final claim/evidence matrix

Purpose: thesis-safe claim boundary.

Source file:

- `tables/final_claim_evidence_matrix.csv`

Columns:

- claim;
- status;
- key evidence;
- caveat;
- thesis use.
