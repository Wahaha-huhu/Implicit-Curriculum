# Sequence DSL analysis report

This is B1-specific analysis. It treats token accuracy, exact match, loss/AUC, and right-censored acquisition as separate calibration observables rather than relying on a single exact-match threshold.

## Acquisition threshold sensitivity

- exact_match threshold `0.2`: acquisition_rate=0.488, time-Spearman(freq)=-0.037, time-Spearman(learnability)=0.723, time-Spearman(utility)=-0.169
- exact_match threshold `0.5`: acquisition_rate=0.280, time-Spearman(freq)=-0.099, time-Spearman(learnability)=0.029, time-Spearman(utility)=-0.138
- exact_match threshold `0.8`: acquisition_rate=0.040, time-Spearman(freq)=0.354, time-Spearman(learnability)=0.250, time-Spearman(utility)=-0.395
- token_accuracy threshold `0.5`: acquisition_rate=0.832, time-Spearman(freq)=-0.076, time-Spearman(learnability)=0.411, time-Spearman(utility)=-0.198
- token_accuracy threshold `0.7`: acquisition_rate=0.640, time-Spearman(freq)=-0.064, time-Spearman(learnability)=0.701, time-Spearman(utility)=-0.128
- token_accuracy threshold `0.85`: acquisition_rate=0.392, time-Spearman(freq)=0.059, time-Spearman(learnability)=0.655, time-Spearman(utility)=-0.049

## Final metrics by kind

- atomic: n=40, exact=0.350, token=0.828, loss=0.503
- composite: n=40, exact=0.220, token=0.826, loss=0.446
- shortcut: n=15, exact=0.759, token=0.958, loss=0.167
- surface_control: n=15, exact=0.000, token=0.355, loss=2.702
- unrelated: n=15, exact=0.001, token=0.255, loss=2.277

## Frequency realization

- seed `0`: Spearman(intended,realized)=1.000, MAE=0.000, max_abs_error=0.001
- seed `1`: Spearman(intended,realized)=1.000, MAE=0.000, max_abs_error=0.001
- seed `2`: Spearman(intended,realized)=1.000, MAE=0.000, max_abs_error=0.001
- seed `3`: Spearman(intended,realized)=1.000, MAE=0.000, max_abs_error=0.001
- seed `4`: Spearman(intended,realized)=1.000, MAE=0.000, max_abs_error=0.002

## Stratified ordering highlights

- all: n_tasks=25, acq=0.640, time-Spearman(freq)=-0.064, learn=0.701, utility=-0.128
- true_tasks_atomic_composite: n_tasks=16, acq=0.812, time-Spearman(freq)=-0.012, learn=0.522, utility=-0.362
- kind=atomic: n_tasks=8, acq=0.750, time-Spearman(freq)=-0.269, learn=0.931, utility=-0.090
- kind=composite: n_tasks=8, acq=0.875, time-Spearman(freq)=0.431, learn=nan, utility=nan
- kind=shortcut: n_tasks=3, acq=1.000, time-Spearman(freq)=nan, learn=nan, utility=nan
- kind=surface_control: n_tasks=3, acq=0.000, time-Spearman(freq)=nan, learn=nan, utility=nan
- kind=unrelated: n_tasks=3, acq=0.000, time-Spearman(freq)=nan, learn=nan, utility=nan
- op=copy: n_tasks=3, acq=1.000, time-Spearman(freq)=nan, learn=nan, utility=nan
- op=copy_then_substitute: n_tasks=2, acq=1.000, time-Spearman(freq)=0.112, learn=nan, utility=nan
- op=reverse: n_tasks=3, acq=1.000, time-Spearman(freq)=0.030, learn=nan, utility=0.000
- op=reverse_then_substitute: n_tasks=3, acq=0.667, time-Spearman(freq)=0.000, learn=nan, utility=nan
- op=shortcut_identity: n_tasks=3, acq=1.000, time-Spearman(freq)=nan, learn=nan, utility=nan

## Calibration decision rule

GREEN requires nonzero and non-saturated token-accuracy acquisition, improving exact match or loss, at least moderate composite/control coverage, and interpretable within-stratum predictor signs. Exact-match 0.90 is intentionally not required at this stage.