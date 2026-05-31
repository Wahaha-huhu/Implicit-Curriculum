# Hypothesis Audit after v1.4 Evidence Consolidation

This file records what the current experiments can and cannot justify. It is deliberately conservative.

## Current evidence base

- Exp 0 synthetic recovery validates the analysis pipeline on known synthetic mechanisms.
- B2 sparse parity gives a quanta-style frequency/difficulty baseline, though acquisition coverage should be improved for final quantitative use.
- B1 sequence DSL calibration establishes a trainable controlled sequence-transformer substrate.
- B1 H1 shared sweep shows stable ordering signs across six configurations.
- B1 H2 predictor ladder shows simple atomic predictors with configuration drift and structured composite residuals.
- B1 H3 C06 interventions show mixed component-level evidence:
  - `A02_substitute → C06_reverse_then_substitute_02_00`: positive pair-specific evidence under exact pretraining and strong corruption.
  - `A00_copy → C06_reverse_then_substitute_02_00`: weak/mixed, so dependency is not uniform across formal components.

## Original high-level hypothesis

> Capability acquisition order is predicted by structural properties, and observed composite-after-component order reflects genuine developmental dependency rather than only parallel resolution.

This is too strong as one global statement. The current evidence supports a decomposed version:

1. structural properties predict acquisition order in controlled settings;
2. atomic acquisition can often be summarized by simple configuration-dependent predictors;
3. residuals from atomic parallel-rate models can identify candidate dependency sites;
4. interventions are needed because residuals are not automatically dependency;
5. exact dependency is pair- and component-specific in current evidence.

## Audited hypotheses

| Hypothesis | Current verdict | Safe claim | Unsafe claim |
|---|---|---|---|
| H1: Structural properties predict acquisition order. | Supported in B1 pilot, strongest for reference learnability. | Reference learnability robustly predicts later acquisition in controlled B1; frequency is weaker and stratum-dependent. | Frequency universally determines acquisition order. |
| H1b: Effect directions are stable across configs. | Supported as pilot. | Effect signs are stable across the six-config B1 pilot. | This proves config-invariant universal laws. |
| H2: Atomic acquisition can be summarized by simple predictors. | Supported as pilot. | Simple one-factor atomic predictors work within configs, with config drift. | One fixed scalar law explains all configs/tasks. |
| H2b: Composite residuals identify dependency candidates. | Supported observationally. | Residuals are useful pair-selection signals. | Residuals prove dependency. |
| H3: Composite acquisition can causally depend on exact components. | Supported for one pair only. | `A02_substitute → C06` shows pair-specific causal evidence in controlled B1 under pretraining and strong corruption. | Developmental dependency is universal, or C06 depends equally on all listed components. |
| H3b: Dependency is uniform across components. | Not supported. | Dependency appears component-specific. | Every formal component causally enables its composite. |
| LLM mechanism claim. | Not tested. | Controlled findings are candidate mechanisms to test observationally later. | Real LLM training proceeds by this mechanism. |

## Updated central thesis framing

The current evidence supports a **controlled, scoped mechanism map**, not a universal mechanism:

> In a controlled sequence-transformer setting, acquisition order is predictably related to pre-training structural properties, especially reference learnability. Atomic acquisition is often captured by simple configuration-dependent predictors. Composite residuals identify candidate sites where the parallel-rate account fails. Interventions show that at least one delayed composite is causally sensitive to one exact component, but the effect is component-specific rather than universal across all formal components.

## Strongest defensible claims now

1. The recovery gate distinguishes known synthetic acquisition mechanisms.
2. Sparse parity provides a contrasting frequency-dominated/quanta-style regime, pending stronger coverage.
3. In B1, reference learnability is a robust predictor of later acquisition across configs; frequency is weaker and stratum-dependent.
4. Atomic acquisition can be predicted by simple one-factor models, but the selected factor drifts by configuration.
5. Atomic-parallel residuals can select meaningful H3 intervention targets.
6. For `A02_substitute → C06_reverse_then_substitute_02_00`, exact component pretraining and strong corruption move composite acquisition beyond same-operation and different-operation controls.

## Claims that remain unsupported

1. A universal closed-form law of capability acquisition timing.
2. Frequency alone explaining acquisition order in sequence-transformer tasks.
3. All composite ordering reflecting developmental dependency.
4. Every formal component of a composite being causally relevant.
5. A causal claim about real LLM training.

## Consequence for next experiments

The next experiments should widen the evidence base:

1. test a second delayed composite/pair, such as C07;
2. replicate A02→C06 on another B1 family;
3. add gradient/representation/probe mediators for A02→C06;
4. improve B2 sparse-parity acquisition coverage for a cleaner baseline.
