from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Any

from ic_experiments.run_management import write_manifest, append_registry


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _copy_if_exists(src: Path, dst_dir: Path) -> str:
    if src.exists():
        dst_dir.mkdir(parents=True, exist_ok=True)
        dst = dst_dir / src.name
        dst.write_bytes(src.read_bytes())
        return str(dst)
    return ""


def build_summary_text() -> str:
    return """# First-stage experiment summary

This summary freezes the first controlled evidence arc and the first Pythia-style observational bridge. It is intended to support the thesis Methodology & Implementation and Results & Discussion sections. It is not a final paper draft; it is a claim-bounded evidence map.

## Core thesis position after the first stage

The first-stage evidence supports a controlled-methodology claim, not a universal LLM-mechanism claim.

**Supported claim:** acquisition order and composite residuals are not self-interpreting. In controlled sequence-transformer training, structural predictors and atomic-parallel residuals can identify candidate composite bottlenecks, but matched interventions and readiness checks are needed to distinguish exact-component dependency, operation-family transfer, and hard-composite failure. In the first B1 family, one substitution-side pair shows localized exact-component sensitivity with behavioral and gradient evidence. In the second B1 family, H1/H2 structure replicates, but exact H3 dependency does not replicate under tested settings.

**Unsupported claim:** there is a universal component-before-composite mechanism that explains LLM pretraining. The controlled B1 evidence is causal only inside the constructed task families. The Pythia experiments are observational and can only test for analogous signatures.

## Evidence arc

1. **Recovery and controlled task-design gates.** The project first checks that the analysis can recover known synthetic mechanisms before interpreting neural training. This protects against overfitting the analysis pipeline to desired conclusions.
2. **B1 family 1 controlled transformer experiments.** H1 shows structured acquisition; H2 identifies composite residuals; H3 shows one localized exact-component dependency site; mediator diagnostics show that the positive pair has unusually high early gradient alignment.
3. **B1 family 2 replication/stress test.** H1/H2 again show structured acquisition, but the learnability proxy reverses and H3 does not replicate exact dependency. Family 2 exposes the need for H3-readiness checks.
4. **Pythia observational bridge.** Pythia-70M slice experiments are not causal, but continuous multiple-choice scores now show measurable primitive/composite trajectories and valid H2-style residual rows in the expanded slice suite.

## First-stage result in one sentence

The controlled experiments support a boundary-mapping view of skill acquisition: some composite residuals correspond to localized exact-component sensitivity, others reflect operation-family transfer, and others are simply too hard or subthreshold for intervention; observational Pythia results currently support feasibility of the bridge, not causal generalization.
"""


def build_methodology_text() -> str:
    return """# Methodology & Implementation draft notes

## Methodological design

The experiments are staged to avoid interpreting acquisition order as causality. The pipeline is:

1. **Synthetic recovery.** Validate that the predictor ladder and residual logic can recover known synthetic worlds.
2. **Controlled task families.** Build sequence-DSL families with atomic tasks, true composites, shortcut/fake components, surface controls, same-operation controls, and different-operation controls.
3. **H1 ordering analysis.** Train small transformers over mixed task data and measure per-task acquisition curves across configurations and seeds.
4. **H2 atomic parallel-null analysis.** Fit predictor ladders on atomic tasks only, then predict composite acquisition times. Composite residuals select candidates, but are explicitly treated as observational.
5. **H3 interventions.** Manipulate candidate components with pretraining, upweighting, corruption, and delay, and compare against matched same-operation, different-operation, fake, and surface controls.
6. **Mediator diagnostics.** Compare positive and negative H3 pairs using early gradient and representation coupling.
7. **Cross-family replication/stress test.** Repeat the framework on a second generated B1 family and explicitly track which claims replicate.
8. **Pythia observational bridge.** Evaluate checkpointed Pythia-style models on primitive/composite/control slices with multiple-choice likelihood scores. This stage tests only observational analogues.

## Key implementation choices

- Acquisition is measured primarily with held-out token accuracy for B1 and continuous multiple-choice scores for Pythia.
- Thresholds are analysis hyperparameters, not training hyperparameters. Threshold sensitivity is used to distinguish clear acquisition from subthreshold movement.
- H3 candidate selection now uses both residual magnitude and readiness: a candidate must be delayed enough to be interesting but not so hard that no intervention can move it.
- Pythia evaluation uses observational slices and continuous scores because top-1 accuracy can be too harsh for small checkpointed models.

## Validity controls

The task design includes several controls to reduce spurious interpretation:

- **Same-operation controls** test whether a result is exact-component-specific or merely operation-family transfer.
- **Different-operation controls** test whether an intervention effect is generic data-budget transfer.
- **Fake/shortcut controls** test whether formal labels or shortcut structure are sufficient.
- **Surface controls** test whether shared tokens/templates explain the effect.
- **Negative and mixed results** are retained as evidence boundaries rather than discarded.

## Implementation boundary

Causal claims are limited to controlled B1 interventions. Pythia experiments are observational and cannot establish causal dependency without pretraining interventions.
"""


def build_results_text() -> str:
    return """# Results & Discussion draft notes

## Result 1: acquisition is structured but not governed by one universal scalar predictor

Both B1 families show structured acquisition, but predictor dominance differs. Family 1 supported expected frequency and learnability directions, with learnability especially strong. Family 2 showed stable frequency but reversed learnability-proxy signs. This argues against a universal scalar law and motivates the predictor-ladder approach.

## Result 2: H2 residuals are useful candidate selectors, not causal evidence

In family 1, H2 residuals selected candidates that included one localized H3-positive pair. In family 2, H2 residuals were large but often selected composites that were too hard or only subthreshold-ready. Residual magnitude alone is therefore insufficient.

## Result 3: H3 reveals heterogeneous mechanisms

Family 1 H3 synthesis shows four outcomes: one positive exact-component pair, one weak/mixed pair, one operation-family transfer pair, and one negative pair. This heterogeneity is the central result: formal component graphs and acquisition order do not by themselves reveal the mechanism.

## Result 4: the strongest localized dependency site has mediator support

The positive family-1 pair, A02_substitute → C06_reverse_then_substitute_02_00, is supported by exact-component pretraining/corruption and by high early gradient alignment relative to same-operation, different-operation, fake, and surface controls. CKA was not discriminative, so the mediator claim should be gradient-based.

## Result 5: second-family replication is a stress test, not a positive H3 replication

Family 2 replicates that acquisition is structured and H2 residuals can be large, but it does not replicate exact-component dependency under the tested H3 settings. It contributes a methodological boundary: H3-readiness checks are necessary.

## Result 6: Pythia bridge is now feasible but observational

The expanded Pythia H2-ready suite has enough atomics and composites for continuous H2-style residual analysis. Pythia-70M produces measurable continuous-score movement and valid composite residual rows, especially under log-probability and margin-like metrics. These results are observational and should be used as a bridge, not causal evidence.

## Discussion-level takeaway

The first-stage experiments support a careful contribution: they provide a framework for distinguishing parallel rate effects, operation-family transfer, localized exact-component dependency, and hard-composite failure. This is more defensible than claiming a universal curriculum mechanism.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Create first-stage thesis experiment summary package.")
    parser.add_argument("--evidence-dir", default="thesis_evidence")
    parser.add_argument("--output-dir", default="thesis_evidence/first_stage_summary")
    parser.add_argument("--code-version", default="v2.8")
    parser.add_argument("--archive-root", default="results/archive")
    parser.add_argument("--thesis-use", default="candidate")
    args = parser.parse_args()

    evidence_dir = Path(args.evidence_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / "FIRST_STAGE_EXPERIMENT_SUMMARY.md").write_text(build_summary_text(), encoding="utf-8")
    (output_dir / "METHODOLOGY_IMPLEMENTATION_DRAFT.md").write_text(build_methodology_text(), encoding="utf-8")
    (output_dir / "RESULTS_DISCUSSION_DRAFT.md").write_text(build_results_text(), encoding="utf-8")

    claim_rows = [
        {"claim": "B1 acquisition is structured", "status": "supported across two controlled families", "evidence": "H1/H2 available in both families", "boundary": "predictor signs differ; no universal scalar law"},
        {"claim": "Reference learnability universally predicts later acquisition", "status": "not supported", "evidence": "family 2 reverses the proxy sign", "boundary": "treat as family-specific structural proxy until audited"},
        {"claim": "H2 residuals select useful candidates", "status": "supported with readiness gate", "evidence": "family 1 selected a positive pair; family 2 exposed hard candidates", "boundary": "residual magnitude alone is insufficient"},
        {"claim": "Exact-component dependency occurs", "status": "localized support", "evidence": "A02_substitute to C06 in family 1", "boundary": "not replicated as broad cross-family phenomenon"},
        {"claim": "Operation-family transfer is an alternative mechanism", "status": "supported pilot", "evidence": "reverse-side cases where exact and same-operation controls match", "boundary": "prevalence not quantified"},
        {"claim": "Pythia shows observational primitive/composite dynamics", "status": "supported as feasibility/bridge", "evidence": "v2.7 H2-ready slice suite yields valid continuous residual rows", "boundary": "observational only; no causal dependency"},
        {"claim": "Controlled results causally explain Pythia/LLMs", "status": "not tested", "evidence": "no pretraining interventions on Pythia", "boundary": "only observational analogues are allowed"},
    ]
    _write_csv(output_dir / "first_stage_claim_table.csv", claim_rows)

    experiment_rows = [
        {"stage": "Exp0", "purpose": "synthetic recovery", "status": "completed", "thesis_role": "pipeline validity"},
        {"stage": "B2", "purpose": "sparse-parity frequency/quanta baseline", "status": "partial", "thesis_role": "contrast regime; needs strengthening"},
        {"stage": "B1 family 1 H1/H2/H3", "purpose": "controlled causal arc", "status": "completed", "thesis_role": "main controlled positive and heterogeneity evidence"},
        {"stage": "B1 family 1 mediator", "purpose": "gradient/representation corroboration", "status": "completed", "thesis_role": "gradient support for positive pair; CKA negative"},
        {"stage": "B1 family 2", "purpose": "replication/stress test", "status": "completed diagnostic", "thesis_role": "regime contrast and H3-readiness boundary"},
        {"stage": "Pythia v2.4-v2.7", "purpose": "observational bridge", "status": "calibrated and H2-ready", "thesis_role": "observational feasibility, not causal evidence"},
    ]
    _write_csv(output_dir / "first_stage_experiment_map.csv", experiment_rows)

    figure_rows = [
        {"figure_or_table": "Figure: staged methodology pipeline", "source": "summary/design docs", "section": "Methodology"},
        {"figure_or_table": "Table: claim boundary matrix", "source": "first_stage_claim_table.csv", "section": "Results/Discussion"},
        {"figure_or_table": "Figure: B1 H1 predictor signs by family", "source": "H1 reports/summaries", "section": "Results"},
        {"figure_or_table": "Figure: H3 pair evidence matrix", "source": "h3_pair_evidence_matrix.csv and cross-family synthesis", "section": "Results"},
        {"figure_or_table": "Figure: mediator gradient alignment", "source": "mediator_contrast_summary.csv", "section": "Results"},
        {"figure_or_table": "Table: family 2 readiness diagnostic", "source": "h3_readiness_report/table", "section": "Discussion"},
        {"figure_or_table": "Figure: Pythia continuous residuals", "source": "pythia_continuous_h2_residuals.csv", "section": "Observational bridge"},
    ]
    _write_csv(output_dir / "first_stage_figure_table_plan.csv", figure_rows)

    # Also place stable copies at top-level thesis_evidence for visibility.
    top_level_files = {
        "FIRST_STAGE_EXPERIMENT_SUMMARY.md": build_summary_text(),
        "METHODOLOGY_IMPLEMENTATION_DRAFT.md": build_methodology_text(),
        "RESULTS_DISCUSSION_DRAFT.md": build_results_text(),
    }
    evidence_dir.mkdir(parents=True, exist_ok=True)
    for name, text in top_level_files.items():
        (evidence_dir / name).write_text(text, encoding="utf-8")

    tables_dir = evidence_dir / "tables"
    _write_csv(tables_dir / "first_stage_claim_table.csv", claim_rows)
    _write_csv(tables_dir / "first_stage_experiment_map.csv", experiment_rows)
    _write_csv(tables_dir / "first_stage_figure_table_plan.csv", figure_rows)

    manifest = write_manifest(
        output_dir,
        experiment="first_stage_experiment_summary",
        backend="thesis_evidence",
        code_version=args.code_version,
        input_paths={"evidence_dir": str(evidence_dir)},
        extra={"thesis_use": args.thesis_use},
    )
    append_registry(
        Path(args.archive_root) / "results_registry.csv",
        {
            "run_id": manifest["run_id"],
            "code_version": args.code_version,
            "experiment": "first_stage_experiment_summary",
            "output_path": str(output_dir),
            "thesis_use": args.thesis_use,
            "status": "created",
        },
    )

    index = f"""# First-stage summary package index

Generated by `make_first_stage_experiment_summary`.

## Files

- `FIRST_STAGE_EXPERIMENT_SUMMARY.md`
- `METHODOLOGY_IMPLEMENTATION_DRAFT.md`
- `RESULTS_DISCUSSION_DRAFT.md`
- `first_stage_claim_table.csv`
- `first_stage_experiment_map.csv`
- `first_stage_figure_table_plan.csv`
- `run_manifest.json`

## Claim boundary

This package summarizes the first-stage controlled and observational experiments. It supports controlled-methodology and localized-dependency claims, not a universal LLM causal mechanism.
"""
    (output_dir / "first_stage_summary_index.md").write_text(index, encoding="utf-8")
    print(f"Wrote first-stage experiment summary to {output_dir}")


if __name__ == "__main__":
    main()
