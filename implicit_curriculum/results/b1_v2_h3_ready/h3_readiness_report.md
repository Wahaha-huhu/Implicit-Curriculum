# B1 H3-readiness selection report

This report combines H2 residuals with H1 learning/readiness metrics. It is designed to avoid selecting composites that are maximally delayed but too hard to test by intervention.

Metric: `token_accuracy`
Readiness threshold column: `acq_rate_t0p5`

## Composite readiness summary
- candidate composites: `2`
- H3-ready composites: `0`
- min_final: `0.15`; max_final: `0.9`; min_acq_rate: `0.05`; min_residual: `0.0`

## Top composites
- `C03_reverse_then_substitute_07_02`: ready=False, score=2.229, residual=-1.250, final=0.739, acq_rate_t0p5=0.900
- `C06_reverse_then_substitute_05_07`: ready=False, score=2.221, residual=-1.250, final=0.742, acq_rate_t0p5=0.900

## Top pair candidates
- `A07_reverse` → `C03_reverse_then_substitute_07_02`: ready=False, score=2.229, residual=-1.250
- `A02_substitute` → `C03_reverse_then_substitute_07_02`: ready=False, score=2.229, residual=-1.250
- `A07_reverse` → `C03_reverse_then_substitute_07_02`: ready=False, score=2.229, residual=-1.277
- `A02_substitute` → `C03_reverse_then_substitute_07_02`: ready=False, score=2.229, residual=-1.277
- `A07_reverse` → `C03_reverse_then_substitute_07_02`: ready=False, score=2.229, residual=-1.295
- `A02_substitute` → `C03_reverse_then_substitute_07_02`: ready=False, score=2.229, residual=-1.295
- `A07_reverse` → `C03_reverse_then_substitute_07_02`: ready=False, score=2.229, residual=-1.368
- `A02_substitute` → `C03_reverse_then_substitute_07_02`: ready=False, score=2.229, residual=-1.368
- `A07_reverse` → `C03_reverse_then_substitute_07_02`: ready=False, score=2.229, residual=-1.419
- `A02_substitute` → `C03_reverse_then_substitute_07_02`: ready=False, score=2.229, residual=-1.419
- `A05_substitute` → `C06_reverse_then_substitute_05_07`: ready=False, score=2.221, residual=-1.250
- `A07_reverse` → `C06_reverse_then_substitute_05_07`: ready=False, score=2.221, residual=-1.250

## Interpretation rule
Use this selector before expensive H3 runs. Very large residuals with near-zero final metric or zero low-threshold acquisition should be considered hard-composite failures rather than good intervention candidates.