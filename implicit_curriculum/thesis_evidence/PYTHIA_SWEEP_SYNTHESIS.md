# Pythia sweep evidence synthesis

This note records the first cross-model Pythia-style observational bridge result. It should be read together with the controlled B1 evidence: the Pythia runs test whether primitive/composite residual signatures are measurable in checkpointed LLMs, but they do not test causal dependency.

## Inputs
- Sweep synthesis directory: `results/pythia_sweep_synthesis_v30`

## Main result
The Pythia sweep is now useful as observational bridge evidence. The 70M/160M runs both use the H2-ready slice suite with 29 slices and continuous multiple-choice metrics. Across two model sizes, several composites show stable underperformance relative to primitive-predictor expectations.

## Run coverage
- Run summary not available.

## Stable composite residuals
- No residual stability rows available.

## Composite-family pattern
- Family stability table not available.

## Thesis interpretation
The sweep strengthens the observational bridge: primitive-to-composite residual analysis is feasible in checkpointed Pythia-like models and some residual patterns persist across model size. This aligns with the controlled B1 lesson that residuals are informative but not self-interpreting.

The thesis-safe statement is: arithmetic and string composites show stable observational underperformance in the 70M/160M Pythia sweep, while retrieval composites are more model/config dependent. This motivates further observational or mechanistic follow-up, but it is not causal evidence of exact-component dependency.

## Claim boundary
- **Pythia-style checkpointed models show measurable primitive/composite slice dynamics under continuous scores.** — `supported_observational_pilot`. Boundary: This is observational and does not establish causal dependency.
- **Primitive-to-composite residual analysis is feasible in Pythia-like checkpoints.** — `supported_observational_pilot`. Boundary: Residuals are candidate signatures, not proof of component reuse.
- **Some residual patterns persist across Pythia model sizes/configurations.** — `supported_observational_pilot`. Boundary: Only two model sizes have been swept so far; 410M or denser checkpoints would strengthen this.
- **Pythia causally learns composites from primitive components.** — `not_supported`. Boundary: This claim would require interventions or stronger mechanistic evidence beyond observational trajectories.
- **Pythia replicates the B1 exact-component dependency result.** — `not_supported`. Boundary: Use Pythia as observational bridge only.

## Recommended next experiments
1. Run the same H2-ready slice suite on Pythia-410M if compute allows.
2. Run denser checkpoints for 70M/160M to improve trajectory and acquisition-time analyses.
3. Add focused arithmetic-composite slices because arithmetic underperformance is the most stable cross-model residual family so far.
4. Keep the causal language reserved for controlled B1 interventions, not Pythia residuals.
