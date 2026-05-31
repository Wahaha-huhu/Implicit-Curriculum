# Pythia continuous-score observational bridge plan

The first Pythia-style bridge runs showed that top-1 multiple-choice accuracy is too brittle for a small Pythia-70M pilot: slices may move below threshold without becoming acquired. This document records the v2.6 calibration addition.

## What v2.6 measures

For each slice and checkpoint, future runner outputs include:

- top-1 accuracy;
- mean log probability of the correct option;
- correct-option margin: correct log probability minus best incorrect log probability;
- mean rank of the correct option;
- mean reciprocal rank of the correct option.

The continuous analyzer summarizes each metric by:

- initial value;
- final value;
- final-minus-initial improvement;
- AUC over checkpoints;
- max/min over checkpoints;
- H1-like correlations with structural proxies;
- H2-like composite residuals relative to atomic slices;
- composite-vs-component descriptive coupling.

## Claim boundary

Continuous-score movement is observational calibration evidence only. It can show that the correct option becomes more competitive over checkpoints, but it cannot establish causal dependency. It should be used to select better Pythia slices/checkpoints before any thesis-level observational comparison.

## Current expected use

1. Reanalyze existing Pythia pilot outputs using metrics already present, especially accuracy and correct log probability.
2. Rerun future Pythia pilots with v2.6 so correct margin and rank are recorded.
3. Prefer slices that show nonzero continuous improvement without saturation.
4. Only then attempt H1/H2-like observational comparisons.
