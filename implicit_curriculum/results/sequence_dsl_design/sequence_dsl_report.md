# Sequence DSL backend report

This is B1: the primary controlled sequence/transformer substrate skeleton.
The current implementation is a smoke-testable version of the stronger operational design.

Passed design diagnostics: **True**
n_tasks: `20`
vocab_size: `68`
input_len: `8`

## Key diagnostics
- design_condition_number: `1.302`
- vif_frequency: `1.065`
- vif_reference_learnability: `1.06`
- vif_formal_utility: `1.057`

## Interpretation
This backend is now the preferred target for the main controlled experiments. B0 Boolean remains a debugging sandbox; B2 sparse parity is the quanta-comparable baseline.