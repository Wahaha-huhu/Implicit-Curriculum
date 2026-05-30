# Sparse parity backend report

This is B2: a quanta-comparable multitask sparse-parity backend.
It is intended as a baseline where frequency and parity degree should dominate acquisition timing.

Passed design diagnostics: **True**
n_tasks: `24`
n_bits: `40`
frequency_mode: `zipf`
degrees: `(3, 5)`

## Key diagnostics
- design_condition_number: `1.054`
- vif_frequency: `1.003`
- vif_reference_learnability: `1.003`
- formal_utility: `not identifiable / absent in B2 baseline`

## How to use
Use `structure_table.csv` with the existing `run_h1_ordering_pilot` command and `--model mlp`.
This backend has no formal composites by default, so it is for H1/H2/quanta-baseline checks rather than H3 dependency claims.