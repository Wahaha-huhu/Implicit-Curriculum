# B1 H3 readiness-aware operation-family plan

This plan is generated from the H3-readiness selector, not from residual magnitude alone. It is meant to avoid the family-2 failure mode where the largest residual composites were too hard for useful intervention contrasts.

- ready pair selection: `results/family_replication_01/h3_readiness_v21/h3_ready_pair_selection.csv`
- input rows: `10`
- rows after filtering: `4`
- planned rows: `2`
- selected composites: `C06_reverse_then_substitute_01_05`
- condition set: `strong`

## Planned pairs
- row `0`: `A01_reverse` → `C06_reverse_then_substitute_01_05`; same-op=`A07_reverse`, diff-op=`U00_unrelated_substitute`, ready=`True`, score=7.295, residual=4.960, final=0.401
- row `1`: `A05_substitute` → `C06_reverse_then_substitute_01_05`; same-op=`U01_unrelated_substitute`, diff-op=`A03_copy`, ready=`True`, score=7.295, residual=4.960, final=0.401

## Recommended condition set
`baseline pretrain_component pretrain_same_operation_unrelated pretrain_different_operation_matched corrupt_component_strong corrupt_same_operation_unrelated_strong corrupt_different_operation_matched_strong delay_component_strong delay_same_operation_unrelated_strong delay_different_operation_matched_strong`

## Interpretation rule
A readiness-aware plan can still produce negative H3 results. Its purpose is only to ensure the candidate is measurable enough that a negative result is informative rather than a hard-composite failure.