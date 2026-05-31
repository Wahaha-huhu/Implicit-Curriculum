from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from ic_experiments.run_management import append_registry, write_manifest

DOCS = [
    "TASK_DESIGN_JUSTIFICATION.md",
    "PYTHIA_BRIDGE_EXPERIMENT_DESIGN.md",
    "TOP_CONFERENCE_POSITIONING.md",
    "HYPOTHESIS_AUDIT.md",
    "OVERALL_RESULTS_SYNTHESIS.md",
    "H3_SYNTHESIS.md",
]
TABLES = [
    "tables/task_design_validity_matrix.csv",
    "tables/contribution_claim_map.csv",
    "tables/pythia_bridge_slice_design.csv",
    "tables/h3_pair_evidence_matrix.csv",
    "tables/h3_claim_boundary_table.csv",
]


def parse_args():
    p = argparse.ArgumentParser(description="Create a compact index of thesis design/evidence documents.")
    p.add_argument("--evidence-dir", type=Path, default=Path("thesis_evidence"))
    p.add_argument("--output-dir", type=Path, default=Path("thesis_evidence/design_dossier"))
    p.add_argument("--code-version", type=str, default="v1.7")
    p.add_argument("--archive-root", type=Path, default=None)
    p.add_argument("--thesis-use", type=str, default="candidate")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    ev = args.evidence_dir
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for rel in DOCS + TABLES:
        path = ev / rel
        rows.append({
            "relative_path": rel,
            "exists": path.exists(),
            "size_bytes": path.stat().st_size if path.exists() else 0,
            "role": "document" if rel.endswith(".md") else "table",
        })
    df = pd.DataFrame(rows)
    df.to_csv(out / "design_dossier_index.csv", index=False)
    md = [
        "# Thesis design dossier index",
        "",
        "This index records the task-design, claim-boundary, and Pythia-bridge documents that should persist across implementation versions.",
        "",
        "| File | Exists | Role |",
        "|---|---:|---|",
    ]
    for r in rows:
        md.append(f"| `{r['relative_path']}` | {r['exists']} | {r['role']} |")
    md += [
        "",
        "## Usage",
        "",
        "Use these files when writing the thesis introduction, methods validity argument, and discussion of LLM/Pythia transfer limits.",
    ]
    (out / "design_dossier_index.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    manifest = write_manifest(
        out,
        experiment="thesis_design_dossier_index",
        backend="evidence_archive",
        code_version=args.code_version,
        run_id="thesis_design_dossier_index",
        command=sys.argv,
        input_paths={"evidence_dir": str(ev)},
        extra={"thesis_use": args.thesis_use},
    )
    if args.archive_root is not None:
        append_registry(args.archive_root / "results_registry.csv", {
            "run_id": manifest["run_id"],
            "code_version": args.code_version,
            "git_sha": manifest["git_sha"],
            "experiment": manifest["experiment"],
            "backend": manifest["backend"],
            "output_path": str(out),
            "status": "indexed",
            "thesis_use": args.thesis_use,
            "created_at_utc": manifest["created_at_utc"],
        })
    print(f"Wrote {out / 'design_dossier_index.md'}")
    print(f"Wrote {out / 'design_dossier_index.csv'}")


if __name__ == "__main__":
    main()
