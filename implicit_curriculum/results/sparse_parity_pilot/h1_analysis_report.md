# Generated-family pilot analysis report

Chosen component: `P00_parity_d3_1_15_16`
Composite targets: ``
Controls: `P00_parity_d3_1_15_16, P00_parity_d3_1_15_16, P00_parity_d3_1_15_16`

## Baseline acquisition coverage

- n baseline tasks: `24`
- mean acquisition rate across tasks: `0.008`

## Ordering summary

- all / frequency: time-Spearman=-0.152, time-sign=True, final-metric-Spearman=0.096, final-sign=True
- all / reference_learnability: time-Spearman=0.092, time-sign=True, final-metric-Spearman=-0.082, final-sign=True
- all / formal_utility: time-Spearman=nan, time-sign=nan, final-metric-Spearman=nan, final-sign=nan
- atomic / frequency: time-Spearman=-0.152, time-sign=True, final-metric-Spearman=0.096, final-sign=True
- atomic / reference_learnability: time-Spearman=0.092, time-sign=True, final-metric-Spearman=-0.082, final-sign=True
- atomic / formal_utility: time-Spearman=nan, time-sign=nan, final-metric-Spearman=nan, final-sign=nan
- atomic_composite / frequency: time-Spearman=-0.152, time-sign=True, final-metric-Spearman=0.096, final-sign=True
- atomic_composite / reference_learnability: time-Spearman=0.092, time-sign=True, final-metric-Spearman=-0.082, final-sign=True
- atomic_composite / formal_utility: time-Spearman=nan, time-sign=nan, final-metric-Spearman=nan, final-sign=nan

## Intervention contrasts

No intervention contrasts were available. Run with intervention conditions to populate this section.

## Component-vs-control diagnostics

No gradient/CKA diagnostics were available.

## Decision rule

GREEN requires nontrivial acquisition coverage, expected ordering signs on baseline atomics/composites, and component interventions/diagnostics that beat fake, surface, and unrelated controls. YELLOW means redesign or tune before scaling. RED means fix the task family or analysis gate.