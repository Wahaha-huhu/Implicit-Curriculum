# Pythia model/configuration sweep plan

This stage tests whether the observational primitive-to-composite residual signatures found in the Pythia-70M pilot persist across model size or evaluation configuration. It is a replication/stability stage for the Pythia bridge, not causal evidence.

## Motivation

The v2.7/v2.9 Pythia bridge showed that an expanded slice suite can produce measurable continuous-score residuals. Arithmetic composites tended to underperform primitive predictions, while retrieval composites tended to outperform. Before using this as a thesis result, the pattern should be checked across at least one additional model size or evaluation budget.

## Primary question

Do the same composite families remain underperforming or outperforming across model/config sweeps?

## Planned comparisons

Recommended first sweep:

- `EleutherAI/pythia-70m`, same checkpoints as the pilot, as the anchor run.
- `EleutherAI/pythia-160m`, same checkpoints, as the first model-size replication.
- Optionally `EleutherAI/pythia-410m` if memory allows.
- Optionally compare `max_examples_per_slice=32` and `64` to verify that residuals are not dominated by evaluation noise.

## Expected outputs

The sweep planner writes a CSV and shell script. Each planned run should produce:

- `pythia_eval_curves.csv`
- `pythia_h2_readiness_report.md`
- `pythia_continuous_score_report.md`
- `pythia_residual_refinement_report.md`

The sweep synthesizer then aggregates these into:

- `PYTHIA_SWEEP_SYNTHESIS.md`
- `pythia_sweep_run_summary.csv`
- `pythia_sweep_residual_stability.csv`
- `pythia_sweep_family_stability.csv`

## Claim boundary

A pattern that persists across model sizes is stronger observational evidence that the slice suite captures stable primitive/composite structure. It still does not establish causal dependency, because the model pretraining process is not intervened on.
