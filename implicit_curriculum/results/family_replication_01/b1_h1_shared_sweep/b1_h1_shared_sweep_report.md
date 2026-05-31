# B1 H1 shared-sweep report

This run is the first shared-sweep object for H1 ordering/sign-stability on the B1 sequence-DSL transformer substrate.
It trains once across configs/seeds and stores the checkpoint/evaluation tables used by downstream H1/H2/H3 analyses.

## Run summary
- configs: `base, lr_low, lr_high, wd_zero, batch_small, batch_large`
- seeds: `0, 1, 2, 3, 4, 5, 6, 7, 8, 9`
- max_data_seen: `250000`
- n_checkpoints: `100`
- rows in eval_curves: `151500`
- default token-threshold acquisition rate: `0.567`

## Next step
Run `analyze_b1_h1_shared_sweep` on this directory. H1 claims should be based on the analysis report, not this raw sweep report.