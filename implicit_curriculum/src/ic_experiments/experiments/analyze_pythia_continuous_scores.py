from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from ic_experiments.run_management import append_registry, write_manifest


FEATURES = ["frequency_proxy", "reference_learnability", "formal_utility", "composition_depth", "answer_entropy_proxy"]


def _spearman(x: pd.Series, y: pd.Series) -> float:
    df = pd.DataFrame({"x": x, "y": y}).dropna()
    if len(df) < 3 or df["x"].nunique() < 2 or df["y"].nunique() < 2:
        return float("nan")
    return float(df["x"].rank().corr(df["y"].rank()))


def _available_metrics(curves: pd.DataFrame, requested: list[str] | None) -> list[str]:
    default = [
        "accuracy",
        "mean_logprob_correct",
        "mean_correct_margin",
        "mean_correct_mrr",
        "mean_logprob_margin",
    ]
    metrics = requested or default
    return [m for m in metrics if m in curves.columns]


def _summarize_metric(curves: pd.DataFrame, slices: pd.DataFrame, metric: str) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for (model_name, slice_id), g in curves.groupby(["model_name", "slice_id"]):
        g = g.sort_values("checkpoint_index")
        vals = g[metric].astype(float)
        rec = {
            "model_name": model_name,
            "slice_id": slice_id,
            "metric": metric,
            "initial_metric": float(vals.iloc[0]),
            "final_metric": float(vals.iloc[-1]),
            "delta_metric": float(vals.iloc[-1] - vals.iloc[0]),
            "auc_metric": float(vals.mean()),
            "max_metric": float(vals.max()),
            "min_metric": float(vals.min()),
            "n_checkpoints": int(len(g)),
        }
        rows.append(rec)
    out = pd.DataFrame(rows).merge(slices, on="slice_id", how="left")
    # A heuristic, not evidence: does this metric show any usable movement/range?
    def status(r: pd.Series) -> str:
        if r["metric"] == "accuracy":
            if r["max_metric"] >= 0.3 and r["final_metric"] <= 0.95:
                return "usable_or_near_usable"
            return "weak_or_uninformative"
        if r["metric"] == "mean_correct_mrr":
            if abs(r["delta_metric"]) >= 0.02 or r["max_metric"] >= 0.35:
                return "usable_or_near_usable"
            return "weak_or_uninformative"
        if "logprob" in r["metric"] or "margin" in r["metric"]:
            if abs(r["delta_metric"]) >= 0.05 or abs(r["max_metric"] - r["min_metric"]) >= 0.1:
                return "usable_or_near_usable"
            return "weak_or_uninformative"
        return "diagnostic"
    out["continuous_status"] = out.apply(status, axis=1)
    return out


def _h1_continuous(summary: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for (model_name, metric), df in summary.groupby(["model_name", "metric"]):
        groups = [
            ("all", df),
            ("atomic", df[df["kind"] == "atomic"]),
            ("composite", df[df["kind"] == "composite"]),
            ("true_atomic_composite", df[df["kind"].isin(["atomic", "composite"])]),
        ]
        for group, sub in groups:
            rec: dict[str, Any] = {
                "model_name": model_name,
                "metric": metric,
                "group": group,
                "n": int(len(sub)),
                "mean_final": float(sub["final_metric"].mean()) if len(sub) else float("nan"),
                "mean_delta": float(sub["delta_metric"].mean()) if len(sub) else float("nan"),
                "mean_auc": float(sub["auc_metric"].mean()) if len(sub) else float("nan"),
            }
            for feat in FEATURES:
                if feat in sub.columns:
                    rec[f"rho_{feat}_final"] = _spearman(sub[feat], sub["final_metric"])
                    rec[f"rho_{feat}_delta"] = _spearman(sub[feat], sub["delta_metric"])
                    rec[f"rho_{feat}_auc"] = _spearman(sub[feat], sub["auc_metric"])
            rows.append(rec)
    return pd.DataFrame(rows)


def _fit_predict(train: pd.DataFrame, test: pd.DataFrame, target: str) -> tuple[np.ndarray | None, int]:
    usable_features = [f for f in FEATURES if f in train.columns and pd.to_numeric(train[f], errors="coerce").notna().any()]
    if len(train) < max(3, len(usable_features) + 1) or len(test) == 0 or not usable_features:
        return None, len(train)
    tr = train.copy()
    te = test.copy()
    for f in usable_features:
        tr[f] = pd.to_numeric(tr[f], errors="coerce")
        te[f] = pd.to_numeric(te[f], errors="coerce")
    tr[target] = pd.to_numeric(tr[target], errors="coerce")
    tr = tr.dropna(subset=usable_features + [target])
    te = te.dropna(subset=usable_features)
    if len(tr) < max(3, len(usable_features) + 1) or len(te) == 0:
        return None, len(tr)
    X = tr[usable_features].astype(float).to_numpy()
    y = tr[target].astype(float).to_numpy()
    X1 = np.column_stack([np.ones(len(X)), X])
    coef, *_ = np.linalg.lstsq(X1, y, rcond=None)
    Xc = te[usable_features].astype(float).to_numpy()
    pred = np.column_stack([np.ones(len(Xc)), Xc]) @ coef
    return pred, len(tr)


def _h2_continuous(summary: pd.DataFrame, target: str) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for (model_name, metric), df in summary.groupby(["model_name", "metric"]):
        atom = df[df["kind"] == "atomic"].copy()
        comp = df[df["kind"] == "composite"].copy()
        pred, n_fit = _fit_predict(atom, comp, target)
        if pred is None:
            for _, r in comp.iterrows():
                rows.append({
                    "model_name": model_name,
                    "metric": metric,
                    "target_summary": target,
                    "slice_id": r["slice_id"],
                    "component_ids": r.get("component_ids", ""),
                    "observed": float(r[target]),
                    "predicted": float("nan"),
                    "residual": float("nan"),
                    "n_atomic_fit": int(n_fit),
                })
        else:
            comp2 = comp.dropna(subset=[f for f in FEATURES if f in comp.columns]).copy()
            # If dropna removed rows differently, recompute an aligned prediction fallback.
            if len(comp2) != len(pred):
                comp2 = comp.copy()
            for i, (_, r) in enumerate(comp.iterrows()):
                p = float(pred[i]) if i < len(pred) else float("nan")
                rows.append({
                    "model_name": model_name,
                    "metric": metric,
                    "target_summary": target,
                    "slice_id": r["slice_id"],
                    "component_ids": r.get("component_ids", ""),
                    "observed": float(r[target]),
                    "predicted": p,
                    "residual": float(r[target] - p) if np.isfinite(p) else float("nan"),
                    "n_atomic_fit": int(n_fit),
                })
    return pd.DataFrame(rows)


def _component_coupling(summary: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    index = {(r.model_name, r.metric, r.slice_id): r for r in summary.itertuples(index=False)}
    comps = summary[summary["kind"] == "composite"]
    for r in comps.itertuples(index=False):
        comp_ids = str(getattr(r, "component_ids", "") or "")
        ids = [x.strip() for x in comp_ids.split(";") if x.strip()]
        comp_vals = []
        for cid in ids:
            cr = index.get((r.model_name, r.metric, cid))
            if cr is not None:
                comp_vals.append(cr)
        if not comp_vals:
            continue
        rows.append({
            "model_name": r.model_name,
            "metric": r.metric,
            "composite_slice_id": r.slice_id,
            "component_ids": comp_ids,
            "n_components_found": len(comp_vals),
            "composite_final": float(r.final_metric),
            "component_mean_final": float(np.mean([c.final_metric for c in comp_vals])),
            "composite_minus_component_final": float(r.final_metric - np.mean([c.final_metric for c in comp_vals])),
            "composite_delta": float(r.delta_metric),
            "component_mean_delta": float(np.mean([c.delta_metric for c in comp_vals])),
            "composite_minus_component_delta": float(r.delta_metric - np.mean([c.delta_metric for c in comp_vals])),
        })
    return pd.DataFrame(rows)


def main() -> None:
    p = argparse.ArgumentParser(description="Continuous-score analysis for Pythia-style observational pilots.")
    p.add_argument("--result-dir", required=True)
    p.add_argument("--metrics", nargs="*", default=None, help="Optional metrics to analyze. Defaults to all available continuous metrics.")
    p.add_argument("--h2-target", choices=["final_metric", "delta_metric", "auc_metric", "max_metric"], default="final_metric")
    p.add_argument("--code-version", default="v2.6")
    p.add_argument("--archive-root", default="results/archive")
    p.add_argument("--thesis-use", default="diagnostic")
    args = p.parse_args()

    result_dir = Path(args.result_dir)
    curves = pd.read_csv(result_dir / "pythia_eval_curves.csv")
    slices = pd.read_csv(result_dir / "pythia_slice_table.csv")
    metrics = _available_metrics(curves, args.metrics)
    if not metrics:
        raise ValueError("No requested continuous metrics found in pythia_eval_curves.csv")

    summaries = [_summarize_metric(curves, slices, m) for m in metrics]
    summary = pd.concat(summaries, ignore_index=True)
    h1 = _h1_continuous(summary)
    h2 = _h2_continuous(summary, args.h2_target)
    coupling = _component_coupling(summary)

    summary.to_csv(result_dir / "pythia_continuous_slice_summary.csv", index=False)
    h1.to_csv(result_dir / "pythia_continuous_h1_summary.csv", index=False)
    h2.to_csv(result_dir / "pythia_continuous_h2_residuals.csv", index=False)
    coupling.to_csv(result_dir / "pythia_continuous_component_coupling.csv", index=False)

    lines = [
        "# Pythia observational continuous-score analysis",
        "",
        "This analysis is observational. Continuous scores can reveal subthreshold movement, but they do not establish causal dependency.",
        "",
        f"- metrics analyzed: `{', '.join(metrics)}`",
        f"- H2 target summary: `{args.h2_target}`",
        f"- slices: `{summary['slice_id'].nunique()}`",
        f"- models: `{summary['model_name'].nunique()}`",
        "",
        "## Best final slices by metric",
    ]
    for metric, sub in summary.groupby("metric"):
        lines.append(f"### `{metric}`")
        top = sub.sort_values("final_metric", ascending=False).head(8)
        for _, r in top.iterrows():
            lines.append(f"- `{r['slice_id']}` ({r['kind']}): final={r['final_metric']:.3f}, delta={r['delta_metric']:.3f}, AUC={r['auc_metric']:.3f}, status={r['continuous_status']}")
    lines += ["", "## H1-like continuous signatures"]
    true = h1[h1["group"] == "true_atomic_composite"]
    for _, r in true.iterrows():
        freq_final = r.get("rho_frequency_proxy_final", float("nan"))
        learn_final = r.get("rho_reference_learnability_final", float("nan"))
        freq_delta = r.get("rho_frequency_proxy_delta", float("nan"))
        learn_delta = r.get("rho_reference_learnability_delta", float("nan"))
        lines.append(f"- `{r['model_name']}` / `{r['metric']}`: mean_final={r['mean_final']:.3f}, mean_delta={r['mean_delta']:.3f}, rho(freq, final)={freq_final:.3f}, rho(learn, final)={learn_final:.3f}, rho(freq, delta)={freq_delta:.3f}, rho(learn, delta)={learn_delta:.3f}")
    lines += ["", "## H2-like continuous residuals"]
    valid = h2.dropna(subset=["residual"])
    if len(valid):
        for metric, sub in valid.groupby("metric"):
            lines.append(f"- `{metric}`: n={len(sub)}, mean residual={sub['residual'].mean():.3f}")
            top = sub.sort_values("residual", ascending=True).head(3)
            # For higher-is-better metrics, negative residual means composite underperforms atomic prediction.
            for _, r in top.iterrows():
                lines.append(f"  - underperforming composite `{r['slice_id']}`: residual={r['residual']:.3f}, observed={r['observed']:.3f}, predicted={r['predicted']:.3f}")
    else:
        lines.append("- No valid H2 continuous residuals; likely too few atomic slices or missing features.")
    lines += ["", "## Component coupling", "Component coupling compares composite continuous scores to the mean of its listed primitive slices. It is descriptive only."]
    if len(coupling):
        for _, r in coupling.head(10).iterrows():
            lines.append(f"- `{r['metric']}` / `{r['composite_slice_id']}`: composite_final={r['composite_final']:.3f}, component_mean_final={r['component_mean_final']:.3f}, diff={r['composite_minus_component_final']:.3f}")
    lines += ["", "## Claim boundary", "Use continuous-score outputs as calibration and observational bridge evidence only. They can show that a slice moves below top-1 accuracy, but they cannot establish causal dependency without interventions."]
    (result_dir / "pythia_continuous_score_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    manifest = write_manifest(
        result_dir,
        experiment="Pythia_observational_continuous_score_analysis",
        backend="Pythia_observational",
        code_version=args.code_version,
        input_paths={"result_dir": str(result_dir)},
        extra={"metrics": metrics, "h2_target": args.h2_target, "thesis_use": args.thesis_use},
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
    print(f"Wrote Pythia continuous-score outputs to {result_dir}")


if __name__ == "__main__":
    main()
