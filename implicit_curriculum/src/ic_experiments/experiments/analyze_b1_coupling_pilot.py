from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from ic_experiments.coupling import bootstrap_ci, linear_slope
from ic_experiments.run_management import append_registry, write_manifest


OUTCOME_COLUMNS = [
    "target_final_token_accuracy",
    "target_auc_token_accuracy",
    "target_final_exact_match",
    "target_auc_exact_match",
    "target_final_loss",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Analyze N1 B1 cross-task coupling pilot outputs.")
    p.add_argument("--result-dir", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, default=None)
    p.add_argument("--bootstrap-samples", type=int, default=2000)
    p.add_argument("--predictor-stage", type=str, default="early", choices=["init", "early"])
    p.add_argument("--predictor-multiplier", type=float, default=1.0, help="Use predictors from this source multiplier as the leading-indicator baseline.")
    p.add_argument("--code-version", type=str, default="n1.0")
    p.add_argument("--run-id", type=str, default=None)
    p.add_argument("--archive-root", type=Path, default=None)
    p.add_argument("--thesis-use", type=str, default="candidate")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    result_dir = args.result_dir
    out = args.output_dir or (result_dir / "analysis")
    out.mkdir(parents=True, exist_ok=True)

    outcomes = pd.read_csv(result_dir / "target_outcomes.csv")
    predictors = pd.read_csv(result_dir / "early_coupling_predictors.csv")
    pair_plan_path = result_dir / "b1_coupling_pair_plan.csv"
    pair_plan = pd.read_csv(pair_plan_path) if pair_plan_path.exists() else pd.DataFrame()

    per_seed = estimate_seed_slopes(outcomes)
    per_seed.to_csv(out / "b1_coupling_seed_interaction_effects.csv", index=False)
    pair_summary = summarize_pair_effects(per_seed, args.bootstrap_samples)
    pair_summary.to_csv(out / "b1_coupling_pair_interaction_summary.csv", index=False)

    predictor_summary = summarize_predictors(predictors, args.predictor_stage, args.predictor_multiplier)
    predictor_summary.to_csv(out / "b1_coupling_pair_predictor_summary.csv", index=False)

    merged = pair_summary.merge(predictor_summary, on="pair_id", how="left", suffixes=("", "_predictor"))
    if not pair_plan.empty:
        keep_cols = [c for c in pair_plan.columns if c not in merged.columns or c == "pair_id"]
        merged = merged.merge(pair_plan[keep_cols], on="pair_id", how="left")
    merged.to_csv(out / "b1_coupling_predictor_vs_interaction.csv", index=False)

    correlations = predictor_correlations(merged)
    correlations.to_csv(out / "b1_coupling_predictor_correlations.csv", index=False)

    gate = pilot_gate_summary(merged, correlations)
    (out / "b1_coupling_pilot_analysis_report.md").write_text(render_report(args, outcomes, predictors, per_seed, merged, correlations, gate), encoding="utf-8")
    (out / "summary.json").write_text(
        json.dumps(
            {
                "experiment": "N1_B1_cross_task_coupling_pilot_analysis",
                "result_dir": str(result_dir),
                "n_pairs": int(merged["pair_id"].nunique()) if "pair_id" in merged else 0,
                "n_outcome_rows": int(len(outcomes)),
                "n_predictor_rows": int(len(predictors)),
                "pilot_gate": gate,
                "paths": {
                    "seed_interaction_effects": str(out / "b1_coupling_seed_interaction_effects.csv"),
                    "pair_interaction_summary": str(out / "b1_coupling_pair_interaction_summary.csv"),
                    "predictor_vs_interaction": str(out / "b1_coupling_predictor_vs_interaction.csv"),
                    "predictor_correlations": str(out / "b1_coupling_predictor_correlations.csv"),
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    manifest = write_manifest(
        out,
        experiment="N1_B1_cross_task_coupling_pilot_analysis",
        backend="B1_sequence_dsl",
        code_version=args.code_version,
        run_id=args.run_id or "b1_coupling_pilot_analysis",
        command=sys.argv,
        input_paths={"result_dir": str(result_dir)},
        extra={"thesis_use": args.thesis_use, "pilot_gate": gate},
    )
    if args.archive_root is not None:
        append_registry(
            args.archive_root / "results_registry.csv",
            {
                "run_id": manifest["run_id"],
                "code_version": args.code_version,
                "git_sha": manifest["git_sha"],
                "experiment": manifest["experiment"],
                "backend": manifest["backend"],
                "output_path": str(out),
                "status": "analyzed",
                "thesis_use": args.thesis_use,
                "created_at_utc": manifest["created_at_utc"],
            },
        )

    print("Saved B1 coupling pilot analysis outputs:")
    for name in ["b1_coupling_pilot_analysis_report.md", "b1_coupling_seed_interaction_effects.csv", "b1_coupling_pair_interaction_summary.csv", "b1_coupling_predictor_vs_interaction.csv", "b1_coupling_predictor_correlations.csv", "run_manifest.json"]:
        print(f"  {out / name}")


def estimate_seed_slopes(outcomes: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    group_cols = ["pair_id", "pair_type", "source_task", "target_task", "filler_task", "seed"]
    for keys, g in outcomes.groupby(group_cols, dropna=False):
        pair_id, pair_type, source, target, filler, seed = keys
        x = g["source_multiplier"].astype(float).to_numpy()
        row = {
            "pair_id": pair_id,
            "pair_type": pair_type,
            "source_task": source,
            "target_task": target,
            "filler_task": filler,
            "seed": int(seed),
            "n_dose_levels": int(g["source_multiplier"].nunique()),
        }
        for col in OUTCOME_COLUMNS:
            if col in g.columns:
                row[f"slope_{col}"] = linear_slope(x, g[col].astype(float).to_numpy())
        if "target_acquired_at" in g.columns:
            acq = g["target_acquired_at"].astype(float).to_numpy()
            max_seen = float(g["max_data_seen"].iloc[0]) if "max_data_seen" in g.columns else np.nan
            # Earlier acquisition is beneficial, so reverse the sign and normalize.
            slope_acq = linear_slope(x, acq)
            row["slope_target_acquisition_transfer"] = float(-slope_acq / max(1.0, max_seen)) if np.isfinite(slope_acq) else float("nan")
        rows.append(row)
    return pd.DataFrame(rows)


def summarize_pair_effects(per_seed: pd.DataFrame, n_bootstrap: int) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    effect_cols = [c for c in per_seed.columns if c.startswith("slope_")]
    base_cols = ["pair_id", "pair_type", "source_task", "target_task", "filler_task"]
    for keys, g in per_seed.groupby(base_cols, dropna=False):
        row = dict(zip(base_cols, keys))
        row["n_seeds"] = int(g["seed"].nunique())
        for c in effect_cols:
            mean, lo, hi = bootstrap_ci(g[c].astype(float).to_numpy(), n_bootstrap=n_bootstrap, seed=stable_int_seed(str(keys) + c))
            row[f"mean_{c}"] = mean
            row[f"ci_low_{c}"] = lo
            row[f"ci_high_{c}"] = hi
            row[f"positive_rate_{c}"] = float(np.nanmean(g[c].astype(float).to_numpy() > 0)) if len(g) else float("nan")
        rows.append(row)
    return pd.DataFrame(rows)


def summarize_predictors(predictors: pd.DataFrame, stage: str, multiplier: float) -> pd.DataFrame:
    pred = predictors.copy()
    if "probe_stage" in pred.columns:
        pred = pred[pred["probe_stage"].astype(str).eq(stage)].copy()
    if "source_multiplier" in pred.columns:
        # Prefer baseline multiplier, but fall back to all rows if absent.
        base = pred[np.isclose(pred["source_multiplier"].astype(float), float(multiplier))].copy()
        if not base.empty:
            pred = base
    predictor_cols = [
        "gradient_cosine",
        "gradient_inner_product",
        "first_order_transfer_score",
        "source_gradient_norm",
        "target_gradient_norm",
        "source_gradient_snr",
        "target_gradient_snr",
        "linear_cka",
    ]
    rows = []
    for pair_id, g in pred.groupby("pair_id"):
        row = {"pair_id": pair_id, "predictor_stage": stage, "predictor_multiplier": float(multiplier), "n_predictor_rows": int(len(g))}
        for c in predictor_cols:
            if c in g.columns:
                row[f"mean_{c}"] = float(np.nanmean(g[c].astype(float)))
                row[f"std_{c}"] = float(np.nanstd(g[c].astype(float)))
        rows.append(row)
    return pd.DataFrame(rows)


def predictor_correlations(merged: pd.DataFrame) -> pd.DataFrame:
    pred_cols = [c for c in merged.columns if c.startswith("mean_") and any(k in c for k in ["gradient", "cka", "transfer_score"])]
    # Primary outcomes are AUC/final accuracy transfer slopes.
    outcome_cols = [c for c in merged.columns if c.startswith("mean_slope_target_")]
    rows = []
    for p in pred_cols:
        for o in outcome_cols:
            x = pd.to_numeric(merged[p], errors="coerce").to_numpy(dtype=float)
            y = pd.to_numeric(merged[o], errors="coerce").to_numpy(dtype=float)
            ok = np.isfinite(x) & np.isfinite(y)
            if ok.sum() < 3 or np.nanstd(x[ok]) <= 1e-12 or np.nanstd(y[ok]) <= 1e-12:
                corr = float("nan")
            else:
                corr = float(np.corrcoef(x[ok], y[ok])[0, 1])
            sign_acc = sign_accuracy(x[ok], y[ok]) if ok.sum() else float("nan")
            rows.append({"predictor": p, "outcome": o, "n_pairs": int(ok.sum()), "pearson_r": corr, "sign_accuracy": sign_acc})
    return pd.DataFrame(rows)


def sign_accuracy(x: np.ndarray, y: np.ndarray) -> float:
    if len(x) == 0:
        return float("nan")
    ok = np.isfinite(x) & np.isfinite(y) & (np.abs(x) > 1e-12) & (np.abs(y) > 1e-12)
    if ok.sum() == 0:
        return float("nan")
    return float(np.mean(np.sign(x[ok]) == np.sign(y[ok])))


def pilot_gate_summary(merged: pd.DataFrame, correlations: pd.DataFrame) -> dict[str, Any]:
    primary = "mean_slope_target_auc_token_accuracy"
    if primary not in merged.columns:
        primary = "mean_slope_target_final_token_accuracy"
    effects = pd.to_numeric(merged.get(primary, pd.Series(dtype=float)), errors="coerce").to_numpy(dtype=float)
    effect_var = float(np.nanstd(effects)) if len(effects) else float("nan")
    nonzero_rate = float(np.nanmean(np.abs(effects) > 1e-4)) if len(effects) else float("nan")
    best = correlations.sort_values("pearson_r", key=lambda s: s.abs(), ascending=False).head(1) if not correlations.empty else pd.DataFrame()
    return {
        "primary_effect_column": primary,
        "n_pairs": int(merged["pair_id"].nunique()) if "pair_id" in merged else 0,
        "effect_std": effect_var,
        "nonzero_effect_rate_abs_gt_1e_minus_4": nonzero_rate,
        "best_abs_correlation": None if best.empty else best.iloc[0].to_dict(),
        "pilot_interpretation": "proceed_if_effects_have_variance_and_predictors_are_not_degenerate",
    }


def render_report(args: argparse.Namespace, outcomes: pd.DataFrame, predictors: pd.DataFrame, per_seed: pd.DataFrame, merged: pd.DataFrame, correlations: pd.DataFrame, gate: dict[str, Any]) -> str:
    lines = [
        "# B1 N1 cross-task coupling pilot analysis",
        "",
        "This analysis estimates directional interaction effects from source-dose slopes and tests whether early coupling predictors track those effects.",
        "",
        "## Data",
        f"- result_dir: `{args.result_dir}`",
        f"- outcome rows: `{len(outcomes)}`",
        f"- predictor rows: `{len(predictors)}`",
        f"- seed-level effect rows: `{len(per_seed)}`",
        f"- pair summary rows: `{len(merged)}`",
        "",
        "## Pilot gate diagnostics",
        f"- primary effect column: `{gate.get('primary_effect_column')}`",
        f"- n_pairs: `{gate.get('n_pairs')}`",
        f"- effect std: `{gate.get('effect_std')}`",
        f"- nonzero effect rate |effect|>1e-4: `{gate.get('nonzero_effect_rate_abs_gt_1e_minus_4')}`",
        "",
        "## Best predictor correlations",
    ]
    if correlations.empty:
        lines.append("No correlations were estimable. This usually means too few pairs or degenerate effects/predictors.")
    else:
        show = correlations.sort_values("pearson_r", key=lambda s: s.abs(), ascending=False).head(10)
        for _, r in show.iterrows():
            lines.append(f"- `{r['predictor']}` vs `{r['outcome']}`: r=`{r['pearson_r']}`, sign_acc=`{r['sign_accuracy']}`, n=`{int(r['n_pairs'])}`")
    lines.extend(
        [
            "",
            "## How to read this pilot",
            "This pilot is not a thesis-grade claim. It decides whether the next full N1 run is worth launching: the interaction effects should have nontrivial variance, the dose-response should not be dominated by failed/non-learning targets, and the leading predictors should not be degenerate.",
        ]
    )
    return "\n".join(lines)


def stable_int_seed(s: str) -> int:
    return int(abs(hash(s)) % (2**31 - 1))


if __name__ == "__main__":
    main()
