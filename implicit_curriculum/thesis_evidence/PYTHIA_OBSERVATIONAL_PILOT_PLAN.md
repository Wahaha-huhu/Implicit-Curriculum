# Pythia-style observational pilot plan

This stage is the first bridge from the controlled B1 experiments to checkpointed LLMs. It is deliberately observational: it evaluates behavioral slices across model checkpoints and reuses the H1/H2 analysis logic, but it does not claim causal dependency because we do not intervene on pretraining.

## Purpose

The controlled results imply that acquisition order and residuals are not self-interpreting. The Pythia-style pilot therefore asks whether analogous signatures are observable in checkpointed language models:

1. Do primitive/atomic behavioral slices improve before composite slices?
2. Do structural proxies such as frequency, reference difficulty, and composition depth correlate with acquisition timing?
3. Do composite slices show residuals relative to an atomic predictor fit?
4. Are residuals heterogeneous across task families, as in B1?

## Claim boundary

Allowed claims:

- Pythia-like checkpoints show or do not show H1/H2-like observational signatures.
- Controlled B1 findings inform how to interpret these signatures cautiously.
- Residuals in checkpointed LMs are candidate indicators for further analysis, not causal evidence.

Not allowed claims:

- A slice residual proves developmental dependency in Pythia.
- Primitive-to-composite ordering proves exact component reuse.
- The controlled B1 causal mechanism directly explains real LLM pretraining.

## Initial slice families

The v2.4 pilot suite includes small multiple-choice slices across:

- arithmetic: single-step addition/comparison and add-then-compare;
- syntax: local agreement and agreement with distractors;
- retrieval: key-value retrieval and retrieve-then-compare;
- string operations: copy, reverse, reverse-then-copy;
- surface controls.

These are deliberately small and diagnostic. Later versions should replace or augment them with richer, validated benchmark slices.

## Analysis outputs

The pilot analysis writes:

- `pythia_acquisition_times.csv`
- `pythia_h1_ordering_summary.csv`
- `pythia_h2_composite_residuals.csv`
- `pythia_observational_analysis_report.md`

These outputs should be interpreted alongside the B1 cross-family claim matrix.
