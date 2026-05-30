from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from ic_experiments.design import DesignCriteria, PropertyDesignConfig
from ic_experiments.recovery import RecoveryConfig, run_recovery_suite


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run simulated recovery and decorrelated-design gate.")
    parser.add_argument("--output-dir", type=Path, default=Path("results/recovery_gate"))
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--n-atomic", type=int, default=12)
    parser.add_argument("--n-composite", type=int, default=8)
    parser.add_argument("--n-replicates", type=int, default=30)
    parser.add_argument("--noise-sd", type=float, default=0.18)
    parser.add_argument("--dependency-delay", type=float, default=0.55)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--max-vif", type=float, default=5.0)
    parser.add_argument("--max-abs-pearson", type=float, default=0.65)
    parser.add_argument("--max-abs-spearman", type=float, default=0.70)
    parser.add_argument("--max-condition-number", type=float, default=50.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    criteria = DesignCriteria(
        max_vif=args.max_vif,
        max_abs_pearson=args.max_abs_pearson,
        max_abs_spearman=args.max_abs_spearman,
        max_condition_number=args.max_condition_number,
        min_rows=args.n_atomic + args.n_composite,
    )
    property_design = PropertyDesignConfig(
        n_atomic=args.n_atomic,
        n_composite=args.n_composite,
        seed=args.seed,
        criteria=criteria,
    )
    config = RecoveryConfig(
        seed=args.seed,
        n_replicates=args.n_replicates,
        noise_sd=args.noise_sd,
        dependency_delay=args.dependency_delay,
        n_folds=args.n_folds,
        property_design=property_design,
    )
    outputs = run_recovery_suite(config)

    paths: dict[str, str] = {}
    for name, value in outputs.items():
        if isinstance(value, pd.DataFrame):
            path = args.output_dir / f"{name}.csv"
            value.to_csv(path, index=False)
            paths[name] = str(path)
    summary = {
        "config": {
            "recovery": asdict(config),
            "property_design": asdict(property_design),
            "criteria": asdict(criteria),
        },
        "design_diagnostics": outputs["design_diagnostics"],
        "paths": paths,
    }
    summary_path = args.output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    paths["summary"] = str(summary_path)

    # A compact markdown report for fast human inspection.
    verdict = outputs["verdict"]
    lines = [
        "# Simulated recovery gate report",
        "",
        "This gate checks whether the analysis pipeline can recover known synthetic worlds before expensive neural training.",
        "",
        "## Design diagnostics",
        "",
    ]
    for key, value in outputs["design_diagnostics"].items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## Recovery verdict", "", _df_to_markdown(verdict), ""])
    (args.output_dir / "recovery_report.md").write_text("\n".join(lines), encoding="utf-8")

    print("Saved recovery-gate outputs:")
    for key, path in paths.items():
        print(f"  {key}: {path}")
    print(f"  report: {args.output_dir / 'recovery_report.md'}")


def _df_to_markdown(df: pd.DataFrame) -> str:
    if df.empty:
        return "(empty)"
    cols = list(df.columns)
    header = "| " + " | ".join(cols) + " |"
    sep = "| " + " | ".join(["---"] * len(cols)) + " |"
    rows = []
    for _, row in df.iterrows():
        vals = []
        for col in cols:
            value = row[col]
            if isinstance(value, float):
                vals.append(f"{value:.4g}")
            else:
                vals.append(str(value))
        rows.append("| " + " | ".join(vals) + " |")
    return "\n".join([header, sep] + rows)


if __name__ == "__main__":
    main()
