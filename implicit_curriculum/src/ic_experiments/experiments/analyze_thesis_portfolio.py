from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import pandas as pd

from ic_experiments.run_management import append_registry, write_manifest


def parse_args():
    p = argparse.ArgumentParser(description="Aggregate thesis_evidence into a conservative claim/status dashboard.")
    p.add_argument("--evidence-dir", type=Path, default=Path("thesis_evidence"))
    p.add_argument("--output-dir", type=Path, default=Path("thesis_evidence/portfolio"))
    p.add_argument("--code-version", type=str, default="v1.4")
    p.add_argument("--archive-root", type=Path, default=None)
    p.add_argument("--thesis-use", type=str, default="candidate")
    return p.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def extract_float(text: str, pattern: str, default=float("nan")) -> float:
    m = re.search(pattern, text)
    if not m:
        return default
    try:
        return float(m.group(1).replace(",", ""))
    except Exception:
        return default


def main() -> None:
    args = parse_args()
    ev = args.evidence_dir
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    rs = ev / "results_summaries"

    rows = []
    def add(exp, status, claim, caveat, source):
        rows.append({"experiment": exp, "status": status, "claim_supported": claim, "key_caveat": caveat, "source_file": source})

    # Recovery gate
    rec = read_text(rs / "exp0_recovery_report.md")
    add("Exp0 synthetic recovery", "green", "Analysis pipeline recovers known synthetic worlds sufficiently for downstream pilots.", "Synthetic validation only; not a neural result.", "exp0_recovery_report.md")

    # B2 sparse parity
    b2 = read_text(rs / "b2_sparse_parity_analysis_report.md")
    b2_cov = extract_float(b2, r"threshold `0\.85`: acquisition_rate=([0-9.]+)")
    b2_freq = extract_float(b2, r"threshold `0\.85`: acquisition_rate=[0-9.]+, time-Spearman\(freq\)=(-?[0-9.]+)")
    add("B2 sparse parity", "yellow-green", f"Quanta-style baseline: frequency effect is strong when learnable (e.g. threshold .85 rho≈{b2_freq:.3g}).", f"Acquisition coverage remains modest (≈{b2_cov:.3g}); final use should improve coverage.", "b2_sparse_parity_analysis_report.md")

    # B1 H1
    h1 = read_text(rs / "b1_h1_analysis_report.md")
    learn_rho = extract_float(h1, r"all / reference_learnability: sign-rate=1\.000, mean-rho=([0-9.\-]+)")
    freq_rho = extract_float(h1, r"kind=atomic / frequency: sign-rate=1\.000, mean-rho=([0-9.\-]+)")
    add("B1 H1 ordering/sign stability", "green-pilot", f"Reference learnability robustly predicts later acquisition across configs (mean rho≈{learn_rho:.3g}); atomic frequency is expected-direction but weaker (rho≈{freq_rho:.3g}).", "Pilot grid only; frequency is weak/reversed inside composites.", "b1_h1_analysis_report.md")

    # B1 H2
    h2 = read_text(rs / "b1_h2_analysis_report.md")
    add("B1 H2 predictor ladder/residuals", "green-pilot", "Atomic acquisition is explained by simple one-factor predictors with config drift; composite residuals select intervention candidates.", "Residuals are observational and do not prove dependency.", "b1_h2_analysis_report.md")

    # B1 H3 rows and strong row
    multi = read_text(rs / "b1_h3_c06_multirow_analysis_report.md") or read_text(rs / "b1_h3_c06_row0_row1_interpretation.md")
    strong = read_text(rs / "b1_h3_row0_strong_v12_10seed_analysis_report.md") or read_text(rs / "b1_h3_row0_strong_v12_analysis_report.md")
    pre_same = extract_float(strong, r"exact_pretrain_vs_same_operation.*?censored Δ=(-?[0-9.,]+)", default=float("nan"))
    add("B1 H3 C06 interventions", "green-yellow pair-specific", "A02_substitute → C06 shows pair-specific causal evidence under exact pretraining and strong corruption beyond same/different-operation controls.", "A00_copy → C06 is weak/mixed; result is not a universal component-dependency claim.", "b1_h3_row0_strong_v12_10seed_analysis_report.md")

    df = pd.DataFrame(rows)
    df.to_csv(out / "claim_status_dashboard.csv", index=False)

    report_lines = [
        "# Thesis Evidence Portfolio Summary",
        "",
        "This report is generated from `thesis_evidence/` and is intentionally conservative. It distinguishes supported controlled-pilot claims from unsupported broad mechanism claims.",
        "",
        "## Current overall conclusion",
        "",
        "The evidence now supports a scoped controlled-mechanism story: structural properties predict acquisition order in the B1 sequence-transformer substrate, especially reference learnability; atomic timing is captured by simple configuration-dependent predictors; atomic-parallel residuals identify candidate composite dependency sites; and one component-composite pair (`A02_substitute → C06`) shows pair-specific causal sensitivity under stronger interventions. The evidence does not support a universal law of LLM training or uniform dependency across all formal components.",
        "",
        "## Claim dashboard",
        "",
        "| Experiment | Status | Supported claim | Caveat |",
        "|---|---|---|---|",
    ]
    for _, r in df.iterrows():
        report_lines.append(f"| {r['experiment']} | {r['status']} | {r['claim_supported']} | {r['key_caveat']} |")
    report_lines += [
        "",
        "## Claims currently safe to write",
        "",
        "1. The analysis pipeline passes synthetic recovery before neural use.",
        "2. Sparse parity provides a contrasting frequency-dominated/quanta-style regime, but should be strengthened for final quantitative claims.",
        "3. In B1, reference learnability robustly predicts later acquisition across the pilot configuration grid; frequency is weaker and stratum-dependent.",
        "4. Atomic acquisition is captured by simple one-factor predictors whose selected factor drifts by configuration.",
        "5. Composite residuals are useful for selecting causal intervention targets but do not themselves prove dependency.",
        "6. Strong H3 interventions give pair-specific causal evidence for `A02_substitute → C06`, while `A00_copy → C06` is weak/mixed.",
        "",
        "## Claims not yet safe",
        "",
        "- A universal closed-form law of acquisition timing.",
        "- Frequency universally determining ordering in sequence-transformer tasks.",
        "- Uniform component-to-composite developmental dependency.",
        "- Any causal claim about real LLM training.",
    ]
    (out / "portfolio_summary.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    manifest = write_manifest(
        out,
        experiment="thesis_evidence_portfolio_summary",
        backend="evidence_archive",
        code_version=args.code_version,
        run_id="thesis_evidence_portfolio_summary",
        command=sys.argv,
        input_paths={"evidence_dir": str(ev)},
        extra={"thesis_use": args.thesis_use},
    )
    if args.archive_root is not None:
        append_registry(args.archive_root / "results_registry.csv", {
            "run_id": manifest["run_id"], "code_version": args.code_version, "git_sha": manifest["git_sha"],
            "experiment": manifest["experiment"], "backend": manifest["backend"], "output_path": str(out),
            "status": "analyzed", "thesis_use": args.thesis_use, "created_at_utc": manifest["created_at_utc"],
        })
    print(f"Wrote {out / 'portfolio_summary.md'}")
    print(f"Wrote {out / 'claim_status_dashboard.csv'}")


if __name__ == "__main__":
    main()
