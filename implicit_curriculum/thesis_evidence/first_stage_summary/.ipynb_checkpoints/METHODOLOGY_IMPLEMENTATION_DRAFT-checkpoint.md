# Methodology & Implementation draft notes

## Methodological design

The experiments are staged to avoid interpreting acquisition order as causality. The pipeline is:

1. **Synthetic recovery.** Validate that the predictor ladder and residual logic can recover known synthetic worlds.
2. **Controlled task families.** Build sequence-DSL families with atomic tasks, true composites, shortcut/fake components, surface controls, same-operation controls, and different-operation controls.
3. **H1 ordering analysis.** Train small transformers over mixed task data and measure per-task acquisition curves across configurations and seeds.
4. **H2 atomic parallel-null analysis.** Fit predictor ladders on atomic tasks only, then predict composite acquisition times. Composite residuals select candidates, but are explicitly treated as observational.
5. **H3 interventions.** Manipulate candidate components with pretraining, upweighting, corruption, and delay, and compare against matched same-operation, different-operation, fake, and surface controls.
6. **Mediator diagnostics.** Compare positive and negative H3 pairs using early gradient and representation coupling.
7. **Cross-family replication/stress test.** Repeat the framework on a second generated B1 family and explicitly track which claims replicate.
8. **Pythia observational bridge.** Evaluate checkpointed Pythia-style models on primitive/composite/control slices with multiple-choice likelihood scores. This stage tests only observational analogues.

## Key implementation choices

- Acquisition is measured primarily with held-out token accuracy for B1 and continuous multiple-choice scores for Pythia.
- Thresholds are analysis hyperparameters, not training hyperparameters. Threshold sensitivity is used to distinguish clear acquisition from subthreshold movement.
- H3 candidate selection now uses both residual magnitude and readiness: a candidate must be delayed enough to be interesting but not so hard that no intervention can move it.
- Pythia evaluation uses observational slices and continuous scores because top-1 accuracy can be too harsh for small checkpointed models.

## Validity controls

The task design includes several controls to reduce spurious interpretation:

- **Same-operation controls** test whether a result is exact-component-specific or merely operation-family transfer.
- **Different-operation controls** test whether an intervention effect is generic data-budget transfer.
- **Fake/shortcut controls** test whether formal labels or shortcut structure are sufficient.
- **Surface controls** test whether shared tokens/templates explain the effect.
- **Negative and mixed results** are retained as evidence boundaries rather than discarded.

## Implementation boundary

Causal claims are limited to controlled B1 interventions. Pythia experiments are observational and cannot establish causal dependency without pretraining interventions.
