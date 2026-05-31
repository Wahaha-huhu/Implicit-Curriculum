# B1 H3-readiness selection report

This report combines H2 residuals with H1 learning/readiness metrics. It is designed to avoid selecting composites that are maximally delayed but too hard to test by intervention.

Metric: `token_accuracy`
Readiness threshold column: `acq_rate_t0p5`

## Composite readiness summary
- candidate composites: `2`
- H3-ready composites: `1`
- min_final: `0.15`; max_final: `0.9`; min_acq_rate: `0.05`; min_residual: `0.0`

## Top composites
- `C06_reverse_then_substitute_01_05`: ready=True, score=7.295, residual=4.960, final=0.401, acq_rate_t0p5=0.333
- `C00_reverse_then_substitute_02_05`: ready=False, score=5.001, residual=5.001, final=0.040, acq_rate_t0p5=0.000

## Top pair candidates
- `A01_reverse` → `C06_reverse_then_substitute_01_05`: ready=True, score=7.295, residual=4.960
- `A05_substitute` → `C06_reverse_then_substitute_01_05`: ready=True, score=7.295, residual=4.960
- `A01_reverse` → `C06_reverse_then_substitute_01_05`: ready=True, score=7.295, residual=4.913
- `A05_substitute` → `C06_reverse_then_substitute_01_05`: ready=True, score=7.295, residual=4.913
- `A02_substitute` → `C00_reverse_then_substitute_02_05`: ready=False, score=5.001, residual=5.001
- `A05_substitute` → `C00_reverse_then_substitute_02_05`: ready=False, score=5.001, residual=5.001
- `A02_substitute` → `C00_reverse_then_substitute_02_05`: ready=False, score=5.001, residual=4.921
- `A05_substitute` → `C00_reverse_then_substitute_02_05`: ready=False, score=5.001, residual=4.921
- `A02_substitute` → `C00_reverse_then_substitute_02_05`: ready=False, score=5.001, residual=4.913
- `A05_substitute` → `C00_reverse_then_substitute_02_05`: ready=False, score=5.001, residual=4.913

## Interpretation rule
Use this selector before expensive H3 runs. Very large residuals with near-zero final metric or zero low-threshold acquisition should be considered hard-composite failures rather than good intervention candidates.