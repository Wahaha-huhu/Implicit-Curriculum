# Sequence DSL backend report

This is B1: the primary controlled sequence/transformer substrate skeleton.
The current implementation is a smoke-testable version of the stronger operational design.

Passed design diagnostics: **True**
n_tasks: `25`
vocab_size: `36`
input_len: `6`

## Key diagnostics
- design_condition_number: `2.645`
- vif_frequency: `2.173`
- vif_reference_learnability: `1.336`
- vif_formal_utility: `2.232`

## Interpretation
This backend is now the preferred target for the main controlled experiments. B0 Boolean remains a debugging sandbox; B2 sparse parity is the quanta-comparable baseline.