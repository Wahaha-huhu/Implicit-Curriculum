# H3 evidence synthesis

This synthesis combines pair-specific B1 H3 intervention runs. It is intended for thesis writing and claim calibration. It does not create new causal evidence beyond the underlying runs; it records which claims the existing runs can and cannot support.

## Inputs
- `results/b1_h3_row0_strong_v12`
- `results/b1_h3_opfamily_row1_v11`
- `results/b1_h3_secondary_v15_row0_A04_reverse_to_C07_substitute_then_reverse_04_03_strong`
- `results/b1_h3_secondary_v15_row1_A03_copy_to_C07_substitute_then_reverse_04_03_strong`

## Pair-level evidence matrix
- `A02_substitute` → `C06_reverse_then_substitute_02_00`: **positive_exact_component_pair_specific**; primary signal=`pretrain_exact_component`; scope: supports localized exact-component causal sensitivity
- `A00_copy` → `C06_reverse_then_substitute_02_00`: **weak_or_negative**; primary signal=`corrupt_exact_component`; scope: negative or weak evidence for exact-component dependency
- `A04_reverse` → `C07_substitute_then_reverse_04_03`: **operation_family_transfer**; primary signal=`none_or_weak`; scope: supports operation-family transfer rather than exact-component dependency
- `A03_copy` → `C07_substitute_then_reverse_04_03`: **weak_or_negative**; primary signal=`none_or_weak`; scope: negative or weak evidence for exact-component dependency

## Composite-level interpretation
- `C06_reverse_then_substitute_02_00`: verdict=`has_localized_exact_component_site`, tested=2, positive_exact=1, operation_family=0, weak_or_negative=1
- `C07_substitute_then_reverse_04_03`: verdict=`operation_family_or_saturation`, tested=2, positive_exact=0, operation_family=1, weak_or_negative=1

## Overall interpretation
The current H3 evidence supports a heterogeneous causal picture. H2 residuals are useful for selecting candidate composites, but a residual is not itself evidence of exact-component dependency. In the tested B1 family, one substitution-side component of C06 shows localized exact-component sensitivity, while other listed formal components are weak, negative, or better explained by operation-family transfer/saturation.

## Thesis-safe wording
The intervention results refine, rather than simply confirm, the developmental-dependency hypothesis: some composite residuals can correspond to exact-component causal sensitivity, but this is not uniform across all formal components. The safe thesis claim is localized and controlled-setting-specific; it should not be stated as a universal mechanism of LLM training.

## Claim boundary table
- **H3 residuals imply universal exact-component dependency** — not supported. Only one tested component-composite pair is positive; several formal components are weak, negative, or operation-family-level.
- **H3 residuals identify useful candidate intervention sites** — supported as pilot evidence. H2-selected C06 produced one localized exact-component positive pair; C07 produced boundary/negative evidence.
- **Exact-component dependency is heterogeneous across components/composites** — supported in controlled B1 pilot. A02→C06 positive; A00→C06 weak/mixed; C07 rows operation-family/negative.
- **Controlled B1 evidence generalizes causally to real LLMs** — not tested. No real LLM interventions have been run; any LLM claim must remain observational/corroborative.
