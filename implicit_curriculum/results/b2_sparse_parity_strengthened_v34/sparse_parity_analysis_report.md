# Sparse parity pilot analysis report

This is B2-specific analysis. It intentionally ignores components, controls, and formal utility because sparse parity is the quanta-comparable baseline, not a dependency test.

Metric: `balanced_accuracy`

## Threshold sensitivity

- threshold `0.65`: acquisition_rate=0.503, time-Spearman(freq)=-0.187, time-Spearman(degree)=0.775, final-Spearman(freq)=0.430, final-Spearman(degree)=-0.702
- threshold `0.75`: acquisition_rate=0.483, time-Spearman(freq)=-0.202, time-Spearman(degree)=0.753, final-Spearman(freq)=0.430, final-Spearman(degree)=-0.702
- threshold `0.85`: acquisition_rate=0.467, time-Spearman(freq)=-0.232, time-Spearman(degree)=0.732, final-Spearman(freq)=0.430, final-Spearman(degree)=-0.702
- threshold `0.9`: acquisition_rate=0.464, time-Spearman(freq)=-0.243, time-Spearman(degree)=0.733, final-Spearman(freq)=0.430, final-Spearman(degree)=-0.702

## Final metric by degree

- degree `1.0`: n=120, mean_final_metric=0.998, mean_final_loss=0.006
- degree `2.0`: n=120, mean_final_metric=0.677, mean_final_loss=0.484
- degree `3.0`: n=120, mean_final_metric=0.555, mean_final_loss=0.633

## Decision rule

GREEN requires nontrivial acquisition coverage under at least one threshold, frequency/final-metric signs in the expected direction, and degree making harder parities worse or later. If acquisition remains near zero, tune degree/budget before using B2 as a quanta baseline.