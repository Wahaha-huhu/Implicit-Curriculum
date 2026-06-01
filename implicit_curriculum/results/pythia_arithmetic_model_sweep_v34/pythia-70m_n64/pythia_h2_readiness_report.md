# Pythia H2-readiness analysis

This report checks whether an observational Pythia run has enough primitive and composite slice movement for H2-style residual analysis.

- metrics analyzed: `accuracy, mean_correct_margin, mean_correct_mrr, mean_logprob_correct, mean_logprob_margin`
- movement threshold: `0.02`
- minimum atomic slices: `8`
- minimum composite slices: `4`

## Metric readiness
- `accuracy`: h2_ready=True, atomic=12, composite=10, moving_atomic=9, moving_composite=7, mean_atomic_delta=-0.012, mean_composite_delta=0.016
- `mean_correct_margin`: h2_ready=True, atomic=12, composite=10, moving_atomic=12, moving_composite=10, mean_atomic_delta=0.086, mean_composite_delta=0.278
- `mean_correct_mrr`: h2_ready=True, atomic=12, composite=10, moving_atomic=8, moving_composite=6, mean_atomic_delta=-0.007, mean_composite_delta=0.015
- `mean_logprob_correct`: h2_ready=True, atomic=12, composite=10, moving_atomic=12, moving_composite=10, mean_atomic_delta=6.240, mean_composite_delta=6.503
- `mean_logprob_margin`: h2_ready=True, atomic=12, composite=10, moving_atomic=12, moving_composite=10, mean_atomic_delta=-0.016, mean_composite_delta=-0.082

## Decision
- H2-ready metrics: `accuracy, mean_correct_margin, mean_correct_mrr, mean_logprob_correct, mean_logprob_margin`

If no metric is H2-ready, use the run as calibration only. If one or more continuous metrics are H2-ready, analyze primitive-to-composite residuals using `analyze_pythia_continuous_scores` with that metric and keep the claim observational.
