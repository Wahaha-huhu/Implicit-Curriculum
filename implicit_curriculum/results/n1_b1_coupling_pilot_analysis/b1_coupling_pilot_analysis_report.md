# B1 N1 cross-task coupling pilot analysis

This analysis estimates directional interaction effects from source-dose slopes and tests whether early coupling predictors track those effects.

## Data
- result_dir: `results/n1_b1_coupling_pilot`
- outcome rows: `144`
- predictor rows: `288`
- seed-level effect rows: `36`
- pair summary rows: `12`

## Pilot gate diagnostics
- primary effect column: `mean_slope_target_auc_token_accuracy`
- n_pairs: `12`
- effect std: `0.03830718184204614`
- nonzero effect rate |effect|>1e-4: `1.0`

## Best predictor correlations
- `mean_gradient_cosine` vs `mean_slope_target_auc_token_accuracy`: r=`0.5783445623247255`, sign_acc=`0.6666666666666666`, n=`12`
- `mean_source_gradient_norm` vs `mean_slope_target_final_loss`: r=`0.5582126632922041`, sign_acc=`0.25`, n=`12`
- `mean_first_order_transfer_score` vs `mean_slope_target_auc_token_accuracy`: r=`0.5524870701642006`, sign_acc=`0.6666666666666666`, n=`12`
- `mean_gradient_inner_product` vs `mean_slope_target_auc_token_accuracy`: r=`0.5524870701642006`, sign_acc=`0.6666666666666666`, n=`12`
- `mean_target_gradient_norm` vs `mean_slope_target_final_loss`: r=`0.4847869535235597`, sign_acc=`0.25`, n=`12`
- `mean_target_gradient_snr` vs `mean_slope_target_final_loss`: r=`0.45659563021095695`, sign_acc=`0.25`, n=`12`
- `mean_target_gradient_norm` vs `mean_slope_target_final_token_accuracy`: r=`-0.45280925270865025`, sign_acc=`0.8333333333333334`, n=`12`
- `mean_gradient_cosine` vs `mean_slope_target_final_token_accuracy`: r=`0.44727576910705197`, sign_acc=`0.8333333333333334`, n=`12`
- `mean_source_gradient_snr` vs `mean_slope_target_final_loss`: r=`0.42273753572192185`, sign_acc=`0.25`, n=`12`
- `mean_target_gradient_snr` vs `mean_slope_target_final_token_accuracy`: r=`-0.4142411130987147`, sign_acc=`0.8333333333333334`, n=`12`

## How to read this pilot
This pilot is not a thesis-grade claim. It decides whether the next full N1 run is worth launching: the interaction effects should have nontrivial variance, the dose-response should not be dominated by failed/non-learning targets, and the leading predictors should not be degenerate.