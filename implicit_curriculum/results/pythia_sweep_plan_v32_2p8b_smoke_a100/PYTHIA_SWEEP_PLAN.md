# Pythia observational model/config sweep plan

This plan evaluates the same H2-ready slice suite across Pythia-like model sizes and/or evaluation budgets. It remains observational and cannot establish causal dependency.

- slice_table: `thesis_evidence/pythia_slice_suites/v27_h2_ready/pythia_slice_table.csv`
- examples: `thesis_evidence/pythia_slice_suites/v27_h2_ready/pythia_slice_examples.jsonl`
- models: `EleutherAI/pythia-2.8b`
- revisions: `step0, step10000, step143000`
- max_examples_per_slice: `16`
- planned runs: `1`

## Planned runs
- `pythia-2.8b_n16`: model=`EleutherAI/pythia-2.8b`, n_examples_per_slice=`16`, output=`results/pythia_model_sweep_v32_2p8b_smoke_a100/pythia-2.8b_n16`

## Interpretation rule
A Pythia residual pattern becomes more thesis-useful if it persists across model size, checkpoint density, or evaluation budget. It remains observational unless pretraining or finetuning interventions are added.
