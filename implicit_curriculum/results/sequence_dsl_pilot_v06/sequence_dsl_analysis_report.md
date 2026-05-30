# Sequence DSL analysis report

This is B1-specific analysis. It treats token accuracy, exact match, loss/AUC, and right-censored acquisition as separate calibration observables rather than relying on a single exact-match threshold.

## Acquisition threshold sensitivity

- exact_match threshold `0.2`: acquisition_rate=0.320, time-Spearman(freq)=0.150, time-Spearman(learnability)=0.397, time-Spearman(utility)=-0.131
- exact_match threshold `0.5`: acquisition_rate=0.320, time-Spearman(freq)=-0.095, time-Spearman(learnability)=-0.211, time-Spearman(utility)=0.087
- exact_match threshold `0.8`: acquisition_rate=0.000, time-Spearman(freq)=nan, time-Spearman(learnability)=nan, time-Spearman(utility)=nan
- token_accuracy threshold `0.5`: acquisition_rate=0.672, time-Spearman(freq)=0.291, time-Spearman(learnability)=0.510, time-Spearman(utility)=0.033
- token_accuracy threshold `0.7`: acquisition_rate=0.600, time-Spearman(freq)=0.183, time-Spearman(learnability)=0.543, time-Spearman(utility)=0.184
- token_accuracy threshold `0.85`: acquisition_rate=0.320, time-Spearman(freq)=0.148, time-Spearman(learnability)=0.175, time-Spearman(utility)=0.011

## Final metrics by kind

- atomic: n=40, exact=0.307, token=0.675, loss=1.133
- composite: n=40, exact=0.224, token=0.755, loss=0.672
- shortcut: n=15, exact=0.726, token=0.952, loss=0.233
- surface_control: n=15, exact=0.003, token=0.342, loss=2.796
- unrelated: n=15, exact=0.000, token=0.034, loss=4.780

## Calibration decision rule

GREEN requires nonzero and non-saturated token-accuracy acquisition, improving exact match or loss, and at least moderate composite/control coverage. Exact-match 0.90 is intentionally not required at this stage.