from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from ic_experiments.run_management import append_registry, write_manifest


def _safe_float(x: Any, default: float = float("nan")) -> float:
    try:
        v = float(x)
        return v
    except Exception:
        return default


def _metric_label(metric: str) -> str:
    # All currently emitted metrics are higher-is-better in their reported scale.
    # Residual = observed - predicted, so negative means composite underperforms primitive prediction.
    return "higher_is_better"


def _load_required(result_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    h2_path = result_dir / "pythia_continuous_h2_residuals.csv"
    summary_path = result_dir / "pythia_continuous_slice_summary.csv"
    coupling_path = result_dir / "pythia_continuous_component_coupling.csv"
    missing = [str(p) for p in [h2_path, summary_path, coupling_path] if not p.exists()]
    if missing:
        raise FileNotFoundError("Missing required Pythia continuous outputs: " + ", ".join(missing))
    return pd.read_csv(h2_path), pd.read_csv(summary_path), pd.read_csv(coupling_path)


def _filter_metrics(df: pd.DataFrame, metrics: list[str] | None) -> pd.DataFrame:
    if metrics:
        return df[df["metric"].isin(metrics)].copy()
    return df.copy()


def _residual_matrix(h2: pd.DataFrame, slices: pd.DataFrame) -> pd.DataFrame:
    valid = h2.dropna(subset=["residual", "observed", "predicted"]).copy()
    if valid.empty:
        return pd.DataFrame()
    # Standardize residual within each metric so mixed units can be compared cautiously.
    parts = []
    for metric, g in valid.groupby("metric"):
        g = g.copy()
        sd = float(g["residual"].std(ddof=0))
        if not np.isfinite(sd) or sd <= 1e-12:
            g["residual_z"] = 0.0
        else:
            g["residual_z"] = (g["residual"] - float(g["residual"].mean())) / sd
        g["residual_direction"] = np.where(g["residual"] < 0, "under", np.where(g["residual"] > 0, "over", "zero"))
        g["metric_direction"] = _metric_label(str(metric))
        parts.append(g)
    valid = pd.concat(parts, ignore_index=True)
    meta_cols = [
        "slice_id", "family", "prompt_family", "operation_type", "composition_depth",
        "frequency_proxy", "reference_learnability", "formal_utility", "answer_entropy_proxy",
        "component_ids", "control_type", "kind",
    ]
    meta_cols = [c for c in meta_cols if c in slices.columns]
    meta = slices[meta_cols].drop_duplicates("slice_id")
    valid = valid.merge(meta, on="slice_id", how="left", suffixes=("", "_meta"))
    return valid


def _composite_metric_agreement(matrix: pd.DataFrame) -> pd.DataFrame:
    if matrix.empty:
        return pd.DataFrame()
    rows: list[dict[str, Any]] = []
    group_cols = ["model_name", "slice_id"]
    for (model_name, slice_id), g in matrix.groupby(group_cols):
        n = len(g)
        n_under = int((g["residual"] < 0).sum())
        n_over = int((g["residual"] > 0).sum())
        n_zero = int((g["residual"] == 0).sum())
        under_rate = n_under / n if n else float("nan")
        over_rate = n_over / n if n else float("nan")
        median_resid = float(g["residual"].median())
        mean_resid = float(g["residual"].mean())
        median_z = float(g["residual_z"].median())
        mean_z = float(g["residual_z"].mean())
        if n_under >= math.ceil(0.6 * n) and median_resid < 0:
            verdict = "consistent_underperforming_observational"
        elif n_over >= math.ceil(0.6 * n) and median_resid > 0:
            verdict = "consistent_outperforming_observational"
        else:
            verdict = "metric_dependent_or_mixed"
        first = g.iloc[0]
        rows.append({
            "model_name": model_name,
            "slice_id": slice_id,
            "family": first.get("family", ""),
            "prompt_family": first.get("prompt_family", ""),
            "operation_type": first.get("operation_type", ""),
            "composition_depth": first.get("composition_depth", np.nan),
            "component_ids": first.get("component_ids", ""),
            "n_metrics": n,
            "n_underperforming_metrics": n_under,
            "n_outperforming_metrics": n_over,
            "n_zero_metrics": n_zero,
            "underperforming_metric_rate": under_rate,
            "outperforming_metric_rate": over_rate,
            "mean_residual": mean_resid,
            "median_residual": median_resid,
            "mean_residual_z": mean_z,
            "median_residual_z": median_z,
            "max_abs_residual_z": float(g["residual_z"].abs().max()),
            "verdict": verdict,
            "underperforming_metrics": ";".join(g.loc[g["residual"] < 0, "metric"].astype(str).tolist()),
            "outperforming_metrics": ";".join(g.loc[g["residual"] > 0, "metric"].astype(str).tolist()),
        })
    return pd.DataFrame(rows).sort_values(["underperforming_metric_rate", "median_residual_z"], ascending=[False, True])


def _family_summary(comp: pd.DataFrame) -> pd.DataFrame:
    if comp.empty:
        return pd.DataFrame()
    rows: list[dict[str, Any]] = []
    for (model_name, prompt_family), g in comp.groupby(["model_name", "prompt_family"], dropna=False):
        rows.append({
            "model_name": model_name,
            "prompt_family": prompt_family,
            "n_composites": int(len(g)),
            "mean_underperforming_metric_rate": float(g["underperforming_metric_rate"].mean()),
            "mean_outperforming_metric_rate": float(g["outperforming_metric_rate"].mean()),
            "n_consistent_underperforming": int((g["verdict"] == "consistent_underperforming_observational").sum()),
            "n_consistent_outperforming": int((g["verdict"] == "consistent_outperforming_observational").sum()),
            "n_mixed": int((g["verdict"] == "metric_dependent_or_mixed").sum()),
            "top_underperforming_composites": ";".join(g.sort_values(["underperforming_metric_rate", "median_residual_z"], ascending=[False, True])["slice_id"].head(5).astype(str).tolist()),
        })
    return pd.DataFrame(rows).sort_values(["mean_underperforming_metric_rate", "n_consistent_underperforming"], ascending=[False, False])


def _component_coupling_agreement(coupling: pd.DataFrame, metrics: list[str] | None) -> pd.DataFrame:
    if coupling.empty:
        return pd.DataFrame()
    df = _filter_metrics(coupling, metrics)
    if df.empty:
        return pd.DataFrame()
    rows: list[dict[str, Any]] = []
    for (model_name, comp), g in df.groupby(["model_name", "composite_slice_id"]):
        n = len(g)
        n_lag = int((g["composite_minus_component_final"] < 0).sum())
        n_ahead = int((g["composite_minus_component_final"] > 0).sum())
        if n_lag >= math.ceil(0.6 * n):
            verdict = "component_lag_observational"
        elif n_ahead >= math.ceil(0.6 * n):
            verdict = "composite_ahead_observational"
        else:
            verdict = "mixed_component_coupling"
        first = g.iloc[0]
        rows.append({
            "model_name": model_name,
            "composite_slice_id": comp,
            "component_ids": first.get("component_ids", ""),
            "n_metrics": n,
            "n_component_lag_metrics": n_lag,
            "n_composite_ahead_metrics": n_ahead,
            "component_lag_rate": n_lag / n if n else float("nan"),
            "composite_ahead_rate": n_ahead / n if n else float("nan"),
            "mean_composite_minus_component_final": float(g["composite_minus_component_final"].mean()),
            "mean_composite_minus_component_delta": float(g.get("composite_minus_component_delta", pd.Series(dtype=float)).mean()) if "composite_minus_component_delta" in g.columns else float("nan"),
            "verdict": verdict,
            "lag_metrics": ";".join(g.loc[g["composite_minus_component_final"] < 0, "metric"].astype(str).tolist()),
            "ahead_metrics": ";".join(g.loc[g["composite_minus_component_final"] > 0, "metric"].astype(str).tolist()),
        })
    return pd.DataFrame(rows).sort_values(["component_lag_rate", "mean_composite_minus_component_final"], ascending=[False, True])


def _write_report(
    out_path: Path,
    result_dir: Path,
    matrix: pd.DataFrame,
    comp: pd.DataFrame,
    family: pd.DataFrame,
    coupling_agree: pd.DataFrame,
    metrics: list[str],
) -> None:
    lines: list[str] = [
        "# Pythia observational residual refinement",
        "",
        "This report refines the Pythia observational bridge by asking whether primitive-to-composite residuals agree across continuous metrics and composite families. It remains observational and cannot establish causal dependency.",
        "",
        f"- result_dir: `{result_dir}`",
        f"- metrics included: `{', '.join(metrics) if metrics else 'all available'}`",
        f"- valid residual rows: `{len(matrix)}`",
        f"- composites with residuals: `{comp['slice_id'].nunique() if len(comp) else 0}`",
        "",
        "## Composite residual agreement",
    ]
    if len(comp):
        for _, r in comp.head(10).iterrows():
            lines.append(
                f"- `{r['slice_id']}` ({r.get('prompt_family','')}): verdict=`{r['verdict']}`, "
                f"under-rate={r['underperforming_metric_rate']:.3f}, over-rate={r['outperforming_metric_rate']:.3f}, "
                f"median-z={r['median_residual_z']:.3f}; under metrics=`{r['underperforming_metrics']}`"
            )
    else:
        lines.append("- No valid composite residuals found.")
    lines += ["", "## Composite-family summary"]
    if len(family):
        for _, r in family.iterrows():
            lines.append(
                f"- `{r['prompt_family']}`: n={int(r['n_composites'])}, "
                f"mean under-rate={r['mean_underperforming_metric_rate']:.3f}, "
                f"consistent-under={int(r['n_consistent_underperforming'])}, "
                f"consistent-over={int(r['n_consistent_outperforming'])}, mixed={int(r['n_mixed'])}; "
                f"top=`{r['top_underperforming_composites']}`"
            )
    else:
        lines.append("- No family summary available.")
    lines += ["", "## Component-coupling agreement"]
    if len(coupling_agree):
        for _, r in coupling_agree.head(10).iterrows():
            lines.append(
                f"- `{r['composite_slice_id']}`: verdict=`{r['verdict']}`, "
                f"lag-rate={r['component_lag_rate']:.3f}, ahead-rate={r['composite_ahead_rate']:.3f}, "
                f"mean final diff={r['mean_composite_minus_component_final']:.3f}"
            )
    else:
        lines.append("- No component-coupling rows available.")
    lines += [
        "",
        "## Claim boundary",
        "A robust observational Pythia finding requires residual agreement across multiple continuous metrics and preferably across model sizes/checkpoint densities. These outputs can motivate controlled or observational follow-ups, but they are not H3 causal evidence.",
    ]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    p = argparse.ArgumentParser(description="Refine Pythia observational residuals by metric agreement and composite family.")
    p.add_argument("--result-dir", required=True)
    p.add_argument("--metrics", nargs="*", default=None, help="Optional subset of metrics to include.")
    p.add_argument("--output-dir", default=None, help="Defaults to result-dir.")
    p.add_argument("--code-version", default="v2.9")
    p.add_argument("--archive-root", default="results/archive")
    p.add_argument("--thesis-use", default="diagnostic")
    args = p.parse_args()

    result_dir = Path(args.result_dir)
    output_dir = Path(args.output_dir) if args.output_dir else result_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    h2, summary, coupling = _load_required(result_dir)
    h2 = _filter_metrics(h2, args.metrics)
    summary = _filter_metrics(summary, args.metrics)
    coupling = _filter_metrics(coupling, args.metrics)
    metrics = sorted(h2["metric"].dropna().astype(str).unique().tolist()) if "metric" in h2.columns else []

    matrix = _residual_matrix(h2, summary[[c for c in summary.columns if c != "metric"]].drop_duplicates("slice_id"))
    comp = _composite_metric_agreement(matrix)
    fam = _family_summary(comp)
    cagree = _component_coupling_agreement(coupling, args.metrics)

    matrix.to_csv(output_dir / "pythia_residual_metric_matrix.csv", index=False)
    comp.to_csv(output_dir / "pythia_residual_agreement_by_composite.csv", index=False)
    fam.to_csv(output_dir / "pythia_residual_family_summary.csv", index=False)
    cagree.to_csv(output_dir / "pythia_component_coupling_agreement.csv", index=False)
    _write_report(output_dir / "pythia_residual_refinement_report.md", result_dir, matrix, comp, fam, cagree, metrics)

    manifest = write_manifest(
        output_dir,
        experiment="Pythia_observational_residual_refinement",
        backend="Pythia_observational",
        code_version=args.code_version,
        input_paths={"result_dir": str(result_dir)},
        extra={"metrics": metrics, "thesis_use": args.thesis_use},
    )
    append_registry(Path(args.archive_root) / "results_registry.csv", {
        "run_id": manifest["run_id"],
        "code_version": args.code_version,
        "experiment": manifest["experiment"],
        "backend": manifest["backend"],
        "output_path": str(output_dir),
        "status": "analyzed",
        "thesis_use": args.thesis_use,
        "created_at_utc": manifest["created_at_utc"],
    })
    print(f"Wrote Pythia residual refinement outputs to {output_dir}")


if __name__ == "__main__":
    main()
