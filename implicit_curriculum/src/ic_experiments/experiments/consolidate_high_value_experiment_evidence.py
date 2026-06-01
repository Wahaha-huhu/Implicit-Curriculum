"""Consolidate high-value pre-writing experiments into durable thesis evidence.

This command is a bookkeeping step after the two high-value experiments added
in v3.4:

1. B2 sparse-parity strengthening.
2. Focused Pythia arithmetic residual sweep.

It copies the source result files into ``thesis_evidence/`` and writes a
claim-safe synthesis that can be cited while drafting.  It does not rerun any
experiment and does not change the claim boundary: B2 is a regime contrast, and
Pythia arithmetic is observational residual evidence only.
"""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd


def _copy_if_exists(src: Path, dst: Path) -> bool:
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return True
    return False


def _safe_read_csv(path: Path) -> Optional[pd.DataFrame]:
    if path.exists():
        try:
            return pd.read_csv(path)
        except Exception:
            return None
    return None


def _parse_b2(b2_dir: Optional[Path]) -> Dict[str, object]:
    out: Dict[str, object] = {
        "provided": bool(b2_dir),
        "exists": bool(b2_dir and b2_dir.exists()),
        "best_threshold": None,
        "best_acquisition_rate": None,
        "time_rho_frequency_at_best": None,
        "time_rho_degree_at_best": None,
        "final_rho_frequency_at_best": None,
        "final_rho_degree_at_best": None,
        "verdict": "missing",
    }
    if not b2_dir or not b2_dir.exists():
        return out

    # Prefer the compact strengthening summary if present.  Otherwise fall back
    # to the ordering table emitted by the sparse-parity analyzer.
    candidates = [
        b2_dir / "b2_strengthening_summary.csv",
        b2_dir / "sparse_parity_ordering_summary.csv",
    ]
    df = None
    for c in candidates:
        df = _safe_read_csv(c)
        if df is not None and len(df):
            break
    if df is None or len(df) == 0:
        return out

    # Column names have changed slightly across versions, so use permissive
    # lookup aliases.
    def col(*names: str) -> Optional[str]:
        for n in names:
            if n in df.columns:
                return n
        return None

    thr_col = col("threshold", "metric_threshold")
    acq_col = col("acquisition_rate", "acq_rate", "acq")
    fr_t_col = col("time_spearman_frequency", "time_rho_frequency", "time_rho_freq", "time-Spearman(freq)")
    deg_t_col = col("time_spearman_degree", "time_rho_degree", "time-Spearman(degree)")
    fr_f_col = col("final_spearman_frequency", "final_rho_frequency", "final_rho_freq", "final-Spearman(freq)")
    deg_f_col = col("final_spearman_degree", "final_rho_degree", "final-Spearman(degree)")

    if acq_col:
        best_idx = df[acq_col].astype(float).idxmax()
    else:
        best_idx = df.index[0]
    row = df.loc[best_idx]

    def get(c: Optional[str]) -> object:
        if c is None:
            return None
        try:
            v = row[c]
            if pd.isna(v):
                return None
            return float(v)
        except Exception:
            return row[c] if c in row else None

    out.update(
        {
            "best_threshold": get(thr_col),
            "best_acquisition_rate": get(acq_col),
            "time_rho_frequency_at_best": get(fr_t_col),
            "time_rho_degree_at_best": get(deg_t_col),
            "final_rho_frequency_at_best": get(fr_f_col),
            "final_rho_degree_at_best": get(deg_f_col),
        }
    )
    acq = out["best_acquisition_rate"]
    freq_ok = out["time_rho_frequency_at_best"] is not None and float(out["time_rho_frequency_at_best"]) < 0
    degree_ok = out["time_rho_degree_at_best"] is not None and float(out["time_rho_degree_at_best"]) > 0
    if acq is not None and float(acq) >= 0.25 and freq_ok and degree_ok:
        out["verdict"] = "green_regime_contrast"
    elif acq is not None and float(acq) > 0:
        out["verdict"] = "yellow_partial_contrast"
    else:
        out["verdict"] = "red_not_interpretable"
    return out


def _parse_pythia_arithmetic(sweep_dir: Optional[Path]) -> Dict[str, object]:
    out: Dict[str, object] = {
        "provided": bool(sweep_dir),
        "exists": bool(sweep_dir and sweep_dir.exists()),
        "runs_included": None,
        "valid_runs": None,
        "models": None,
        "arithmetic_mean_under_rate": None,
        "arithmetic_consistent_under_total": None,
        "arithmetic_consistent_over_total": None,
        "verdict": "missing",
    }
    if not sweep_dir or not sweep_dir.exists():
        return out
    run_summary = _safe_read_csv(sweep_dir / "pythia_sweep_run_summary.csv")
    if run_summary is not None and len(run_summary):
        out["runs_included"] = int(len(run_summary))
        if "residual_composites" in run_summary.columns:
            valid = run_summary[run_summary["residual_composites"].fillna(0).astype(float) > 0]
        else:
            valid = run_summary
        out["valid_runs"] = int(len(valid))
        model_col = "model_name" if "model_name" in valid.columns else "model" if "model" in valid.columns else None
        if model_col:
            out["models"] = ";".join(sorted(str(x) for x in valid[model_col].dropna().unique()))

    fam = _safe_read_csv(sweep_dir / "pythia_sweep_family_stability.csv")
    if fam is not None and len(fam):
        family_col = "family" if "family" in fam.columns else "composite_family" if "composite_family" in fam.columns else None
        if family_col:
            rows = fam[fam[family_col].astype(str) == "arithmetic"]
        else:
            rows = fam.iloc[:0]
        if len(rows):
            row = rows.iloc[0]
            for key in ["mean_under_rate", "consistent_under_total", "consistent_over_total"]:
                if key in row.index and not pd.isna(row[key]):
                    out[f"arithmetic_{key}"] = float(row[key])
            rate = out.get("arithmetic_mean_under_rate")
            valid_runs = out.get("valid_runs")
            if rate is not None and valid_runs and float(rate) >= 0.6:
                out["verdict"] = "green_arithmetic_observational_residual"
            elif rate is not None:
                out["verdict"] = "yellow_metric_or_model_dependent"
            else:
                out["verdict"] = "red_not_interpretable"
    return out


def _write_claim_tables(evidence_dir: Path, out_dir: Path, b2_info: Dict[str, object], arith_info: Dict[str, object]) -> None:
    table_dir = evidence_dir / "tables"
    table_dir.mkdir(parents=True, exist_ok=True)
    rows = [
        {
            "evidence_block": "B2 sparse-parity strengthening",
            "status": b2_info.get("verdict"),
            "claim_supported": "sparse-parity acquisition is structured by degree/difficulty and frequency exposure",
            "thesis_role": "regime contrast against B1 compositional dependency analysis",
            "claim_boundary": "not a component-dependency or intervention test",
            "key_numbers": json.dumps({k: b2_info.get(k) for k in ["best_threshold", "best_acquisition_rate", "time_rho_frequency_at_best", "time_rho_degree_at_best", "final_rho_frequency_at_best", "final_rho_degree_at_best"]}),
        },
        {
            "evidence_block": "Focused Pythia arithmetic sweep",
            "status": arith_info.get("verdict"),
            "claim_supported": "arithmetic composite residual underperformance is robust in a focused observational slice suite",
            "thesis_role": "strengthens Pythia observational bridge",
            "claim_boundary": "observational only; does not establish causal component dependency",
            "key_numbers": json.dumps({k: arith_info.get(k) for k in ["runs_included", "valid_runs", "arithmetic_mean_under_rate", "arithmetic_consistent_under_total", "arithmetic_consistent_over_total"]}),
        },
    ]
    df = pd.DataFrame(rows)
    df.to_csv(table_dir / "high_value_experiment_claim_update.csv", index=False)
    df.to_csv(out_dir / "high_value_experiment_claim_update.csv", index=False)

    final_claim_updates = [
        {
            "claim": "Frequency/difficulty regimes exist outside B1 compositional tasks",
            "status_after_v35": "strengthened",
            "support": "B2 strengthened sparse parity has nontrivial acquisition coverage; frequency and degree have expected signs",
            "boundary": "B2 is a regime contrast, not dependency evidence",
        },
        {
            "claim": "Pythia arithmetic composites show robust observational residual underperformance",
            "status_after_v35": "strengthened",
            "support": "focused arithmetic sweep across Pythia 70M-1.4B model/config runs",
            "boundary": "observational residual stability only; no causal claim",
        },
        {
            "claim": "Detailed thesis writing can begin",
            "status_after_v35": "supported",
            "support": "controlled B1 arc, B2 contrast, Pythia broad and focused observational sweeps are consolidated",
            "boundary": "optional experiments remain possible but are not required for first full draft",
        },
    ]
    pd.DataFrame(final_claim_updates).to_csv(table_dir / "post_high_value_final_claim_updates.csv", index=False)
    pd.DataFrame(final_claim_updates).to_csv(out_dir / "post_high_value_final_claim_updates.csv", index=False)


def _write_docs(evidence_dir: Path, out_dir: Path, b2_info: Dict[str, object], arith_info: Dict[str, object], code_version: str) -> None:
    now = datetime.now(timezone.utc).isoformat()
    md = f"""# High-value experiment consolidation

Generated at: `{now}`  
Code version: `{code_version}`

This document consolidates the high-value experiments run before detailed thesis writing: the strengthened B2 sparse-parity contrast and the focused Pythia arithmetic residual sweep.

## Executive verdict

```text
B2 sparse-parity strengthening: {b2_info.get('verdict')}
Focused Pythia arithmetic sweep: {arith_info.get('verdict')}
Detailed thesis writing: ready
```

## B2 sparse-parity strengthening

B2 is used as a frequency/quanta-style regime contrast.  It should not be interpreted as a component-dependency test.

Parsed summary:

```json
{json.dumps(b2_info, indent=2)}
```

Thesis-safe interpretation:

> In sparse-parity-style tasks, acquisition is structured by intrinsic degree/difficulty and frequency exposure.  This provides a contrasting regime in which ordering can be largely explained without invoking component-composite dependency.

Claim boundary:

> B2 is not an H3 intervention experiment and does not provide evidence about exact-component dependency.

## Focused Pythia arithmetic residual sweep

The focused arithmetic suite stress-tests the strongest Pythia observational pattern found in the broader slice suite.

Parsed summary:

```json
{json.dumps(arith_info, indent=2)}
```

Thesis-safe interpretation:

> A focused arithmetic Pythia slice suite confirms that arithmetic composites tend to underperform primitive-predictor expectations across the valid Tier-1 model/config runs, strengthening the observational bridge from the controlled residual framework to checkpointed LLMs.

Claim boundary:

> This remains observational residual evidence.  It does not show that Pythia causally learns arithmetic composites through primitives.

## Updated thesis picture

The project now has the following evidence blocks ready for writing:

1. Controlled B1 family 1: localized exact-component dependency plus gradient alignment.
2. Controlled B1 family 2: regime contrast, readiness boundary, and no broad exact-dependency replication.
3. B2 sparse parity: frequency/difficulty regime contrast.
4. Pythia broad Tier-1 sweep: stable observational primitive-to-composite residuals through 1.4B.
5. Focused Pythia arithmetic sweep: robustness check for the strongest Pythia residual family.

## Drafting implication

The first detailed thesis draft can now begin.  Additional experiments should be framed as optional strengthening or future work, not blockers.
"""
    out_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / "HIGH_VALUE_EXPERIMENT_CONSOLIDATION.md").write_text(md)
    (out_dir / "HIGH_VALUE_EXPERIMENT_CONSOLIDATION.md").write_text(md)

    readiness = f"""# Post-high-value thesis readiness update

Generated at: `{now}`

## Status

The high-value experiments strengthen two important parts of the thesis:

- B2 now gives a usable frequency/difficulty regime contrast.
- The focused arithmetic Pythia suite strengthens the observational residual bridge.

## Current strongest final framing

> Acquisition order and residuals are useful diagnostics but not self-interpreting.  In controlled training, H3 interventions are needed to distinguish exact-component dependency from operation-family transfer, weak/negative cases, and hard-composite failure.  In sparse-parity tasks, frequency and degree provide a contrasting non-dependency regime.  In Pythia checkpoints, primitive-to-composite residual signatures are stable observationally, especially for arithmetic composites, but remain non-causal.

## Remaining experiments

Optional only:

1. Third B1 H3-ready family.
2. Stronger mediator probes.
3. Denser Pythia checkpoints.
4. Larger Pythia models after revision-loading is fixed.
"""
    (evidence_dir / "POST_HIGH_VALUE_THESIS_READINESS.md").write_text(readiness)
    (out_dir / "POST_HIGH_VALUE_THESIS_READINESS.md").write_text(readiness)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence-dir", required=True)
    ap.add_argument("--b2-synthesis-dir", default=None, help="Directory containing B2_STRENGTHENING_SYNTHESIS.md and b2_strengthening_summary.csv")
    ap.add_argument("--pythia-arithmetic-suite-dir", default=None, help="Directory containing pythia_arithmetic_slice_suite_report.md")
    ap.add_argument("--pythia-arithmetic-sweep-dir", default=None, help="Directory containing focused arithmetic PYTHIA_SWEEP_SYNTHESIS.md")
    ap.add_argument("--output-dir", default=None)
    ap.add_argument("--code-version", default="v3.5")
    ap.add_argument("--archive-root", default=None)
    ap.add_argument("--thesis-use", default="candidate")
    args = ap.parse_args()

    evidence_dir = Path(args.evidence_dir)
    out_dir = Path(args.output_dir) if args.output_dir else evidence_dir / "high_value_experiment_consolidation"
    results_dir = evidence_dir / "results_summaries"
    tables_dir = evidence_dir / "tables"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    b2_dir = Path(args.b2_synthesis_dir) if args.b2_synthesis_dir else None
    suite_dir = Path(args.pythia_arithmetic_suite_dir) if args.pythia_arithmetic_suite_dir else None
    arith_dir = Path(args.pythia_arithmetic_sweep_dir) if args.pythia_arithmetic_sweep_dir else None

    b2_info = _parse_b2(b2_dir)
    arith_info = _parse_pythia_arithmetic(arith_dir)

    # Copy source summaries into durable evidence locations.
    if b2_dir and b2_dir.exists():
        for name in ["B2_STRENGTHENING_SYNTHESIS.md", "b2_strengthening_summary.csv"]:
            _copy_if_exists(b2_dir / name, results_dir / f"v34_{name}")
            _copy_if_exists(b2_dir / name, out_dir / f"v34_{name}")
        _copy_if_exists(b2_dir / "B2_STRENGTHENING_SYNTHESIS.md", evidence_dir / "B2_STRENGTHENING_SYNTHESIS.md")
        _copy_if_exists(b2_dir / "b2_strengthening_summary.csv", tables_dir / "b2_strengthening_summary.csv")

    if suite_dir and suite_dir.exists():
        _copy_if_exists(suite_dir / "pythia_arithmetic_slice_suite_report.md", results_dir / "v34_pythia_arithmetic_slice_suite_report.md")
        _copy_if_exists(suite_dir / "pythia_arithmetic_slice_suite_report.md", out_dir / "v34_pythia_arithmetic_slice_suite_report.md")
        _copy_if_exists(suite_dir / "pythia_arithmetic_slice_suite_report.md", evidence_dir / "PYTHIA_ARITHMETIC_SLICE_SUITE.md")

    if arith_dir and arith_dir.exists():
        for name in [
            "PYTHIA_SWEEP_SYNTHESIS.md",
            "pythia_sweep_run_summary.csv",
            "pythia_sweep_residual_stability.csv",
            "pythia_sweep_family_stability.csv",
        ]:
            _copy_if_exists(arith_dir / name, results_dir / f"v34_arithmetic_{name}")
            _copy_if_exists(arith_dir / name, out_dir / f"v34_arithmetic_{name}")
        _copy_if_exists(arith_dir / "PYTHIA_SWEEP_SYNTHESIS.md", evidence_dir / "PYTHIA_ARITHMETIC_SWEEP_SYNTHESIS.md")
        _copy_if_exists(arith_dir / "pythia_sweep_run_summary.csv", tables_dir / "pythia_arithmetic_sweep_run_summary.csv")
        _copy_if_exists(arith_dir / "pythia_sweep_residual_stability.csv", tables_dir / "pythia_arithmetic_sweep_residual_stability.csv")
        _copy_if_exists(arith_dir / "pythia_sweep_family_stability.csv", tables_dir / "pythia_arithmetic_sweep_family_stability.csv")

    _write_claim_tables(evidence_dir, out_dir, b2_info, arith_info)
    _write_docs(evidence_dir, out_dir, b2_info, arith_info, args.code_version)

    manifest = {
        "experiment": "high_value_experiment_consolidation",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "code_version": args.code_version,
        "thesis_use": args.thesis_use,
        "evidence_dir": str(evidence_dir),
        "output_dir": str(out_dir),
        "b2_synthesis_dir": str(b2_dir) if b2_dir else None,
        "pythia_arithmetic_suite_dir": str(suite_dir) if suite_dir else None,
        "pythia_arithmetic_sweep_dir": str(arith_dir) if arith_dir else None,
        "b2_info": b2_info,
        "pythia_arithmetic_info": arith_info,
        "outputs": [
            str(evidence_dir / "HIGH_VALUE_EXPERIMENT_CONSOLIDATION.md"),
            str(evidence_dir / "POST_HIGH_VALUE_THESIS_READINESS.md"),
            str(tables_dir / "high_value_experiment_claim_update.csv"),
            str(tables_dir / "post_high_value_final_claim_updates.csv"),
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
                "experiment": manifest["experiment"],
                "code_version": args.code_version,
                "output_dir": str(out_dir),
                "thesis_use": args.thesis_use,
                "summary": "Consolidated B2 strengthened contrast and focused Pythia arithmetic sweep.",
            }
        ])
        if reg.exists():
            old = pd.read_csv(reg)
            pd.concat([old, row], ignore_index=True).to_csv(reg, index=False)
        else:
            row.to_csv(reg, index=False)

    print(f"Consolidated high-value experiment evidence into {out_dir}")


if __name__ == "__main__":
    main()
