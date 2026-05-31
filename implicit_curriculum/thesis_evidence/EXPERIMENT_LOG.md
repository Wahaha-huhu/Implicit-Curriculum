# Experiment Log and Current Evidence State

This document records experiment outcomes that may later support thesis claims or motivate follow-up hypotheses. It is cumulative and should be updated after each serious run.

## Current headline status

1. **Analysis recovery is validated.** Synthetic recovery distinguishes frequency-only, learnability-only, three-factor, and dependency-gated worlds.
2. **B2 sparse parity gives a quanta-style baseline.** Frequency strongly predicts acquisition time; parity degree controls final difficulty.
3. **B1 sequence DSL is the main controlled transformer substrate.** It now reaches nonzero/non-saturated acquisition and supports H1/H2 pilot analyses.
4. **H1 ordering/sign-stability is positive but scoped.** Reference learnability is the dominant stable predictor; frequency is stable but weak, strongest in atomics.
5. **H2 predictor ladder/residual analysis is positive.** Simple atomic predictors suffice within configs; composites show structured residuals, selecting C06 for H3.
6. **First H3 intervention is not a positive dependency result.** Component upweighting helps relative to fake/surface controls, but not relative to same-operation unrelated control. This suggests operation-family transfer rather than exact-component dependency.

---

## Exp 0 — Simulated recovery gate

**Status:** green.  
**Role:** validates analysis pipeline before neural training.  
**Evidence file:** `results_summaries/exp0_recovery_report.md`.

Key result:

- Design diagnostics passed with low collinearity.
- Frequency-only, learnability-only, and three-factor synthetic worlds were recovered correctly.
- Dependency-gated world showed strong positive composite residual.

Use in thesis:

- Methods/instrument validation.
- Justifies using the predictor ladder and residual analysis on neural runs.

Do not use as:

- Evidence about neural training dynamics.

---

## B0 — Boolean sandbox pilots

**Status:** diagnostic / yellow-green.  
**Role:** engineering sandbox for acquisition metrics, interventions, censored analysis, gradient/CKA diagnostics.

Key result:

- Hand-built Boolean tasks produced promising component-specific effects for `AB_and`.
- Generated Boolean families had low composite coverage, motivating the shift to B1 sequence DSL.

Use in thesis:

- Possibly brief appendix as development path or instrument debugging.

Do not use as:

- Main evidence for the scientific mechanism.

---

## B2 — Sparse parity baseline

**Status:** yellow-green.  
**Role:** quanta-comparable baseline where frequency/degree should dominate.
**Evidence files:**

- `results_summaries/b2_sparse_parity_analysis_report.md`
- `results_summaries/b2_sparse_parity_ordering_summary.csv`
- `results_summaries/b2_sparse_parity_degree_summary.csv`

Key result:

- Acquisition rate around 0.23--0.24 across thresholds 0.75, 0.85, 0.90.
- Frequency strongly predicts earlier acquisition: time-Spearman roughly -0.68 to -0.71.
- Degree controls final difficulty: degree-2 tasks reached much higher final balanced accuracy than degree-3 tasks.

Use in thesis:

- Baseline showing that the pipeline can recover a frequency-dominated regime.
- Contrast with B1, where learnability dominates and frequency is weaker.

Caveat:

- Acquisition coverage is still modest; should be treated as a pilot baseline unless rerun with higher coverage.

---

## B1 — Sequence DSL calibration

**Status:** green.  
**Role:** establishes trainable controlled transformer substrate.
**Evidence files:**

- `results_summaries/b1_sequence_dsl_calibration_report.md`
- `results_summaries/b1_sequence_candidate_calibration_summary.csv`

Key result:

- Selected family passed calibration with nonzero/non-saturated token acquisition.
- Token acquisition rate about 0.69, composite token acquisition about 0.92, atomic token acquisition about 0.83.
- Mean final token accuracy about 0.75.

Use in thesis:

- Justifies B1 as the primary controlled sequence/transformer substrate.

Caveat:

- Exact match remains much stricter and lower; token accuracy/loss are primary for calibration.

---

## B1 H1 — Ordering and sign-stability shared sweep

**Status:** green with caveats.  
**Role:** first real controlled H1 pilot.
**Evidence files:**

- `results_summaries/b1_h1_analysis_report.md`
- `results_summaries/b1_h1_sign_stability.csv`
- `results_summaries/b1_h1_config_summary.csv`
- `results_summaries/b1_h1_threshold_sensitivity.csv`

Key result:

- Nonzero/non-saturated acquisition across six configurations.
- Frequency realization was accurate.
- Reference learnability had stable positive association with acquisition time across configs.
- Frequency had stable but weak negative association overall and stronger negative association in atomics.
- Composite-only frequency effect was reversed, indicating that composite operation/type effects dominate frequency within composites.

Use in thesis:

- Tier-2 controlled claim: acquisition order is predictably related to pre-training structural properties, especially reference learnability.
- Supports config-robust sign-stability, not universal timing law.

Caveats:

- Frequency is weak in B1.
- Utility remains exploratory due shallow task graph.
- Not yet full-scale final experiment.

---

## B1 H2 — Predictor ladder and atomic parallel-null residuals

**Status:** green.  
**Role:** tests simple predictors and selects residual pairs for H3.
**Evidence files:**

- `results_summaries/b1_h2_analysis_report.md`
- `results_summaries/b1_h2_selected_models.csv`
- `results_summaries/b1_h2_pair_selection.csv`
- `results_summaries/b1_h2_composite_residual_summary_by_task.csv`

Key result:

- Atomic acquisition is explained by simple one-factor predictors within each config.
- Selected atomic predictor drifts by config: frequency-only in base/batch_small/lr_high/wd_zero, learnability-only in batch_large/lr_low.
- Selected predictors beat permutation reasonably often.
- Composite residuals are structured rather than uniformly delayed.
- `C06_reverse_then_substitute_02_00` is the strongest delayed composite across several configs.

Use in thesis:

- Supports the claim that a simple parallel-rate predictor can model atomics but composites can show structured residuals.
- Provides principled pair selection for H3.

Caveat:

- Residuals are observational only. They do not establish dependency.

---

## B1 H3 — C06 pair-specific intervention pilot

**Status:** yellow / borderline red for exact-component dependency.  
**Role:** first causal intervention test on H2-selected pair.
**Evidence files:**

- `results_summaries/b1_h3_c06_analysis_report.md`
- `results_summaries/b1_h3_c06_intervention_contrasts.csv`
- `results_summaries/b1_h3_c06_pair_summary.csv`

Pair tested:

- Component: `A02_substitute`
- Composite: `C06_reverse_then_substitute_02_00`

Key result:

- `upweight_component` improved acquisition relative to fake and surface controls.
- `upweight_component` did **not** clearly beat the unrelated matched substitution control.
- Delay/corruption contrasts were weak.

Interpretation:

- This does not support a clean exact-component dependency claim.
- More plausible current hypothesis: C06 benefits from operation-family transfer, especially substitution-like training, rather than the exact component `A02_substitute`.

Use in thesis:

- Important negative/mixed result.
- Motivates sharper H3 controls and operation-family decomposition.

Do not use as:

- Evidence that developmental dependency has been causally established.

### v1.1 implementation note — operation-family H3 controls

After the v1.0 C06 H3 pilot returned a mixed/negative exact-dependency result, v1.1 adds operation-family controls. The goal is to separate exact-component dependency from operation-family transfer. No new claim is added yet; this is an implementation milestone preparing the next H3 run.
