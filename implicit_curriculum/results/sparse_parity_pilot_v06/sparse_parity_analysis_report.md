# Sparse parity pilot analysis report

This is B2-specific analysis. It intentionally ignores components, controls, and formal utility because sparse parity is the quanta-comparable baseline, not a dependency test.

Metric: `balanced_accuracy`

## Threshold sensitivity

- threshold `0.75`: acquisition_rate=0.242, time-Spearman(freq)=-0.684, time-Spearman(degree)=0.203, final-Spearman(freq)=0.471, final-Spearman(degree)=-0.451
- threshold `0.85`: acquisition_rate=0.242, time-Spearman(freq)=-0.710, time-Spearman(degree)=0.158, final-Spearman(freq)=0.471, final-Spearman(degree)=-0.451
- threshold `0.9`: acquisition_rate=0.233, time-Spearman(freq)=-0.701, time-Spearman(degree)=0.250, final-Spearman(freq)=0.471, final-Spearman(degree)=-0.451

## Final metric by degree

- degree `2.0`: n=60, mean_final_metric=0.698, mean_final_loss=0.443
- degree `3.0`: n=60, mean_final_metric=0.508, mean_final_loss=0.690

## Decision rule

GREEN requires nontrivial acquisition coverage under at least one threshold, frequency/final-metric signs in the expected direction, and degree making harder parities worse or later. If acquisition remains near zero, tune degree/budget before using B2 as a quanta baseline.