from __future__ import annotations

import argparse
import shutil
from pathlib import Path
from typing import Any

import pandas as pd

from ic_experiments.run_management import append_registry, write_manifest


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def _copy_if_exists(src: Path, dst: Path) -> bool:
    if not src.exists():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def _top_rows(df: pd.DataFrame, n: int = 10) -> list[str]:
    if df.empty:
        return []
    rows: list[str] = []
    for _, r in df.head(n).iterrows():
        sid = r.get("slice_id", r.get("prompt_family", ""))
        verdict = r.get("stability_verdict", "")
        if "mean_underperforming_metric_rate" in r:
            rows.append(f"- `{sid}`: `{verdict}`, mean under-rate={float(r['mean_underperforming_metric_rate']):.3f}")
        else:
            rows.append(f"- `{sid}`: `{verdict}`")
    return rows


def _claim_table() -> pd.DataFrame:
    return pd.DataFrame([
        {
            "claim": "Pythia-style checkpointed models show measurable primitive/composite slice dynamics under continuous scores.",
            "status": "supported_observational_pilot",
            "evidence": "The v2.7/v3.0 H2-ready slice suite yields moving atomic and composite slices across multiple continuous metrics.",
            "boundary": "This is observational and does not establish causal dependency.",
        },
        {
            "claim": "Primitive-to-composite residual analysis is feasible in Pythia-like checkpoints.",
            "status": "supported_observational_pilot",
            "evidence": "The v2.9/v3.0 analyses produce residual rows for 10 composites across five metrics.",
            "boundary": "Residuals are candidate signatures, not proof of component reuse.",
        },
        {
            "claim": "Some residual patterns persist across Pythia model sizes/configurations.",
            "status": "supported_observational_pilot",
            "evidence": "The 70M/160M sweep identifies several stable underperforming composites, especially arithmetic and string composites.",
            "boundary": "Only two model sizes have been swept so far; 410M or denser checkpoints would strengthen this.",
        },
        {
            "claim": "Pythia causally learns composites from primitive components.",
            "status": "not_supported",
            "evidence": "No Pythia pretraining interventions have been run.",
            "boundary": "This claim would require interventions or stronger mechanistic evidence beyond observational trajectories.",
        },
        {
            "claim": "Pythia replicates the B1 exact-component dependency result.",
            "status": "not_supported",
            "evidence": "The Pythia bridge has residual/coupling signatures, not H3-style matched interventions.",
            "boundary": "Use Pythia as observational bridge only.",
        },
    ])


def _write_synthesis(evidence_dir: Path, sweep_dir: Path, run_summary: pd.DataFrame, residual: pd.DataFrame, family: pd.DataFrame, claims: pd.DataFrame) -> None:
    lines = [
        "# Pythia sweep evidence synthesis",
        "",
        "This note records the first cross-model Pythia-style observational bridge result. It should be read together with the controlled B1 evidence: the Pythia runs test whether primitive/composite residual signatures are measurable in checkpointed LLMs, but they do not test causal dependency.",
        "",
        "## Inputs",
        f"- Sweep synthesis directory: `{sweep_dir}`",
        "",
        "## Main result",
        "The Pythia sweep is now useful as observational bridge evidence. The 70M/160M runs both use the H2-ready slice suite with 29 slices and continuous multiple-choice metrics. Across two model sizes, several composites show stable underperformance relative to primitive-predictor expectations.",
        "",
        "## Run coverage",
    ]
    if not run_summary.empty:
        for _, r in run_summary.iterrows():
            lines.append(
                f"- `{r.get('model_name','')}`: slices={int(r.get('n_slices', 0))}, checkpoints={int(r.get('n_checkpoints', 0))}, "
                f"residual_composites={int(r.get('n_residual_composites', 0))}, under={int(r.get('n_consistent_under', 0))}, over={int(r.get('n_consistent_over', 0))}"
            )
    else:
        lines.append("- Run summary not available.")
    lines += ["", "## Stable composite residuals"]
    top = _top_rows(residual, 12)
    lines.extend(top or ["- No residual stability rows available."])
    lines += ["", "## Composite-family pattern"]
    if not family.empty:
        for _, r in family.iterrows():
            lines.append(
                f"- `{r.get('prompt_family','')}`: runs={int(r.get('n_runs', 0))}, "
                f"mean under-rate={float(r.get('mean_underperforming_metric_rate', float('nan'))):.3f}, "
                f"consistent-under total={int(r.get('total_consistent_under', 0))}, consistent-over total={int(r.get('total_consistent_over', 0))}"
            )
    else:
        lines.append("- Family stability table not available.")
    lines += [
        "",
        "## Thesis interpretation",
        "The sweep strengthens the observational bridge: primitive-to-composite residual analysis is feasible in checkpointed Pythia-like models and some residual patterns persist across model size. This aligns with the controlled B1 lesson that residuals are informative but not self-interpreting.",
        "",
        "The thesis-safe statement is: arithmetic and string composites show stable observational underperformance in the 70M/160M Pythia sweep, while retrieval composites are more model/config dependent. This motivates further observational or mechanistic follow-up, but it is not causal evidence of exact-component dependency.",
        "",
        "## Claim boundary",
    ]
    for _, r in claims.iterrows():
        lines.append(f"- **{r['claim']}** — `{r['status']}`. Boundary: {r['boundary']}")
    lines += [
        "",
        "## Recommended next experiments",
        "1. Run the same H2-ready slice suite on Pythia-410M if compute allows.",
        "2. Run denser checkpoints for 70M/160M to improve trajectory and acquisition-time analyses.",
        "3. Add focused arithmetic-composite slices because arithmetic underperformance is the most stable cross-model residual family so far.",
        "4. Keep the causal language reserved for controlled B1 interventions, not Pythia residuals.",
    ]
    (evidence_dir / "PYTHIA_SWEEP_SYNTHESIS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _update_overall(evidence_dir: Path) -> None:
    path = evidence_dir / "OVERALL_RESULTS_SYNTHESIS.md"
    block = """

## Pythia observational sweep update (v3.1)

The Pythia bridge has progressed from calibration to a useful observational result. With an H2-ready slice suite, Pythia-70M and Pythia-160M both yield primitive/composite residual signatures under continuous multiple-choice metrics. Several arithmetic and string composites are stable underperformers across the two models, while retrieval composites are more model/config dependent. This supports the observational bridge claim that residual analysis can be applied to checkpointed LLMs. It does not establish causal component dependency, because no Pythia pretraining intervention was performed.
"""
    if path.exists():
        txt = path.read_text(encoding="utf-8")
        if "Pythia observational sweep update (v3.1)" not in txt:
            path.write_text(txt.rstrip() + block + "\n", encoding="utf-8")
    else:
        path.write_text("# Overall results synthesis\n" + block + "\n", encoding="utf-8")


def main() -> None:
    p = argparse.ArgumentParser(description="Consolidate Pythia sweep outputs into the durable thesis evidence archive.")
    p.add_argument("--sweep-synthesis-dir", default="results/pythia_sweep_synthesis_v30")
    p.add_argument("--evidence-dir", default="thesis_evidence")
    p.add_argument("--code-version", default="v3.1")
    p.add_argument("--archive-root", default="results/archive")
    p.add_argument("--thesis-use", default="candidate")
    args = p.parse_args()

    sweep_dir = Path(args.sweep_synthesis_dir)
    evidence_dir = Path(args.evidence_dir)
    tables_dir = evidence_dir / "tables"
    summaries_dir = evidence_dir / "results_summaries"
    tables_dir.mkdir(parents=True, exist_ok=True)
    summaries_dir.mkdir(parents=True, exist_ok=True)

    run_summary = _read_csv(sweep_dir / "pythia_sweep_run_summary.csv")
    residual = _read_csv(sweep_dir / "pythia_sweep_residual_stability.csv")
    family = _read_csv(sweep_dir / "pythia_sweep_family_stability.csv")
    claims = _claim_table()

    # Copy canonical tables into thesis_evidence/tables.
    copies = {
        "pythia_sweep_run_summary.csv": "pythia_sweep_run_summary.csv",
        "pythia_sweep_residual_stability.csv": "pythia_sweep_residual_stability.csv",
        "pythia_sweep_family_stability.csv": "pythia_sweep_family_stability.csv",
    }
    copied: list[str] = []
    for src_name, dst_name in copies.items():
        if _copy_if_exists(sweep_dir / src_name, tables_dir / dst_name):
            copied.append(str(tables_dir / dst_name))
        if _copy_if_exists(sweep_dir / src_name, summaries_dir / f"v30_{src_name}"):
            copied.append(str(summaries_dir / f"v30_{src_name}"))
    if _copy_if_exists(sweep_dir / "PYTHIA_SWEEP_SYNTHESIS.md", summaries_dir / "v30_PYTHIA_SWEEP_SYNTHESIS.md"):
        copied.append(str(summaries_dir / "v30_PYTHIA_SWEEP_SYNTHESIS.md"))

    claims.to_csv(tables_dir / "pythia_sweep_claim_boundary.csv", index=False)
    _write_synthesis(evidence_dir, sweep_dir, run_summary, residual, family, claims)
    _update_overall(evidence_dir)

    manifest = write_manifest(
        evidence_dir / "pythia_sweep_evidence_package",
        experiment="Pythia_sweep_evidence_consolidation",
        backend="Pythia_observational",
        code_version=args.code_version,
        input_paths={"sweep_synthesis_dir": str(sweep_dir), "evidence_dir": str(evidence_dir)},
        extra={"thesis_use": args.thesis_use, "copied_outputs": copied},
    )
    append_registry(Path(args.archive_root) / "results_registry.csv", {
        "run_id": manifest["run_id"],
        "code_version": args.code_version,
        "experiment": manifest["experiment"],
        "backend": manifest["backend"],
        "output_path": str(evidence_dir / "pythia_sweep_evidence_package"),
        "status": "created",
        "thesis_use": args.thesis_use,
        "created_at_utc": manifest["created_at_utc"],
    })
    print(f"Consolidated Pythia sweep evidence into {evidence_dir}")


if __name__ == "__main__":
    main()
