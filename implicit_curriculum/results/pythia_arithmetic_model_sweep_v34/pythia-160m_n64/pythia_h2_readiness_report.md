# Pythia H2-readiness analysis

This report checks whether an observational Pythia run has enough primitive and composite slice movement for H2-style residual analysis.

- metrics analyzed: `accuracy, mean_correct_margin, mean_correct_mrr, mean_logprob_correct, mean_logprob_margin`
- movement threshold: `0.02`
- minimum atomic slices: `8`
- minimum composite slices: `4`

## Metric readiness
- `accuracy`: h2_ready=True, atomic=12, composite=10, moving_atomic=5, moving_composite=5, mean_atomic_delta=-0.005, mean_composite_delta=-0.016
- `mean_correct_margin`: h2_ready=True, atomic=12, composite=10, moving_atomic=12, moving_composite=10, mean_atomic_delta=-1.153, mean_composite_delta=-1.225
- `mean_correct_mrr`: h2_ready=False, atomic=12, composite=10, moving_atomic=3, moving_composite=6, mean_atomic_delta=-0.003, mean_composite_delta=-0.004
- `mean_logprob_correct`: h2_ready=True, atomic=12, composite=10, moving_atomic=12, moving_composite=10, mean_atomic_delta=7.074, mean_composite_delta=7.273
- `mean_logprob_margin`: h2_ready=True, atomic=12, composite=10, moving_atomic=12, moving_composite=10, mean_atomic_delta=1.906, mean_composite_delta=1.737

## Decision
- H2-ready metrics: `accuracy, mean_correct_margin, mean_logprob_correct, mean_logprob_margin`

If no metric is H2-ready, use the run as calibration only. If one or more continuous metrics are H2-ready, analyze primitive-to-composite residuals using `analyze_pythia_continuous_scores` with that metric and keep the claim observational.
