"""Create a draft-ready final experiment-state package.

This command is intended as a thesis bookkeeping step after the first full
controlled arc and the Tier-1 Pythia observational sweep.  It does not rerun
experiments.  It records what is complete, what is thesis-useful, what remains
optional, and the claim boundary that should guide drafting.
"""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List

import pandas as pd


CONTROLLED_ROWS: List[Dict[str, object]] = [
    {
        "block": "Exp0 recovery gate",
        "status": "complete",
        "thesis_use": "sanity_check",
        "claim_supported": "analysis pipeline can recover known synthetic dependency/order structure",
        "claim_boundary": "not substantive evidence about LLMs",
        "recommended_action": "cite briefly in methods/validation appendix",
    },
    {
        "block": "B1 family 1 H1/H2",
        "status": "complete",
        "thesis_use": "core_controlled_evidence",
        "claim_supported": "acquisition is structured; atomic parallel-null residuals select composite candidates",
        "claim_boundary": "observational residuals are candidate selectors, not causal evidence",
        "recommended_action": "use in controlled results section",
    },
    {
        "block": "B1 family 1 H3 interventions",
        "status": "complete",
        "thesis_use": "core_controlled_evidence",
        "claim_supported": "one localized exact-component dependency site, A02_substitute -> C06_reverse_then_substitute_02_00; other rows weak/operation-family",
        "claim_boundary": "pair-specific; not universal component-before-composite law",
        "recommended_action": "use as main causal controlled result",
    },
    {
        "block": "B1 family 1 mediator diagnostics",
        "status": "complete",
        "thesis_use": "mechanistic_support",
        "claim_supported": "positive H3 pair has unusually high early gradient alignment relative to controls",
        "claim_boundary": "gradient-mediator support only; current CKA was not discriminative",
        "recommended_action": "use as mechanism corroboration, not standalone causal proof",
    },
    {
        "block": "B1 family 2 H1/H2",
        "status": "complete",
        "thesis_use": "regime_contrast",
        "claim_supported": "acquisition/residual structure recurs, but predictor semantics differ and learnability proxy reverses",
        "claim_boundary": "no universal scalar predictor; reference_learnability requires auditing/interpretation",
        "recommended_action": "use to argue against over-simple laws",
    },
    {
        "block": "B1 family 2 H3/readiness",
        "status": "complete_enough",
        "thesis_use": "boundary_condition",
        "claim_supported": "large residuals can be hard-composite failures or operation-family/weak-negative cases; readiness gate is necessary",
        "claim_boundary": "does not replicate exact dependency; do not present as positive H3 evidence",
        "recommended_action": "use as methodological caution and cross-family boundary",
    },
    {
        "block": "B1 cross-family synthesis",
        "status": "complete",
        "thesis_use": "claim_boundary",
        "claim_supported": "controlled evidence supports heterogeneous mechanisms: exact dependency, operation-family transfer, weak/negative cases, hard-composite failure",
        "claim_boundary": "exact dependency currently localized, not broadly replicated",
        "recommended_action": "use as central discussion framing",
    },
    {
        "block": "B2 sparse-parity baseline",
        "status": "partial_optional",
        "thesis_use": "contrast_if_space",
        "claim_supported": "frequency/quanta-like regime contrast is plausible but not yet as complete as B1",
        "claim_boundary": "do not over-weight unless strengthened",
        "recommended_action": "optional strengthening experiment or brief appendix",
    },
]

PYTHIA_ROWS: List[Dict[str, object]] = [
    {
        "block": "Pythia calibration v2.4-v2.6",
        "status": "complete",
        "thesis_use": "methods_bridge",
        "claim_supported": "top-1 accuracy is too harsh; continuous multiple-choice scores reveal subthreshold movement",
        "claim_boundary": "calibration only; no H2 claim from early small slice suites",
        "recommended_action": "use to justify continuous-score methodology",
    },
    {
        "block": "Pythia H2-ready slice suite v2.7",
        "status": "complete",
        "thesis_use": "observational_bridge",
        "claim_supported": "29-slice suite with 16 atomics, 10 composites, 3 controls enables primitive-to-composite residual fitting",
        "claim_boundary": "observational slice design; no causal dependency claim",
        "recommended_action": "describe in methodology/implementation",
    },
    {
        "block": "Pythia residual refinement v2.9",
        "status": "complete",
        "thesis_use": "observational_bridge",
        "claim_supported": "single-model residuals become interpretable across multiple continuous metrics and composite families",
        "claim_boundary": "single-model result is weaker than sweep; use mainly as stepping stone",
        "recommended_action": "summarize briefly before sweep result",
    },
    {
        "block": "Pythia Tier-1 sweep through 1.4B",
        "status": "complete",
        "thesis_use": "main_pythia_observational_result",
        "claim_supported": "stable primitive-to-composite residual underperformance across valid runs from 70M through 1.4B; strongest for arithmetic and string composites",
        "claim_boundary": "observational residual stability, not causal component dependency and not B1 H3 replication",
        "recommended_action": "use as main Pythia bridge result",
    },
    {
        "block": "Pythia 2.8B+ large tier",
        "status": "skipped_for_now_engineering",
        "thesis_use": "future_work",
        "claim_supported": "none for checkpoint dynamics yet",
        "claim_boundary": "revision/loading issue produced static or untrusted checkpoint curves; do not use as dynamic evidence",
        "recommended_action": "record as future work or engineering limitation; skip for thesis core",
    },
]

CLAIM_ROWS: List[Dict[str, object]] = [
    {
        "claim": "Acquisition order and residuals are informative diagnostics",
        "status": "supported",
        "evidence": "B1 H1/H2 across two families; Pythia H2-ready residual sweep",
        "boundary": "diagnostic, not automatically causal",
    },
    {
        "claim": "H2 residuals identify useful candidate composites",
        "status": "supported_with_readiness_gate",
        "evidence": "family 1 selected positive H3 pair; family 2 exposed hard/subthreshold candidates",
        "boundary": "residual magnitude alone is insufficient",
    },
    {
        "claim": "Exact-component dependency exists in the controlled setup",
        "status": "localized_supported",
        "evidence": "A02_substitute -> C06 intervention result plus gradient alignment",
        "boundary": "one localized pair; not broadly replicated",
    },
    {
        "claim": "Operation-family transfer is an alternative mechanism",
        "status": "supported_pilot",
        "evidence": "reverse-side H3 rows where exact and same-operation controls match",
        "boundary": "prevalence not fully quantified",
    },
    {
        "claim": "Hard-composite failure/readiness is a separate failure mode",
        "status": "supported",
        "evidence": "family 2 C00/C06 readiness and threshold diagnostics",
        "boundary": "methodological lesson rather than dependency evidence",
    },
    {
        "claim": "A universal component-before-composite law holds",
        "status": "not_supported",
        "evidence": "family 2 no positive exact dependency; multiple weak/negative rows",
        "boundary": "should explicitly reject/avoid this wording",
    },
    {
        "claim": "Reference learnability universally predicts acquisition order",
        "status": "not_supported",
        "evidence": "family 2 reverses the reference_learnability sign",
        "boundary": "treat as family-specific structural proxy",
    },
    {
        "claim": "Pythia shows stable primitive-to-composite residual signatures",
        "status": "supported_observational_through_1p4b",
        "evidence": "Tier-1 sweep across valid runs from 70M through 1.4B",
        "boundary": "observational only; no pretraining intervention",
    },
    {
        "claim": "Pythia causally learns composites through primitives",
        "status": "not_supported",
        "evidence": "Pythia experiments are checkpoint observations only",
        "boundary": "requires interventions or stronger causal/mechanistic probes not currently done",
    },
]

REMAINING_ROWS: List[Dict[str, object]] = [
    {
        "experiment": "B2 sparse-parity strengthening",
        "priority": "optional_high_value",
        "why": "improves contrast with frequency/quanta-style theories",
        "expected_decision": "whether frequency-dominated regime contrasts with B1 compositional regime",
        "needed_for_draft": "no",
    },
    {
        "experiment": "Third B1 family with H3-readiness built into selection",
        "priority": "optional_high_value",
        "why": "tests whether localized exact dependency recurs under a better replication design",
        "expected_decision": "replicated localized dependency vs family-specific result",
        "needed_for_draft": "no, but useful if time permits",
    },
    {
        "experiment": "Stronger mediator diagnostics",
        "priority": "optional_high_value",
        "why": "deepens mechanism beyond gradient cosine; probes/layerwise gradients/finetune transfer",
        "expected_decision": "whether positive H3 pair has broader mechanistic signatures",
        "needed_for_draft": "no",
    },
    {
        "experiment": "Focused Pythia arithmetic residual suite",
        "priority": "optional_high_value",
        "why": "arithmetic composites have the strongest stable Pythia underperformance",
        "expected_decision": "whether arithmetic residuals persist in richer slice family",
        "needed_for_draft": "no, but useful for paper-quality Pythia section",
    },
    {
        "experiment": "Pythia 2.8B/6.9B/12B after checkpoint-loading fix",
        "priority": "nice_to_have",
        "why": "extends model-size trend beyond 1.4B",
        "expected_decision": "whether Tier-1 residual pattern survives larger models",
        "needed_for_draft": "no; current issue should be reported as engineering/future work",
    },
    {
        "experiment": "Denser Pythia checkpoints for 70M/160M/410M",
        "priority": "nice_to_have",
        "why": "improves trajectory/acquisition timing rather than final residuals",
        "expected_decision": "whether residual signatures have stable temporal onset",
        "needed_for_draft": "no",
    },
]

FIGURE_ROWS: List[Dict[str, object]] = [
    {
        "figure_or_table": "Fig 1: Method pipeline diagram",
        "section": "Methodology",
        "source": "conceptual: H1 -> H2 residuals -> H3 interventions -> mediator -> Pythia observational bridge",
        "status": "draft_ready",
    },
    {
        "figure_or_table": "Table 1: Controlled task design and controls",
        "section": "Methodology",
        "source": "TASK_DESIGN_JUSTIFICATION, B1 task metadata",
        "status": "draft_ready",
    },
    {
        "figure_or_table": "Fig 2/Table 2: B1 family 1 H3 evidence matrix",
        "section": "Controlled Results",
        "source": "h3_pair_evidence_matrix, mediator diagnostics",
        "status": "draft_ready",
    },
    {
        "figure_or_table": "Fig 3: Mediator gradient alignment contrasts",
        "section": "Controlled Results",
        "source": "b1_mediator_h3_pairs_v18 contrast summary",
        "status": "draft_ready",
    },
    {
        "figure_or_table": "Table 3: Cross-family controlled synthesis",
        "section": "Controlled Results/Discussion",
        "source": "cross_family_claim_matrix and cross_family_stage_summary",
        "status": "draft_ready",
    },
    {
        "figure_or_table": "Fig 4: Pythia residual stability by composite",
        "section": "Pythia Observational Bridge",
        "source": "pythia_sweep_residual_stability.csv from Tier-1 sweep",
        "status": "draft_ready_after_consolidation",
    },
    {
        "figure_or_table": "Fig 5/Table 4: Pythia residual stability by family",
        "section": "Pythia Observational Bridge",
        "source": "pythia_sweep_family_stability.csv from Tier-1 sweep",
        "status": "draft_ready_after_consolidation",
    },
    {
        "figure_or_table": "Table 5: Final claim-boundary matrix",
        "section": "Discussion",
        "source": "final_claim_boundary_matrix.csv",
        "status": "draft_ready",
    },
]


def _write_csv(path: Path, rows: List[Dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(path, index=False)


def _copy_if_exists(src: Path, dst: Path) -> bool:
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return True
    return False


def _load_pythia_sweep_summary(sweep_dir: Path | None) -> Dict[str, object]:
    out: Dict[str, object] = {
        "provided": bool(sweep_dir),
        "exists": bool(sweep_dir and sweep_dir.exists()),
        "runs_included": None,
        "valid_runs": None,
        "models": "not parsed",
        "arithmetic_mean_under_rate": None,
        "string_mean_under_rate": None,
        "retrieval_mean_under_rate": None,
    }
    if not sweep_dir or not sweep_dir.exists():
        return out
    run_summary = sweep_dir / "pythia_sweep_run_summary.csv"
    family_summary = sweep_dir / "pythia_sweep_family_stability.csv"
    if run_summary.exists():
        df = pd.read_csv(run_summary)
        out["runs_included"] = len(df)
        valid = df[df.get("residual_composites", 0).fillna(0) > 0] if "residual_composites" in df.columns else df
        out["valid_runs"] = len(valid)
        if "model_name" in valid.columns:
            out["models"] = ";".join(sorted(str(x) for x in valid["model_name"].dropna().unique()))
        elif "model" in valid.columns:
            out["models"] = ";".join(sorted(str(x) for x in valid["model"].dropna().unique()))
    if family_summary.exists():
        fam = pd.read_csv(family_summary)
        for _, row in fam.iterrows():
            name = str(row.get("family", row.get("composite_family", "")))
            rate = row.get("mean_under_rate")
            if name in {"arithmetic", "string", "retrieval"}:
                out[f"{name}_mean_under_rate"] = rate
    return out


def _markdown_table(rows: List[Dict[str, object]], columns: List[str]) -> str:
    if not rows:
        return ""
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join(["---"] * len(columns)) + " |"
    lines = [header, sep]
    for row in rows:
        vals = [str(row.get(c, "")).replace("\n", " ") for c in columns]
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def build_docs(evidence_dir: Path, out_dir: Path, sweep_info: Dict[str, object], code_version: str) -> None:
    now = datetime.now(timezone.utc).isoformat()
    all_rows = CONTROLLED_ROWS + PYTHIA_ROWS

    final_state = f"""# Final experiment-state consolidation

Generated at: `{now}`  
Code version: `{code_version}`

## Bottom-line state

The project is ready to begin thesis drafting after this consolidation.  The controlled core is complete, and the Pythia observational bridge is complete through the Tier-1 sweep up to 1.4B.  Larger Pythia models are explicitly marked as future work because the current checkpoint-loading path did not yet provide trustworthy multi-checkpoint dynamics for 2.8B+.

```text
CONTROLLED_CORE_COMPLETE = yes
B1_CROSS_FAMILY_SYNTHESIS_COMPLETE = yes
PYTHIA_BRIDGE_COMPLETE_THROUGH_1P4B = yes
LARGE_PYTHIA_2P8B_PLUS = skipped_for_now_engineering
CLAIMS_READY_FOR_DRAFT = yes
```

## Current supported thesis claim

The supported thesis claim is a boundary-mapping claim, not a universal skill-law claim:

> Acquisition order and primitive-to-composite residuals are useful diagnostics, but they are not self-interpreting.  In controlled B1 training, interventions distinguish localized exact-component dependency from operation-family transfer, weak/negative cases, and hard-composite failure.  In checkpointed Pythia models through the Tier-1 sweep, analogous primitive-to-composite residual signatures are measurable and stable observationally, but they remain non-causal.

## Experiment blocks

{_markdown_table(all_rows, ["block", "status", "thesis_use", "claim_supported", "claim_boundary"])}

## Pythia sweep summary parsed from latest synthesis

```json
{json.dumps(sweep_info, indent=2)}
```

## Drafting decision

Start the thesis draft now.  Additional experiments should be treated as strengthening/future-work unless they directly address a reviewer-risk point.
"""

    readiness = f"""# Thesis draft readiness memo

Generated at: `{now}`

## Ready sections

### Methodology & Implementation

Ready to draft:

1. Controlled B1 sequence-DSL task family and matched controls.
2. H1 ordering analysis, H2 atomic parallel-null residuals, H3 interventions.
3. H3-readiness gate and threshold sensitivity.
4. Mediator diagnostics with gradient alignment.
5. Pythia observational bridge: slice suite, continuous multiple-choice scores, residual refinement, Tier-1 sweep.

### Results & Discussion

Ready to draft:

1. Family 1 localized exact dependency: `A02_substitute -> C06_reverse_then_substitute_02_00`.
2. Family 1 heterogeneity: weak/negative and operation-family cases.
3. Mediator support: early gradient alignment supports the positive pair; CKA is non-discriminative.
4. Family 2 stress test: predictor regime shift, H3-readiness boundary, no positive exact replication.
5. Pythia Tier-1 observational residuals: stable primitive-to-composite underperformance through 1.4B, strongest for arithmetic and string composites.

## Required caution language

Use:

> observational residual signatures

Do not use:

> Pythia causal dependency

Use:

> localized exact-component sensitivity in one controlled pair

Do not use:

> universal component-before-composite mechanism

## Large-model note

The 2.8B+ Pythia stage should be described as future work or an engineering limitation unless revision-loading is repaired and multi-checkpoint fingerprints/curves differ.  Current 2.8B static residuals should not be used as acquisition-dynamics evidence.
"""

    out_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / "FINAL_EXPERIMENT_STATE.md").write_text(final_state)
    (evidence_dir / "THESIS_DRAFT_READINESS.md").write_text(readiness)
    (out_dir / "FINAL_EXPERIMENT_STATE.md").write_text(final_state)
    (out_dir / "THESIS_DRAFT_READINESS.md").write_text(readiness)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence-dir", required=True)
    ap.add_argument("--pythia-sweep-synthesis-dir", default=None)
    ap.add_argument("--output-dir", default=None)
    ap.add_argument("--code-version", default="v3.3")
    ap.add_argument("--archive-root", default=None)
    ap.add_argument("--thesis-use", default="candidate")
    args = ap.parse_args()

    evidence_dir = Path(args.evidence_dir)
    out_dir = Path(args.output_dir) if args.output_dir else evidence_dir / "final_experiment_state"
    table_dir = evidence_dir / "tables"
    summary_dir = evidence_dir / "results_summaries"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    table_dir.mkdir(parents=True, exist_ok=True)
    summary_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    sweep_dir = Path(args.pythia_sweep_synthesis_dir) if args.pythia_sweep_synthesis_dir else None
    sweep_info = _load_pythia_sweep_summary(sweep_dir)

    _write_csv(table_dir / "final_experiment_state_table.csv", CONTROLLED_ROWS + PYTHIA_ROWS)
    _write_csv(table_dir / "final_claim_boundary_matrix.csv", CLAIM_ROWS)
    _write_csv(table_dir / "final_remaining_experiments.csv", REMAINING_ROWS)
    _write_csv(table_dir / "final_figure_table_checklist.csv", FIGURE_ROWS)

    _write_csv(out_dir / "final_experiment_state_table.csv", CONTROLLED_ROWS + PYTHIA_ROWS)
    _write_csv(out_dir / "final_claim_boundary_matrix.csv", CLAIM_ROWS)
    _write_csv(out_dir / "final_remaining_experiments.csv", REMAINING_ROWS)
    _write_csv(out_dir / "final_figure_table_checklist.csv", FIGURE_ROWS)

    if sweep_dir and sweep_dir.exists():
        copied = []
        for name in [
            "PYTHIA_SWEEP_SYNTHESIS.md",
            "pythia_sweep_run_summary.csv",
            "pythia_sweep_residual_stability.csv",
            "pythia_sweep_family_stability.csv",
        ]:
            src = sweep_dir / name
            dst1 = summary_dir / f"v32_tier1_{name}"
            dst2 = out_dir / f"v32_tier1_{name}"
            if _copy_if_exists(src, dst1):
                copied.append(str(dst1))
            _copy_if_exists(src, dst2)
        # Copy canonical current Pythia result into thesis_evidence root/tables as well.
        _copy_if_exists(sweep_dir / "PYTHIA_SWEEP_SYNTHESIS.md", evidence_dir / "PYTHIA_TIER1_SWEEP_SYNTHESIS.md")
        _copy_if_exists(sweep_dir / "pythia_sweep_run_summary.csv", table_dir / "pythia_tier1_sweep_run_summary.csv")
        _copy_if_exists(sweep_dir / "pythia_sweep_residual_stability.csv", table_dir / "pythia_tier1_sweep_residual_stability.csv")
        _copy_if_exists(sweep_dir / "pythia_sweep_family_stability.csv", table_dir / "pythia_tier1_sweep_family_stability.csv")

    build_docs(evidence_dir, out_dir, sweep_info, args.code_version)

    manifest = {
        "experiment": "final_experiment_state_consolidation",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "code_version": args.code_version,
        "thesis_use": args.thesis_use,
        "evidence_dir": str(evidence_dir),
        "output_dir": str(out_dir),
        "pythia_sweep_synthesis_dir": str(sweep_dir) if sweep_dir else None,
        "pythia_sweep_info": sweep_info,
        "outputs": [
            str(evidence_dir / "FINAL_EXPERIMENT_STATE.md"),
            str(evidence_dir / "THESIS_DRAFT_READINESS.md"),
            str(table_dir / "final_experiment_state_table.csv"),
            str(table_dir / "final_claim_boundary_matrix.csv"),
            str(table_dir / "final_remaining_experiments.csv"),
            str(table_dir / "final_figure_table_checklist.csv"),
        ],
    }
    (out_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2))

    if args.archive_root:
        archive_root = Path(args.archive_root)
        archive_root.mkdir(parents=True, exist_ok=True)
        reg = archive_root / "results_registry.csv"
        row = pd.DataFrame([
            {
                "created_at_utc": manifest["created_at_utc"],
                "code_version": args.code_version,
                "thesis_use": args.thesis_use,
                "experiment": "final_experiment_state_consolidation",
                "output_dir": str(out_dir),
            }
        ])
        if reg.exists():
            try:
                old = pd.read_csv(reg)
                row = pd.concat([old, row], ignore_index=True)
            except Exception:
                pass
        row.to_csv(reg, index=False)

    print(f"Wrote final experiment state to {out_dir}")


if __name__ == "__main__":
    main()
