# Mediator Diagnostic Plan — v1.8

This note defines the next mechanistic test after the H3 evidence synthesis.

## Motivation

The current H3 evidence supports a heterogeneous causal picture. One pair, `A02_substitute → C06_reverse_then_substitute_02_00`, shows localized exact-component causal sensitivity, while other formal component-composite pairs are weak, negative, or operation-family-level. The next question is whether this pair-specific causal pattern has a corresponding *early mediator signature*.

## Core question

Do H3-positive pairs show stronger leading-indicator coupling than weak/negative pairs?

The intended comparison is:

| Pair | H3 status | Mediator prediction |
|---|---|---|
| `A02_substitute → C06` | positive exact-component pair-specific | exact component should show higher early gradient cosine and/or representation CKA with C06 than same-operation and different-operation controls |
| `A00_copy → C06` | weak/mixed | exact component should not strongly separate from controls |
| `A04_reverse → C07` | operation-family transfer | exact component and same-operation reverse control should look similar |
| `A03_copy → C07` | weak/negative | exact component should not separate from controls |

## Methodology

The v1.8 mediator diagnostics train a baseline B1 sequence-transformer run and probe selected pairs at fixed early checkpoint fractions. For each task, the runner computes:

- gradient norm;
- gradient noise RMS;
- gradient SNR;
- within-task gradient alignment;
- hidden-state representations on fixed probe batches.

For each component/control → composite pair, it computes:

- cross-task gradient cosine;
- source/target gradient norms;
- linear CKA between hidden representations.

The primary interpretation window is early training, e.g. checkpoint fraction <= 0.20. This follows the leading-indicator rule: mediators should predict or explain later acquisition rather than being measured only after the composite has already been learned.

## Claim boundary

Mediator diagnostics are mechanistic corroboration, not standalone causal evidence. A positive mediator result strengthens the gradient-mediated interpretation of H3; it does not replace intervention evidence.

## Expected thesis use

If the positive H3 pair shows stronger early exact-component coupling than weak/negative pairs, this can support the claim that localized dependency sites are accompanied by measurable gradient/representation coupling. If it does not, the causal result remains behavioral/interventional but the proposed gradient-mediated explanation needs revision.
