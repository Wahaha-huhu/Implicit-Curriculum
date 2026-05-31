# Overall results synthesis

This file records the current thesis-level interpretation of the experiments. It is deliberately conservative: claim strength is calibrated to the evidence currently available.

## High-level summary

The project currently supports a scoped controlled-mechanism story:

1. The simulated recovery gate validates the analysis pipeline on known synthetic worlds.
2. Sparse parity provides a quanta-style baseline where frequency and parity degree behave in expected directions, though coverage can still be improved.
3. In the B1 sequence-DSL transformer substrate, acquisition order is stably related to structural properties across configurations, especially reference learnability; frequency is weaker and more stratum-dependent.
4. Atomic acquisition can be modeled by simple configuration-dependent predictors, and applying the atomic parallel-rate model to composites reveals structured residuals.
5. H3 interventions show heterogeneous causal structure: one exact component–composite pair is positive, while other formal components are weak, negative, or operation-family-level.

## Main thesis claim currently supported

> In controlled sequence-transformer training, structural properties help predict capability acquisition order, and atomic parallel-rate residuals can identify candidate composite dependency sites. However, intervention results show that dependency is heterogeneous: exact-component causal sensitivity can occur locally, but formal component membership does not generally imply causal enablement.

## What is not supported

The current evidence does not support a universal law of LLM training, a universal frequency-only account, or a universal component-before-composite dependency mechanism.

## H3 synthesis update

The current H3 matrix has four tested pairs:

- `A02_substitute → C06`: positive pair-specific exact-component evidence.
- `A00_copy → C06`: weak/mixed.
- `A04_reverse → C07`: operation-family transfer.
- `A03_copy → C07`: negative.

This makes the H3 conclusion stronger but narrower: residuals are useful candidate selectors, but interventions are necessary to map the actual causal structure.

## Mediator diagnostic update

The mediator diagnostic stage adds mechanistic corroboration for the localized H3 positive pair. `A02_substitute → C06_reverse_then_substitute_02_00` has much stronger early gradient alignment with its composite than same-operation, different-operation, fake, or surface controls. Weak/negative pairs do not show this exact-component gradient separation, and the operation-family pair `A04_reverse → C07` shows exact and same-operation reverse gradients that are nearly matched.

This supports the gradient-mediated interpretation for the localized positive pair, but current CKA is not discriminative and should not be used as representation-level evidence for exact dependency.

Updated core claim:

> In controlled sequence-transformer training, structural predictors and atomic residuals identify candidate composite interactions; interventions and mediator diagnostics show that exact-component reuse is localized and gradient-aligned rather than universal across formal components.

## Pythia observational sweep update (v3.1)

The Pythia bridge has progressed from calibration to a useful observational result. With an H2-ready slice suite, Pythia-70M and Pythia-160M both yield primitive/composite residual signatures under continuous multiple-choice metrics. Several arithmetic and string composites are stable underperformers across the two models, while retrieval composites are more model/config dependent. This supports the observational bridge claim that residual analysis can be applied to checkpointed LLMs. It does not establish causal component dependency, because no Pythia pretraining intervention was performed.
