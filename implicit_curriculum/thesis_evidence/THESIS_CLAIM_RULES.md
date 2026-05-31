# Thesis Claim Rules

Use this file as a guardrail when writing the thesis.

## Rule 1 — Separate ordering, prediction, residuals, and causality

- H1 ordering: structural properties correlate with acquisition order.
- H2 prediction/residuals: predictors explain atomics and identify composite deviations.
- H3 causality: only interventions can support dependency.

Do not use H1 or H2 evidence as causal evidence.

## Rule 2 — State the B1 result as controlled, not LLM-general

Use:

> In a controlled sequence-transformer substrate...

Avoid:

> In LLM training generally...

until Pythia or another LLM-scale observational rung is run.

## Rule 3 — Treat frequency carefully

B2 supports a strong frequency effect. B1 supports only a weak, stratum-dependent frequency effect. Do not claim frequency universally dominates.

## Rule 4 — Treat utility as exploratory

The current B1 graph is shallow. Formal utility should be reported as exploratory unless a deeper graph or stronger utility-specific design is run.

## Rule 5 — H3 is currently pair-specific

The current positive H3 evidence is strongest for:

`A02_substitute -> C06_reverse_then_substitute_02_00`

Do not generalize it to all components or all composites. Row 1 (`A00_copy -> C06`) was weak/mixed.

## Rule 6 — Positive H3 requires matched controls

A positive exact-component dependency claim requires the exact component to beat:

- same-operation unrelated control;
- different-operation matched control;
- fake/no-reuse control where applicable;
- surface control where applicable.

The strongest v1.2 result satisfies this most clearly for pretraining and strong corruption, not for delay.

## Rule 7 — Record negative results

The mixed and negative H3 results are not failures. They are evidence that residuals do not automatically imply dependency and that dependency may be localized.
