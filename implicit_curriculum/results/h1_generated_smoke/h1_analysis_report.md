# Generated-family pilot analysis report

Chosen component: `A05_and_bits_5_25`
Composite targets: `C02_and_05_09, C03_and_04_05, C06_and_05_09`
Controls: `U02_and_bits_10_16, K01_shortcut_for_09_bit45, S00_surface_xor_12_45`

## Baseline acquisition coverage

- n baseline tasks: `32`
- mean acquisition rate across tasks: `0.000`

## Ordering summary

- all / frequency: time-Spearman=nan, time-sign=nan, final-metric-Spearman=nan, final-sign=nan
- all / reference_learnability: time-Spearman=nan, time-sign=nan, final-metric-Spearman=nan, final-sign=nan
- all / formal_utility: time-Spearman=nan, time-sign=nan, final-metric-Spearman=nan, final-sign=nan
- atomic / frequency: time-Spearman=nan, time-sign=nan, final-metric-Spearman=nan, final-sign=nan
- atomic / reference_learnability: time-Spearman=nan, time-sign=nan, final-metric-Spearman=nan, final-sign=nan
- atomic / formal_utility: time-Spearman=nan, time-sign=nan, final-metric-Spearman=nan, final-sign=nan
- atomic_composite / frequency: time-Spearman=nan, time-sign=nan, final-metric-Spearman=nan, final-sign=nan
- atomic_composite / reference_learnability: time-Spearman=nan, time-sign=nan, final-metric-Spearman=nan, final-sign=nan
- atomic_composite / formal_utility: time-Spearman=nan, time-sign=nan, final-metric-Spearman=nan, final-sign=nan

## Intervention contrasts

- C02_and_05_09: upweight_component vs upweight_unrelated_matched mean Δacq=nan, expected-direction-rate=nan
- C02_and_05_09: upweight_component vs upweight_fake_component mean Δacq=nan, expected-direction-rate=nan
- C02_and_05_09: upweight_component vs upweight_surface_control mean Δacq=nan, expected-direction-rate=nan
- C02_and_05_09: corrupt_component vs corrupt_unrelated_matched mean Δacq=nan, expected-direction-rate=nan
- C02_and_05_09: delay_component vs delay_unrelated_matched mean Δacq=nan, expected-direction-rate=nan
- C03_and_04_05: upweight_component vs upweight_unrelated_matched mean Δacq=nan, expected-direction-rate=nan
- C03_and_04_05: upweight_component vs upweight_fake_component mean Δacq=nan, expected-direction-rate=nan
- C03_and_04_05: upweight_component vs upweight_surface_control mean Δacq=nan, expected-direction-rate=nan
- C03_and_04_05: corrupt_component vs corrupt_unrelated_matched mean Δacq=nan, expected-direction-rate=nan
- C03_and_04_05: delay_component vs delay_unrelated_matched mean Δacq=nan, expected-direction-rate=nan
- C06_and_05_09: upweight_component vs upweight_unrelated_matched mean Δacq=nan, expected-direction-rate=nan
- C06_and_05_09: upweight_component vs upweight_fake_component mean Δacq=nan, expected-direction-rate=nan
- C06_and_05_09: upweight_component vs upweight_surface_control mean Δacq=nan, expected-direction-rate=nan
- C06_and_05_09: corrupt_component vs corrupt_unrelated_matched mean Δacq=nan, expected-direction-rate=nan
- C06_and_05_09: delay_component vs delay_unrelated_matched mean Δacq=nan, expected-direction-rate=nan

## Component-vs-control diagnostics

- mean component-minus-controls gradient cosine: `1.1639`
- mean component-minus-controls linear CKA: `-0.0035`

## Decision rule

GREEN requires nontrivial acquisition coverage, expected ordering signs on baseline atomics/composites, and component interventions/diagnostics that beat fake, surface, and unrelated controls. YELLOW means redesign or tune before scaling. RED means fix the task family or analysis gate.