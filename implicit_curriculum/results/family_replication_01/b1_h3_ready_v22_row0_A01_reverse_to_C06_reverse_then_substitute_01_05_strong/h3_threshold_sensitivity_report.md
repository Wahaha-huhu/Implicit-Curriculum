# B1 H3 threshold-sensitivity analysis

This analysis reuses an H3 intervention run and recomputes acquisition-time contrasts at several token-accuracy thresholds. It is intended to diagnose whether a candidate is truly negative or merely too hard for the default threshold.

Metric family: `token_accuracy`
Thresholds: `0.3, 0.4, 0.5, 0.6, 0.7`

## Pair
- component: `A01_reverse`
- composite: `C06_reverse_then_substitute_01_05`
- same_operation_control: `A07_reverse`
- different_operation_control: `U00_unrelated_substitute`

## Composite acquisition by threshold
- threshold `0.3` / `baseline`: acq=0.900, final=0.418, censored_time=222720.0
- threshold `0.3` / `corrupt_component_strong`: acq=0.300, final=0.292, censored_time=243481.6
- threshold `0.3` / `corrupt_different_operation_matched_strong`: acq=0.800, final=0.424, censored_time=226048.0
- threshold `0.3` / `corrupt_same_operation_unrelated_strong`: acq=0.900, final=0.425, censored_time=225740.8
- threshold `0.3` / `delay_component_strong`: acq=0.700, final=0.470, censored_time=211788.8
- threshold `0.3` / `delay_different_operation_matched_strong`: acq=0.700, final=0.404, censored_time=224896.0
- threshold `0.3` / `delay_same_operation_unrelated_strong`: acq=0.700, final=0.407, censored_time=221593.6
- threshold `0.3` / `pretrain_component`: acq=0.800, final=0.445, censored_time=215500.8
- threshold `0.3` / `pretrain_different_operation_matched`: acq=0.100, final=0.236, censored_time=248422.4
- threshold `0.3` / `pretrain_same_operation_unrelated`: acq=0.800, final=0.445, censored_time=215500.8
- threshold `0.4` / `baseline`: acq=0.300, final=0.418, censored_time=243481.6
- threshold `0.4` / `corrupt_component_strong`: acq=0.100, final=0.292, censored_time=248422.4
- threshold `0.4` / `corrupt_different_operation_matched_strong`: acq=0.400, final=0.424, censored_time=240230.4
- threshold `0.4` / `corrupt_same_operation_unrelated_strong`: acq=0.300, final=0.425, censored_time=245043.2
- threshold `0.4` / `delay_component_strong`: acq=0.600, final=0.470, censored_time=229888.0
- threshold `0.4` / `delay_different_operation_matched_strong`: acq=0.300, final=0.404, censored_time=238899.2
- threshold `0.4` / `delay_same_operation_unrelated_strong`: acq=0.400, final=0.407, censored_time=238771.2
- threshold `0.4` / `pretrain_component`: acq=0.500, final=0.445, censored_time=236979.2
- threshold `0.4` / `pretrain_different_operation_matched`: acq=0.000, final=0.236, censored_time=250112.0
- threshold `0.4` / `pretrain_same_operation_unrelated`: acq=0.500, final=0.445, censored_time=236979.2
- threshold `0.5` / `baseline`: acq=0.100, final=0.418, censored_time=246860.8
- threshold `0.5` / `corrupt_component_strong`: acq=0.000, final=0.292, censored_time=250112.0
- threshold `0.5` / `corrupt_different_operation_matched_strong`: acq=0.100, final=0.424, censored_time=248422.4
- threshold `0.5` / `corrupt_same_operation_unrelated_strong`: acq=0.000, final=0.425, censored_time=250112.0
- threshold `0.5` / `delay_component_strong`: acq=0.200, final=0.470, censored_time=239308.8
- threshold `0.5` / `delay_different_operation_matched_strong`: acq=0.200, final=0.404, censored_time=245171.2
- threshold `0.5` / `delay_same_operation_unrelated_strong`: acq=0.200, final=0.407, censored_time=246732.8
- threshold `0.5` / `pretrain_component`: acq=0.200, final=0.445, censored_time=246732.8
- threshold `0.5` / `pretrain_different_operation_matched`: acq=0.000, final=0.236, censored_time=250112.0
- threshold `0.5` / `pretrain_same_operation_unrelated`: acq=0.200, final=0.445, censored_time=246732.8
- threshold `0.6` / `baseline`: acq=0.100, final=0.418, censored_time=248422.4
- threshold `0.6` / `corrupt_component_strong`: acq=0.000, final=0.292, censored_time=250112.0
- threshold `0.6` / `corrupt_different_operation_matched_strong`: acq=0.000, final=0.424, censored_time=250112.0
- threshold `0.6` / `corrupt_same_operation_unrelated_strong`: acq=0.000, final=0.425, censored_time=250112.0
- threshold `0.6` / `delay_component_strong`: acq=0.100, final=0.470, censored_time=248422.4
- threshold `0.6` / `delay_different_operation_matched_strong`: acq=0.000, final=0.404, censored_time=250112.0
- threshold `0.6` / `delay_same_operation_unrelated_strong`: acq=0.000, final=0.407, censored_time=250112.0
- threshold `0.6` / `pretrain_component`: acq=0.000, final=0.445, censored_time=250112.0
- threshold `0.6` / `pretrain_different_operation_matched`: acq=0.000, final=0.236, censored_time=250112.0
- threshold `0.6` / `pretrain_same_operation_unrelated`: acq=0.000, final=0.445, censored_time=250112.0
- threshold `0.7` / `baseline`: acq=0.000, final=0.418, censored_time=250112.0
- threshold `0.7` / `corrupt_component_strong`: acq=0.000, final=0.292, censored_time=250112.0
- threshold `0.7` / `corrupt_different_operation_matched_strong`: acq=0.000, final=0.424, censored_time=250112.0
- threshold `0.7` / `corrupt_same_operation_unrelated_strong`: acq=0.000, final=0.425, censored_time=250112.0
- threshold `0.7` / `delay_component_strong`: acq=0.000, final=0.470, censored_time=250112.0
- threshold `0.7` / `delay_different_operation_matched_strong`: acq=0.000, final=0.404, censored_time=250112.0
- threshold `0.7` / `delay_same_operation_unrelated_strong`: acq=0.000, final=0.407, censored_time=250112.0
- threshold `0.7` / `pretrain_component`: acq=0.000, final=0.445, censored_time=250112.0
- threshold `0.7` / `pretrain_different_operation_matched`: acq=0.000, final=0.236, censored_time=250112.0
- threshold `0.7` / `pretrain_same_operation_unrelated`: acq=0.000, final=0.445, censored_time=250112.0

## Key exact-vs-control contrasts
- threshold `0.3` / `exact_pretrain_vs_same_operation`: censored Δ=0.000, censored-rate=0.000, Δfinal=0.000
- threshold `0.3` / `exact_pretrain_vs_different_operation`: censored Δ=-32921.600, censored-rate=0.800, Δfinal=0.209
- threshold `0.3` / `exact_strong_corrupt_vs_same_operation`: censored Δ=17740.800, censored-rate=0.700, Δfinal=-0.133
- threshold `0.3` / `exact_strong_corrupt_vs_different_operation`: censored Δ=17433.600, censored-rate=0.600, Δfinal=-0.132
- threshold `0.3` / `exact_strong_delay_vs_same_operation`: censored Δ=-9804.800, censored-rate=0.200, Δfinal=0.062
- threshold `0.3` / `exact_strong_delay_vs_different_operation`: censored Δ=-13107.200, censored-rate=0.300, Δfinal=0.066
- threshold `0.4` / `exact_pretrain_vs_same_operation`: censored Δ=0.000, censored-rate=0.000, Δfinal=0.000
- threshold `0.4` / `exact_pretrain_vs_different_operation`: censored Δ=-13132.800, censored-rate=0.500, Δfinal=0.209
- threshold `0.4` / `exact_strong_corrupt_vs_same_operation`: censored Δ=3379.200, censored-rate=0.300, Δfinal=-0.133
- threshold `0.4` / `exact_strong_corrupt_vs_different_operation`: censored Δ=8192.000, censored-rate=0.400, Δfinal=-0.132
- threshold `0.4` / `exact_strong_delay_vs_same_operation`: censored Δ=-8883.200, censored-rate=0.100, Δfinal=0.062
- threshold `0.4` / `exact_strong_delay_vs_different_operation`: censored Δ=-9011.200, censored-rate=0.200, Δfinal=0.066
- threshold `0.5` / `exact_pretrain_vs_same_operation`: censored Δ=0.000, censored-rate=0.000, Δfinal=0.000
- threshold `0.5` / `exact_pretrain_vs_different_operation`: censored Δ=-3379.200, censored-rate=0.200, Δfinal=0.209
- threshold `0.5` / `exact_strong_corrupt_vs_same_operation`: censored Δ=0.000, censored-rate=0.000, Δfinal=-0.133
- threshold `0.5` / `exact_strong_corrupt_vs_different_operation`: censored Δ=1689.600, censored-rate=0.100, Δfinal=-0.132
- threshold `0.5` / `exact_strong_delay_vs_same_operation`: censored Δ=-7424.000, censored-rate=0.100, Δfinal=0.062
- threshold `0.5` / `exact_strong_delay_vs_different_operation`: censored Δ=-5862.400, censored-rate=0.100, Δfinal=0.066
- threshold `0.6` / `exact_pretrain_vs_same_operation`: censored Δ=0.000, censored-rate=0.000, Δfinal=0.000
- threshold `0.6` / `exact_pretrain_vs_different_operation`: censored Δ=0.000, censored-rate=0.000, Δfinal=0.209
- threshold `0.6` / `exact_strong_corrupt_vs_same_operation`: censored Δ=0.000, censored-rate=0.000, Δfinal=-0.133
- threshold `0.6` / `exact_strong_corrupt_vs_different_operation`: censored Δ=0.000, censored-rate=0.000, Δfinal=-0.132
- threshold `0.6` / `exact_strong_delay_vs_same_operation`: censored Δ=-1689.600, censored-rate=0.000, Δfinal=0.062
- threshold `0.6` / `exact_strong_delay_vs_different_operation`: censored Δ=-1689.600, censored-rate=0.000, Δfinal=0.066
- threshold `0.7` / `exact_pretrain_vs_same_operation`: censored Δ=0.000, censored-rate=0.000, Δfinal=0.000
- threshold `0.7` / `exact_pretrain_vs_different_operation`: censored Δ=0.000, censored-rate=0.000, Δfinal=0.209
- threshold `0.7` / `exact_strong_corrupt_vs_same_operation`: censored Δ=0.000, censored-rate=0.000, Δfinal=-0.133
- threshold `0.7` / `exact_strong_corrupt_vs_different_operation`: censored Δ=0.000, censored-rate=0.000, Δfinal=-0.132
- threshold `0.7` / `exact_strong_delay_vs_same_operation`: censored Δ=0.000, censored-rate=0.000, Δfinal=0.062
- threshold `0.7` / `exact_strong_delay_vs_different_operation`: censored Δ=0.000, censored-rate=0.000, Δfinal=0.066

## AUC note
- `baseline`: mean AUC=0.132
- `corrupt_component_strong`: mean AUC=0.077
- `corrupt_different_operation_matched_strong`: mean AUC=0.125
- `corrupt_same_operation_unrelated_strong`: mean AUC=0.117
- `delay_component_strong`: mean AUC=0.151
- `delay_different_operation_matched_strong`: mean AUC=0.133
- `delay_same_operation_unrelated_strong`: mean AUC=0.132
- `pretrain_component`: mean AUC=0.138
- `pretrain_different_operation_matched`: mean AUC=0.057
- `pretrain_same_operation_unrelated`: mean AUC=0.138

## Interpretation rule
If contrasts appear only at very low thresholds, interpret them as subthreshold learning shifts rather than clear acquisition. If no threshold shows contrast and final/AUC are flat, the pair is non-informative. If exact-component contrasts persist across moderate thresholds and final/AUC agree, the result is stronger.