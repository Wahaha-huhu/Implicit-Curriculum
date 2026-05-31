# Pythia H2-ready observational slice plan

The first Pythia bridge runs showed that top-1 accuracy is too harsh and that the easy calibration suite has too few atomic slices for primitive-to-composite residual analysis. v2.7 expands the observational bridge with a larger multiple-choice slice suite.

## Purpose

The goal is not to establish causal dependency in Pythia. The goal is to test whether checkpointed LMs show observational H1/H2-like signatures analogous to the controlled B1 framework:

- primitive/atomic slice movement across checkpoints;
- composite slice movement across checkpoints;
- structural correlations with frequency/difficulty proxies;
- composite residuals relative to a primitive-slice predictor;
- descriptive component/composite coupling.

## Claim boundary

A positive Pythia result can only be described as observational consistency with the controlled framework. It cannot establish H3 causal dependency because pretraining is not intervened on.

## Readiness criteria

A Pythia run becomes H2-ready when at least one continuous metric has:

- enough atomic slices;
- enough composite slices;
- non-flat movement in several atomics;
- non-flat movement in several composites;
- valid primitive-to-composite residual rows.

If these criteria fail, the Pythia run remains calibration-only.
