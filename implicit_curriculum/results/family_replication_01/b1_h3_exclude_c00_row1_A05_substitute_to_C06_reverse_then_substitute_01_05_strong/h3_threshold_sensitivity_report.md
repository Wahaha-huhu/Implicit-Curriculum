# B1 H3 threshold-sensitivity analysis

This analysis reuses an H3 intervention run and recomputes acquisition-time contrasts at several token-accuracy thresholds. It is intended to diagnose whether a candidate is truly negative or merely too hard for the default threshold.

Metric family: `token_accuracy`
Thresholds: `0.3, 0.4, 0.5, 0.6, 0.7`

## Pair
- component: `A05_substitute`
- composite: `C06_reverse_then_substitute_01_05`
- same_operation_control: `U01_unrelated_substitute`
- different_operation_control: `A03_copy`

## Composite acquisition by threshold
- threshold `0.3` / `baseline`: acq=0.900, final=0.418, censored_time=222720.0
- threshold `0.3` / `corrupt_component_strong`: acq=0.800, final=0.410, censored_time=222924.8
- threshold `0.3` / `corrupt_different_operation_matched_strong`: acq=0.800, final=0.414, censored_time=224768.0
- threshold `0.3` / `corrupt_same_operation_unrelated_strong`: acq=0.600, final=0.400, censored_time=229350.4
- threshold `0.3` / `delay_component_strong`: acq=0.800, final=0.430, censored_time=214425.6
- threshold `0.3` / `delay_different_operation_matched_strong`: acq=0.900, final=0.441, censored_time=218137.6
- threshold `0.3` / `delay_same_operation_unrelated_strong`: acq=0.700, final=0.451, censored_time=213171.2
- threshold `0.3` / `pretrain_component`: acq=0.400, final=0.330, censored_time=243353.6
- threshold `0.3` / `pretrain_different_operation_matched`: acq=0.700, final=0.464, censored_time=220492.8
- threshold `0.3` / `pretrain_same_operation_unrelated`: acq=0.400, final=0.345, censored_time=237209.6
- threshold `0.4` / `baseline`: acq=0.300, final=0.418, censored_time=243481.6
- threshold `0.4` / `corrupt_component_strong`: acq=0.100, final=0.410, censored_time=246860.8
- threshold `0.4` / `corrupt_different_operation_matched_strong`: acq=0.300, final=0.414, censored_time=240640.0
- threshold `0.4` / `corrupt_same_operation_unrelated_strong`: acq=0.300, final=0.400, censored_time=241920.0
- threshold `0.4` / `delay_component_strong`: acq=0.400, final=0.430, censored_time=237209.6
- threshold `0.4` / `delay_different_operation_matched_strong`: acq=0.500, final=0.441, censored_time=238540.8
- threshold `0.4` / `delay_same_operation_unrelated_strong`: acq=0.500, final=0.451, censored_time=234137.6
- threshold `0.4` / `pretrain_component`: acq=0.000, final=0.330, censored_time=250112.0
- threshold `0.4` / `pretrain_different_operation_matched`: acq=0.500, final=0.464, censored_time=232678.4
- threshold `0.4` / `pretrain_same_operation_unrelated`: acq=0.100, final=0.345, censored_time=246860.8
- threshold `0.5` / `baseline`: acq=0.100, final=0.418, censored_time=246860.8
- threshold `0.5` / `corrupt_component_strong`: acq=0.100, final=0.410, censored_time=248422.4
- threshold `0.5` / `corrupt_different_operation_matched_strong`: acq=0.100, final=0.414, censored_time=245401.6
- threshold `0.5` / `corrupt_same_operation_unrelated_strong`: acq=0.100, final=0.400, censored_time=248422.4
- threshold `0.5` / `delay_component_strong`: acq=0.200, final=0.430, censored_time=246732.8
- threshold `0.5` / `delay_different_operation_matched_strong`: acq=0.100, final=0.441, censored_time=248422.4
- threshold `0.5` / `delay_same_operation_unrelated_strong`: acq=0.200, final=0.451, censored_time=245171.2
- threshold `0.5` / `pretrain_component`: acq=0.000, final=0.330, censored_time=250112.0
- threshold `0.5` / `pretrain_different_operation_matched`: acq=0.300, final=0.464, censored_time=240460.8
- threshold `0.5` / `pretrain_same_operation_unrelated`: acq=0.100, final=0.345, censored_time=248422.4
- threshold `0.6` / `baseline`: acq=0.100, final=0.418, censored_time=248422.4
- threshold `0.6` / `corrupt_component_strong`: acq=0.000, final=0.410, censored_time=250112.0
- threshold `0.6` / `corrupt_different_operation_matched_strong`: acq=0.100, final=0.414, censored_time=248422.4
- threshold `0.6` / `corrupt_same_operation_unrelated_strong`: acq=0.000, final=0.400, censored_time=250112.0
- threshold `0.6` / `delay_component_strong`: acq=0.000, final=0.430, censored_time=250112.0
- threshold `0.6` / `delay_different_operation_matched_strong`: acq=0.000, final=0.441, censored_time=250112.0
- threshold `0.6` / `delay_same_operation_unrelated_strong`: acq=0.000, final=0.451, censored_time=250112.0
- threshold `0.6` / `pretrain_component`: acq=0.000, final=0.330, censored_time=250112.0
- threshold `0.6` / `pretrain_different_operation_matched`: acq=0.100, final=0.464, censored_time=246860.8
- threshold `0.6` / `pretrain_same_operation_unrelated`: acq=0.000, final=0.345, censored_time=250112.0
- threshold `0.7` / `baseline`: acq=0.000, final=0.418, censored_time=250112.0
- threshold `0.7` / `corrupt_component_strong`: acq=0.000, final=0.410, censored_time=250112.0
- threshold `0.7` / `corrupt_different_operation_matched_strong`: acq=0.000, final=0.414, censored_time=250112.0
- threshold `0.7` / `corrupt_same_operation_unrelated_strong`: acq=0.000, final=0.400, censored_time=250112.0
- threshold `0.7` / `delay_component_strong`: acq=0.000, final=0.430, censored_time=250112.0
- threshold `0.7` / `delay_different_operation_matched_strong`: acq=0.000, final=0.441, censored_time=250112.0
- threshold `0.7` / `delay_same_operation_unrelated_strong`: acq=0.000, final=0.451, censored_time=250112.0
- threshold `0.7` / `pretrain_component`: acq=0.000, final=0.330, censored_time=250112.0
- threshold `0.7` / `pretrain_different_operation_matched`: acq=0.000, final=0.464, censored_time=250112.0
- threshold `0.7` / `pretrain_same_operation_unrelated`: acq=0.000, final=0.345, censored_time=250112.0

## Key exact-vs-control contrasts
- threshold `0.3` / `exact_pretrain_vs_same_operation`: censored Δ=6144.000, censored-rate=0.100, Δfinal=-0.015
- threshold `0.3` / `exact_pretrain_vs_different_operation`: censored Δ=22860.800, censored-rate=0.100, Δfinal=-0.135
- threshold `0.3` / `exact_strong_corrupt_vs_same_operation`: censored Δ=-6425.600, censored-rate=0.100, Δfinal=0.009
- threshold `0.3` / `exact_strong_corrupt_vs_different_operation`: censored Δ=-1843.200, censored-rate=0.200, Δfinal=-0.004
- threshold `0.3` / `exact_strong_delay_vs_same_operation`: censored Δ=1254.400, censored-rate=0.200, Δfinal=-0.021
- threshold `0.3` / `exact_strong_delay_vs_different_operation`: censored Δ=-3712.000, censored-rate=0.200, Δfinal=-0.011
- threshold `0.4` / `exact_pretrain_vs_same_operation`: censored Δ=3251.200, censored-rate=0.000, Δfinal=-0.015
- threshold `0.4` / `exact_pretrain_vs_different_operation`: censored Δ=17433.600, censored-rate=0.000, Δfinal=-0.135
- threshold `0.4` / `exact_strong_corrupt_vs_same_operation`: censored Δ=4940.800, censored-rate=0.200, Δfinal=0.009
- threshold `0.4` / `exact_strong_corrupt_vs_different_operation`: censored Δ=6220.800, censored-rate=0.200, Δfinal=-0.004
- threshold `0.4` / `exact_strong_delay_vs_same_operation`: censored Δ=3072.000, censored-rate=0.200, Δfinal=-0.021
- threshold `0.4` / `exact_strong_delay_vs_different_operation`: censored Δ=-1331.200, censored-rate=0.200, Δfinal=-0.011
- threshold `0.5` / `exact_pretrain_vs_same_operation`: censored Δ=1689.600, censored-rate=0.000, Δfinal=-0.015
- threshold `0.5` / `exact_pretrain_vs_different_operation`: censored Δ=9651.200, censored-rate=0.000, Δfinal=-0.135
- threshold `0.5` / `exact_strong_corrupt_vs_same_operation`: censored Δ=0.000, censored-rate=0.100, Δfinal=0.009
- threshold `0.5` / `exact_strong_corrupt_vs_different_operation`: censored Δ=3020.800, censored-rate=0.100, Δfinal=-0.004
- threshold `0.5` / `exact_strong_delay_vs_same_operation`: censored Δ=1561.600, censored-rate=0.100, Δfinal=-0.021
- threshold `0.5` / `exact_strong_delay_vs_different_operation`: censored Δ=-1689.600, censored-rate=0.000, Δfinal=-0.011
- threshold `0.6` / `exact_pretrain_vs_same_operation`: censored Δ=0.000, censored-rate=0.000, Δfinal=-0.015
- threshold `0.6` / `exact_pretrain_vs_different_operation`: censored Δ=3251.200, censored-rate=0.000, Δfinal=-0.135
- threshold `0.6` / `exact_strong_corrupt_vs_same_operation`: censored Δ=0.000, censored-rate=0.000, Δfinal=0.009
- threshold `0.6` / `exact_strong_corrupt_vs_different_operation`: censored Δ=1689.600, censored-rate=0.100, Δfinal=-0.004
- threshold `0.6` / `exact_strong_delay_vs_same_operation`: censored Δ=0.000, censored-rate=0.000, Δfinal=-0.021
- threshold `0.6` / `exact_strong_delay_vs_different_operation`: censored Δ=0.000, censored-rate=0.000, Δfinal=-0.011
- threshold `0.7` / `exact_pretrain_vs_same_operation`: censored Δ=0.000, censored-rate=0.000, Δfinal=-0.015
- threshold `0.7` / `exact_pretrain_vs_different_operation`: censored Δ=0.000, censored-rate=0.000, Δfinal=-0.135
- threshold `0.7` / `exact_strong_corrupt_vs_same_operation`: censored Δ=0.000, censored-rate=0.000, Δfinal=0.009
- threshold `0.7` / `exact_strong_corrupt_vs_different_operation`: censored Δ=0.000, censored-rate=0.000, Δfinal=-0.004
- threshold `0.7` / `exact_strong_delay_vs_same_operation`: censored Δ=0.000, censored-rate=0.000, Δfinal=-0.021
- threshold `0.7` / `exact_strong_delay_vs_different_operation`: censored Δ=0.000, censored-rate=0.000, Δfinal=-0.011

## AUC note
- `baseline`: mean AUC=0.132
- `corrupt_component_strong`: mean AUC=0.132
- `corrupt_different_operation_matched_strong`: mean AUC=0.126
- `corrupt_same_operation_unrelated_strong`: mean AUC=0.116
- `delay_component_strong`: mean AUC=0.156
- `delay_different_operation_matched_strong`: mean AUC=0.134
- `delay_same_operation_unrelated_strong`: mean AUC=0.151
- `pretrain_component`: mean AUC=0.089
- `pretrain_different_operation_matched`: mean AUC=0.124
- `pretrain_same_operation_unrelated`: mean AUC=0.084

## Interpretation rule
If contrasts appear only at very low thresholds, interpret them as subthreshold learning shifts rather than clear acquisition. If no threshold shows contrast and final/AUC are flat, the pair is non-informative. If exact-component contrasts persist across moderate thresholds and final/AUC agree, the result is stronger.