# Generated-family pilot analysis report

Chosen component: `A05_and_bits_5_25`
Composite targets: `C02_and_05_09, C03_and_04_05, C06_and_05_09`
Controls: `U02_and_bits_10_16, K01_shortcut_for_09_bit45, S00_surface_xor_12_45`

## Baseline acquisition coverage

- n baseline tasks: `32`
- mean acquisition rate across tasks: `0.237`

## Ordering summary

- all / frequency: time-Spearman=-0.499, time-sign=True, final-metric-Spearman=0.605, final-sign=True
- all / reference_learnability: time-Spearman=0.428, time-sign=True, final-metric-Spearman=-0.329, final-sign=True
- all / formal_utility: time-Spearman=-0.250, time-sign=True, final-metric-Spearman=0.264, final-sign=True
- atomic / frequency: time-Spearman=-0.359, time-sign=True, final-metric-Spearman=0.045, final-sign=True
- atomic / reference_learnability: time-Spearman=0.424, time-sign=True, final-metric-Spearman=-0.652, final-sign=True
- atomic / formal_utility: time-Spearman=-0.357, time-sign=True, final-metric-Spearman=0.318, final-sign=True
- atomic_composite / frequency: time-Spearman=-0.366, time-sign=True, final-metric-Spearman=0.367, final-sign=True
- atomic_composite / reference_learnability: time-Spearman=0.461, time-sign=True, final-metric-Spearman=-0.426, final-sign=True
- atomic_composite / formal_utility: time-Spearman=-0.396, time-sign=True, final-metric-Spearman=0.275, final-sign=True

## Intervention contrasts

No intervention contrasts were available. Run with intervention conditions to populate this section.

## Component-vs-control diagnostics

- mean component-minus-controls gradient cosine: `0.4395`
- mean component-minus-controls linear CKA: `0.7867`

## Decision rule

GREEN requires nontrivial acquisition coverage, expected ordering signs on baseline atomics/composites, and component interventions/diagnostics that beat fake, surface, and unrelated controls. YELLOW means redesign or tune before scaling. RED means fix the task family or analysis gate.