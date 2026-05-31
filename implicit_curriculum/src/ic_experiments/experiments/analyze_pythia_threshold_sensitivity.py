from __future__ import annotations

import argparse
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


def _first_acq(g: pd.DataFrame, metric: str, threshold: float, direction: str) -> dict[str, Any]:
    g = g.sort_values("checkpoint_index")
    vals = g[metric]
    hit = g[vals >= threshold] if direction == "ge" else g[vals <= threshold]
    if len(hit):
        row = hit.iloc[0]
        return {"acquired": 1, "acquired_at_index": int(row["checkpoint_index"]), "acquired_at_data_seen_proxy": float(row["data_seen_proxy"])}
    last = g.iloc[-1]
    return {"acquired": 0, "acquired_at_index": float("nan"), "acquired_at_data_seen_proxy": float(last["data_seen_proxy"])}


def _build_acq(curves: pd.DataFrame, slices: pd.DataFrame, metric: str, threshold: float, direction: str) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for (model_name, slice_id), g in curves.groupby(["model_name", "slice_id"]):
        g = g.sort_values("checkpoint_index")
        rec = {"model_name": model_name, "slice_id": slice_id, "metric": metric, "threshold": threshold}
        rec.update(_first_acq(g, metric, threshold, direction))
        rec["initial_metric"] = float(g.iloc[0][metric])
        rec["final_metric"] = float(g.iloc[-1][metric])
        rec["delta_metric"] = rec["final_metric"] - rec["initial_metric"]
        rec["auc_metric"] = float(g[metric].mean())
        rows.append(rec)
    return pd.DataFrame(rows).merge(slices, on="slice_id", how="left")


def _h1(acq: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (model_name, metric, threshold), df in acq.groupby(["model_name", "metric", "threshold"]):
        groups = [
            ("all", df),
            ("atomic", df[df["kind"] == "atomic"]),
            ("composite", df[df["kind"] == "composite"]),
            ("true_atomic_composite", df[df["kind"].isin(["atomic", "composite"])]),
        ]
        for group, sub in groups:
            acquired = sub[sub["acquired"] == 1]
            rows.append({
                "model_name": model_name,
                "metric": metric,
                "threshold": threshold,
                "group": group,
                "n": int(len(sub)),
                "acq_rate": float(sub["acquired"].mean()) if len(sub) else float("nan"),
                "mean_final": float(sub["final_metric"].mean()) if len(sub) else float("nan"),
                "mean_delta": float(sub["delta_metric"].mean()) if len(sub) else float("nan"),
                "rho_frequency_time": _spearman(acquired["frequency_proxy"], acquired["acquired_at_data_seen_proxy"]),
                "rho_learnability_time": _spearman(acquired["reference_learnability"], acquired["acquired_at_data_seen_proxy"]),
                "rho_utility_time": _spearman(acquired["formal_utility"], acquired["acquired_at_data_seen_proxy"]),
                "rho_frequency_final": _spearman(sub["frequency_proxy"], sub["final_metric"]),
                "rho_learnability_final": _spearman(sub["reference_learnability"], sub["final_metric"]),
            })
    return pd.DataFrame(rows)


def _h2(acq: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (model_name, metric, threshold), df in acq.groupby(["model_name", "metric", "threshold"]):
        atom = df[(df["kind"] == "atomic") & (df["acquired"] == 1)].copy()
        comp = df[df["kind"] == "composite"].copy()
        if len(atom) >= 3:
            X = atom[["frequency_proxy", "reference_learnability", "formal_utility"]].astype(float).to_numpy()
            y = np.log1p(atom["acquired_at_data_seen_proxy"].astype(float).to_numpy())
            X1 = np.column_stack([np.ones(len(X)), X])
            coef, *_ = np.linalg.lstsq(X1, y, rcond=None)
            Xc = comp[["frequency_proxy", "reference_learnability", "formal_utility"]].astype(float).to_numpy()
            pred = np.column_stack([np.ones(len(Xc)), Xc]) @ coef if len(comp) else []
            obs = np.log1p(comp["acquired_at_data_seen_proxy"].astype(float).to_numpy()) if len(comp) else []
            for i, (_, row) in enumerate(comp.iterrows()):
                rows.append({
                    "model_name": model_name,
                    "metric": metric,
                    "threshold": threshold,
                    "slice_id": row["slice_id"],
                    "component_ids": row.get("component_ids", ""),
                    "acquired": int(row["acquired"]),
                    "final_metric": float(row["final_metric"]),
                    "observed_log_time": float(obs[i]),
                    "predicted_log_time": float(pred[i]),
                    "residual_log_time": float(obs[i] - pred[i]),
                    "n_atomic_fit": int(len(atom)),
                })
        else:
            for _, row in comp.iterrows():
                rows.append({
                    "model_name": model_name,
                    "metric": metric,
                    "threshold": threshold,
                    "slice_id": row["slice_id"],
                    "component_ids": row.get("component_ids", ""),
                    "acquired": int(row["acquired"]),
                    "final_metric": float(row["final_metric"]),
                    "observed_log_time": float("nan"),
                    "predicted_log_time": float("nan"),
                    "residual_log_time": float("nan"),
                    "n_atomic_fit": int(len(atom)),
                })
    return pd.DataFrame(rows)


def main() -> None:
    p = argparse.ArgumentParser(description="Threshold-sensitivity and calibration analysis for Pythia observational pilot outputs.")
    p.add_argument("--result-dir", required=True)
    p.add_argument("--metric", default="accuracy")
    p.add_argument("--thresholds", nargs="+", type=float, default=[0.2, 0.3, 0.4, 0.5])
    p.add_argument("--direction", choices=["ge", "le"], default="ge")
    p.add_argument("--code-version", default="v2.5")
    p.add_argument("--archive-root", default="results/archive")
    p.add_argument("--thesis-use", default="diagnostic")
    args = p.parse_args()

    result_dir = Path(args.result_dir)
    curves = pd.read_csv(result_dir / "pythia_eval_curves.csv")
    slices = pd.read_csv(result_dir / "pythia_slice_table.csv")
    if args.metric not in curves.columns:
        raise ValueError(f"Metric {args.metric!r} not found in pythia_eval_curves.csv columns {list(curves.columns)}")

    acq_parts = [_build_acq(curves, slices, args.metric, th, args.direction) for th in args.thresholds]
    acq = pd.concat(acq_parts, ignore_index=True)
    h1 = _h1(acq)
    h2 = _h2(acq)

    # Slice calibration ignores threshold and summarizes continuous curves.
    cal_rows = []
    for (model_name, slice_id), g in curves.groupby(["model_name", "slice_id"]):
        g = g.sort_values("checkpoint_index")
        rec = {"model_name": model_name, "slice_id": slice_id}
        rec["initial_metric"] = float(g.iloc[0][args.metric])
        rec["final_metric"] = float(g.iloc[-1][args.metric])
        rec["delta_metric"] = rec["final_metric"] - rec["initial_metric"]
        rec["auc_metric"] = float(g[args.metric].mean())
        rec["max_metric"] = float(g[args.metric].max())
        rec["n_checkpoints"] = int(len(g))
        cal_rows.append(rec)
    cal = pd.DataFrame(cal_rows).merge(slices, on="slice_id", how="left")
    # A useful slice is neither random-flat nor saturated, with some checkpoint movement.
    cal["calibration_status"] = np.where(
        (cal["max_metric"] >= 0.3) & (cal["final_metric"] <= 0.95),
        "usable_or_near_usable",
        "too_hard_or_uninformative",
    )

    acq.to_csv(result_dir / "pythia_threshold_acquisition_times.csv", index=False)
    h1.to_csv(result_dir / "pythia_threshold_h1_summary.csv", index=False)
    h2.to_csv(result_dir / "pythia_threshold_h2_residuals.csv", index=False)
    cal.to_csv(result_dir / "pythia_slice_calibration_summary.csv", index=False)

    lines = [
        "# Pythia observational threshold-sensitivity analysis",
        "",
        "This analysis is observational. Thresholds diagnose whether the pilot is in a measurable regime; they do not create causal evidence.",
        "",
        f"- metric: `{args.metric}`",
        f"- thresholds: `{', '.join(str(t) for t in args.thresholds)}`",
        f"- slices: `{cal['slice_id'].nunique()}`",
        f"- models: `{cal['model_name'].nunique()}`",
        "",
        "## Slice calibration",
    ]
    for _, r in cal.sort_values("final_metric", ascending=False).iterrows():
        lines.append(f"- `{r['slice_id']}` ({r['kind']}): final={r['final_metric']:.3f}, max={r['max_metric']:.3f}, AUC={r['auc_metric']:.3f}, status={r['calibration_status']}")
    lines += ["", "## Threshold acquisition summary"]
    for _, r in h1[h1["group"] == "true_atomic_composite"].iterrows():
        lines.append(f"- `{r['model_name']}` threshold `{r['threshold']}`: acq={r['acq_rate']:.3f}, freq-rho={r['rho_frequency_time']:.3f}, learn-rho={r['rho_learnability_time']:.3f}")
    lines += ["", "## H2 residual availability"]
    for th, sub in h2.groupby("threshold"):
        valid = sub.dropna(subset=["residual_log_time"])
        lines.append(f"- threshold `{th}`: composite rows={len(sub)}, valid residual rows={len(valid)}")
        if len(valid):
            top = valid.sort_values("residual_log_time", ascending=False).head(3)
            for _, r in top.iterrows():
                lines.append(f"  - `{r['slice_id']}` residual={r['residual_log_time']:.3f}, final={r['final_metric']:.3f}")
    lines += ["", "## Claim boundary", "Use this as calibration for a Pythia-style bridge. If acquisition appears only at low thresholds or only in final/AUC, describe it as subthreshold observational signal, not acquisition evidence and never causal evidence."]
    (result_dir / "pythia_threshold_sensitivity_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    manifest = write_manifest(
        result_dir,
        experiment="Pythia_observational_threshold_sensitivity",
        backend="Pythia_observational",
        code_version=args.code_version,
        input_paths={"result_dir": str(result_dir)},
        extra={"metric": args.metric, "thresholds": args.thresholds, "thesis_use": args.thesis_use},
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
    print(f"Wrote Pythia threshold-sensitivity outputs to {result_dir}")


if __name__ == "__main__":
    main()
