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
    p = argparse.ArgumentParser(description="Analyze B1 mediator diagnostics for H3 pairs.")
    p.add_argument("--result-dir", type=Path, required=True)
    p.add_argument("--h3-evidence-matrix", type=Path, default=None, help="Optional h3_pair_evidence_matrix.csv for verdict labels.")
    p.add_argument("--early-max-fraction", type=float, default=0.20)
    p.add_argument("--code-version", type=str, default="v1.8")
    p.add_argument("--archive-root", type=Path, default=None)
    p.add_argument("--thesis-use", type=str, default="candidate")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    out = args.result_dir
    pair_stats = pd.read_csv(out / "mediator_pair_stats.csv")
    task_stats = pd.read_csv(out / "mediator_task_stats.csv")
    pair_cfg = pd.read_csv(out / "mediator_pair_config.csv") if (out / "mediator_pair_config.csv").exists() else pd.DataFrame()
    evidence = load_evidence(args.h3_evidence_matrix)

    early = pair_stats[pair_stats["checkpoint_fraction"].astype(float) <= float(args.early_max_fraction)].copy()
    if early.empty:
        early = pair_stats.copy()
    pair_summary = summarize_pair_roles(early, evidence)
    contrast_summary = summarize_contrasts(pair_summary)
    task_summary = summarize_task_stats(task_stats, args.early_max_fraction)

    pair_summary.to_csv(out / "mediator_pair_role_summary.csv", index=False)
    contrast_summary.to_csv(out / "mediator_contrast_summary.csv", index=False)
    task_summary.to_csv(out / "mediator_task_summary.csv", index=False)
    report = render_report(pair_summary, contrast_summary, task_summary, args.early_max_fraction)
    (out / "mediator_analysis_report.md").write_text(report, encoding="utf-8")

    manifest = write_manifest(
        out,
        experiment="B1_mediator_diagnostics_analysis",
        backend="B1_sequence_dsl",
        code_version=args.code_version,
        run_id="b1_mediator_analysis",
        command=sys.argv,
        input_paths={"result_dir": str(args.result_dir), "h3_evidence_matrix": str(args.h3_evidence_matrix or "")},
        extra={"early_max_fraction": args.early_max_fraction, "thesis_use": args.thesis_use},
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
                "output_path": str(out),
                "status": "analyzed",
                "thesis_use": args.thesis_use,
                "created_at_utc": manifest["created_at_utc"],
            },
        )
    print("Saved mediator analysis outputs:")
    for name in ["mediator_analysis_report.md", "mediator_pair_role_summary.csv", "mediator_contrast_summary.csv", "mediator_task_summary.csv", "run_manifest.json"]:
        print(f"  {out / name}")


def load_evidence(path: Path | None) -> pd.DataFrame:
    if path is None or not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    # Normalize likely column names.
    ren = {}
    for c in df.columns:
        lc = c.lower()
        if lc in {"component", "component_id"}:
            ren[c] = "component"
        elif lc in {"composite", "composite_id"}:
            ren[c] = "composite"
        elif lc in {"verdict", "result", "pair_verdict"}:
            ren[c] = "h3_verdict"
    return df.rename(columns=ren)


def summarize_pair_roles(df: pd.DataFrame, evidence: pd.DataFrame) -> pd.DataFrame:
    group_cols = ["pair_id", "component", "composite", "source_role", "source_task", "target_task"]
    rows = []
    for keys, g in df.groupby(group_cols, dropna=False):
        d = dict(zip(group_cols, keys))
        d.update(
            {
                "n_rows": int(len(g)),
                "n_seeds": int(g["seed"].nunique()) if "seed" in g else np.nan,
                "mean_gradient_cosine": float(g["gradient_cosine"].mean()),
                "median_gradient_cosine": float(g["gradient_cosine"].median()),
                "mean_linear_cka": float(g["linear_cka"].mean()),
                "median_linear_cka": float(g["linear_cka"].median()),
                "mean_source_gradient_norm": float(g["source_gradient_norm"].mean()),
                "mean_target_gradient_norm": float(g["target_gradient_norm"].mean()),
            }
        )
        rows.append(d)
    out = pd.DataFrame(rows)
    if not evidence.empty and {"component", "composite"}.issubset(evidence.columns):
        keep = [c for c in ["component", "composite", "h3_verdict", "verdict", "interpretation", "scope"] if c in evidence.columns]
        ev = evidence[keep].drop_duplicates(["component", "composite"])
        out = out.merge(ev, on=["component", "composite"], how="left")
    return out.sort_values(["pair_id", "source_role"]).reset_index(drop=True)


def summarize_contrasts(pair_summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (pair_id, component, composite), g in pair_summary.groupby(["pair_id", "component", "composite"], dropna=False):
        by_role = {r: row for r, row in g.set_index("source_role").to_dict(orient="index").items()}
        exact = by_role.get("exact_component")
        if exact is None:
            continue
        for role in ["same_operation_control", "different_operation_control", "fake_component_control", "surface_control"]:
            ctrl = by_role.get(role)
            if ctrl is None:
                continue
            rows.append(
                {
                    "pair_id": pair_id,
                    "component": component,
                    "composite": composite,
                    "contrast": f"exact_minus_{role}",
                    "delta_gradient_cosine": float(exact["mean_gradient_cosine"] - ctrl["mean_gradient_cosine"]),
                    "delta_linear_cka": float(exact["mean_linear_cka"] - ctrl["mean_linear_cka"]),
                    "exact_gradient_cosine": float(exact["mean_gradient_cosine"]),
                    "control_gradient_cosine": float(ctrl["mean_gradient_cosine"]),
                    "exact_linear_cka": float(exact["mean_linear_cka"]),
                    "control_linear_cka": float(ctrl["mean_linear_cka"]),
                    "h3_verdict": exact.get("h3_verdict", exact.get("verdict", "")),
                }
            )
    return pd.DataFrame(rows).sort_values(["pair_id", "contrast"]).reset_index(drop=True)


def summarize_task_stats(df: pd.DataFrame, early_max_fraction: float) -> pd.DataFrame:
    early = df[df["checkpoint_fraction"].astype(float) <= float(early_max_fraction)].copy()
    if early.empty:
        early = df.copy()
    rows = []
    for task, g in early.groupby("task_name", dropna=False):
        rows.append(
            {
                "task_name": task,
                "n_rows": int(len(g)),
                "mean_gradient_norm": float(g["gradient_norm"].mean()),
                "mean_gradient_snr": float(g["gradient_snr"].replace([np.inf, -np.inf], np.nan).mean()),
                "mean_within_gradient_alignment": float(g["within_gradient_alignment"].mean()),
            }
        )
    return pd.DataFrame(rows).sort_values("task_name").reset_index(drop=True)


def render_report(pair_summary: pd.DataFrame, contrasts: pd.DataFrame, task_summary: pd.DataFrame, early_max_fraction: float) -> str:
    lines = [
        "# B1 mediator diagnostics analysis",
        "",
        "This analysis tests whether H3-positive component-composite pairs show stronger leading-indicator gradient/representation coupling than controls.",
        "It is mechanistic corroboration, not a standalone causal test.",
        "",
        f"Early window: checkpoint_fraction <= `{early_max_fraction}`",
        "",
        "## Pair-role summary",
    ]
    if pair_summary.empty:
        lines.append("No pair-role summaries were available.")
    else:
        for _, r in pair_summary.iterrows():
            lines.append(
                f"- `{r['source_role']}` `{r['source_task']}` → `{r['target_task']}`: "
                f"grad_cos={float(r['mean_gradient_cosine']):.3f}, CKA={float(r['mean_linear_cka']):.3f}"
            )
    lines.extend(["", "## Exact-vs-control contrasts"])
    if contrasts.empty:
        lines.append("No contrasts were available.")
    else:
        for _, r in contrasts.iterrows():
            lines.append(
                f"- `{r['component']}` → `{r['composite']}` / `{r['contrast']}`: "
                f"Δgrad_cos={float(r['delta_gradient_cosine']):.3f}, ΔCKA={float(r['delta_linear_cka']):.3f}"
            )
    lines.extend(
        [
            "",
            "## Interpretation rule",
            "Mediator support for exact-component dependency requires the exact component to show higher early gradient cosine and/or representation CKA with the composite than same-operation and different-operation controls. If same-operation controls match the exact component, interpret the pattern as operation-family transfer rather than exact-component reuse.",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    main()
