# B1 reference-learnability proxy audit

This audit checks whether `reference_learnability` behaves like the intended difficulty proxy or is confounded with operation type / output statistics in this family.

Metric: `token_accuracy` threshold `0.7`

## Key correlations
- `all`: learnability vs `composition_depth` Spearman=0.457 (n=25)
- `all`: learnability vs `copy_fraction` Spearman=-0.292 (n=25)
- `all`: learnability vs `frequency` Spearman=0.319 (n=25)
- `all`: learnability vs `mean_censored_acquired_at` Spearman=-0.318 (n=25)
- `all`: learnability vs `mean_final_metric` Spearman=0.301 (n=25)
- `all`: learnability vs `output_entropy` Spearman=0.203 (n=25)
- `all`: learnability vs `random_baseline_token_accuracy` Spearman=nan (n=25)
- `kind=atomic`: learnability vs `composition_depth` Spearman=nan (n=8)
- `kind=atomic`: learnability vs `copy_fraction` Spearman=-0.600 (n=8)
- `kind=atomic`: learnability vs `frequency` Spearman=0.315 (n=8)
- `kind=atomic`: learnability vs `mean_censored_acquired_at` Spearman=-0.570 (n=8)
- `kind=atomic`: learnability vs `mean_final_metric` Spearman=0.567 (n=8)
- `kind=atomic`: learnability vs `output_entropy` Spearman=nan (n=8)
- `kind=atomic`: learnability vs `random_baseline_token_accuracy` Spearman=nan (n=8)
- `kind=composite`: learnability vs `composition_depth` Spearman=nan (n=8)
- `kind=composite`: learnability vs `copy_fraction` Spearman=nan (n=8)
- `kind=composite`: learnability vs `frequency` Spearman=nan (n=8)
- `kind=composite`: learnability vs `mean_censored_acquired_at` Spearman=nan (n=8)
- `kind=composite`: learnability vs `mean_final_metric` Spearman=nan (n=8)
- `kind=composite`: learnability vs `output_entropy` Spearman=nan (n=8)
- `kind=composite`: learnability vs `random_baseline_token_accuracy` Spearman=nan (n=8)
- `true_tasks_atomic_composite`: learnability vs `composition_depth` Spearman=0.934 (n=16)
- `true_tasks_atomic_composite`: learnability vs `copy_fraction` Spearman=-0.234 (n=16)
- `true_tasks_atomic_composite`: learnability vs `frequency` Spearman=0.255 (n=16)
- `true_tasks_atomic_composite`: learnability vs `mean_censored_acquired_at` Spearman=-0.432 (n=16)
- `true_tasks_atomic_composite`: learnability vs `mean_final_metric` Spearman=0.294 (n=16)
- `true_tasks_atomic_composite`: learnability vs `output_entropy` Spearman=0.241 (n=16)
- `true_tasks_atomic_composite`: learnability vs `random_baseline_token_accuracy` Spearman=nan (n=16)

## Interpretation rule
If reference_learnability correlates with earlier acquisition or higher final metric, it is not functioning as a simple 'harder means later' variable in this family. Treat it as a family-specific structural proxy and avoid universal learnability claims.