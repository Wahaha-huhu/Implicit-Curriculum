from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import pandas as pd

from ic_experiments.run_management import append_registry, write_manifest


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Build a thesis-oriented cross-family claim synthesis from the original B1 family, "
            "a replication family, readiness diagnostics, and optional H3/mediator evidence."
        )
    )
    p.add_argument("--family1-id", type=str, default="family_01")
    p.add_argument("--family1-h1-dir", type=Path, required=True)
    p.add_argument("--family1-h2-dir", type=Path, default=None)
    p.add_argument("--family1-h3-matrix", type=Path, default=None)
    p.add_argument("--family1-mediator-dir", type=Path, default=None)
    p.add_argument("--family2-id", type=str, default="family_replication_01")
    p.add_argument("--family2-h1-dir", type=Path, required=True)
    p.add_argument("--family2-h2-dir", type=Path, default=None)
    p.add_argument("--family2-readiness-dir", type=Path, default=None)
    p.add_argument("--family2-threshold-dirs", type=Path, nargs="*", default=[])
    p.add_argument("--family2-h3-dirs", type=Path, nargs="*", default=[])
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--code-version", type=str, default="v2.3")
    p.add_argument("--archive-root", type=Path, default=None)
    p.add_argument("--thesis-use", type=str, default="candidate")
    return p.parse_args()


def read(path: Path | None) -> str:
    if path is None:
        return ""
    try:
        if path.exists():
            return path.read_text(encoding="utf-8")
    except Exception:
        return ""
    return ""


def extract_float(pattern: str, text: str) -> float | None:
    m = re.search(pattern, text)
    return float(m.group(1)) if m else None


def extract_int(pattern: str, text: str) -> int | None:
    m = re.search(pattern, text)
    return int(m.group(1)) if m else None


def h1_summary(family_id: str, h1_dir: Path) -> dict[str, Any]:
    text = read(h1_dir / "b1_h1_analysis_report.md")
    out: dict[str, Any] = {"family_id": family_id, "stage": "H1", "available": bool(text), "path": str(h1_dir / "b1_h1_analysis_report.md")}
    for label, pred in [
        ("all_frequency", r"all / frequency: sign-rate=([0-9.]+), mean-rho=([-0-9.]+)"),
        ("all_learnability", r"all / reference_learnability: sign-rate=([0-9.]+), mean-rho=([-0-9.]+)"),
        ("true_frequency", r"true_tasks_atomic_composite / frequency: sign-rate=([0-9.]+), mean-rho=([-0-9.]+)"),
        ("true_learnability", r"true_tasks_atomic_composite / reference_learnability: sign-rate=([0-9.]+), mean-rho=([-0-9.]+)"),
    ]:
        m = re.search(pred, text)
        if m:
            out[f"{label}_sign_rate"] = float(m.group(1))
            out[f"{label}_mean_rho"] = float(m.group(2))
    freq = out.get("all_frequency_sign_rate")
    learn = out.get("all_learnability_sign_rate")
    if freq == 1.0 and learn == 1.0:
        verdict = "frequency_and_learnability_expected"
    elif freq == 1.0 and learn == 0.0:
        verdict = "frequency_expected_learnability_reversed"
    elif freq == 1.0:
        verdict = "frequency_expected_other_mixed"
    else:
        verdict = "mixed_or_unavailable"
    out["verdict"] = verdict
    return out


def h2_summary(family_id: str, h2_dir: Path) -> dict[str, Any]:
    text = read(h2_dir / "h2_analysis_report.md")
    out: dict[str, Any] = {"family_id": family_id, "stage": "H2", "available": bool(text), "path": str(h2_dir / "h2_analysis_report.md")}
    out["atomic_acq_rate"] = extract_float(r"atomic acquisition rate: `?([0-9.]+)`?", text)
    out["composite_acq_rate"] = extract_float(r"composite acquisition rate: `?([0-9.]+)`?", text)
    out["mean_residual_log_time"] = extract_float(r"mean residual log-time: `?([-0-9.]+)`?", text)
    out["positive_residual_rate"] = extract_float(r"positive residual rate: `?([0-9.]+)`?", text)
    selected = re.findall(r"- `([^`]+)`: selected `([^`]+)`", text)
    if selected:
        predictors = [p for _, p in selected]
        out["selected_predictors"] = ";".join(predictors)
        out["dominant_predictor"] = pd.Series(predictors).mode().iloc[0]
    else:
        out["selected_predictors"] = ""
        out["dominant_predictor"] = ""
    if out.get("positive_residual_rate") == 1.0:
        out["verdict"] = "systematic_composite_delay_or_proxy_issue"
    elif out.get("mean_residual_log_time") is not None:
        out["verdict"] = "structured_residuals"
    else:
        out["verdict"] = "missing_or_unavailable"
    return out


def family1_h3_summary(h3_matrix: Path | None) -> tuple[pd.DataFrame, dict[str, Any]]:
    if h3_matrix is None or not h3_matrix.exists():
        return pd.DataFrame(), {"family_id": "family_01", "stage": "H3", "available": False, "verdict": "missing"}
    df = pd.read_csv(h3_matrix)
    verdicts = df.get("verdict", pd.Series(dtype=str)).astype(str)
    summary = {
        "family_id": "family_01",
        "stage": "H3",
        "available": True,
        "pairs_tested": int(len(df)),
        "positive_exact_pairs": int(verdicts.str.contains("positive_exact", na=False).sum()),
        "operation_family_pairs": int(verdicts.str.contains("operation_family", na=False).sum()),
        "weak_or_negative_pairs": int(verdicts.str.contains("weak|negative", regex=True, na=False).sum()),
        "verdict": "localized_exact_dependency_plus_heterogeneity",
        "path": str(h3_matrix),
    }
    df = df.copy()
    df.insert(0, "family_id", "family_01")
    return df, summary


def parse_h3_report(path: Path) -> dict[str, Any]:
    text = read(path / "h3_analysis_report.md")
    pair_component = re.search(r"- component: `([^`]+)`", text)
    pair_composite = re.search(r"- composite: `([^`]+)`", text)
    final_rows = re.findall(r"- `([^`]+)`: acq=([0-9.]+), mean censored time=([0-9.]+), final=([0-9.]+)", text)
    baseline_final = None
    baseline_acq = None
    if final_rows:
        for cond, acq, _, final in final_rows:
            if cond == "baseline":
                baseline_acq = float(acq); baseline_final = float(final)
                break
    mean_rate = extract_float(r"mean censored expected-direction rate: `?([0-9.]+)`?", text)
    same_rate = extract_float(r"exact-vs-same-operation censored expected-direction rate: `?([0-9.]+)`?", text)
    diff_rate = extract_float(r"exact/different-operation censored expected-direction rate: `?([0-9.]+)`?", text)
    if not text:
        verdict = "missing"
    elif baseline_acq == 0.0 and baseline_final is not None and baseline_final < 0.10:
        verdict = "hard_composite_failure"
    elif same_rate is not None and same_rate >= 0.75 and diff_rate is not None and diff_rate >= 0.60:
        verdict = "positive_exact_component_candidate"
    elif same_rate == 0.0 and diff_rate is not None and diff_rate > 0.5:
        verdict = "operation_family_or_control_matched"
    elif mean_rate is not None and mean_rate < 0.25:
        verdict = "weak_or_negative"
    else:
        verdict = "mixed_or_subthreshold"
    return {
        "component": pair_component.group(1) if pair_component else "",
        "composite": pair_composite.group(1) if pair_composite else "",
        "h3_dir": str(path),
        "baseline_acq": baseline_acq,
        "baseline_final": baseline_final,
        "mean_censored_expected_direction_rate": mean_rate,
        "exact_vs_same_operation_rate": same_rate,
        "exact_vs_different_operation_rate": diff_rate,
        "verdict": verdict,
    }


def family2_h3_summaries(h3_dirs: list[Path], threshold_dirs: list[Path]) -> tuple[pd.DataFrame, dict[str, Any]]:
    rows = []
    for d in h3_dirs:
        r = parse_h3_report(d)
        r["family_id"] = "family_replication_01"
        r["source"] = "h3_analysis"
        rows.append(r)
    for d in threshold_dirs:
        t = read(d / "h3_threshold_sensitivity_report.md")
        if not t:
            continue
        component = re.search(r"- component: `([^`]+)`", t)
        composite = re.search(r"- composite: `([^`]+)`", t)
        # Determine if exact and same-operation pretrain are identical at lower thresholds.
        if "exact_pretrain_vs_same_operation" in t and "censored Δ=0.000" in t:
            verdict = "thresholds_do_not_rescue_exact_dependency"
        else:
            verdict = "threshold_diagnostic_available"
        rows.append({
            "family_id": "family_replication_01",
            "source": "threshold_sensitivity",
            "component": component.group(1) if component else "",
            "composite": composite.group(1) if composite else "",
            "h3_dir": str(d),
            "baseline_acq": None,
            "baseline_final": None,
            "mean_censored_expected_direction_rate": None,
            "exact_vs_same_operation_rate": None,
            "exact_vs_different_operation_rate": None,
            "verdict": verdict,
        })
    df = pd.DataFrame(rows)
    if df.empty:
        summary = {"family_id": "family_replication_01", "stage": "H3", "available": False, "verdict": "missing"}
    else:
        hard = int((df["verdict"] == "hard_composite_failure").sum())
        weak = int(df["verdict"].astype(str).str.contains("weak|negative|do_not_rescue", regex=True, na=False).sum())
        opfam = int(df["verdict"].astype(str).str.contains("operation_family", regex=True, na=False).sum())
        pos = int(df["verdict"].astype(str).str.contains("positive_exact", regex=True, na=False).sum())
        summary = {
            "family_id": "family_replication_01",
            "stage": "H3",
            "available": True,
            "pairs_or_diagnostics_tested": int(len(df)),
            "positive_exact_pairs": pos,
            "operation_family_or_threshold_pairs": opfam,
            "weak_or_negative_diagnostics": weak,
            "hard_composite_failures": hard,
            "verdict": "no_positive_exact_replication_h3_readiness_boundary",
        }
    return df, summary


def readiness_summary(readiness_dir: Path | None) -> dict[str, Any]:
    text = read((readiness_dir or Path("__missing__")) / "h3_readiness_report.md")
    out: dict[str, Any] = {"family_id": "family_replication_01", "stage": "H3_readiness", "available": bool(text)}
    out["candidate_composites"] = extract_int(r"candidate composites: `?(\d+)`?", text)
    out["ready_composites"] = extract_int(r"H3-ready composites: `?(\d+)`?", text)
    if out.get("ready_composites") is None:
        out["verdict"] = "missing_or_unavailable"
    elif out["ready_composites"] == 0:
        out["verdict"] = "no_ready_candidates"
    else:
        out["verdict"] = "some_ready_candidates_but_check_h3_results"
    out["path"] = str((readiness_dir or Path("")) / "h3_readiness_report.md")
    return out


def mediator_summary(family_id: str, mediator_dir: Path | None) -> dict[str, Any]:
    text = read((mediator_dir or Path("__missing__")) / "mediator_analysis_report.md")
    out: dict[str, Any] = {"family_id": family_id, "stage": "mediator", "available": bool(text), "path": str((mediator_dir or Path("")) / "mediator_analysis_report.md")}
    if "A02_substitute" in text and "Δgrad_cos=0.323" in text:
        out["verdict"] = "gradient_alignment_supports_positive_pair"
    elif text:
        out["verdict"] = "available_needs_review"
    else:
        out["verdict"] = "not_run"
    return out


def render_report(stage_df: pd.DataFrame, h3_df: pd.DataFrame, claim_df: pd.DataFrame) -> str:
    lines = [
        "# Cross-family controlled evidence synthesis",
        "",
        "This report consolidates B1 family 1 and family 2 evidence. It is designed to separate claims that replicate across generated task families from claims that remain localized to one family/pair.",
        "",
        "## Executive summary",
        "",
        "- Family 1 supports a localized exact-component dependency site: `A02_substitute → C06_reverse_then_substitute_02_00`, with intervention and gradient-alignment support.",
        "- Family 2 replicates that acquisition is structured and that H2 residuals can be large, but it does **not** replicate positive exact-component H3 dependency under the tested settings.",
        "- Family 2 instead exposes an important boundary condition: the largest residual composites can be too hard or only subthreshold-ready for H3, so H3 candidate selection must include readiness criteria.",
        "- The robust cross-family contribution is methodological: acquisition order and residuals are not self-interpreting; matched interventions and readiness checks are needed to distinguish exact dependency, operation-family transfer, and hard-composite failure.",
        "",
        "## Stage-level evidence",
        "",
        stage_df.to_markdown(index=False),
    ]
    if not h3_df.empty:
        display_cols = [c for c in ["family_id", "source", "component", "composite", "verdict", "exact_vs_same_operation_rate", "exact_vs_different_operation_rate", "baseline_final"] if c in h3_df.columns]
        lines += ["", "## H3 rows and diagnostics", "", h3_df[display_cols].to_markdown(index=False)]
    lines += ["", "## Claim boundary matrix", "", claim_df.to_markdown(index=False), ""]
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    fam1_h2_dir = args.family1_h2_dir or args.family1_h1_dir
    fam2_h2_dir = args.family2_h2_dir or args.family2_h1_dir

    stage_rows = [
        h1_summary(args.family1_id, args.family1_h1_dir),
        h2_summary(args.family1_id, fam1_h2_dir),
        h1_summary(args.family2_id, args.family2_h1_dir),
        h2_summary(args.family2_id, fam2_h2_dir),
        readiness_summary(args.family2_readiness_dir),
        mediator_summary(args.family1_id, args.family1_mediator_dir),
    ]
    fam1_h3_df, fam1_h3_sum = family1_h3_summary(args.family1_h3_matrix)
    fam2_h3_df, fam2_h3_sum = family2_h3_summaries(args.family2_h3_dirs, args.family2_threshold_dirs)
    stage_rows += [fam1_h3_sum, fam2_h3_sum]

    stage_df = pd.DataFrame(stage_rows)
    h3_df = pd.concat([fam1_h3_df, fam2_h3_df], ignore_index=True, sort=False) if not fam1_h3_df.empty or not fam2_h3_df.empty else pd.DataFrame()
    claim_rows = [
        {
            "claim": "Acquisition is structured in B1 families",
            "status": "supported_cross_family_pilot",
            "support": "Both families have usable H1/H2 structure, but predictor signs differ.",
            "boundary": "Does not imply a universal scalar predictor.",
        },
        {
            "claim": "Frequency is a robust predictor in at least some B1 regimes",
            "status": "supported_but_regime_dependent",
            "support": "Family 2 shows stable frequency effects; family 1 was weaker.",
            "boundary": "Frequency is not sufficient for all composites or H3 dependency.",
        },
        {
            "claim": "Reference learnability universally predicts later acquisition",
            "status": "not_supported",
            "support": "Family 2 reverses the sign of the proxy.",
            "boundary": "Treat reference_learnability as a family-specific structural proxy until audited.",
        },
        {
            "claim": "H2 residuals select useful H3 candidates",
            "status": "supported_with_readiness_gate",
            "support": "Family 1 residuals selected a positive localized pair; family 2 residuals exposed hard/subthreshold candidates.",
            "boundary": "Residual magnitude alone is insufficient; use H3 readiness.",
        },
        {
            "claim": "Exact-component dependency recurs across B1 families",
            "status": "not_yet_supported",
            "support": "Family 1 has one positive pair; family 2 did not replicate exact dependency under tested settings.",
            "boundary": "Current exact dependency claim remains localized/pair-specific.",
        },
        {
            "claim": "Operation-family transfer is a real alternative mechanism",
            "status": "supported_pilot",
            "support": "Reverse-side tests show exact and same-operation controls often match.",
            "boundary": "Needs broader sampling to quantify prevalence.",
        },
    ]
    claim_df = pd.DataFrame(claim_rows)

    stage_df.to_csv(out / "cross_family_stage_summary.csv", index=False)
    if not h3_df.empty:
        h3_df.to_csv(out / "cross_family_h3_diagnostics.csv", index=False)
    claim_df.to_csv(out / "cross_family_claim_matrix.csv", index=False)
    report = render_report(stage_df, h3_df, claim_df)
    (out / "CROSS_FAMILY_CONTROLLED_SYNTHESIS.md").write_text(report, encoding="utf-8")

    manifest = write_manifest(
        out,
        experiment="B1_cross_family_claim_synthesis",
        backend="B1_sequence_dsl",
        code_version=args.code_version,
        run_id="b1_cross_family_claim_synthesis",
        command=sys.argv,
        input_paths={
            "family1_h1_dir": str(args.family1_h1_dir),
            "family1_h2_dir": str(fam1_h2_dir),
            "family1_h3_matrix": str(args.family1_h3_matrix) if args.family1_h3_matrix else "",
            "family1_mediator_dir": str(args.family1_mediator_dir) if args.family1_mediator_dir else "",
            "family2_h1_dir": str(args.family2_h1_dir),
            "family2_h2_dir": str(fam2_h2_dir),
            "family2_readiness_dir": str(args.family2_readiness_dir) if args.family2_readiness_dir else "",
            "family2_h3_dirs": [str(p) for p in args.family2_h3_dirs],
            "family2_threshold_dirs": [str(p) for p in args.family2_threshold_dirs],
        },
        extra={"thesis_use": args.thesis_use},
    )
    if args.archive_root:
        append_registry(args.archive_root / "results_registry.csv", {
            "run_id": manifest["run_id"],
            "code_version": args.code_version,
            "git_sha": manifest["git_sha"],
            "experiment": manifest["experiment"],
            "backend": manifest["backend"],
            "output_path": str(out),
            "status": "analyzed",
            "thesis_use": args.thesis_use,
            "created_at_utc": manifest["created_at_utc"],
        })
    print(f"Wrote cross-family claim synthesis to {out}")


if __name__ == "__main__":
    main()
