# Pythia H2-readiness analysis

This report checks whether an observational Pythia run has enough primitive and composite slice movement for H2-style residual analysis.

- metrics analyzed: `accuracy, mean_correct_margin, mean_correct_mrr, mean_logprob_correct, mean_logprob_margin`
- movement threshold: `0.02`
- minimum atomic slices: `8`
- minimum composite slices: `4`

## Metric readiness
- `accuracy`: h2_ready=True, atomic=16, composite=10, moving_atomic=12, moving_composite=7, mean_atomic_delta=0.004, mean_composite_delta=-0.013
- `mean_correct_margin`: h2_ready=True, atomic=16, composite=10, moving_atomic=16, moving_composite=10, mean_atomic_delta=-0.396, mean_composite_delta=-0.207
- `mean_correct_mrr`: h2_ready=True, atomic=16, composite=10, moving_atomic=13, moving_composite=9, mean_atomic_delta=-0.010, mean_composite_delta=-0.016
- `mean_logprob_correct`: h2_ready=True, atomic=16, composite=10, moving_atomic=16, moving_composite=10, mean_atomic_delta=8.604, mean_composite_delta=8.807
- `mean_logprob_margin`: h2_ready=True, atomic=16, composite=10, moving_atomic=16, moving_composite=10, mean_atomic_delta=0.707, mean_composite_delta=0.426

## Decision
- H2-ready metrics: `accuracy, mean_correct_margin, mean_correct_mrr, mean_logprob_correct, mean_logprob_margin`

If no metric is H2-ready, use the run as calibration only. If one or more continuous metrics are H2-ready, analyze primitive-to-composite residuals using `analyze_pythia_continuous_scores` with that metric and keep the claim observational.
