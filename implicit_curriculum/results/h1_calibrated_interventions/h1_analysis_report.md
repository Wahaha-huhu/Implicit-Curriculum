# Generated-family pilot analysis report

Chosen component: `A07_bit_10`
Composite targets: `C05_and_07_05`
Controls: `U03_and_bits_37_42, K01_shortcut_for_02_bit46, S02_surface_xor_8_39`

## Baseline acquisition coverage

- n baseline tasks: `34`
- mean acquisition rate across tasks: `0.253`

## Ordering summary

- all / frequency: time-Spearman=-0.339, time-sign=True, final-metric-Spearman=0.260, final-sign=True
- all / reference_learnability: time-Spearman=0.480, time-sign=True, final-metric-Spearman=-0.533, final-sign=True
- all / formal_utility: time-Spearman=-0.167, time-sign=True, final-metric-Spearman=0.213, final-sign=True
- atomic / frequency: time-Spearman=-0.418, time-sign=True, final-metric-Spearman=0.436, final-sign=True
- atomic / reference_learnability: time-Spearman=0.634, time-sign=True, final-metric-Spearman=-0.713, final-sign=True
- atomic / formal_utility: time-Spearman=0.023, time-sign=False, final-metric-Spearman=0.026, final-sign=True
- atomic_composite / frequency: time-Spearman=-0.409, time-sign=True, final-metric-Spearman=0.352, final-sign=True
- atomic_composite / reference_learnability: time-Spearman=0.559, time-sign=True, final-metric-Spearman=-0.619, final-sign=True
- atomic_composite / formal_utility: time-Spearman=-0.157, time-sign=True, final-metric-Spearman=0.243, final-sign=True

## Intervention contrasts

- C05_and_07_05: upweight_component vs upweight_unrelated_matched strict Δacq=-27904.0 (n=4), censored Δacq=-29491.2 (n=5), strict-rate=1.00, censored-rate=1.00, Δfinal=0.038
- C05_and_07_05: upweight_component vs upweight_fake_component strict Δacq=-24960.0 (n=4), censored Δacq=-27545.6 (n=5), strict-rate=1.00, censored-rate=1.00, Δfinal=0.082
- C05_and_07_05: upweight_component vs upweight_surface_control strict Δacq=-25856.0 (n=2), censored Δacq=-33177.6 (n=5), strict-rate=1.00, censored-rate=1.00, Δfinal=0.051
- C05_and_07_05: corrupt_component vs corrupt_unrelated_matched strict Δacq=nan (n=0), censored Δacq=12902.4 (n=5), strict-rate=nan, censored-rate=1.00, Δfinal=-0.188
- C05_and_07_05: delay_component vs delay_unrelated_matched strict Δacq=0.0 (n=1), censored Δacq=6041.6 (n=5), strict-rate=0.00, censored-rate=0.80, Δfinal=-0.032

## Component-vs-control diagnostics

- mean component-minus-controls gradient cosine: `0.3593`
- mean component-minus-controls linear CKA: `0.2757`

## Decision rule

GREEN requires nontrivial acquisition coverage, expected ordering signs on baseline atomics/composites, and component interventions/diagnostics that beat fake, surface, and unrelated controls. YELLOW means redesign or tune before scaling. RED means fix the task family or analysis gate.