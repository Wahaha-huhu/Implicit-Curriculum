from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd

from ic_experiments.run_management import write_manifest, append_registry


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Aggregate B1 evidence across multiple generated families using existing reports.")
    p.add_argument("--family-registry", type=Path, required=True, help="CSV with columns family_id,h1_report,h2_report,h3_matrix(optional),mediator_report(optional)")
    p.add_argument("--output-dir", type=Path, default=Path("results/b1_cross_family_synthesis"))
    p.add_argument("--code-version", type=str, default="v2.0")
    p.add_argument("--archive-root", type=Path, default=Path("results/archive"))
    p.add_argument("--thesis-use", type=str, default="candidate")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    reg = pd.read_csv(args.family_registry)
    rows = []
    h3_rows = []
    for _, r in reg.iterrows():
        family_id = str(r["family_id"])
        h1 = parse_h1(Path(str(r.get("h1_report", ""))))
        h2 = parse_h2(Path(str(r.get("h2_report", ""))))
        row = {"family_id": family_id, **h1, **h2}
        h3_path = str(r.get("h3_matrix", ""))
        if h3_path and h3_path != "nan" and Path(h3_path).exists():
            h3 = pd.read_csv(h3_path)
            for _, hr in h3.iterrows():
                h3_rows.append({"family_id": family_id, **hr.to_dict()})
            row["h3_pairs_tested"] = int(len(h3))
            row["h3_positive_exact_pairs"] = int((h3.get("verdict", pd.Series(dtype=str)).astype(str).str.contains("positive_exact", na=False)).sum())
            row["h3_operation_family_pairs"] = int((h3.get("verdict", pd.Series(dtype=str)).astype(str).str.contains("operation_family", na=False)).sum())
            row["h3_weak_or_negative_pairs"] = int((h3.get("verdict", pd.Series(dtype=str)).astype(str).str.contains("weak|negative", regex=True, na=False)).sum())
        else:
            row["h3_pairs_tested"] = 0
            row["h3_positive_exact_pairs"] = 0
            row["h3_operation_family_pairs"] = 0
            row["h3_weak_or_negative_pairs"] = 0
        rows.append(row)
    summary = pd.DataFrame(rows)
    summary.to_csv(out / "cross_family_summary.csv", index=False)
    if h3_rows:
        pd.DataFrame(h3_rows).to_csv(out / "cross_family_h3_pairs.csv", index=False)
    report = make_report(summary, pd.DataFrame(h3_rows) if h3_rows else pd.DataFrame())
    (out / "CROSS_FAMILY_SYNTHESIS.md").write_text(report, encoding="utf-8")
    manifest = write_manifest(
        out,
        experiment="B1_cross_family_synthesis",
        backend="B1_sequence_dsl",
        code_version=args.code_version,
        run_id="b1_cross_family_synthesis",
        command=None,
        input_paths={"family_registry": str(args.family_registry)},
        extra={"thesis_use": args.thesis_use},
    )
    if args.archive_root:
        append_registry(args.archive_root / "results_registry.csv", {
            "run_id": manifest["run_id"], "code_version": args.code_version, "git_sha": manifest["git_sha"],
            "experiment": manifest["experiment"], "backend": manifest["backend"], "output_path": str(out),
            "status": "analyzed", "thesis_use": args.thesis_use, "created_at_utc": manifest["created_at_utc"],
        })
    print(f"Wrote {out / 'CROSS_FAMILY_SYNTHESIS.md'}")


def parse_h1(path: Path) -> dict:
    text = safe_read(path)
    out = {"h1_report": str(path) if path.exists() else "", "h1_available": path.exists()}
    if not text:
        return out
    m = re.search(r"all / reference_learnability: sign-rate=([0-9.]+), mean-rho=([-0-9.]+)", text)
    if m:
        out["h1_all_learnability_sign_rate"] = float(m.group(1)); out["h1_all_learnability_mean_rho"] = float(m.group(2))
    m = re.search(r"all / frequency: sign-rate=([0-9.]+), mean-rho=([-0-9.]+)", text)
    if m:
        out["h1_all_frequency_sign_rate"] = float(m.group(1)); out["h1_all_frequency_mean_rho"] = float(m.group(2))
    m = re.search(r"true_tasks_atomic_composite / reference_learnability: sign-rate=([0-9.]+), mean-rho=([-0-9.]+)", text)
    if m:
        out["h1_true_learnability_sign_rate"] = float(m.group(1)); out["h1_true_learnability_mean_rho"] = float(m.group(2))
    m = re.search(r"true_tasks_atomic_composite / frequency: sign-rate=([0-9.]+), mean-rho=([-0-9.]+)", text)
    if m:
        out["h1_true_frequency_sign_rate"] = float(m.group(1)); out["h1_true_frequency_mean_rho"] = float(m.group(2))
    return out


def parse_h2(path: Path) -> dict:
    text = safe_read(path)
    out = {"h2_report": str(path) if path.exists() else "", "h2_available": path.exists()}
    if not text:
        return out
    m = re.search(r"atomic acquisition rate: `?([0-9.]+)`?", text)
    if m:
        out["h2_atomic_acq_rate"] = float(m.group(1))
    m = re.search(r"composite acquisition rate: `?([0-9.]+)`?", text)
    if m:
        out["h2_composite_acq_rate"] = float(m.group(1))
    m = re.search(r"mean residual log-time: `?([-0-9.]+)`?", text)
    if m:
        out["h2_mean_composite_residual_log_time"] = float(m.group(1))
    m = re.search(r"positive residual rate: `?([0-9.]+)`?", text)
    if m:
        out["h2_positive_residual_rate"] = float(m.group(1))
    return out


def safe_read(path: Path) -> str:
    try:
        if path.exists():
            return path.read_text(encoding="utf-8")
    except Exception:
        pass
    return ""


def make_report(summary: pd.DataFrame, h3: pd.DataFrame) -> str:
    n = len(summary)
    h1_n = int(summary.get("h1_available", pd.Series(dtype=bool)).fillna(False).sum()) if n else 0
    h2_n = int(summary.get("h2_available", pd.Series(dtype=bool)).fillna(False).sum()) if n else 0
    pos = int(summary.get("h3_positive_exact_pairs", pd.Series(dtype=int)).fillna(0).sum()) if n else 0
    tested = int(summary.get("h3_pairs_tested", pd.Series(dtype=int)).fillna(0).sum()) if n else 0
    lines = [
        "# B1 Cross-Family Synthesis",
        "",
        "This report aggregates B1 evidence across generated families. It is intended to determine which claims replicate beyond the first family.",
        "",
        f"- families listed: `{n}`",
        f"- families with H1 reports: `{h1_n}`",
        f"- families with H2 reports: `{h2_n}`",
        f"- H3 pairs tested across families: `{tested}`",
        f"- positive exact-component H3 pairs: `{pos}`",
        "",
        "## Interpretation rule",
        "",
        "A cross-family claim requires the same qualitative pattern in at least two independently generated B1 families. A single-family result remains pair-specific pilot evidence.",
    ]
    if n:
        lines += ["", "## Family summary", "", summary.to_markdown(index=False)]
    if not h3.empty:
        cols = [c for c in ["family_id", "component", "composite", "verdict", "primary_signal", "scope"] if c in h3.columns]
        lines += ["", "## H3 pair summary", "", h3[cols].to_markdown(index=False)]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
