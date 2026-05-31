"""Create a compact final evidence index from thesis_evidence/.

This command does not run experiments. It validates that the durable thesis evidence
folder contains the key summary artifacts and writes an index suitable for thesis
writing.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from ic_experiments.run_management import get_git_sha, get_git_status, write_manifest

REQUIRED = [
    "FINAL_RESULTS_SYNTHESIS.md",
    "OVERALL_RESULTS_SYNTHESIS.md",
    "H3_SYNTHESIS.md",
    "MEDIATOR_DIAGNOSTIC_SYNTHESIS.md",
    "HYPOTHESIS_AUDIT.md",
    "THESIS_CLAIM_RULES.md",
    "tables/final_claim_evidence_matrix.csv",
    "tables/h3_pair_evidence_matrix.csv",
    "tables/mediator_pair_evidence_matrix.csv",
    "tables/figure_source_map.csv",
    "results_summaries/b1_mediator_h3_pairs_v18_analysis_report.md",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-dir", default="thesis_evidence")
    parser.add_argument("--output-dir", default="thesis_evidence/final_evidence_package")
    parser.add_argument("--code-version", default="v1.9")
    args = parser.parse_args()

    evidence = Path(args.evidence_dir)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    rows = []
    missing = []
    for rel in REQUIRED:
        p = evidence / rel
        exists = p.exists()
        rows.append((rel, exists, str(p)))
        if not exists:
            missing.append(rel)

    index_md = [
        "# Final thesis evidence package index",
        "",
        f"Created: {datetime.now(timezone.utc).isoformat()}",
        f"Code version: {args.code_version}",
        "",
        "This package indexes the durable evidence artifacts used to write the thesis. It does not create new experimental evidence.",
        "",
        "## Required artifact check",
        "",
        "| Artifact | Present | Path |",
        "|---|---:|---|",
    ]
    for rel, exists, path in rows:
        index_md.append(f"| `{rel}` | {exists} | `{path}` |")
    index_md += [
        "",
        "## Current thesis-safe claim",
        "",
        "> The current evidence supports a controlled, localized, and heterogeneous account of dependency: structural predictors and atomic residuals identify candidate sites, interventions distinguish exact-component dependency from operation-family transfer, and the strongest exact-dependency pair is accompanied by early gradient alignment. The evidence does not support a universal LLM-training mechanism or universal component-before-composite law.",
        "",
        "## Recommended next additions",
        "",
        "1. Second B1-family replication.",
        "2. Stronger representation/probe diagnostics because current CKA is not discriminative.",
        "3. Improved B2 sparse-parity coverage.",
        "4. Pythia-style observational pilot after controlled claims are stable.",
    ]
    (out / "final_evidence_package_index.md").write_text("\n".join(index_md) + "\n")

    with (out / "final_evidence_package_index.csv").open("w") as f:
        f.write("artifact,present,path\n")
        for rel, exists, path in rows:
            f.write(f'"{rel}",{str(exists).lower()},"{path}"\n')

    manifest = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "code_version": args.code_version,
        "experiment": "final_thesis_evidence_package_index",
        "evidence_dir": str(evidence),
        "output_dir": str(out),
        "git_sha": get_git_sha(),
        "git_status_short": get_git_status(),
        "missing_required_artifacts": missing,
    }
    (out / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    write_manifest(out, experiment="final_thesis_evidence_package_index", backend="thesis_evidence", code_version=args.code_version, input_paths={"evidence_dir": str(evidence)}, extra={"missing_required_artifacts": missing})

    print(f"Wrote final evidence package index to {out}")
    if missing:
        print("Missing required artifacts:")
        for rel in missing:
            print(f"- {rel}")


if __name__ == "__main__":
    main()
