# B1 mediator diagnostics run report

This run logs leading-indicator gradient and representation diagnostics for selected H3 pairs.
It is mechanistic corroboration only; it does not by itself establish causality.

## Setup
- pairs: `4`
- seeds: `0, 1, 2, 3, 4`
- probe_fractions: `0.0, 0.05, 0.1, 0.2, 0.4, 1.0`
- param_subset: `last_block_ln_head`
- task-stat rows: `480`
- pair-stat rows: `600`

## Pairs
- `A07_reverse` → `C03_reverse_then_substitute_07_02`; same-op=`A01_reverse`, diff-op=`U01_unrelated_substitute`
- `A02_substitute` → `C03_reverse_then_substitute_07_02`; same-op=`U00_unrelated_substitute`, diff-op=`A03_copy`
- `A05_substitute` → `C06_reverse_then_substitute_05_07`; same-op=`U01_unrelated_substitute`, diff-op=`A04_reverse`
- `A07_reverse` → `C06_reverse_then_substitute_05_07`; same-op=`A01_reverse`, diff-op=`U01_unrelated_substitute`