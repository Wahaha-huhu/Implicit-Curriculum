# Sequence DSL calibration report

This gate trains several B1 sequence-DSL candidate families briefly and selects the one with identifiable structure and nontrivial token-accuracy acquisition coverage.

## Selected family

- passed: `True`
- candidate_seed: `4`
- token_acquisition_rate: `0.600`
- composite_token_acquisition_rate: `0.750`
- atomic_token_acquisition_rate: `0.750`
- mean_final_token_accuracy: `0.594`
- mean_final_exact_match: `0.257`

## Candidate summary

|   candidate_seed | passed   | family_design_passed   |   token_acquisition_rate |   composite_token_acquisition_rate |   atomic_token_acquisition_rate |   mean_final_token_accuracy |   mean_final_exact_match |   n_tasks |   n_composites |   design_condition_number |
|-----------------:|:---------|:-----------------------|-------------------------:|-----------------------------------:|--------------------------------:|----------------------------:|-------------------------:|----------:|---------------:|--------------------------:|
|                0 | True     | True                   |                     0.32 |                             0.25   |                          0.375  |                    0.615221 |                 0.296914 |        25 |              8 |                   1.43814 |
|                1 | True     | True                   |                     0.42 |                             0.5625 |                          0.5625 |                    0.491432 |                 0.189609 |        25 |              8 |                   1.23825 |
|                2 | False    | True                   |                     0.28 |                             0.25   |                          0.375  |                    0.425931 |                 0.05     |        25 |              8 |                   1.48873 |
|                3 | True     | True                   |                     0.48 |                             0.375  |                          0.75   |                    0.497695 |                 0.203086 |        25 |              8 |                   1.60324 |
|                4 | True     | True                   |                     0.6  |                             0.75   |                          0.75   |                    0.594492 |                 0.256875 |        25 |              8 |                   1.71874 |

## Interpretation

If this passes, use the selected `structure_table.csv` with `run_sequence_dsl_pilot` for a larger B1 pilot. If it fails, reduce sequence difficulty, increase budget, or simplify the task mix before running shared sweeps.