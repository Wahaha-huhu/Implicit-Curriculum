# B1 Second-Family Replication Plan

This plan is designed to test whether the current localized dependency result is specific to the first generated B1 family or recurs in a new controlled sequence-transformer family.

## Family

- family_id: `family_replication_01`
- candidate seeds: `20 21 22 23 24 25 26 27 28 29`
- calibration seeds: `0 1 2`
- H1 sweep seeds: `0 1 2 3 4 5 6 7 8 9`
- H3 seeds: `0 1 2 3 4 5 6 7 8 9`
- configs: `base lr_low lr_high wd_zero batch_small batch_large`

## Outputs

| Stage | Output directory | Claim role |
|---|---|---|
| 1_calibration | `results/family_replication_01/sequence_dsl_calibration` | validates this replication family as a trainable B1 substrate |
| 2_h1_shared_sweep | `results/family_replication_01/b1_h1_shared_sweep` | tests whether H1 sign stability replicates in a new family |
| 3_h2_predictor_residuals | `results/family_replication_01/b1_h1_shared_sweep` | tests whether residual-based candidate selection replicates |
| 4_h3_plan | `results/family_replication_01/b1_h3_plan` | pre-registers pair-specific H3 replication targets |
| 5_h3_interventions | `results/family_replication_01/b1_h3_row*` | tests whether localized exact-component sensitivity recurs |
| 6_optional_mediators | `results/family_replication_01/b1_mediator_h3_pairs` | tests whether mediator pattern replicates |

## Success criteria

A strong replication would show:

1. calibration passes with nonzero/non-saturated acquisition;
2. H1 signs replicate, especially positive reference-learnability timing effect;
3. H2 selects structured composite residuals beyond the atomic parallel null;
4. at least one H3 pair shows exact-component sensitivity beyond same-operation and different-operation controls;
5. if mediator diagnostics are run, H3-positive pairs show stronger early gradient coupling than controls.

A negative or mixed replication is still useful: it would support the current thesis boundary that exact dependency is localized and heterogeneous, not universal.

## Ready-to-run script

Run sections in:

```bash
bash results/.../recommended_replication_commands.sh
```

The actual script is written to `recommended_replication_commands.sh` in this plan directory.
