from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

from ic_experiments.run_management import append_registry, write_manifest


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Summarize B1 family H1/H2/H3 readiness diagnostics into a claim-boundary report.")
    p.add_argument("--family-id", type=str, required=True)
    p.add_argument("--h1-dir", type=Path, required=True)
    p.add_argument("--h2-dir", type=Path, default=None)
    p.add_argument("--readiness-dir", type=Path, default=None)
    p.add_argument("--threshold-sensitivity-dir", type=Path, default=None)
    p.add_argument("--learnability-audit-dir", type=Path, default=None)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--code-version", type=str, default="v2.2")
    p.add_argument("--archive-root", type=Path, default=None)
    p.add_argument("--thesis-use", type=str, default="diagnostic")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    h2_dir = args.h2_dir or args.h1_dir
    rows = []
    h1 = read_report(args.h1_dir / "b1_h1_analysis_report.md")
    h2 = read_report(h2_dir / "h2_analysis_report.md")
    readiness = read_report((args.readiness_dir or Path("__missing__")) / "h3_readiness_report.md")
    thresh = read_report((args.threshold_sensitivity_dir or Path("__missing__")) / "h3_threshold_sensitivity_report.md")
    audit = read_report((args.learnability_audit_dir or Path("__missing__")) / "learnability_proxy_audit_report.md")

    h1_status = infer_h1_status(args.h1_dir)
    h2_status = infer_h2_status(h2_dir)
    readiness_status = infer_readiness_status(args.readiness_dir) if args.readiness_dir else "not_run"
    threshold_status = infer_threshold_status(args.threshold_sensitivity_dir) if args.threshold_sensitivity_dir else "not_run"
    audit_status = "available" if audit else "not_run"

    rows += [
        {"stage": "H1_ordering", "status": h1_status, "evidence_path": str(args.h1_dir / "b1_h1_analysis_report.md")},
        {"stage": "H2_predictor_residuals", "status": h2_status, "evidence_path": str(h2_dir / "h2_analysis_report.md")},
        {"stage": "H3_readiness", "status": readiness_status, "evidence_path": str((args.readiness_dir or Path('')) / "h3_readiness_report.md")},
        {"stage": "H3_threshold_sensitivity", "status": threshold_status, "evidence_path": str((args.threshold_sensitivity_dir or Path('')) / "h3_threshold_sensitivity_report.md")},
        {"stage": "learnability_proxy_audit", "status": audit_status, "evidence_path": str((args.learnability_audit_dir or Path('')) / "learnability_proxy_audit_report.md")},
    ]
    stage_table = pd.DataFrame(rows)
    stage_table.to_csv(args.output_dir / "family_diagnostic_stage_table.csv", index=False)
    report = render_report(args, stage_table, h1, h2, readiness, thresh, audit)
    (args.output_dir / "family_diagnostic_synthesis.md").write_text(report, encoding="utf-8")
    manifest = write_manifest(
        args.output_dir,
        experiment="B1_family_diagnostic_synthesis",
        backend="B1_sequence_dsl",
        code_version=args.code_version,
        run_id=f"{args.family_id}_diagnostic_synthesis",
        command=sys.argv,
        input_paths={
            "h1_dir": str(args.h1_dir),
            "h2_dir": str(h2_dir),
            "readiness_dir": str(args.readiness_dir) if args.readiness_dir else "",
            "threshold_sensitivity_dir": str(args.threshold_sensitivity_dir) if args.threshold_sensitivity_dir else "",
            "learnability_audit_dir": str(args.learnability_audit_dir) if args.learnability_audit_dir else "",
        },
        extra={"family_id": args.family_id, "thesis_use": args.thesis_use},
    )
    if args.archive_root is not None:
        append_registry(args.archive_root / "results_registry.csv", {
            "run_id": manifest["run_id"], "code_version": args.code_version, "git_sha": manifest["git_sha"],
            "experiment": manifest["experiment"], "backend": manifest["backend"], "output_path": str(args.output_dir),
            "status": "analyzed", "thesis_use": args.thesis_use, "created_at_utc": manifest["created_at_utc"],
        })
    print(f"Wrote family diagnostic synthesis to {args.output_dir}")


def read_report(path: Path) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def infer_h1_status(h1_dir: Path) -> str:
    report = read_report(h1_dir / "b1_h1_analysis_report.md")
    if not report:
        return "missing"
    if "all / frequency: sign-rate=1.000" in report and "reference_learnability: sign-rate=0.000" in report:
        return "frequency_stable_learnability_reversed"
    if "all / frequency: sign-rate=1.000" in report and "reference_learnability: sign-rate=1.000" in report:
        return "frequency_and_learnability_expected"
    return "available_needs_review"


def infer_h2_status(h2_dir: Path) -> str:
    report = read_report(h2_dir / "h2_analysis_report.md")
    if not report:
        return "missing"
    if "positive residual rate: `1.000`" in report:
        return "all_composites_delayed_or_proxy_issue"
    if "Composite residuals" in report:
        return "available"
    return "available_needs_review"


def infer_readiness_status(readiness_dir: Path | None) -> str:
    if readiness_dir is None:
        return "not_run"
    path = readiness_dir / "h3_readiness_report.md"
    text = read_report(path)
    if not text:
        return "missing"
    # Look for '- H3-ready composites: `N`'.
    import re
    m = re.search(r"H3-ready composites: `?(\d+)`?", text)
    if m:
        return "has_ready_candidates" if int(m.group(1)) > 0 else "no_ready_candidates"
    return "available_needs_review"


def infer_threshold_status(threshold_dir: Path | None) -> str:
    if threshold_dir is None:
        return "not_run"
    text = read_report(threshold_dir / "h3_threshold_sensitivity_report.md")
    if not text:
        return "missing"
    if "exact_pretrain_vs_different_operation" in text and "Δfinal=-0.135" in text:
        return "thresholds_do_not_rescue_exact_dependency"
    return "available_needs_review"


def render_report(args, stage_table, h1, h2, readiness, thresh, audit) -> str:
    lines = [
        f"# B1 family diagnostic synthesis: {args.family_id}",
        "",
        "This report summarizes whether a B1 family is useful for H1/H2/H3 claims. It is intended to prevent overinterpreting a family where residuals are large but H3 candidates are not intervention-ready.",
        "",
        "## Stage table",
    ]
    for _, r in stage_table.iterrows():
        lines.append(f"- `{r['stage']}`: `{r['status']}`")
    lines += [
        "",
        "## Current interpretation",
        "Family-level evidence should be used according to the weakest stage. If H1/H2 are strong but H3-readiness fails, the family supports regime/predictor/residual claims but not exact-dependency replication.",
        "",
        "## Claim boundary",
        "- H1/H2 evidence can support structured acquisition and residual-selection claims.",
        "- H3 claims require readiness plus exact-vs-control intervention contrasts.",
        "- If threshold sensitivity does not rescue an H3 candidate, record it as subthreshold/weak-negative rather than positive dependency evidence.",
    ]
    if audit:
        lines += ["", "## Learnability audit", "A learnability-proxy audit was provided; use it to decide whether reference_learnability is a valid difficulty proxy in this family."]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
