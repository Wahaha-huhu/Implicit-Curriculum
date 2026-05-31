# Next experiment plan after H3 C06/A02 positive result

## Current state

The strongest H3 evidence is the 10-seed strong row-0 test for `A02_substitute -> C06_reverse_then_substitute_02_00`. Exact component pretraining accelerated the composite beyond same-operation and different-operation controls, and exact component corruption impaired it relative to controls. This supports a localized pair-specific dependency site, not a general dependency law.

## Why the next experiment should be a secondary composite

A second-family replication would be ideal but more expensive. The next cheaper test is to ask whether H2-selected residuals identify another composite where exact-component interventions matter. This tests generality across composite type while reusing the same B1 family and existing H1/H2 outputs.

## Recommended v1.5 command

```bash
PYTHONPATH=src python -m ic_experiments.experiments.make_b1_h3_operation_family_plan \
  --structure-table results/b1_h1_shared_sweep_v08/structure_table.csv \
  --pair-selection results/b1_h1_shared_sweep_v08/h2_pair_selection.csv \
  --output-dir results/b1_h3_secondary_plan_v15 \
  --exclude-composites C06_reverse_then_substitute_02_00 \
  --top-composites 1 \
  --components-per-composite 2 \
  --write-run-script \
  --condition-set strong \
  --run-output-prefix results/b1_h3_secondary_v15 \
  --code-version v1.5 \
  --thesis-use candidate
```

Then run:

```bash
bash results/b1_h3_secondary_plan_v15/recommended_h3_commands.sh
```

## Evidence interpretation

- Positive secondary composite: strengthens H3 as a controlled phenomenon, though still not an LLM-general claim.
- Mixed secondary composite: supports the current cautious thesis framing that dependency is localized and component-specific.
- Negative secondary composite: strengthens the claim that residuals are useful candidate selectors but not evidence of dependency by themselves.
