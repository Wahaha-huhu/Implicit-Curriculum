# Pythia sweep evidence synthesis

This note records the first cross-model Pythia-style observational bridge result. It should be read together with the controlled B1 evidence: the Pythia runs test whether primitive/composite residual signatures are measurable in checkpointed LLMs, but they do not test causal dependency.

## Main result

The Pythia sweep is useful as observational bridge evidence. The 70M/160M runs use the H2-ready slice suite with 29 slices and continuous multiple-choice metrics. Across two model sizes, several composites show stable underperformance relative to primitive-predictor expectations.

## Stable composite residuals

The stable underperforming composites across Pythia-70M and Pythia-160M are:

- `comp_add_then_compare`
- `comp_sub_then_compare`
- `comp_reverse_then_last`
- `comp_add_then_even`
- `comp_first_then_same`
- `comp_reverse_then_same`
- `comp_max_then_compare`

Arithmetic and string composites are the most stable underperforming families. Retrieval composites are more model/config dependent.

## Thesis interpretation

The sweep strengthens the observational bridge: primitive-to-composite residual analysis is feasible in checkpointed Pythia-like models and some residual patterns persist across model size. This aligns with the controlled B1 lesson that residuals are informative but not self-interpreting.

The thesis-safe statement is: arithmetic and string composites show stable observational underperformance in the 70M/160M Pythia sweep, while retrieval composites are more model/config dependent. This motivates further observational or mechanistic follow-up, but it is not causal evidence of exact-component dependency.

## Claim boundary

Supported:

- Pythia-style checkpointed models show measurable primitive/composite slice dynamics under continuous scores.
- Primitive-to-composite residual analysis is feasible in Pythia-like checkpoints.
- Some residual patterns persist across two model sizes/configurations.

Not supported:

- Pythia causally learns composites from primitive components.
- Pythia replicates the B1 exact-component dependency result.
- Residuals alone prove prerequisite structure.

## Recommended next experiments

1. Run the same H2-ready slice suite on Pythia-410M if compute allows.
2. Run denser checkpoints for 70M/160M to improve trajectory and acquisition-time analyses.
3. Add focused arithmetic-composite slices because arithmetic underperformance is the most stable cross-model residual family so far.
4. Keep causal language reserved for controlled B1 interventions, not Pythia residuals.
