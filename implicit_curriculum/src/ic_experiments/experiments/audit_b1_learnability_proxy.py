from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from ic_experiments.run_management import append_registry, write_manifest
from ic_experiments.sequence_analysis import spearman, final_metrics
from ic_experiments.metrics import acquisition_times


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Audit the B1 reference_learnability proxy against task descriptors and observed acquisition.")
    p.add_argument("--h1-result-dir", type=Path, required=True)
    p.add_argument("--metric-family", type=str, default="token_accuracy")
    p.add_argument("--threshold", type=float, default=0.7)
    p.add_argument("--output-dir", type=Path, default=None)
    p.add_argument("--code-version", type=str, default="v2.1")
    p.add_argument("--archive-root", type=Path, default=None)
    p.add_argument("--thesis-use", type=str, default="diagnostic")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    outdir = args.output_dir or (args.h1_result_dir / "learnability_proxy_audit")
    outdir.mkdir(parents=True, exist_ok=True)
    structure = pd.read_csv(args.h1_result_dir / "structure_table.csv")
    diff_path = args.h1_result_dir / "sequence_difficulty_table.csv"
    difficulty = pd.read_csv(diff_path) if diff_path.exists() else pd.DataFrame()
    eval_df = pd.read_csv(args.h1_result_dir / "eval_curves.csv")
    final = final_metrics(eval_df)
    acq = acquisition_times(eval_df, threshold=args.threshold, patience=2, metric=args.metric_family)
    obs = acq.copy()
    obs["censored_acquired_at"] = obs["acquired_at"].fillna(eval_df.groupby(["condition", "seed"])["data_seen"].transform("max").max())
    final_col = args.metric_family if args.metric_family in final.columns else "token_accuracy"
    final_agg = final.groupby("task_name", as_index=False).agg(mean_final_metric=(final_col, "mean"))
    acq_agg = obs.groupby("task_name", as_index=False).agg(acquisition_rate=("acquired_at", lambda s: float(s.notna().mean())), mean_censored_acquired_at=("censored_acquired_at", "mean"))
    meta = structure.copy()
    if not difficulty.empty:
        add_cols = [c for c in difficulty.columns if c not in meta.columns or c == "task_name"]
        meta = meta.merge(difficulty[add_cols].drop_duplicates("task_name"), on="task_name", how="left")
    meta = meta.merge(final_agg, on="task_name", how="left").merge(acq_agg, on="task_name", how="left")
    corr_rows = []
    targets = [
        "frequency", "formal_utility", "composition_depth", "output_entropy", "positionwise_entropy_mean",
        "random_baseline_token_accuracy", "copy_fraction", "n_components", "mean_final_metric", "mean_censored_acquired_at", "acquisition_rate",
    ]
    for scope, g in _scopes(meta):
        for col in targets:
            if col in g.columns:
                corr_rows.append({"scope": scope, "x": "reference_learnability", "y": col, "spearman": spearman(g["reference_learnability"], g[col]), "n": int(g[["reference_learnability", col]].dropna().shape[0])})
    corr = pd.DataFrame(corr_rows)
    corr.to_csv(outdir / "learnability_proxy_correlations.csv", index=False)
    meta.to_csv(outdir / "learnability_proxy_task_table.csv", index=False)
    report = make_report(corr, meta, args)
    (outdir / "learnability_proxy_audit_report.md").write_text(report, encoding="utf-8")
    manifest = write_manifest(outdir, experiment="B1_learnability_proxy_audit", backend="B1_sequence_dsl", code_version=args.code_version, run_id="b1_learnability_proxy_audit", command=sys.argv, input_paths={"h1_result_dir": str(args.h1_result_dir)}, extra={"threshold": args.threshold, "metric_family": args.metric_family, "thesis_use": args.thesis_use})
    if args.archive_root is not None:
        append_registry(args.archive_root / "results_registry.csv", {"run_id": manifest["run_id"], "code_version": args.code_version, "git_sha": manifest["git_sha"], "experiment": manifest["experiment"], "backend": manifest["backend"], "output_path": str(outdir), "status": "analyzed", "thesis_use": args.thesis_use, "created_at_utc": manifest["created_at_utc"]})
    print("Saved learnability proxy audit outputs:")
    for name in ["learnability_proxy_audit_report.md", "learnability_proxy_correlations.csv", "learnability_proxy_task_table.csv", "run_manifest.json"]:
        print(f"  {outdir / name}")


def _scopes(df: pd.DataFrame):
    yield "all", df
    if "kind" in df.columns:
        yield "true_tasks_atomic_composite", df[df["kind"].isin(["atomic", "composite"])]
        for kind, g in df.groupby("kind"):
            yield f"kind={kind}", g
    if "op" in df.columns:
        for op, g in df.groupby("op"):
            if len(g) >= 3:
                yield f"op={op}", g


def make_report(corr: pd.DataFrame, meta: pd.DataFrame, args: argparse.Namespace) -> str:
    lines = [
        "# B1 reference-learnability proxy audit",
        "",
        "This audit checks whether `reference_learnability` behaves like the intended difficulty proxy or is confounded with operation type / output statistics in this family.",
        "",
        f"Metric: `{args.metric_family}` threshold `{args.threshold}`",
        "",
        "## Key correlations",
    ]
    key = corr[corr["scope"].isin(["all", "true_tasks_atomic_composite", "kind=atomic", "kind=composite"])]
    for _, r in key.sort_values(["scope", "y"]).iterrows():
        if r["y"] in ["mean_censored_acquired_at", "mean_final_metric", "frequency", "output_entropy", "random_baseline_token_accuracy", "copy_fraction", "composition_depth"]:
            lines.append(f"- `{r['scope']}`: learnability vs `{r['y']}` Spearman={r['spearman']:.3f} (n={int(r['n'])})")
    lines += ["", "## Interpretation rule", "If reference_learnability correlates with earlier acquisition or higher final metric, it is not functioning as a simple 'harder means later' variable in this family. Treat it as a family-specific structural proxy and avoid universal learnability claims."]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
