# B1 mediator diagnostics run report

This run logs leading-indicator gradient and representation diagnostics for selected H3 pairs.
It is mechanistic corroboration only; it does not by itself establish causality.

## Setup
- pairs: `4`
- seeds: `0, 1, 2, 3, 4`
- probe_fractions: `0.0, 0.05, 0.1, 0.2, 0.4, 1.0`
- param_subset: `last_block_ln_head`
- task-stat rows: `510`
- pair-stat rows: `600`

## Pairs
- `A02_substitute` → `C06_reverse_then_substitute_02_00`; same-op=`U00_unrelated_substitute`, diff-op=`A07_reverse`
- `A00_copy` → `C06_reverse_then_substitute_02_00`; same-op=`A06_copy`, diff-op=`U02_unrelated_substitute`
- `A04_reverse` → `C07_substitute_then_reverse_04_03`; same-op=`A07_reverse`, diff-op=`U02_unrelated_substitute`
- `A03_copy` → `C07_substitute_then_reverse_04_03`; same-op=`A06_copy`, diff-op=`U01_unrelated_substitute`