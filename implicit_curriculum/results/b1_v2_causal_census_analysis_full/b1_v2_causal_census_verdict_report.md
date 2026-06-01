# B1 v2 causal-census verdict report

This analysis aggregates H3 row-level interventions into the v2 Exp 2 evidence unit: a distribution of causal verdicts over pre-registered pairs.

Primary metric: `token_accuracy`; threshold `0.7`; min direction rate `0.6`; alpha `0.1`.

## Census verdict distribution
- `difficulty_parallel_or_null`: 2/4 = 0.500 [0.000, 1.000]
- `operation_family_transfer`: 2/4 = 0.500 [0.000, 1.000]

## Pair verdict preview
- `A07_reverse` → `C03_reverse_then_substitute_07_02`: `operation_family_transfer` — Exact component separates from different-operation controls but not same-operation controls, consistent with operation-family transfer rather than exact dependency.
- `A02_substitute` → `C03_reverse_then_substitute_07_02`: `difficulty_parallel_or_null` — No exact-component manipulation separates from matched controls under the preregistered direction rule.
- `A05_substitute` → `C06_reverse_then_substitute_05_07`: `difficulty_parallel_or_null` — No exact-component manipulation separates from matched controls under the preregistered direction rule.
- `A07_reverse` → `C06_reverse_then_substitute_05_07`: `operation_family_transfer` — Exact component separates from different-operation controls but not same-operation controls, consistent with operation-family transfer rather than exact dependency.

## Interpretation boundary
This is causal evidence only inside the controlled Sequence DSL setting. Exact-dependency rows require separation from same-operation and different-operation controls; operation-family rows are not failures but a distinct alternative mechanism under the v2 design.