# H3 readiness and threshold-sensitivity plan

Family 2 showed that the largest H2 residuals can select composites that are too hard to evaluate under the default H3 threshold. This does not refute dependency; it means the candidate is outside the measurable regime.

From v2.1 onward, H3 candidate selection should combine:

1. positive H2 residual;
2. non-near-random final metric in H1/H3 pilot runs;
3. nonzero acquisition at lower token-accuracy thresholds such as 0.3, 0.4, or 0.5;
4. enough headroom for exact-component interventions to improve or degrade the composite;
5. matched same-operation and different-operation controls.

Interpretation:

- Positive at 0.7 and final/AUC: clear acquisition-level effect.
- Positive only at 0.3/0.4: subthreshold learning-shift evidence.
- No threshold contrast but final/AUC shifts: continuous learning effect, not acquisition.
- Near-random final metrics everywhere: non-informative hard-composite failure.
