# Second B1-Family Replication Plan

The first controlled B1 evidence arc is coherent but still rests on one generated task family. To support a stronger thesis/top-conference claim, the next experimental priority is a second independently generated B1 family.

## Purpose

The second-family replication asks whether the qualitative pattern survives beyond the original family:

1. H1: structural ordering/sign stability, especially positive reference-learnability timing effects.
2. H2: simple atomic predictors and structured composite residuals.
3. H3: at least one residual-selected pair with exact-component sensitivity beyond same-operation and different-operation controls.
4. Mediators: H3-positive pairs show stronger early gradient alignment than controls.

## Claim boundary

A positive second-family result would support a controlled-setting claim about localized dependency sites recurring in B1 sequence transformers. It would still not prove a universal LLM training mechanism.

A mixed or negative second-family result would not invalidate the first family. It would instead support the current boundary-mapping thesis: residuals and formal graphs identify candidate sites, but exact-component dependency is heterogeneous and regime-specific.

## Recommended command

Use:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.make_b1_replication_plan \
  --output-dir results/b1_replication_plan_v20 \
  --family-id family_replication_01 \
  --candidate-seeds 20 21 22 23 24 25 26 27 28 29 \
  --calibration-seeds 0 1 2 \
  --sweep-seeds 0 1 2 3 4 5 6 7 8 9 \
  --h3-seeds 0 1 2 3 4 5 6 7 8 9 \
  --code-version v2.0
```

Then run sections from:

```bash
bash results/b1_replication_plan_v20/recommended_replication_commands.sh
```

Run sections one at a time and inspect the gate report before proceeding.
