from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from ic_experiments.run_management import append_registry, write_manifest


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Combine multiple B1 H3 pair-specific analyses into a thesis-ready evidence summary.")
    p.add_argument("--row-dirs", type=Path, nargs="+", required=True, help="Directories containing analyzed H3 row outputs.")
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--code-version", type=str, default="v1.2")
    p.add_argument("--run-id", type=str, default="h3_multirow_summary")
    p.add_argument("--archive-root", type=Path, default=None)
    p.add_argument("--thesis-use", type=str, default="candidate")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    row_summaries = []
    contrast_parts = []
    condition_parts = []
    for i, d in enumerate(args.row_dirs):
        pair = load_pair(d)
        contrasts = pd.read_csv(d / "h3_intervention_contrasts.csv") if (d / "h3_intervention_contrasts.csv").exists() else pd.DataFrame()
        pair_summary = pd.read_csv(d / "h3_pair_summary.csv") if (d / "h3_pair_summary.csv").exists() else pd.DataFrame()
        row_id = f"row{i}_{pair.get('component','component')}_to_{pair.get('composite','composite')}"
        if not contrasts.empty:
            contrasts.insert(0, "row_id", row_id)
            for k, v in pair.items():
                contrasts[k] = v
            contrast_parts.append(contrasts)
        if not pair_summary.empty:
            pair_summary.insert(0, "row_id", row_id)
            for k, v in pair.items():
                pair_summary[k] = v
            condition_parts.append(pair_summary)
        row_summaries.append(summarize_row(row_id, pair, contrasts, pair_summary, d))

    row_df = pd.DataFrame(row_summaries)
    contrast_df = pd.concat(contrast_parts, ignore_index=True) if contrast_parts else pd.DataFrame()
    condition_df = pd.concat(condition_parts, ignore_index=True) if condition_parts else pd.DataFrame()
    row_df.to_csv(args.output_dir / "h3_multirow_component_summary.csv", index=False)
    contrast_df.to_csv(args.output_dir / "h3_multirow_contrast_summary.csv", index=False)
    condition_df.to_csv(args.output_dir / "h3_multirow_condition_summary.csv", index=False)
    report = make_report(row_df, contrast_df, condition_df, args.row_dirs)
    (args.output_dir / "h3_multirow_analysis_report.md").write_text(report, encoding="utf-8")

    manifest = write_manifest(
        args.output_dir,
        experiment="B1_H3_multirow_summary",
        backend="B1_sequence_dsl",
        code_version=args.code_version,
        run_id=args.run_id,
        command=sys.argv,
        input_paths={"row_dirs": [str(p) for p in args.row_dirs]},
        extra={"thesis_use": args.thesis_use},
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
                "output_path": str(args.output_dir),
                "status": "analyzed",
                "thesis_use": args.thesis_use,
                "created_at_utc": manifest["created_at_utc"],
            },
        )
    print("Saved B1 H3 multirow summary outputs:")
    for name in ["h3_multirow_analysis_report.md", "h3_multirow_component_summary.csv", "h3_multirow_contrast_summary.csv", "h3_multirow_condition_summary.csv", "run_manifest.json"]:
        print(f"  {args.output_dir / name}")


def load_pair(result_dir: Path) -> dict[str, str]:
    path = result_dir / "h3_pair_config.csv"
    if path.exists():
        df = pd.read_csv(path)
        if not df.empty:
            return {k: str(v) for k, v in df.iloc[0].to_dict().items() if str(v) != "nan"}
    manifest = result_dir / "run_manifest.json"
    if manifest.exists():
        data = json.loads(manifest.read_text(encoding="utf-8"))
        if "pair" in data:
            return {k: str(v) for k, v in data["pair"].items()}
        if "extra" in data and "pair" in data["extra"]:
            return {k: str(v) for k, v in data["extra"]["pair"].items()}
    return {"component": result_dir.name, "composite": "unknown"}


def summarize_row(row_id: str, pair: dict[str, str], contrasts: pd.DataFrame, pair_summary: pd.DataFrame, result_dir: Path) -> dict[str, Any]:
    def get_rate(pattern: str, col: str = "censored_expected_direction_rate") -> float:
        if contrasts.empty or "contrast_type" not in contrasts.columns:
            return np.nan
        sub = contrasts[contrasts["contrast_type"].astype(str).str.contains(pattern, na=False)]
        return float(sub[col].mean()) if not sub.empty and col in sub.columns else np.nan

    def get_delta(pattern: str, col: str) -> float:
        if contrasts.empty or "contrast_type" not in contrasts.columns:
            return np.nan
        sub = contrasts[contrasts["contrast_type"].astype(str).str.contains(pattern, na=False)]
        return float(sub[col].mean()) if not sub.empty and col in sub.columns else np.nan

    up_exact_same = get_rate("exact_vs_same_operation")
    up_exact_diff = get_rate("exact_vs_different_operation")
    corrupt_same = get_rate("exact_corrupt_vs_same_operation")
    delay_same = get_rate("exact_delay_vs_same_operation")
    pretrain_same = get_rate("exact_pretrain_vs_same_operation")
    verdict = classify(up_exact_same, up_exact_diff, corrupt_same, delay_same, pretrain_same)
    return {
        "row_id": row_id,
        "result_dir": str(result_dir),
        "component": pair.get("component", ""),
        "composite": pair.get("composite", ""),
        "same_operation_control": pair.get("same_operation_control", ""),
        "different_operation_control": pair.get("different_operation_control", ""),
        "upweight_exact_vs_same_rate": up_exact_same,
        "upweight_exact_vs_diff_rate": up_exact_diff,
        "upweight_exact_vs_same_censored_delta": get_delta("exact_vs_same_operation", "censored_delta_acquired_at_mean"),
        "upweight_exact_vs_diff_censored_delta": get_delta("exact_vs_different_operation", "censored_delta_acquired_at_mean"),
        "corrupt_exact_vs_same_rate": corrupt_same,
        "delay_exact_vs_same_rate": delay_same,
        "pretrain_exact_vs_same_rate": pretrain_same,
        "mean_censored_expected_direction_rate": float(contrasts["censored_expected_direction_rate"].mean()) if not contrasts.empty and "censored_expected_direction_rate" in contrasts else np.nan,
        "mean_final_expected_direction_rate": float(contrasts["final_metric_expected_direction_rate"].mean()) if not contrasts.empty and "final_metric_expected_direction_rate" in contrasts else np.nan,
        "verdict": verdict,
    }


def classify(up_same: float, up_diff: float, corrupt_same: float, delay_same: float, pretrain_same: float) -> str:
    vals = [v for v in [up_same, up_diff, corrupt_same, delay_same, pretrain_same] if np.isfinite(v)]
    if len(vals) == 0:
        return "insufficient"
    # Upweight/pretrain are the cleanest acceleration tests; corruption is supportive; delay is noisy.
    if np.isfinite(up_same) and np.isfinite(up_diff) and up_same >= 0.75 and up_diff >= 0.75:
        if (not np.isfinite(corrupt_same) or corrupt_same >= 0.5) and (not np.isfinite(pretrain_same) or pretrain_same >= 0.6):
            return "promising_exact_component_partial"
    if np.isfinite(up_same) and up_same >= 0.6 and (np.isfinite(corrupt_same) and corrupt_same >= 0.6):
        return "partial_exact_component_signal"
    if np.nanmean(vals) >= 0.55:
        return "mixed_weak_positive"
    return "weak_or_negative"


def make_report(row_df: pd.DataFrame, contrast_df: pd.DataFrame, condition_df: pd.DataFrame, row_dirs: list[Path]) -> str:
    lines = [
        "# B1 H3 multi-row summary",
        "",
        "This report combines pair-specific H3 analyses. It is intended for thesis evidence tracking: it separates exact-component dependency, operation-family transfer, and weak/negative controls.",
        "",
        "## Inputs",
    ]
    for d in row_dirs:
        lines.append(f"- `{d}`")
    lines += ["", "## Row verdicts"]
    if row_df.empty:
        lines.append("No rows available.")
    else:
        for _, r in row_df.iterrows():
            lines.append(
                f"- `{r['component']}` → `{r['composite']}`: verdict=`{r['verdict']}`, "
                f"upweight exact-vs-same rate={fmt(r['upweight_exact_vs_same_rate'])}, "
                f"upweight exact-vs-different rate={fmt(r['upweight_exact_vs_diff_rate'])}, "
                f"corrupt exact-vs-same rate={fmt(r['corrupt_exact_vs_same_rate'])}, "
                f"delay exact-vs-same rate={fmt(r['delay_exact_vs_same_rate'])}"
            )
    lines += ["", "## Combined interpretation"]
    if not row_df.empty:
        promising = row_df[row_df["verdict"].astype(str).str.contains("promising|partial", na=False)]
        weak = row_df[row_df["verdict"].astype(str).str.contains("weak|negative", na=False)]
        if len(promising) and len(weak):
            lines.append("The current evidence is component-specific rather than uniformly positive: at least one component shows an exact-component signal, while another component is weak or negative. This supports using H3 to map where dependency holds, not claiming a universal composite dependency mechanism yet.")
        elif len(promising) == len(row_df):
            lines.append("All analyzed rows show at least partial exact-component signals. This is promising, but still requires replication and preferably a model-state intervention before a strong causal claim.")
        else:
            lines.append("The analyzed rows do not yet support exact-component dependency. Treat H3 evidence as negative/mixed and improve controls or model-state interventions.")
    lines += [
        "",
        "## Thesis-safe wording",
        "Current H3 evidence should be described as pilot and pair-specific. Do not state that the controlled B1 setting proves developmental dependency until exact-component effects replicate across components/families and at least one model-state intervention agrees.",
    ]
    return "\n".join(lines)


def fmt(x: Any) -> str:
    try:
        if pd.isna(x):
            return "nan"
        return f"{float(x):.3f}"
    except Exception:
        return str(x)


if __name__ == "__main__":
    main()
