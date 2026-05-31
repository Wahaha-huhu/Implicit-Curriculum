# Figure Specs

This file is a lightweight planning document. Final plotting scripts should be added later under `scripts/figures/` or `thesis_evidence/figure_scripts/`.

## H1 sign stability plot

Input:

- `results_summaries/b1_h1_sign_stability.csv`
- `results_summaries/b1_h1_config_summary.csv`

Plot:

- x-axis: config;
- y-axis: Spearman rho;
- color/facet: predictor;
- include strata: all, true tasks, atomics.

Thesis claim supported:

- Reference learnability robustly predicts later acquisition.
- Frequency is weak but stable, especially atomics.

## H2 residual heatmap

Input:

- `results_summaries/b1_h2_composite_residual_summary_by_task.csv`
- `results_summaries/b1_h2_pair_selection.csv`

Plot:

- x-axis: config;
- y-axis: composite;
- color: mean residual log-time;
- highlight C06 and C07.

Thesis claim supported:

- Composite residuals are structured and select intervention candidates.

## H3 contrast plot

Input:

- `results_summaries/b1_h3_c06_intervention_contrasts.csv`
- `results_summaries/b1_h3_c06_pair_summary.csv`

Plot:

- condition bars for acquisition rate, censored time, final metric;
- contrast arrows: component vs unrelated/fake/surface.

Thesis claim supported:

- First intervention is mixed/negative for exact dependency and motivates operation-family controls.


## H3 C06 component-specific evidence table

Purpose: show that the same delayed composite (`C06`) responds differently to two listed components.

Rows:
- `A02_substitute → C06`: strong upweight signal; weak delay.
- `A00_copy → C06`: weak/mixed signal.

Candidate columns:
- upweight exact-vs-same-operation censored delta
- upweight exact-vs-same-operation expected-direction rate
- corrupt exact-vs-same-operation expected-direction rate
- delay exact-vs-same-operation expected-direction rate
- thesis-safe verdict

Intended claim: H3 evidence is component-specific and motivates stronger model-state tests, not a final dependency proof.
