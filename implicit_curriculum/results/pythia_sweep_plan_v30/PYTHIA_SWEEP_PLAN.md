# Pythia observational model/config sweep plan

This plan evaluates the same H2-ready slice suite across Pythia-like model sizes and/or evaluation budgets. It remains observational and cannot establish causal dependency.

- slice_table: `results/pythia_h2_ready_slice_suite_v27/pythia_slice_table.csv`
- examples: `results/pythia_h2_ready_slice_suite_v27/pythia_slice_examples.jsonl`
- models: `EleutherAI/pythia-70m, EleutherAI/pythia-160m`
- revisions: `step0, step1000, step10000, step143000`
- max_examples_per_slice: `64`
- planned runs: `2`

## Planned runs
- `pythia-70m_n64`: model=`EleutherAI/pythia-70m`, n_examples_per_slice=`64`, output=`results/pythia_model_sweep_v30/pythia-70m_n64`
- `pythia-160m_n64`: model=`EleutherAI/pythia-160m`, n_examples_per_slice=`64`, output=`results/pythia_model_sweep_v30/pythia-160m_n64`

## Interpretation rule
A Pythia residual pattern becomes more thesis-useful if it persists across model size, checkpoint density, or evaluation budget. It remains observational unless pretraining or finetuning interventions are added.
