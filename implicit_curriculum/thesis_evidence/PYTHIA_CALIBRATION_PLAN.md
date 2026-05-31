# Pythia observational calibration plan

The first Pythia-style observational bridge ran end-to-end but produced no acquired slices at accuracy threshold 0.5. This should be treated as an environment/smoke success, not evidence for or against the controlled mechanism.

The next calibration steps are:

1. Reanalyze the existing run across lower thresholds such as 0.2, 0.3, 0.4, and 0.5.
2. Use continuous metrics such as final accuracy, AUC, and final-minus-initial improvement.
3. Generate an easier slice suite to check whether the model/checkpoints and scoring format can produce measurable acquisition.
4. Only after finding nonzero/non-saturated slices should we run H1/H2-like observational analyses.

Claim boundary: Pythia results are observational. They can compare signatures with the controlled B1 framework, but they cannot establish causal dependency without pretraining interventions.
