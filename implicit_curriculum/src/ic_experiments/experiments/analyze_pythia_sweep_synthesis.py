from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from ic_experiments.run_management import append_registry, write_manifest


def _read_optional(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def _infer_model_name(run_dir: Path, curves: pd.DataFrame) -> str:
    if not curves.empty and "model_name" in curves.columns and curves["model_name"].notna().any():
        vals = curves["model_name"].dropna().astype(str).unique().tolist()
        if vals:
            return vals[0]
    return run_dir.name


def _run_summary(run_dir: Path) -> tuple[dict[str, Any], pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    curves = _read_optional(run_dir / "pythia_eval_curves.csv")
    readiness = _read_optional(run_dir / "pythia_h2_readiness_metric_summary.csv")
    h1 = _read_optional(run_dir / "pythia_continuous_h1_summary.csv")
    residual_agree = _read_optional(run_dir / "pythia_residual_agreement_by_composite.csv")
    family_summary = _read_optional(run_dir / "pythia_residual_family_summary.csv")
    coupling = _read_optional(run_dir / "pythia_component_coupling_agreement.csv")
    model_name = _infer_model_name(run_dir, curves)
    rec: dict[str, Any] = {
        "run_dir": str(run_dir),
        "model_name": model_name,
        "has_curves": not curves.empty,
        "has_readiness": not readiness.empty,
        "has_h1": not h1.empty,
        "has_residual_refinement": not residual_agree.empty,
        "n_slices": int(curves["slice_id"].nunique()) if not curves.empty and "slice_id" in curves.columns else 0,
        "n_checkpoints": int(curves["revision"].nunique()) if not curves.empty and "revision" in curves.columns else 0,
        "h2_ready_metrics": ";".join(readiness.loc[readiness.get("h2_ready", False).astype(bool), "metric"].astype(str).tolist()) if not readiness.empty and "h2_ready" in readiness.columns and "metric" in readiness.columns else "",
        "n_residual_composites": int(residual_agree["slice_id"].nunique()) if not residual_agree.empty and "slice_id" in residual_agree.columns else 0,
        "n_consistent_under": int((residual_agree.get("verdict", pd.Series(dtype=str)) == "consistent_underperforming_observational").sum()) if not residual_agree.empty else 0,
        "n_consistent_over": int((residual_agree.get("verdict", pd.Series(dtype=str)) == "consistent_outperforming_observational").sum()) if not residual_agree.empty else 0,
        "n_mixed": int((residual_agree.get("verdict", pd.Series(dtype=str)) == "metric_dependent_or_mixed").sum()) if not residual_agree.empty else 0,
    }
    for df in [readiness, h1, residual_agree, family_summary, coupling]:
        if not df.empty:
            df.insert(0, "source_run_dir", str(run_dir))
            df.insert(1, "source_model_name", model_name)
    return rec, readiness, h1, residual_agree, family_summary, coupling


def _stability(residuals: pd.DataFrame) -> pd.DataFrame:
    if residuals.empty:
        return pd.DataFrame()
    rows: list[dict[str, Any]] = []
    for sid, g in residuals.groupby("slice_id"):
        n_runs = g["source_run_dir"].nunique()
        verdicts = g.get("verdict", pd.Series(dtype=str)).astype(str)
        under = int((verdicts == "consistent_underperforming_observational").sum())
        over = int((verdicts == "consistent_outperforming_observational").sum())
        mixed = int((verdicts == "metric_dependent_or_mixed").sum())
        first = g.iloc[0]
        if n_runs > 0 and under / len(g) >= 0.6:
            verdict = "stable_underperforming_observational"
        elif n_runs > 0 and over / len(g) >= 0.6:
            verdict = "stable_outperforming_observational"
        else:
            verdict = "model_or_config_dependent"
        rows.append({
            "slice_id": sid,
            "prompt_family": first.get("prompt_family", first.get("family", "")),
            "component_ids": first.get("component_ids", ""),
            "n_rows": int(len(g)),
            "n_runs": int(n_runs),
            "n_under_verdicts": under,
            "n_over_verdicts": over,
            "n_mixed_verdicts": mixed,
            "mean_underperforming_metric_rate": float(pd.to_numeric(g.get("underperforming_metric_rate", pd.Series(dtype=float)), errors="coerce").mean()) if "underperforming_metric_rate" in g.columns else float("nan"),
            "mean_median_residual_z": float(pd.to_numeric(g.get("median_residual_z", pd.Series(dtype=float)), errors="coerce").mean()) if "median_residual_z" in g.columns else float("nan"),
            "runs": ";".join(sorted(g["source_model_name"].astype(str).unique().tolist())),
            "stability_verdict": verdict,
        })
    return pd.DataFrame(rows).sort_values(["n_under_verdicts", "mean_median_residual_z"], ascending=[False, True])


def _family_stability(family_summary: pd.DataFrame) -> pd.DataFrame:
    if family_summary.empty:
        return pd.DataFrame()
    prompt_col = "prompt_family" if "prompt_family" in family_summary.columns else "family"
    rows: list[dict[str, Any]] = []
    for fam, g in family_summary.groupby(prompt_col, dropna=False):
        rows.append({
            "prompt_family": fam,
            "n_runs": int(g["source_run_dir"].nunique()),
            "mean_underperforming_metric_rate": float(pd.to_numeric(g.get("mean_underperforming_metric_rate", pd.Series(dtype=float)), errors="coerce").mean()) if "mean_underperforming_metric_rate" in g.columns else float("nan"),
            "total_consistent_under": int(pd.to_numeric(g.get("n_consistent_underperforming", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()) if "n_consistent_underperforming" in g.columns else 0,
            "total_consistent_over": int(pd.to_numeric(g.get("n_consistent_outperforming", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()) if "n_consistent_outperforming" in g.columns else 0,
            "models": ";".join(sorted(g["source_model_name"].astype(str).unique().tolist())),
        })
    return pd.DataFrame(rows).sort_values(["mean_underperforming_metric_rate", "total_consistent_under"], ascending=[False, False])


def _write_report(out: Path, run_summary: pd.DataFrame, stability: pd.DataFrame, fam_stability: pd.DataFrame) -> None:
    lines = [
        "# Pythia observational sweep synthesis",
        "",
        "This report aggregates Pythia-style observational runs across model sizes or evaluation configurations. It can show whether residual signatures are stable across settings, but it cannot establish causal dependency.",
        "",
        f"- runs included: `{len(run_summary)}`",
        f"- models/configs with residual refinement: `{int(run_summary['has_residual_refinement'].sum()) if len(run_summary) else 0}`",
        "",
        "## Run summary",
    ]
    for _, r in run_summary.iterrows():
        lines.append(
            f"- `{r['model_name']}` / `{r['run_dir']}`: slices={int(r['n_slices'])}, checkpoints={int(r['n_checkpoints'])}, "
            f"H2-ready metrics=`{r.get('h2_ready_metrics','')}`, residual composites={int(r['n_residual_composites'])}, "
            f"under={int(r['n_consistent_under'])}, over={int(r['n_consistent_over'])}, mixed={int(r['n_mixed'])}"
        )
    lines += ["", "## Cross-run composite stability"]
    if not stability.empty:
        for _, r in stability.head(12).iterrows():
            lines.append(
                f"- `{r['slice_id']}`: verdict=`{r['stability_verdict']}`, runs={int(r['n_runs'])}, "
                f"under-verdicts={int(r['n_under_verdicts'])}, over-verdicts={int(r['n_over_verdicts'])}, "
                f"mean under-rate={r['mean_underperforming_metric_rate']:.3f}, models=`{r['runs']}`"
            )
    else:
        lines.append("- No residual stability rows available. Run continuous analysis and residual refinement for each sweep directory first.")
    lines += ["", "## Composite-family stability"]
    if not fam_stability.empty:
        for _, r in fam_stability.iterrows():
            lines.append(
                f"- `{r['prompt_family']}`: runs={int(r['n_runs'])}, mean under-rate={r['mean_underperforming_metric_rate']:.3f}, "
                f"consistent-under total={int(r['total_consistent_under'])}, consistent-over total={int(r['total_consistent_over'])}, models=`{r['models']}`"
            )
    else:
        lines.append("- No family stability rows available.")
    lines += [
        "",
        "## Claim boundary",
        "A stable residual across model/config sweeps is stronger observational evidence than a single-run residual, but it is still not causal evidence. Use it to motivate controlled follow-ups or more focused mechanistic probes, not to claim exact-component dependency in Pythia.",
    ]
    (out / "PYTHIA_SWEEP_SYNTHESIS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    p = argparse.ArgumentParser(description="Aggregate Pythia observational runs across models/configurations.")
    p.add_argument("--run-dirs", nargs="+", required=True, help="Pythia result directories that have continuous/refinement outputs.")
    p.add_argument("--output-dir", default="results/pythia_sweep_synthesis_v30")
    p.add_argument("--code-version", default="v3.0")
    p.add_argument("--archive-root", default="results/archive")
    p.add_argument("--thesis-use", default="diagnostic")
    args = p.parse_args()

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    recs = []
    readiness_parts = []
    h1_parts = []
    residual_parts = []
    family_parts = []
    coupling_parts = []
    for rd_s in args.run_dirs:
        rec, readiness, h1, residual_agree, family_summary, coupling = _run_summary(Path(rd_s))
        recs.append(rec)
        if not readiness.empty:
            readiness_parts.append(readiness)
        if not h1.empty:
            h1_parts.append(h1)
        if not residual_agree.empty:
            residual_parts.append(residual_agree)
        if not family_summary.empty:
            family_parts.append(family_summary)
        if not coupling.empty:
            coupling_parts.append(coupling)

    run_summary = pd.DataFrame(recs)
    readiness_all = pd.concat(readiness_parts, ignore_index=True) if readiness_parts else pd.DataFrame()
    h1_all = pd.concat(h1_parts, ignore_index=True) if h1_parts else pd.DataFrame()
    residual_all = pd.concat(residual_parts, ignore_index=True) if residual_parts else pd.DataFrame()
    family_all = pd.concat(family_parts, ignore_index=True) if family_parts else pd.DataFrame()
    coupling_all = pd.concat(coupling_parts, ignore_index=True) if coupling_parts else pd.DataFrame()
    stability = _stability(residual_all)
    fam_stability = _family_stability(family_all)

    run_summary.to_csv(out / "pythia_sweep_run_summary.csv", index=False)
    readiness_all.to_csv(out / "pythia_sweep_readiness_all.csv", index=False)
    h1_all.to_csv(out / "pythia_sweep_h1_all.csv", index=False)
    residual_all.to_csv(out / "pythia_sweep_residual_agreement_all.csv", index=False)
    family_all.to_csv(out / "pythia_sweep_family_summary_all.csv", index=False)
    coupling_all.to_csv(out / "pythia_sweep_component_coupling_all.csv", index=False)
    stability.to_csv(out / "pythia_sweep_residual_stability.csv", index=False)
    fam_stability.to_csv(out / "pythia_sweep_family_stability.csv", index=False)
    _write_report(out, run_summary, stability, fam_stability)

    manifest = write_manifest(
        out,
        experiment="Pythia_observational_sweep_synthesis",
        backend="Pythia_observational",
        code_version=args.code_version,
        input_paths={"run_dirs": args.run_dirs},
        extra={"thesis_use": args.thesis_use},
    )
    append_registry(Path(args.archive_root) / "results_registry.csv", {
        "run_id": manifest["run_id"],
        "code_version": args.code_version,
        "experiment": manifest["experiment"],
        "backend": manifest["backend"],
        "output_path": str(out),
        "status": "created",
        "thesis_use": args.thesis_use,
        "created_at_utc": manifest["created_at_utc"],
    })
    print(f"Wrote Pythia sweep synthesis to {out}")


if __name__ == "__main__":
    main()
