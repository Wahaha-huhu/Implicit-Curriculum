# Pythia residual refinement plan

This note records the next observational bridge step after the H2-ready slice suite.
The goal is not to make causal claims, but to decide whether Pythia slice residuals are stable enough to include as observational evidence.

## Motivation

The v2.7 Pythia H2-ready suite produced valid primitive-to-composite residuals for multiple continuous metrics. However, metric-specific residuals can disagree. A composite that underperforms under accuracy but outperforms under log-probability should not be treated as a robust residual site.

## v2.9 refinement

The residual-refinement analysis summarizes:

1. residual agreement across metrics for each composite;
2. composite-family summaries, e.g. arithmetic vs word vs retrieval;
3. component-coupling agreement across metrics;
4. claim boundaries for using Pythia as observational bridge evidence.

## Claim boundary

A Pythia residual is thesis-useful only if it is stable across several continuous metrics and ideally across model sizes or checkpoint densities. It remains observational. It does not establish exact-component dependency because no pretraining intervention is performed.
