# Task design justification and validity argument

This document records why the current controlled benchmark design is scientifically useful, what claims it can support, and where it deliberately stops. It is intended to be cited during thesis writing and to prevent task-design choices from being defended only after seeing results.

## 1. Core design question

The scientific question is not merely whether a composite task appears after its components. The core question is:

> When acquisition order suggests a component-before-composite relation, is the composite actually causally dependent on the exact component, or is the apparent order explained by parallel rate differences, operation-family transfer, shortcut learning, surface overlap, or generic data-budget effects?

The task design is therefore built around **separation of mechanisms**, not around maximizing accuracy or reproducing natural language in full.

## 2. Benchmark ladder and why each rung exists

| Backend | Role | Why it is needed | Claim strength |
|---|---|---|---|
| B0 Boolean sandbox | Engineering/debugging | Fast validation of acquisition estimators, interventions, censoring, gradient/CKA logging | Not main scientific evidence |
| B2 sparse parity | Quanta-style baseline | Tests whether the analysis can recover a frequency/difficulty-dominated regime comparable to quantization-style settings | Controlled baseline; no dependency claim |
| B1 sequence DSL | Primary controlled transformer substrate | Combines symbolic ground truth with sequence prediction and a decoder-only transformer, allowing explicit control of atomics, composites, controls, and interventions | Main controlled H1/H2/H3 evidence |
| Future Pythia slices | Observational LLM bridge | Tests whether controlled signatures appear in real checkpointed LLMs | Corroborative only; no causal claim |

This ladder is designed so that negative results remain interpretable. If B2 is frequency-dominated but B1 is learnability/residual dominated, the difference is a regime finding rather than a failure. If B1 residuals do not survive intervention, that distinguishes observational residuals from true dependency.

## 3. Why B1 sequence DSL is the primary controlled substrate

B1 is intentionally more LLM-like than fixed-vector Boolean tasks while remaining intervention-friendly.

It has:

- sequence inputs and sequence targets;
- token-level autoregressive training;
- a decoder-only transformer;
- known structure IDs for every example;
- held-out per-structure evaluation;
- atomic and composite structures with known formal computation graphs;
- shortcut, surface, same-operation, different-operation, and unrelated controls.

This makes B1 a controlled analogue of slice-based LLM evaluation: each structure is an observer-defined behavioral slice, but unlike Pythia, we can intervene on data and component availability.

## 4. Why the five structure classes are mandatory

| Class | Function in design | Threat it addresses |
|---|---|---|
| Atomic | Defines the parallel-rate baseline | Without atomics, composite timing cannot be compared against a no-dependency rate model |
| True composite | Candidate dependency site | Tests whether formal composition produces residuals or causal sensitivity |
| Shortcut/no-reuse control | Formally resembles dependency but can be solved without the component | Rules out inferring neural reuse from formal graph structure alone |
| Surface-overlap control | Shares tokens/template/length without the computation | Rules out surface familiarity or prompt overlap |
| Same-operation unrelated control | Same broad operation family, different exact component | Separates exact-component dependency from operation-family transfer |
| Different-operation matched control | Matched difficulty/frequency/length but different operation | Rules out generic training budget and task difficulty effects |

The same-operation control is especially important. Our H3 results showed that some apparent component effects disappear once same-operation transfer is controlled.

## 5. Why H1/H2/H3 are staged

### H1: ordering and sign stability

H1 asks whether structural properties are associated with acquisition order. It does not imply causality. It establishes that the controlled substrate has a meaningful implicit curriculum.

### H2: atomic parallel-null and residuals

H2 fits acquisition predictors on atomics, then predicts composites. Composites with large residuals are candidates where the rate-only account may fail. H2 is observational and explicitly does not prove dependency.

### H3: interventions

H3 manipulates the component and compares against same-operation, different-operation, fake, and surface controls. Only H3 can support a controlled causal statement, and only for the tested pair/component.

This staging is a contribution in itself: it prevents the common overinterpretation that composite-after-component order alone establishes developmental dependency.

## 6. What current results imply about task-design validity

The task design has already exposed three distinct mechanisms:

1. **Localized exact-component sensitivity**: `A02_substitute → C06` under exact pretraining and strong corruption.
2. **Weak/nonuniform formal dependency**: `A00_copy → C06` does not show the same robust effect.
3. **Operation-family transfer/saturation**: `A04_reverse → C07` is matched by a same-operation reverse control; `A03_copy → C07` is negative.

This is a positive sign for validity: the benchmark does not force every formal component to look causal. It can distinguish exact dependency, operation-family transfer, and negative cases.

## 7. Current limitations and how they affect claims

| Limitation | Consequence | Mitigation |
|---|---|---|
| One B1 family is currently the main family | Positive H3 may be family-specific | Replicate on a second generated B1 family |
| H3 positive result is one pair/component | No universal dependency claim | Frame as localized dependency site |
| Token accuracy is primary metric | Exact-match claims remain weaker | Report exact match and loss as secondary metrics |
| Control matching is imperfect | Some effects may be operation/difficulty confounded | Use same-operation and different-operation controls; add mediator diagnostics |
| No real LLM interventions | No causal LLM claim | Pythia stage is observational/corroborative |

## 8. Thesis-safe task-design claim

A safe claim is:

> The B1 sequence-DSL task design provides a controlled transformer setting in which structural predictors, atomic parallel-rate residuals, and matched interventions can be evaluated separately. The design is strong enough to show that apparent compositional acquisition decomposes into multiple mechanisms: exact-component sensitivity, operation-family transfer, and weak/negative formal dependencies.

An unsafe claim is:

> Because B1 is a transformer sequence task, its causal results directly describe Pythia or real LLM pretraining.

