# B1 v2 preregistration: causal census and alignment predictor

Freeze the Exp 2 causal census and Exp 3 alignment-predicts-verdict analysis before running/adding more rows.

## Frozen inputs
- structure_table: `results/b1_v2_h1_shared_sweep/structure_table.csv`
- ready_pair_selection: `results/b1_v2_h3_ready/h3_ready_pair_selection.csv`
- census_plan: `results/b1_v2_causal_census_plan_full/b1_v2_causal_census_plan.csv`

## Census membership rule
Every formal component→composite pair that passes the readiness gate, with non-ready rows excluded as hard-composite/non-learning coverage when requested.

## Control battery
- `exact_component`
- `same_operation_control`
- `different_operation_control`
- `fake_component_control`
- `surface_control`
- `unrelated_matched_displacement_twin`
- `readiness_gate`

## Conditions
Condition set: `full`

```text
baseline upweight_component upweight_same_operation_unrelated upweight_different_operation_matched upweight_fake_component upweight_surface_control delay_component delay_same_operation_unrelated delay_different_operation_matched corrupt_component corrupt_same_operation_unrelated corrupt_different_operation_matched pretrain_component pretrain_same_operation_unrelated pretrain_different_operation_matched corrupt_component_strong corrupt_same_operation_unrelated_strong corrupt_different_operation_matched_strong delay_component_strong delay_same_operation_unrelated_strong delay_different_operation_matched_strong
```

## Verdict rule
- `exact_component_dependency`: Exact component separates from same-operation and different-operation controls, and from fake/surface controls when those rows are available.
- `operation_family_transfer`: Exact separates from different-operation controls but not same-operation controls.
- `difficulty_parallel_or_null`: No exact-component manipulation separates from matched controls.
- `hard_composite_non_learning`: Helpful exact-component interventions fail to make the composite measurable; row is a coverage exclusion.
- `min_direction_rate`: 0.6
- `alpha`: 0.1

## Alignment predictor
- `ground_truth`: census verdicts from Exp 2 intervention rows
- `primary_score`: early exact-minus-control gradient cosine, measured no later than early_max_fraction of training
- `early_max_fraction`: 0.2
- `evaluation`: AUC against exact_component_dependency labels; leave-family-out when family_id is present, otherwise pair-level AUC only.

## Planned census rows
Rows frozen: `4`
- row `0`: `A07_reverse` → `C03_reverse_then_substitute_07_02`; ready=`False`; battery_complete=`True`
- row `1`: `A02_substitute` → `C03_reverse_then_substitute_07_02`; ready=`False`; battery_complete=`True`
- row `2`: `A05_substitute` → `C06_reverse_then_substitute_05_07`; ready=`False`; battery_complete=`True`
- row `3`: `A07_reverse` → `C06_reverse_then_substitute_05_07`; ready=`False`; battery_complete=`True`