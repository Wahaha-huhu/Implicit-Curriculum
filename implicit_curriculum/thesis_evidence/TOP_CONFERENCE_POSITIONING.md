# Contribution framing for a top-conference-style submission

This document records how the project should be positioned if developed toward a strong thesis chapter or conference paper.

## 1. What the paper should not claim

The paper should not claim a universal law of training, a proof of the mechanism of LLM learning, or a general theorem that composites depend on components.

## 2. Stronger contribution framing

The stronger framing is methodological and empirical:

> We introduce a controlled causal framework for disentangling acquisition-order mechanisms. Apparent component-before-composite learning can arise from rate-only parallel resolution, operation-family transfer, or exact-component dependency. We show how to separate these using structural predictors, atomic parallel-null residuals, and matched interventions in a sequence-transformer substrate.

## 3. Main contributions

1. **Causal diagnostic framework**: a staged H1/H2/H3 methodology separating ordering, residuals, and interventions.
2. **Controlled sequence-transformer benchmark**: B1 sequence DSL with atomics, composites, same-operation controls, different-operation controls, surface controls, and shortcut controls.
3. **Regime contrast**: sparse parity behaves more frequency-like, while sequence DSL is more learnability/residual dominated.
4. **Residuals as candidate selectors, not proof**: H2 residuals find candidate composites, but H3 shows heterogeneous outcomes.
5. **Localized dependency evidence**: one exact component-composite pair shows causal sensitivity under pretraining and corruption.
6. **Claim calibration**: results rule out a naive universal dependency interpretation.

## 4. Why this could be interesting

Many implicit-curriculum or emergence studies are observational. They show order, correlations, or representation similarity. This project adds a causal layer in a controlled transformer setting and demonstrates that observational residuals can correspond to multiple mechanisms.

The negative/mixed H3 results are not failures; they are part of the contribution. They show why interventions are needed.

## 5. Likely reviewer concerns and responses

| Concern | Response |
|---|---|
| The benchmark is synthetic | Yes; causal claims require control. The benchmark is a causal microscope, not a naturalistic LLM replacement. Pythia is used later only observationally. |
| Only one positive H3 pair | Correct; claims are localized. The paper emphasizes heterogeneity and boundary mapping. |
| Token accuracy may be too weak | Exact match/loss are reported as secondary metrics; acquisition is ordinal and sensitivity-tested. |
| Controls are imperfect | Same-operation, different-operation, fake, and surface controls are explicit and reveal nontrivial alternative mechanisms. |
| Does this say anything about LLMs? | It provides a methodology and candidate signatures for checkpointed LLM studies, not causal LLM proof. |

## 6. What would make the work substantially stronger

Priority additions:

1. replicate the H3 positive result on a second B1 family;
2. add mediator diagnostics for positive vs negative pairs;
3. strengthen B2 sparse parity coverage;
4. run a small Pythia observational pilot;
5. add visualization-ready figures and pre-registered analysis tables.

## 7. Candidate title framing

- "Residuals Are Not Dependency: A Controlled Causal Study of Implicit Curriculum in Sequence Transformers"
- "When Does Composite Learning Depend on Components? Controlled Interventions in a Sequence-Transformer Curriculum"
- "Disentangling Parallel Resolution, Operation Transfer, and Dependency in Capability Acquisition"

