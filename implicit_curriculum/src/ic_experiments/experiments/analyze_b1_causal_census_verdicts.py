from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from ic_experiments.census import (
    VerdictConfig,
    analyze_pair_result_dir,
    benjamini_hochberg,
    census_verdict_summary,
)
from ic_experiments.run_management import append_registry, write_manifest


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Analyze B1 v2 causal-census verdicts across many H3 row directories.")
    p.add_argument("--census-plan", type=Path, required=True)
    p.add_argument("--census-result-root", type=Path, default=None, help="Directory containing rowNNN_* H3 result dirs. Optional if --run-index is supplied.")
    p.add_argument("--run-index", type=Path, default=None, help="Optional b1_v2_causal_census_run_index.csv.")
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--metric-family", type=str, default="token_accuracy")
    p.add_argument("--threshold", type=float, default=0.7)
    p.add_argument("--patience", type=int, default=2)
    p.add_argument("--min-direction-rate", type=float, default=0.60)
    p.add_argument("--min-abs-censored-delta", type=float, default=0.0)
    p.add_argument("--alpha", type=float, default=0.10)
    p.add_argument("--bootstrap-samples", type=int, default=2000)
    p.add_argument("--code-version", type=str, default="v3.2")
    p.add_argument("--archive-root", type=Path, default=None)
    p.add_argument("--thesis-use", type=str, default="candidate")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    plan = pd.read_csv(args.census_plan)
    dirs = resolve_result_dirs(args, plan)
    cfg = VerdictConfig(
        metric_family=args.metric_family,
        threshold=args.threshold,
        patience=args.patience,
        min_direction_rate=args.min_direction_rate,
        min_abs_censored_delta=args.min_abs_censored_delta,
        alpha=args.alpha,
        bootstrap_samples=args.bootstrap_samples,
    )
    all_contrasts = []
    verdicts = []
    by_pair = {str(r["pair_id"]): r for _, r in plan.iterrows() if "pair_id" in plan.columns}
    for result_dir in dirs:
        try:
            contrasts, verdict = analyze_pair_result_dir(result_dir, cfg, plan_row=by_pair.get(result_dir.name.split("_", 1)[-1]))
            # Stronger match by pair_id after loading.
            if verdict.get("pair_id") in by_pair:
                contrasts, verdict = analyze_pair_result_dir(result_dir, cfg, plan_row=by_pair[verdict["pair_id"]])
            all_contrasts.append(contrasts)
            verdicts.append(verdict)
        except Exception as e:
            verdicts.append({"result_dir": str(result_dir), "verdict": "analysis_failed", "verdict_tier": "excluded", "verdict_reason": str(e)})
    contrast_df = pd.concat(all_contrasts, ignore_index=True) if all_contrasts else pd.DataFrame()
    if not contrast_df.empty and "time_sign_pvalue" in contrast_df.columns:
        contrast_df["time_sign_qvalue_bh"] = benjamini_hochberg(contrast_df["time_sign_pvalue"])
    verdict_df = pd.DataFrame(verdicts)
    summary = census_verdict_summary(verdict_df, bootstrap_samples=args.bootstrap_samples)
    contrast_df.to_csv(args.output_dir / "b1_v2_causal_census_contrasts.csv", index=False)
    verdict_df.to_csv(args.output_dir / "b1_v2_causal_census_pair_verdicts.csv", index=False)
    summary.to_csv(args.output_dir / "b1_v2_causal_census_verdict_summary.csv", index=False)
    (args.output_dir / "b1_v2_causal_census_verdict_report.md").write_text(render_report(verdict_df, summary, contrast_df, args), encoding="utf-8")
    manifest = write_manifest(
        args.output_dir,
        experiment="B1_v2_causal_census_verdict_analysis",
        backend="B1_sequence_dsl",
        code_version=args.code_version,
        run_id="b1_v2_causal_census_verdict_analysis",
        command=sys.argv,
        input_paths={"census_plan": str(args.census_plan), "run_index": str(args.run_index or ""), "census_result_root": str(args.census_result_root or "")},
        extra={"thesis_use": args.thesis_use, "metric_family": args.metric_family, "threshold": args.threshold},
    )
    if args.archive_root is not None:
        append_registry(args.archive_root / "results_registry.csv", {
            "run_id": manifest["run_id"], "code_version": args.code_version, "git_sha": manifest["git_sha"],
            "experiment": manifest["experiment"], "backend": manifest["backend"], "output_path": str(args.output_dir),
            "status": "analyzed", "thesis_use": args.thesis_use, "created_at_utc": manifest["created_at_utc"],
        })
    print("Saved B1 v2 causal-census verdict outputs:")
    for name in ["b1_v2_causal_census_verdict_report.md", "b1_v2_causal_census_pair_verdicts.csv", "b1_v2_causal_census_contrasts.csv", "b1_v2_causal_census_verdict_summary.csv", "run_manifest.json"]:
        print(f"  {args.output_dir / name}")


def resolve_result_dirs(args: argparse.Namespace, plan: pd.DataFrame) -> list[Path]:
    dirs: list[Path] = []
    if args.run_index is not None and args.run_index.exists():
        idx = pd.read_csv(args.run_index)
        if "result_dir" in idx.columns:
            dirs.extend(Path(str(p)) for p in idx["result_dir"].dropna())
    if args.census_result_root is not None and args.census_result_root.exists():
        dirs.extend(sorted(p for p in args.census_result_root.glob("row*_*") if p.is_dir()))
    # Deduplicate and retain only directories with H3 outputs.
    seen = set()
    out = []
    for d in dirs:
        key = str(d)
        if key not in seen:
            seen.add(key)
            if d.exists():
                out.append(d)
    return out


def render_report(verdicts: pd.DataFrame, summary: pd.DataFrame, contrasts: pd.DataFrame, args: argparse.Namespace) -> str:
    lines = [
        "# B1 v2 causal-census verdict report",
        "",
        "This analysis aggregates H3 row-level interventions into the v2 Exp 2 evidence unit: a distribution of causal verdicts over pre-registered pairs.",
        "",
        f"Primary metric: `{args.metric_family}`; threshold `{args.threshold}`; min direction rate `{args.min_direction_rate}`; alpha `{args.alpha}`.",
        "",
        "## Census verdict distribution",
    ]
    if summary.empty:
        lines.append("No verdicts were available.")
    else:
        for _, r in summary.iterrows():
            lines.append(f"- `{r['verdict']}`: {int(r['n_pairs'])}/{int(r['total_pairs'])} = {float(r['fraction']):.3f} [{float(r['fraction_ci_low']):.3f}, {float(r['fraction_ci_high']):.3f}]")
    lines += ["", "## Pair verdict preview"]
    if verdicts.empty:
        lines.append("No pair verdicts were available.")
    else:
        for _, r in verdicts.head(40).iterrows():
            lines.append(f"- `{r.get('component', '')}` → `{r.get('composite', '')}`: `{r.get('verdict', '')}` — {r.get('verdict_reason', '')}")
        if len(verdicts) > 40:
            lines.append(f"- ... {len(verdicts) - 40} additional rows omitted from preview; see CSV.")
    lines += [
        "",
        "## Interpretation boundary",
        "This is causal evidence only inside the controlled Sequence DSL setting. Exact-dependency rows require separation from same-operation and different-operation controls; operation-family rows are not failures but a distinct alternative mechanism under the v2 design.",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
