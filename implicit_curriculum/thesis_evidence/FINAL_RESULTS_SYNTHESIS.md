# Final current results synthesis after H3 mediator diagnostics

This document consolidates the current experimental arc for thesis writing. It should be updated append-only as new families, mediator diagnostics, or Pythia-style observational studies are added.

## Experimental arc completed so far

1. **Exp0 simulated recovery:** validates that the analysis pipeline can recover known synthetic mechanisms.
2. **B2 sparse parity baseline:** provides a quanta-style contrast where frequency and degree behave in expected directions, though acquisition coverage should be improved for final evidence.
3. **B1 sequence-DSL calibration:** establishes a trainable, non-saturated controlled sequence-transformer task family.
4. **B1 H1 ordering:** shows that acquisition order is structurally predictable, especially by reference learnability; frequency is weaker and stratum-dependent.
5. **B1 H2 atomic parallel null:** fits simple atomic predictors and uses composite residuals to select candidate dependency sites.
6. **B1 H3 interventions:** show heterogeneous causal structure: one pair is exact-component positive, while others are weak, negative, or operation-family-level.
7. **B1 mediator diagnostics:** show that the H3-positive pair also has unusually high early gradient alignment relative to matched controls; current CKA does not distinguish pairs.

## Core contribution now supported

The current work supports a **controlled boundary-mapping account** of capability acquisition:

> Structural predictors and atomic parallel-rate residuals can identify where composite acquisition deviates from simple parallel learning. However, residuals and formal component graphs are not enough to infer dependency. Interventions reveal whether a case reflects exact-component dependency, operation-family transfer, or no exact dependency. In the B1 controlled sequence-transformer family, exact dependency appears localized rather than universal, and the positive pair is accompanied by stronger early gradient alignment.

## Most important positive result

The strongest pair-specific result is:

- `A02_substitute → C06_reverse_then_substitute_02_00`.

Evidence:

- Exact component pretraining makes C06 acquire immediately and beats same-operation and different-operation pretraining controls.
- Exact component corruption delays/degrades C06 beyond same-operation and different-operation corruption controls.
- The exact component has much larger early gradient cosine with C06 than same-operation, different-operation, fake, or surface controls.

## Most important boundary result

Exact-component dependency is not uniform:

- `A00_copy → C06` is weak/mixed.
- `A04_reverse → C07` is better explained as operation-family transfer.
- `A03_copy → C07` is negative.

This makes the negative/mixed findings scientifically useful: they show why interventions are necessary and why formal graphs should not be overinterpreted.

## Current top-conference-style positioning

A strong paper/thesis framing is:

1. **Problem:** We often infer skill dependencies from acquisition order, but this is confounded by frequency, learnability, and operation family.
2. **Method:** Build a controlled sequence-transformer benchmark with atomics, composites, and matched controls; fit atomic parallel-rate models; intervene on candidate components.
3. **Finding:** Acquisition order is predictable, residuals identify candidates, but causal dependency is heterogeneous.
4. **Mechanism:** The strongest exact-dependency pair also shows strong early gradient alignment, suggesting a gradient-mediated route for localized reuse.
5. **Boundary:** The result is controlled-setting-specific; it is not a causal claim about real LLM pretraining. Pythia-like studies should be observational bridge tests.

## Next best evidence additions

1. **Second B1 family replication:** test whether localized exact dependency appears in another generated family.
2. **Stronger representation/probe diagnostics:** current CKA is too coarse; add layerwise CKA, component-state probes, or activation/finetune transfer.
3. **B2 strengthening:** improve sparse-parity coverage to make the frequency/quanta baseline thesis-ready.
4. **Pythia pilot:** observational slice study only, designed using the claim boundary learned from B1.
