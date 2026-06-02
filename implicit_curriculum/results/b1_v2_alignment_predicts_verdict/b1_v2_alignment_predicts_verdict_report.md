# B1 v2 alignment predicts causal verdict

This analysis treats the causal-census verdict as ground truth and tests whether early mediator features, especially exact component→composite gradient alignment, predict exact-component dependency.

Joined pairs: `4`; positive verdict `exact_component_dependency`: `0`.

## AUC by score
- `exact_gradient_cosine`: AUC=nan (n=4)
- `exact_minus_same_operation_gradient_cosine`: AUC=nan (n=4)
- `exact_minus_different_operation_gradient_cosine`: AUC=nan (n=4)
- `min_exact_minus_control_gradient_cosine`: AUC=nan (n=4)
- `exact_linear_cka`: AUC=nan (n=4)
- `min_exact_minus_control_linear_cka`: AUC=nan (n=4)

## Leave-family-out check
No leave-family-out AUC was available; add a family column to the census plan/verdict table for this stronger generalization check.

## Interpretation boundary
A high AUC supports gradient alignment as a cheap leading indicator of the expensive intervention verdict. It does not replace the intervention census; it is validated against it.