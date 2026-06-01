from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from ic_experiments.run_management import append_registry, write_manifest


def _read_csv(path: Path) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def _fmt(x) -> str:
    try:
        if pd.isna(x):
            return "nan"
        return f"{float(x):.3f}"
    except Exception:
        return str(x)


def main() -> None:
    p = argparse.ArgumentParser(description="Synthesize one or more strengthened B2 sparse-parity runs.")
    p.add_argument("--run-dirs", nargs="+", required=True)
    p.add_argument("--output-dir", default="results/b2_strengthening_synthesis_v34")
    p.add_argument("--code-version", default="v3.4")
    p.add_argument("--archive-root", default="results/archive")
    p.add_argument("--thesis-use", default="candidate")
    args = p.parse_args()

    out = Path(args.output_dir); out.mkdir(parents=True, exist_ok=True)
    rows = []
    degree_rows = []
    for rd in args.run_dirs:
        rdir = Path(rd)
        summ = _read_csv(rdir / "sparse_parity_ordering_summary.csv")
        deg = _read_csv(rdir / "sparse_parity_degree_summary.csv")
        for _, row in summ.iterrows():
            d = row.to_dict(); d["run_dir"] = str(rdir); rows.append(d)
        if len(deg):
            deg = deg.copy(); deg["run_dir"] = str(rdir); degree_rows.extend(deg.to_dict(orient="records"))
    summary = pd.DataFrame(rows)
    degree = pd.DataFrame(degree_rows)
    summary.to_csv(out / "b2_strengthening_summary.csv", index=False)
    degree.to_csv(out / "b2_strengthening_degree_summary.csv", index=False)

    lines = [
        "# B2 sparse-parity strengthening synthesis",
        "",
        "This synthesis summarizes B2 sparse-parity runs used as a frequency/quanta-style contrast to B1 compositional sequence learning.",
        "",
        f"- runs included: `{len(args.run_dirs)}`",
    ]
    if len(summary):
        lines += ["", "## Threshold-level summary", ""]
        for row in summary.sort_values(["run_dir", "threshold"]).to_dict(orient="records"):
            lines.append(
                f"- `{row.get('run_dir')}` threshold `{row.get('threshold')}`: "
                f"acq={_fmt(row.get('acquisition_rate'))}, "
                f"time-rho(freq)={_fmt(row.get('time_spearman_frequency'))}, "
                f"time-rho(degree)={_fmt(row.get('time_spearman_degree'))}, "
                f"final-rho(freq)={_fmt(row.get('final_spearman_frequency'))}, "
                f"final-rho(degree)={_fmt(row.get('final_spearman_degree'))}"
            )
        best = summary.copy()
        best["acquisition_rate_num"] = pd.to_numeric(best.get("acquisition_rate"), errors="coerce")
        if best["acquisition_rate_num"].notna().any():
            b = best.sort_values("acquisition_rate_num", ascending=False).iloc[0]
            lines += ["", "## Decision aid", "", f"Best acquisition coverage: run `{b.get('run_dir')}`, threshold `{b.get('threshold')}`, acquisition_rate={_fmt(b.get('acquisition_rate'))}."]
    else:
        lines += ["", "No sparse parity summaries found. Run analyze_sparse_parity_pilot first."]
    lines += ["", "## Claim boundary", "B2 supports a regime contrast only if it has nontrivial acquisition coverage and frequency/degree effects behave plausibly. It is not a dependency/intervention test."]
    (out / "B2_STRENGTHENING_SYNTHESIS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    manifest = write_manifest(out, experiment="B2_strengthening_synthesis", backend="B2_sparse_parity", code_version=args.code_version, input_paths={"run_dirs": args.run_dirs}, extra={"thesis_use": args.thesis_use})
    append_registry(Path(args.archive_root) / "results_registry.csv", {"run_id": manifest["run_id"], "code_version": args.code_version, "experiment": manifest["experiment"], "backend": manifest["backend"], "output_path": str(out), "status": "created", "thesis_use": args.thesis_use, "created_at_utc": manifest["created_at_utc"]})
    print(f"Wrote B2 strengthening synthesis to {out}")


if __name__ == "__main__":
    main()
