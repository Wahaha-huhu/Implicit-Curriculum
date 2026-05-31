# Pythia-like observational bridge design

This document defines how the controlled B1/B2 results could be connected to checkpointed LLMs such as Pythia without overclaiming causal transfer.

## 1. Epistemic status

Pythia-like experiments are **observational corroboration**, not causal evidence. We do not control the training data order, cannot upweight or corrupt components during pretraining, and cannot rerun the full pretraining process with matched interventions. Therefore the allowed claim is:

> Pythia-like checkpoint dynamics are consistent or inconsistent with the controlled signatures.

The disallowed claim is:

> Pythia causally learns by the mechanism proven in B1.

## 2. Controlled signatures to look for observationally

| Controlled result | Pythia analogue | Allowed interpretation |
|---|---|---|
| H1 ordering signs | Structural properties predict slice acquisition order | Corroborates ordering signature |
| Atomic predictor ladder | Primitive slices fit simple predictors | Tests whether rate-only account works for simple behaviors |
| Composite residuals | Composite slices deviate from primitive predictor | Candidate interaction/dependency sites |
| H3 heterogeneity | Some residual slices couple to specific components; others to operation families | Consistent with heterogeneous causal structure, not proof |

## 3. Candidate behavioral slice families

| Domain | Primitive slices | Composite slices | Controls |
|---|---|---|---|
| Arithmetic | single-digit add, carry detection, comparison | multi-step add with carry, compare after transform | length/frequency-matched arithmetic templates |
| Syntax | local agreement, number marking | agreement under distractors/nesting | surface-matched nonsyntactic templates |
| Brackets/formal language | local closing bracket | nested bracket matching | same-token shuffled controls |
| Retrieval | key-value lookup | retrieve then transform/compare | same surface with irrelevant key |
| String operations | copy, reverse, mapping | reverse-then-map, map-then-compare | same tokens without operation |

## 4. Slice properties

For every slice we need a frozen pre-analysis table:

- `slice_id`
- `domain`
- `kind`: primitive/composite/control
- `frequency_proxy`
- `reference_learnability_proxy`
- `formal_utility_proxy`
- `operation_family`
- `component_slice_ids`
- `matched_control_ids`

Frequency proxies may include template/corpus counts. Reference learnability can use small reference-model sample complexity, description length, or operation depth. Formal utility is manually defined from the slice graph and must be treated as observer-imposed.

## 5. Pythia H1 observational analysis

For each checkpoint and model size:

1. evaluate each slice;
2. fit acquisition curves using continuous metrics and thresholds;
3. estimate acquisition order;
4. test whether frequency/reference learnability/formal utility predict acquisition time.

Expected possible outcomes:

- frequency dominates simple/local/factual slices;
- reference learnability dominates structured/compositional slices;
- composite slices show residuals not captured by primitive predictors.

## 6. Pythia H2 residual analysis

Fit predictors on primitive slices, then predict composite slices. Report:

- residual magnitude;
- residual sign;
- residual by domain and operation family;
- residual consistency across model sizes;
- whether residuals shrink after component slices improve.

This mirrors B1 H2 but remains observational.

## 7. Pythia H3-inspired coupling analysis

Because true interventions are unavailable, use weaker signatures:

- lagged component-to-composite trajectory coupling;
- whether component improvement precedes residual shrinkage;
- representation similarity between component and composite prompts;
- probing for component intermediate state in composite prompts;
- activation patching if feasible.

Interpretation must be phrased as consistency evidence only.

## 8. Minimal Pythia pilot

A minimal first pilot should use:

- one Pythia scale;
- 8–12 checkpoints;
- 12–20 slices;
- at least two domains;
- primitive/composite/control grouping;
- continuous metrics and one threshold sensitivity table.

The pilot goal is not a paper result but to determine whether slice acquisition curves are measurable and whether the controlled signatures can be operationalized.

## 9. Thesis-safe Pythia claim template

If positive:

> Observational Pythia slice dynamics show signatures analogous to the controlled setting: primitive-slice predictors explain some acquisition order, while certain composite slices show residual/coupled trajectories with component slices. This is consistent with the controlled mechanism but does not establish causality in LLM pretraining.

If null:

> The controlled mechanism did not transfer observationally under the current slice definitions and frequency proxies. This may reflect slice noise, proxy error, checkpoint sparsity, or a regime difference between controlled sequence learning and real LLM pretraining.

