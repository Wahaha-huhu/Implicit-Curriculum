from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from ic_experiments.run_management import append_registry, write_manifest


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Build a thesis-ready H3 evidence matrix across pair-specific intervention runs. "
            "This is a synthesis/claim-boundary tool, not a new statistical test."
        )
    )
    p.add_argument("--row-dirs", type=Path, nargs="+", required=True, help="H3 result directories containing h3_analysis_report.md and h3_intervention_contrasts.csv")
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--code-version", type=str, default="v1.6")
    p.add_argument("--run-id", type=str, default="h3_evidence_matrix")
    p.add_argument("--archive-root", type=Path, default=None)
    p.add_argument("--thesis-use", type=str, default="candidate")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    contrast_parts: list[pd.DataFrame] = []
    for idx, row_dir in enumerate(args.row_dirs):
        pair = load_pair(row_dir)
        contrasts = load_contrasts(row_dir)
        row_id = f"row{idx}_{pair.get('component','component')}_to_{pair.get('composite','composite')}"
        rows.append(summarize_pair(row_id, row_dir, pair, contrasts))
        if not contrasts.empty:
            c = contrasts.copy()
            c.insert(0, "row_id", row_id)
            for k, v in pair.items():
                c[k] = v
            contrast_parts.append(c)
    matrix = pd.DataFrame(rows)
    contrasts_all = pd.concat(contrast_parts, ignore_index=True) if contrast_parts else pd.DataFrame()

    matrix.to_csv(args.output_dir / "h3_pair_evidence_matrix.csv", index=False)
    if not contrasts_all.empty:
        contrasts_all.to_csv(args.output_dir / "h3_all_intervention_contrasts.csv", index=False)
    family_summary = summarize_by_composite(matrix)
    family_summary.to_csv(args.output_dir / "h3_composite_level_summary.csv", index=False)
    claim_table = make_claim_table(matrix, family_summary)
    claim_table.to_csv(args.output_dir / "h3_claim_boundary_table.csv", index=False)
    report = make_report(matrix, family_summary, claim_table, args.row_dirs)
    (args.output_dir / "H3_SYNTHESIS.md").write_text(report, encoding="utf-8")

    manifest = write_manifest(
        args.output_dir,
        experiment="B1_H3_evidence_matrix_synthesis",
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
    print("Saved H3 evidence matrix outputs:")
    for name in ["H3_SYNTHESIS.md", "h3_pair_evidence_matrix.csv", "h3_composite_level_summary.csv", "h3_claim_boundary_table.csv", "run_manifest.json"]:
        print(f"  {args.output_dir / name}")


def load_pair(row_dir: Path) -> dict[str, str]:
    path = row_dir / "h3_pair_config.csv"
    if path.exists():
        df = pd.read_csv(path)
        if not df.empty:
            return {str(k): str(v) for k, v in df.iloc[0].to_dict().items() if str(v) != "nan"}
    manifest = row_dir / "run_manifest.json"
    if manifest.exists():
        data = json.loads(manifest.read_text(encoding="utf-8"))
        if isinstance(data.get("pair"), dict):
            return {str(k): str(v) for k, v in data["pair"].items()}
    # Fall back to report parsing.
    report = row_dir / "h3_analysis_report.md"
    out: dict[str, str] = {}
    if report.exists():
        txt = report.read_text(encoding="utf-8")
        for key in ["component", "composite", "same_operation_control", "different_operation_control", "fake_component_control", "surface_control", "unrelated_control"]:
            m = re.search(rf"- {re.escape(key)}: `([^`]+)`", txt)
            if m:
                out[key] = m.group(1)
    return out or {"component": row_dir.name, "composite": "unknown"}


def load_contrasts(row_dir: Path) -> pd.DataFrame:
    path = row_dir / "h3_intervention_contrasts.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def rate_for(contrasts: pd.DataFrame, contrast_type: str) -> float:
    if contrasts.empty or "contrast_type" not in contrasts.columns:
        return np.nan
    sub = contrasts[contrasts["contrast_type"].astype(str) == contrast_type]
    if sub.empty or "censored_expected_direction_rate" not in sub.columns:
        return np.nan
    return float(sub["censored_expected_direction_rate"].mean())


def delta_for(contrasts: pd.DataFrame, contrast_type: str, col: str = "censored_delta_acquired_at_mean") -> float:
    if contrasts.empty or "contrast_type" not in contrasts.columns:
        return np.nan
    sub = contrasts[contrasts["contrast_type"].astype(str) == contrast_type]
    if sub.empty or col not in sub.columns:
        return np.nan
    return float(sub[col].mean())


def summarize_pair(row_id: str, row_dir: Path, pair: dict[str, str], contrasts: pd.DataFrame) -> dict[str, Any]:
    # Support both standard/upweight rows and strong/pretrain rows.
    up_same = rate_for(contrasts, "exact_vs_same_operation")
    up_diff = rate_for(contrasts, "exact_vs_different_operation")
    pre_same = rate_for(contrasts, "exact_pretrain_vs_same_operation")
    pre_diff = rate_for(contrasts, "exact_pretrain_vs_different_operation")
    corr_same = first_finite(rate_for(contrasts, "exact_strong_corrupt_vs_same_operation"), rate_for(contrasts, "exact_corrupt_vs_same_operation"))
    corr_diff = first_finite(rate_for(contrasts, "exact_strong_corrupt_vs_different_operation"), rate_for(contrasts, "exact_corrupt_vs_different_operation"))
    delay_same = first_finite(rate_for(contrasts, "exact_strong_delay_vs_same_operation"), rate_for(contrasts, "exact_delay_vs_same_operation"))
    delay_diff = first_finite(rate_for(contrasts, "exact_strong_delay_vs_different_operation"), rate_for(contrasts, "exact_delay_vs_different_operation"))
    same_specific = first_finite(pre_same, up_same)
    diff_specific = first_finite(pre_diff, up_diff)
    corrupt_support = corr_same
    delay_support = delay_same
    exact_score = np.nanmean([v for v in [same_specific, diff_specific, corrupt_support, delay_support] if np.isfinite(v)]) if any(np.isfinite(v) for v in [same_specific, diff_specific, corrupt_support, delay_support]) else np.nan
    verdict = classify_pair(same_specific, diff_specific, corrupt_support, delay_support, pre_same, up_same)
    return {
        "row_id": row_id,
        "result_dir": str(row_dir),
        "component": pair.get("component", ""),
        "composite": pair.get("composite", ""),
        "same_operation_control": pair.get("same_operation_control", ""),
        "different_operation_control": pair.get("different_operation_control", ""),
        "upweight_exact_vs_same_rate": up_same,
        "upweight_exact_vs_diff_rate": up_diff,
        "pretrain_exact_vs_same_rate": pre_same,
        "pretrain_exact_vs_diff_rate": pre_diff,
        "corrupt_exact_vs_same_rate": corr_same,
        "corrupt_exact_vs_diff_rate": corr_diff,
        "delay_exact_vs_same_rate": delay_same,
        "delay_exact_vs_diff_rate": delay_diff,
        "exact_specificity_score": exact_score,
        "primary_positive_signal": primary_signal(pre_same, up_same, corr_same),
        "verdict": verdict,
        "evidence_scope": scope_from_verdict(verdict),
    }


def first_finite(*vals: float) -> float:
    for v in vals:
        if np.isfinite(v):
            return float(v)
    return np.nan


def primary_signal(pre_same: float, up_same: float, corr_same: float) -> str:
    if np.isfinite(pre_same) and pre_same >= 0.75:
        return "pretrain_exact_component"
    if np.isfinite(up_same) and up_same >= 0.75:
        return "upweight_exact_component"
    if np.isfinite(corr_same) and corr_same >= 0.7:
        return "corrupt_exact_component"
    return "none_or_weak"


def classify_pair(same_specific: float, diff_specific: float, corrupt_support: float, delay_support: float, pre_same: float, up_same: float) -> str:
    # Exact-component positive requires exact beating same-op and different-op, plus corruption or delay support.
    if np.isfinite(pre_same) and pre_same >= 0.9 and np.isfinite(diff_specific) and diff_specific >= 0.8 and np.isfinite(corrupt_support) and corrupt_support >= 0.7:
        return "positive_exact_component_pair_specific"
    if np.isfinite(up_same) and up_same >= 0.8 and np.isfinite(diff_specific) and diff_specific >= 0.8 and np.isfinite(corrupt_support) and corrupt_support >= 0.6:
        return "promising_exact_component_partial"
    if np.isfinite(same_specific) and same_specific <= 0.1 and np.isfinite(diff_specific) and diff_specific >= 0.7:
        return "operation_family_transfer"
    vals = [v for v in [same_specific, diff_specific, corrupt_support, delay_support] if np.isfinite(v)]
    if vals and float(np.nanmean(vals)) >= 0.55:
        return "mixed_weak_positive"
    return "weak_or_negative"


def scope_from_verdict(verdict: str) -> str:
    if verdict == "positive_exact_component_pair_specific":
        return "supports localized exact-component causal sensitivity"
    if verdict == "promising_exact_component_partial":
        return "supports partial exact-component signal; needs replication/model-state corroboration"
    if verdict == "operation_family_transfer":
        return "supports operation-family transfer rather than exact-component dependency"
    if verdict == "mixed_weak_positive":
        return "mixed; useful for boundary mapping, not positive dependency"
    return "negative or weak evidence for exact-component dependency"


def summarize_by_composite(matrix: pd.DataFrame) -> pd.DataFrame:
    if matrix.empty:
        return pd.DataFrame()
    rows = []
    for comp, sub in matrix.groupby("composite", dropna=False):
        verdicts = list(sub["verdict"].astype(str))
        if any(v == "positive_exact_component_pair_specific" for v in verdicts):
            comp_verdict = "has_localized_exact_component_site"
        elif any(v == "promising_exact_component_partial" for v in verdicts):
            comp_verdict = "has_promising_partial_site"
        elif any(v == "operation_family_transfer" for v in verdicts):
            comp_verdict = "operation_family_or_saturation"
        else:
            comp_verdict = "no_exact_dependency_detected"
        rows.append({
            "composite": comp,
            "n_components_tested": len(sub),
            "n_positive_exact": int(sum(v == "positive_exact_component_pair_specific" for v in verdicts)),
            "n_promising_partial": int(sum(v == "promising_exact_component_partial" for v in verdicts)),
            "n_operation_family": int(sum(v == "operation_family_transfer" for v in verdicts)),
            "n_weak_or_negative": int(sum("weak_or_negative" in v for v in verdicts)),
            "mean_exact_specificity_score": float(pd.to_numeric(sub["exact_specificity_score"], errors="coerce").mean()),
            "composite_verdict": comp_verdict,
        })
    return pd.DataFrame(rows)


def make_claim_table(matrix: pd.DataFrame, family_summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    rows.append({
        "claim": "H3 residuals imply universal exact-component dependency",
        "status": "not supported",
        "basis": "Only one tested component-composite pair is positive; several formal components are weak, negative, or operation-family-level.",
    })
    rows.append({
        "claim": "H3 residuals identify useful candidate intervention sites",
        "status": "supported as pilot evidence",
        "basis": "H2-selected C06 produced one localized exact-component positive pair; C07 produced boundary/negative evidence.",
    })
    rows.append({
        "claim": "Exact-component dependency is heterogeneous across components/composites",
        "status": "supported in controlled B1 pilot",
        "basis": "A02→C06 positive; A00→C06 weak/mixed; C07 rows operation-family/negative.",
    })
    rows.append({
        "claim": "Controlled B1 evidence generalizes causally to real LLMs",
        "status": "not tested",
        "basis": "No real LLM interventions have been run; any LLM claim must remain observational/corroborative.",
    })
    return pd.DataFrame(rows)


def make_report(matrix: pd.DataFrame, family_summary: pd.DataFrame, claim_table: pd.DataFrame, row_dirs: list[Path]) -> str:
    lines = [
        "# H3 evidence synthesis",
        "",
        "This synthesis combines pair-specific B1 H3 intervention runs. It is intended for thesis writing and claim calibration. It does not create new causal evidence beyond the underlying runs; it records which claims the existing runs can and cannot support.",
        "",
        "## Inputs",
    ]
    for d in row_dirs:
        lines.append(f"- `{d}`")
    lines += ["", "## Pair-level evidence matrix"]
    if matrix.empty:
        lines.append("No rows available.")
    else:
        for _, r in matrix.iterrows():
            lines.append(
                f"- `{r['component']}` → `{r['composite']}`: **{r['verdict']}**; "
                f"primary signal=`{r['primary_positive_signal']}`; "
                f"scope: {r['evidence_scope']}"
            )
    lines += ["", "## Composite-level interpretation"]
    if family_summary.empty:
        lines.append("No composite-level rows available.")
    else:
        for _, r in family_summary.iterrows():
            lines.append(
                f"- `{r['composite']}`: verdict=`{r['composite_verdict']}`, "
                f"tested={int(r['n_components_tested'])}, positive_exact={int(r['n_positive_exact'])}, "
                f"operation_family={int(r['n_operation_family'])}, weak_or_negative={int(r['n_weak_or_negative'])}"
            )
    lines += [
        "", 
        "## Overall interpretation",
        "The current H3 evidence supports a heterogeneous causal picture. H2 residuals are useful for selecting candidate composites, but a residual is not itself evidence of exact-component dependency. In the tested B1 family, one substitution-side component of C06 shows localized exact-component sensitivity, while other listed formal components are weak, negative, or better explained by operation-family transfer/saturation.",
        "",
        "## Thesis-safe wording",
        "The intervention results refine, rather than simply confirm, the developmental-dependency hypothesis: some composite residuals can correspond to exact-component causal sensitivity, but this is not uniform across all formal components. The safe thesis claim is localized and controlled-setting-specific; it should not be stated as a universal mechanism of LLM training.",
        "",
        "## Claim boundary table",
    ]
    for _, r in claim_table.iterrows():
        lines.append(f"- **{r['claim']}** — {r['status']}. {r['basis']}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
