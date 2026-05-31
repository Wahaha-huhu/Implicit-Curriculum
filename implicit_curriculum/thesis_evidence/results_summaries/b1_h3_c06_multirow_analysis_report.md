# B1 H3 multi-row summary

This report combines pair-specific H3 analyses. It is intended for thesis evidence tracking: it separates exact-component dependency, operation-family transfer, and weak/negative controls.

## Inputs
- `results/b1_h3_opfamily_row0_v11`
- `results/b1_h3_opfamily_row1_v11`

## Row verdicts
- `A02_substitute` → `C06_reverse_then_substitute_02_00`: verdict=`promising_exact_component_partial`, upweight exact-vs-same rate=0.900, upweight exact-vs-different rate=0.900, corrupt exact-vs-same rate=0.700, delay exact-vs-same rate=0.200
- `A00_copy` → `C06_reverse_then_substitute_02_00`: verdict=`weak_or_negative`, upweight exact-vs-same rate=0.300, upweight exact-vs-different rate=0.500, corrupt exact-vs-same rate=0.700, delay exact-vs-same rate=0.400

## Combined interpretation
The current evidence is component-specific rather than uniformly positive: at least one component shows an exact-component signal, while another component is weak or negative. This supports using H3 to map where dependency holds, not claiming a universal composite dependency mechanism yet.

## Thesis-safe wording
Current H3 evidence should be described as pilot and pair-specific. Do not state that the controlled B1 setting proves developmental dependency until exact-component effects replicate across components/families and at least one model-state intervention agrees.