# Pythia-style observational slice suite

This suite is a small observational bridge from the controlled B1 experiments to checkpointed language models. It is not a causal intervention benchmark.

- slices: `12`
- examples: `768`
- examples per slice: `64`

## Design

The suite contains atomic, composite, and surface-control behavioral slices across arithmetic, syntax, retrieval, and string-operation families. Each example is multiple-choice so checkpoint evaluation can use choice log probabilities rather than generation.

## Claim boundary

This suite can support H1/H2-style observational signatures: acquisition order, predictor correlations, and primitive-to-composite residuals. It cannot support H3 causal dependency because model pretraining is not intervened on.
