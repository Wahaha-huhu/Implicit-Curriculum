# v2 causal-census implementation

This repo now contains a v2 implementation layer for the causal, powered adjudication design.
It reuses the existing B1/H3 pair-specific intervention trainer and adds a census-level
planning, execution, verdict, and mediator-prediction workflow.

## Added modules

- `src/ic_experiments/census.py` — shared plan construction, v2 condition sets, paired contrast statistics, verdict classification, AUC helpers.
- `src/ic_experiments/experiments/make_b1_v2_preregistration.py` — freezes a preregistration JSON/MD and optional frozen census CSV.
- `src/ic_experiments/experiments/make_b1_causal_census_plan.py` — creates the pre-registered component→composite census plan.
- `src/ic_experiments/experiments/run_b1_causal_census.py` — wraps the existing `run_b1_h3_interventions` runner over many census rows.
- `src/ic_experiments/experiments/analyze_b1_causal_census_verdicts.py` — aggregates H3 rows into v2 causal verdicts and census fractions.
- `src/ic_experiments/experiments/analyze_b1_alignment_predicts_census_verdict.py` — tests whether early mediator features predict the census verdict.
- `tests/v2_census_import_test.py`, `tests/v2_census_unit_test.py` — import and unit coverage for the new workflow.

## Recommended workflow

Generate or choose a structure table and H3-readiness table first. If no readiness table
is supplied, the plan generator lists every formal component→composite edge in the task graph.

```bash
PYTHONPATH=src python -m ic_experiments.experiments.make_b1_causal_census_plan \
  --structure-table results/<family>/structure_table.csv \
  --ready-pair-selection results/<readiness>/h3_ready_pair_selection.csv \
  --output-dir results/b1_v2_causal_census_plan \
  --ready-only --allow-not-ready \
  --write-run-script \
  --condition-set full \
  --run-output-prefix results/b1_v2_causal_census
```

Freeze the preregistration before running the full census:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.make_b1_v2_preregistration \
  --output-dir results/b1_v2_preregistration \
  --structure-table results/<family>/structure_table.csv \
  --ready-pair-selection results/<readiness>/h3_ready_pair_selection.csv \
  --census-plan results/b1_v2_causal_census_plan/b1_v2_causal_census_plan.csv \
  --condition-set full
```

Run the census. This uses the existing H3 runner row-by-row, so it is resumable with
`--skip-existing`.

```bash
PYTHONPATH=src python -m ic_experiments.experiments.run_b1_causal_census \
  --census-plan results/b1_v2_causal_census_plan/b1_v2_causal_census_plan.csv \
  --structure-table results/<family>/structure_table.csv \
  --output-dir results/b1_v2_causal_census \
  --condition-set full \
  --seeds 0 1 2 3 4 5 6 7 8 9 \
  --skip-existing
```

Aggregate verdicts:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.analyze_b1_causal_census_verdicts \
  --census-plan results/b1_v2_causal_census_plan/b1_v2_causal_census_plan.csv \
  --run-index results/b1_v2_causal_census/b1_v2_causal_census_run_index.csv \
  --output-dir results/b1_v2_causal_census_analysis
```

Then connect mediator diagnostics to the causal verdict:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.analyze_b1_alignment_predicts_census_verdict \
  --census-verdicts results/b1_v2_causal_census_analysis/b1_v2_causal_census_pair_verdicts.csv \
  --mediator-pair-role-summary results/<mediator>/mediator_pair_role_summary.csv \
  --mediator-contrast-summary results/<mediator>/mediator_contrast_summary.csv \
  --output-dir results/b1_v2_alignment_predicts_verdict
```

## Verdict boundary

A row is called `exact_component_dependency` only when exact-component interventions
separate from same-operation, different-operation, fake-component, and surface controls.
If fake/surface evidence is missing, the stricter verdict is
`candidate_exact_dependency_incomplete_battery`, not a Tier-1 exact-dependency claim.
This prevents strong claims from runs that use only the reduced strong condition set.
