from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import pandas as pd

from ic_experiments.run_management import append_registry, write_manifest

PRIMARY_METRICS = ["accuracy", "mean_correct_margin", "mean_correct_mrr", "mean_logprob_correct", "mean_logprob_margin"]


def _safe_mean(s: pd.Series) -> float:
    return float(pd.to_numeric(s, errors="coerce").mean()) if len(s) else float("nan")


def main() -> None:
    p = argparse.ArgumentParser(description="Assess whether a Pythia observational run is H2-ready for primitive-to-composite residual analysis.")
    p.add_argument("--result-dir", required=True)
    p.add_argument("--slice-table", default=None, help="Optional slice table path. Defaults to result-dir/pythia_slice_table.csv")
    p.add_argument("--metrics", nargs="*", default=None)
    p.add_argument("--min-atomic", type=int, default=8)
    p.add_argument("--min-composite", type=int, default=4)
    p.add_argument("--min-moving-atomic", type=int, default=4)
    p.add_argument("--min-moving-composite", type=int, default=2)
    p.add_argument("--movement-threshold", type=float, default=0.02)
    p.add_argument("--code-version", default="v2.7")
    p.add_argument("--archive-root", default="results/archive")
    p.add_argument("--thesis-use", default="diagnostic")
    args = p.parse_args()

    result_dir = Path(args.result_dir)
    curves = pd.read_csv(result_dir / "pythia_eval_curves.csv")
    slice_path = Path(args.slice_table) if args.slice_table else result_dir / "pythia_slice_table.csv"
    slices = pd.read_csv(slice_path)
    metrics = [m for m in (args.metrics or PRIMARY_METRICS) if m in curves.columns]
    if not metrics:
        raise ValueError("No requested metrics found in pythia_eval_curves.csv")

    rows: list[dict[str, Any]] = []
    for (model_name, slice_id), g in curves.groupby(["model_name", "slice_id"]):
        g = g.sort_values("checkpoint_index")
        meta = slices[slices["slice_id"] == slice_id]
        meta_row = meta.iloc[0].to_dict() if len(meta) else {}
        for metric in metrics:
            vals = pd.to_numeric(g[metric], errors="coerce")
            rows.append({
                "model_name": model_name,
                "slice_id": slice_id,
                "metric": metric,
                "kind": meta_row.get("kind", ""),
                "family": meta_row.get("family", ""),
                "operation_type": meta_row.get("operation_type", ""),
                "component_ids": meta_row.get("component_ids", ""),
                "initial": float(vals.iloc[0]),
                "final": float(vals.iloc[-1]),
                "delta": float(vals.iloc[-1] - vals.iloc[0]),
                "auc": float(vals.mean()),
                "max": float(vals.max()),
                "min": float(vals.min()),
                "abs_delta": float(abs(vals.iloc[-1] - vals.iloc[0])),
                "moving": bool(abs(vals.iloc[-1] - vals.iloc[0]) >= args.movement_threshold or abs(vals.max() - vals.min()) >= 2 * args.movement_threshold),
            })
    table = pd.DataFrame(rows)
    table.to_csv(result_dir / "pythia_h2_readiness_slice_metric_table.csv", index=False)

    metric_rows: list[dict[str, Any]] = []
    for (model_name, metric), df in table.groupby(["model_name", "metric"]):
        atom = df[df["kind"] == "atomic"]
        comp = df[df["kind"] == "composite"]
        moving_atom = atom[atom["moving"]]
        moving_comp = comp[comp["moving"]]
        h2_ready = len(atom) >= args.min_atomic and len(comp) >= args.min_composite and len(moving_atom) >= args.min_moving_atomic and len(moving_comp) >= args.min_moving_composite
        metric_rows.append({
            "model_name": model_name,
            "metric": metric,
            "n_atomic": int(len(atom)),
            "n_composite": int(len(comp)),
            "n_moving_atomic": int(len(moving_atom)),
            "n_moving_composite": int(len(moving_comp)),
            "mean_atomic_delta": _safe_mean(atom["delta"]),
            "mean_composite_delta": _safe_mean(comp["delta"]),
            "mean_atomic_final": _safe_mean(atom["final"]),
            "mean_composite_final": _safe_mean(comp["final"]),
            "h2_ready": bool(h2_ready),
        })
    metric_summary = pd.DataFrame(metric_rows)
    metric_summary.to_csv(result_dir / "pythia_h2_readiness_metric_summary.csv", index=False)

    lines = [
        "# Pythia H2-readiness analysis",
        "",
        "This report checks whether an observational Pythia run has enough primitive and composite slice movement for H2-style residual analysis.",
        "",
        f"- metrics analyzed: `{', '.join(metrics)}`",
        f"- movement threshold: `{args.movement_threshold}`",
        f"- minimum atomic slices: `{args.min_atomic}`",
        f"- minimum composite slices: `{args.min_composite}`",
        "",
        "## Metric readiness",
    ]
    for _, r in metric_summary.iterrows():
        lines.append(f"- `{r['metric']}`: h2_ready={bool(r['h2_ready'])}, atomic={int(r['n_atomic'])}, composite={int(r['n_composite'])}, moving_atomic={int(r['n_moving_atomic'])}, moving_composite={int(r['n_moving_composite'])}, mean_atomic_delta={r['mean_atomic_delta']:.3f}, mean_composite_delta={r['mean_composite_delta']:.3f}")
    ready_metrics = metric_summary[metric_summary["h2_ready"] == True]["metric"].tolist()
    lines += [
        "",
        "## Decision",
        f"- H2-ready metrics: `{', '.join(ready_metrics) if ready_metrics else 'none'}`",
        "",
        "If no metric is H2-ready, use the run as calibration only. If one or more continuous metrics are H2-ready, analyze primitive-to-composite residuals using `analyze_pythia_continuous_scores` with that metric and keep the claim observational.",
    ]
    (result_dir / "pythia_h2_readiness_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    manifest = write_manifest(
        result_dir,
        experiment="Pythia_H2_readiness_analysis",
        backend="Pythia_observational",
        code_version=args.code_version,
        input_paths={"result_dir": str(result_dir), "slice_table": str(slice_path)},
        extra={"metrics": metrics, "movement_threshold": args.movement_threshold, "thesis_use": args.thesis_use},
    )
    append_registry(Path(args.archive_root) / "results_registry.csv", {
        "run_id": manifest["run_id"],
        "code_version": args.code_version,
        "experiment": manifest["experiment"],
        "backend": manifest["backend"],
        "output_path": str(result_dir),
        "status": "analyzed",
        "thesis_use": args.thesis_use,
        "created_at_utc": manifest["created_at_utc"],
    })
    print(f"Wrote Pythia H2-readiness outputs to {result_dir}")


if __name__ == "__main__":
    main()
