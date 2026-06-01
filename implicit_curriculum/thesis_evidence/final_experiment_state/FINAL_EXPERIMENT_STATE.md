# Final experiment-state consolidation

Generated at: `2026-06-01T10:35:04.096985+00:00`  
Code version: `v3.3`

## Bottom-line state

The project is ready to begin thesis drafting after this consolidation.  The controlled core is complete, and the Pythia observational bridge is complete through the Tier-1 sweep up to 1.4B.  Larger Pythia models are explicitly marked as future work because the current checkpoint-loading path did not yet provide trustworthy multi-checkpoint dynamics for 2.8B+.

```text
CONTROLLED_CORE_COMPLETE = yes
B1_CROSS_FAMILY_SYNTHESIS_COMPLETE = yes
PYTHIA_BRIDGE_COMPLETE_THROUGH_1P4B = yes
LARGE_PYTHIA_2P8B_PLUS = skipped_for_now_engineering
CLAIMS_READY_FOR_DRAFT = yes
```

## Current supported thesis claim

The supported thesis claim is a boundary-mapping claim, not a universal skill-law claim:

> Acquisition order and primitive-to-composite residuals are useful diagnostics, but they are not self-interpreting.  In controlled B1 training, interventions distinguish localized exact-component dependency from operation-family transfer, weak/negative cases, and hard-composite failure.  In checkpointed Pythia models through the Tier-1 sweep, analogous primitive-to-composite residual signatures are measurable and stable observationally, but they remain non-causal.

## Experiment blocks

| block | status | thesis_use | claim_supported | claim_boundary |
| --- | --- | --- | --- | --- |
| Exp0 recovery gate | complete | sanity_check | analysis pipeline can recover known synthetic dependency/order structure | not substantive evidence about LLMs |
| B1 family 1 H1/H2 | complete | core_controlled_evidence | acquisition is structured; atomic parallel-null residuals select composite candidates | observational residuals are candidate selectors, not causal evidence |
| B1 family 1 H3 interventions | complete | core_controlled_evidence | one localized exact-component dependency site, A02_substitute -> C06_reverse_then_substitute_02_00; other rows weak/operation-family | pair-specific; not universal component-before-composite law |
| B1 family 1 mediator diagnostics | complete | mechanistic_support | positive H3 pair has unusually high early gradient alignment relative to controls | gradient-mediator support only; current CKA was not discriminative |
| B1 family 2 H1/H2 | complete | regime_contrast | acquisition/residual structure recurs, but predictor semantics differ and learnability proxy reverses | no universal scalar predictor; reference_learnability requires auditing/interpretation |
| B1 family 2 H3/readiness | complete_enough | boundary_condition | large residuals can be hard-composite failures or operation-family/weak-negative cases; readiness gate is necessary | does not replicate exact dependency; do not present as positive H3 evidence |
| B1 cross-family synthesis | complete | claim_boundary | controlled evidence supports heterogeneous mechanisms: exact dependency, operation-family transfer, weak/negative cases, hard-composite failure | exact dependency currently localized, not broadly replicated |
| B2 sparse-parity baseline | partial_optional | contrast_if_space | frequency/quanta-like regime contrast is plausible but not yet as complete as B1 | do not over-weight unless strengthened |
| Pythia calibration v2.4-v2.6 | complete | methods_bridge | top-1 accuracy is too harsh; continuous multiple-choice scores reveal subthreshold movement | calibration only; no H2 claim from early small slice suites |
| Pythia H2-ready slice suite v2.7 | complete | observational_bridge | 29-slice suite with 16 atomics, 10 composites, 3 controls enables primitive-to-composite residual fitting | observational slice design; no causal dependency claim |
| Pythia residual refinement v2.9 | complete | observational_bridge | single-model residuals become interpretable across multiple continuous metrics and composite families | single-model result is weaker than sweep; use mainly as stepping stone |
| Pythia Tier-1 sweep through 1.4B | complete | main_pythia_observational_result | stable primitive-to-composite residual underperformance across valid runs from 70M through 1.4B; strongest for arithmetic and string composites | observational residual stability, not causal component dependency and not B1 H3 replication |
| Pythia 2.8B+ large tier | skipped_for_now_engineering | future_work | none for checkpoint dynamics yet | revision/loading issue produced static or untrusted checkpoint curves; do not use as dynamic evidence |

## Pythia sweep summary parsed from latest synthesis

```json
{
  "provided": true,
  "exists": true,
  "runs_included": 10,
  "valid_runs": 10,
  "models": "EleutherAI/pythia-1.4b;EleutherAI/pythia-160m;EleutherAI/pythia-1b;EleutherAI/pythia-410m;EleutherAI/pythia-70m;pythia-12b_n16;pythia-2p8b_n16;pythia-6p9b_n16",
  "arithmetic_mean_under_rate": null,
  "string_mean_under_rate": null,
  "retrieval_mean_under_rate": null
}
```

## Drafting decision

Start the thesis draft now.  Additional experiments should be treated as strengthening/future-work unless they directly address a reviewer-risk point.
