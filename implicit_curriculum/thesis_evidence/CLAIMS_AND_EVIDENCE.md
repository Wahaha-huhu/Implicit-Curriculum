# Claims and Evidence Map

This file maps possible thesis claims to current evidence. Claims should not be strengthened beyond the evidence status here.

| Claim ID | Draft claim | Tier | Current status | Supporting evidence | Caveats |
|---|---|---:|---|---|---|
| C0 | The analysis pipeline can recover known synthetic acquisition mechanisms before neural training. | gate | green | Exp 0 recovery gate | Synthetic only; no neural-training claim. |
| C1 | Sparse parity provides a frequency-dominated/quanta-style baseline. | 2 | yellow-green | B2 sparse parity analysis | Acquisition coverage modest; rerun with easier degrees/higher budget for final. |
| C2 | B1 sequence DSL is a usable controlled transformer substrate. | gate/2 | green | B1 calibration and pilot | Token accuracy/loss are primary; exact match is strict and lower. |
| C3 | In B1, reference learnability robustly predicts later acquisition across configs. | 2 | green pilot | H1 shared sweep | Pilot scale; should be rerun for final with archival path and maybe larger model/seeds. |
| C4 | In B1, frequency has a stable but weaker expected-direction effect, strongest in atomics. | 2 | green pilot with caveat | H1 shared sweep | Frequency is weak overall and reversed within composites. |
| C5 | The dominant atomic predictor drifts by configuration rather than obeying a universal scalar law. | 2 | green pilot | H2 selected models | Need final rerun/expanded configs for thesis-strength. |
| C6 | Atomic parallel-rate models leave structured composite residuals. | 2 | green pilot | H2 composite residuals | Observational only; does not imply dependency. |
| C7 | C06 is a principled candidate for dependency intervention. | gate to Tier 1 | green | H2 pair selection | Pair selection only; not a causal result. |
| C8 | The first C06 intervention does not support exact-component developmental dependency. | 1 controlled pilot, negative/mixed | yellow/red | H3 C06 intervention | Control design suggests operation-family transfer; must improve H3. |
| C9 | C06 likely benefits from operation-family transfer, not exact-component reuse. | hypothesis | yellow | H3 contrast: component vs same-operation unrelated | Needs explicit same-operation vs different-operation controls. |

## Current safe thesis wording

Safe:

> In the controlled B1 sequence-DSL transformer pilot, reference learnability robustly predicts acquisition order across a one-axis configuration sweep. Frequency has a weaker but stable expected-direction effect overall and in atomics. Atomic acquisition can be modeled by simple one-factor predictors, but which factor dominates drifts with configuration. Composite residuals identify candidate dependency pairs, but the first intervention test suggests operation-family transfer rather than exact-component dependency.

Unsafe:

> We have shown that LLMs learn capabilities through causal developmental dependency.

Unsafe:

> Frequency universally determines acquisition order.

Unsafe:

> The C06 intervention proves component A02 causally enables C06.
