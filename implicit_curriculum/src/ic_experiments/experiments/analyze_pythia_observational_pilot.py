from __future__ import annotations

import argparse
import csv
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from ic_experiments.run_management import append_registry, write_manifest


def _spearman(x: pd.Series, y: pd.Series) -> float:
    df = pd.DataFrame({"x": x, "y": y}).dropna()
    if len(df) < 3 or df["x"].nunique() < 2 or df["y"].nunique() < 2:
        return float("nan")
    return float(df["x"].rank().corr(df["y"].rank()))


def _first_acq(g: pd.DataFrame, metric: str, threshold: float) -> dict[str, Any]:
    g = g.sort_values("checkpoint_index")
    hit = g[g[metric] >= threshold]
    if len(hit):
        row = hit.iloc[0]
        return {"acquired": 1, "acquired_at_index": int(row["checkpoint_index"]), "acquired_at_data_seen_proxy": float(row["data_seen_proxy"])}
    last = g.iloc[-1]
    return {"acquired": 0, "acquired_at_index": float("nan"), "acquired_at_data_seen_proxy": float(last["data_seen_proxy"])}


def main() -> None:
    p = argparse.ArgumentParser(description="Analyze H1/H2-like signatures in a Pythia observational pilot.")
    p.add_argument("--result-dir", required=True)
    p.add_argument("--metric", default="accuracy")
    p.add_argument("--threshold", type=float, default=0.5)
    p.add_argument("--code-version", default="v2.4")
    p.add_argument("--archive-root", default="results/archive")
    p.add_argument("--thesis-use", default="diagnostic")
    args = p.parse_args()

    result_dir = Path(args.result_dir)
    curves = pd.read_csv(result_dir / "pythia_eval_curves.csv")
    slices = pd.read_csv(result_dir / "pythia_slice_table.csv")
    out = result_dir

    acq_rows = []
    for (model_name, slice_id), g in curves.groupby(["model_name", "slice_id"]):
        rec = {"model_name": model_name, "slice_id": slice_id}
        rec.update(_first_acq(g, args.metric, args.threshold))
        rec["final_metric"] = float(g.sort_values("checkpoint_index").iloc[-1][args.metric])
        # AUC normalized by number of checkpoints; simple diagnostic.
        rec["auc_metric"] = float(g.sort_values("checkpoint_index")[args.metric].mean())
        acq_rows.append(rec)
    acq = pd.DataFrame(acq_rows).merge(slices, on="slice_id", how="left")
    acq.to_csv(out / "pythia_acquisition_times.csv", index=False)

    # H1-like ordering: among acquired slices, lower acquisition time is earlier.
    h1_rows = []
    for model_name, df in acq.groupby("model_name"):
        for group_name, sub in [("all", df), ("atomic", df[df["kind"] == "atomic"]), ("true_atomic_composite", df[df["kind"].isin(["atomic", "composite"])])]:
            acquired = sub[sub["acquired"] == 1]
            h1_rows.append({
                "model_name": model_name,
                "group": group_name,
                "n": int(len(sub)),
                "acq_rate": float(sub["acquired"].mean()) if len(sub) else float("nan"),
                "rho_frequency_time": _spearman(acquired["frequency_proxy"], acquired["acquired_at_data_seen_proxy"]),
                "rho_learnability_time": _spearman(acquired["reference_learnability"], acquired["acquired_at_data_seen_proxy"]),
                "rho_utility_time": _spearman(acquired["formal_utility"], acquired["acquired_at_data_seen_proxy"]),
            })
    h1 = pd.DataFrame(h1_rows)
    h1.to_csv(out / "pythia_h1_ordering_summary.csv", index=False)

    # H2-like residuals: fit a tiny linear model on atomics and predict composites per model.
    res_rows = []
    selected_rows = []
    for model_name, df in acq.groupby("model_name"):
        atom = df[(df["kind"] == "atomic") & (df["acquired"] == 1)].copy()
        comp = df[df["kind"] == "composite"].copy()
        if len(atom) >= 3 and len(comp) > 0:
            X = atom[["frequency_proxy", "reference_learnability", "formal_utility"]].astype(float).to_numpy()
            y = np.log1p(atom["acquired_at_data_seen_proxy"].astype(float).to_numpy())
            X1 = np.column_stack([np.ones(len(X)), X])
            coef, *_ = np.linalg.lstsq(X1, y, rcond=None)
            Xc = comp[["frequency_proxy", "reference_learnability", "formal_utility"]].astype(float).to_numpy()
            Xc1 = np.column_stack([np.ones(len(Xc)), Xc])
            pred = Xc1 @ coef
            obs = np.log1p(comp["acquired_at_data_seen_proxy"].astype(float).to_numpy())
            for i, (_, row) in enumerate(comp.iterrows()):
                residual = float(obs[i] - pred[i])
                res_rows.append({
                    "model_name": model_name,
                    "slice_id": row["slice_id"],
                    "component_ids": row.get("component_ids", ""),
                    "observed_log_time": float(obs[i]),
                    "predicted_log_time": float(pred[i]),
                    "residual_log_time": residual,
                    "acquired": int(row["acquired"]),
                    "final_metric": float(row["final_metric"]),
                })
        else:
            for _, row in comp.iterrows():
                res_rows.append({
                    "model_name": model_name,
                    "slice_id": row["slice_id"],
                    "component_ids": row.get("component_ids", ""),
                    "observed_log_time": float("nan"),
                    "predicted_log_time": float("nan"),
                    "residual_log_time": float("nan"),
                    "acquired": int(row["acquired"]),
                    "final_metric": float(row["final_metric"]),
                })
    residuals = pd.DataFrame(res_rows)
    residuals.to_csv(out / "pythia_h2_composite_residuals.csv", index=False)

    report_lines = [
        "# Pythia observational pilot analysis",
        "",
        "This analysis is observational. It can report acquisition-order and residual signatures, but it cannot establish causal dependency because pretraining was not intervened on.",
        "",
        f"- metric: `{args.metric}`",
        f"- threshold: `{args.threshold}`",
        f"- slices: `{acq['slice_id'].nunique()}`",
        f"- models: `{acq['model_name'].nunique()}`",
        "",
        "## H1 summary",
    ]
    for _, r in h1.iterrows():
        if r["group"] == "true_atomic_composite":
            report_lines.append(f"- `{r['model_name']}` / true slices: acq={r['acq_rate']:.3f}, freq-rho={r['rho_frequency_time']:.3f}, learn-rho={r['rho_learnability_time']:.3f}")
    report_lines.extend(["", "## H2 residual summary"])
    if len(residuals):
        valid = residuals.dropna(subset=["residual_log_time"])
        report_lines.append(f"- composite residual rows: `{len(residuals)}`")
        if len(valid):
            report_lines.append(f"- mean residual log-time: `{valid['residual_log_time'].mean():.3f}`")
            top = valid.sort_values("residual_log_time", ascending=False).head(5)
            for _, r in top.iterrows():
                report_lines.append(f"- top residual: `{r['slice_id']}` residual={r['residual_log_time']:.3f}, final={r['final_metric']:.3f}")
    report_lines.extend(["", "## Claim boundary", "Use this pilot only as a Pythia-style observational bridge. It can motivate slice selection and compare signatures with B1, but it is not H3 evidence."])
    (out / "pythia_observational_analysis_report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    manifest = write_manifest(
        out,
        experiment="Pythia_observational_pilot_analysis",
        backend="Pythia_observational",
        code_version=args.code_version,
        input_paths={"result_dir": str(result_dir)},
        extra={"metric": args.metric, "threshold": args.threshold, "thesis_use": args.thesis_use},
    )
    append_registry(Path(args.archive_root) / "results_registry.csv", {
        "run_id": manifest["run_id"],
        "code_version": args.code_version,
        "experiment": manifest["experiment"],
        "backend": manifest["backend"],
        "output_path": str(out),
        "status": "analyzed",
        "thesis_use": args.thesis_use,
        "created_at_utc": manifest["created_at_utc"],
    })
    print(f"Wrote Pythia observational analysis to {out}")


if __name__ == "__main__":
    main()
