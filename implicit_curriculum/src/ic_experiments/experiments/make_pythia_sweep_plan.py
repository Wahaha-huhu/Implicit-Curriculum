from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from typing import Any

from ic_experiments.run_management import append_registry, write_manifest


def _slug(s: str) -> str:
    s = re.sub(r"^EleutherAI/", "", s)
    s = re.sub(r"[^A-Za-z0-9_.-]+", "_", s)
    return s.strip("_") or "model"


def _sh_quote(s: str) -> str:
    return "'" + s.replace("'", "'\\''") + "'"


def _command(parts: list[str]) -> str:
    return " \\\n  ".join(parts)


def main() -> None:
    p = argparse.ArgumentParser(description="Create a Pythia observational model/config sweep plan.")
    p.add_argument("--slice-table", required=True)
    p.add_argument("--examples", required=True)
    p.add_argument("--output-dir", default="results/pythia_sweep_plan_v30")
    p.add_argument("--run-root", default="results/pythia_model_sweep_v30")
    p.add_argument("--models", nargs="+", default=["EleutherAI/pythia-70m", "EleutherAI/pythia-160m"], help="HF model names to evaluate.")
    p.add_argument("--revisions", nargs="+", default=["step0", "step1000", "step10000", "step143000"], help="Revisions/checkpoints shared by all models.")
    p.add_argument("--max-examples-per-slice", nargs="+", type=int, default=[64], help="One or more evaluation budgets.")
    p.add_argument("--device", default="cuda")
    p.add_argument("--metrics", nargs="*", default=None, help="Optional metrics for continuous analysis/refinement.")
    p.add_argument("--code-version", default="v3.0")
    p.add_argument("--archive-root", default="results/archive")
    p.add_argument("--thesis-use", default="diagnostic")
    args = p.parse_args()

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    run_root = Path(args.run_root)

    rows: list[dict[str, Any]] = []
    script_lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        "# Auto-generated Pythia observational model/config sweep.",
        "# Run section-by-section if you want to inspect each model before continuing.",
        "",
    ]
    for model in args.models:
        for n_ex in args.max_examples_per_slice:
            sweep_id = f"{_slug(model)}_n{n_ex}"
            result_dir = run_root / sweep_id
            run_cmd = _command([
                "PYTHONPATH=src python -m ic_experiments.experiments.run_pythia_observational_pilot",
                f"--slice-table {_sh_quote(args.slice_table)}",
                f"--examples {_sh_quote(args.examples)}",
                f"--output-dir {_sh_quote(str(result_dir))}",
                f"--model-name {_sh_quote(model)}",
                "--revisions " + " ".join(_sh_quote(r) for r in args.revisions),
                f"--max-examples-per-slice {n_ex}",
                f"--device {_sh_quote(args.device)}",
                f"--code-version {_sh_quote(args.code_version)}",
                f"--archive-root {_sh_quote(args.archive_root)}",
                f"--thesis-use {_sh_quote(args.thesis_use)}",
            ])
            readiness_cmd = _command([
                "PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_h2_readiness",
                f"--result-dir {_sh_quote(str(result_dir))}",
                f"--code-version {_sh_quote(args.code_version)}",
                f"--archive-root {_sh_quote(args.archive_root)}",
                f"--thesis-use {_sh_quote(args.thesis_use)}",
            ])
            metrics_part = "" if not args.metrics else " \\\n  --metrics " + " ".join(_sh_quote(m) for m in args.metrics)
            continuous_cmd = _command([
                "PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_continuous_scores",
                f"--result-dir {_sh_quote(str(result_dir))}" + metrics_part,
                f"--code-version {_sh_quote(args.code_version)}",
                f"--archive-root {_sh_quote(args.archive_root)}",
                f"--thesis-use {_sh_quote(args.thesis_use)}",
            ])
            refine_cmd = _command([
                "PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_residual_refinement",
                f"--result-dir {_sh_quote(str(result_dir))}" + metrics_part,
                f"--code-version {_sh_quote(args.code_version)}",
                f"--archive-root {_sh_quote(args.archive_root)}",
                f"--thesis-use {_sh_quote(args.thesis_use)}",
            ])
            rows.append({
                "sweep_id": sweep_id,
                "model_name": model,
                "revisions": ";".join(args.revisions),
                "max_examples_per_slice": n_ex,
                "result_dir": str(result_dir),
                "run_command": run_cmd,
                "readiness_command": readiness_cmd,
                "continuous_command": continuous_cmd,
                "residual_refinement_command": refine_cmd,
            })
            script_lines += [
                f"echo '=== Running {sweep_id} ==='",
                run_cmd,
                "",
                f"echo '=== H2 readiness {sweep_id} ==='",
                readiness_cmd,
                "",
                f"echo '=== Continuous analysis {sweep_id} ==='",
                continuous_cmd,
                "",
                f"echo '=== Residual refinement {sweep_id} ==='",
                refine_cmd,
                "",
            ]

    plan_path = out / "pythia_sweep_plan.csv"
    with plan_path.open("w", newline="", encoding="utf-8") as f:
        fieldnames = ["sweep_id", "model_name", "revisions", "max_examples_per_slice", "result_dir", "run_command", "readiness_command", "continuous_command", "residual_refinement_command"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    script_path = out / "recommended_pythia_sweep_commands.sh"
    script_path.write_text("\n".join(script_lines) + "\n", encoding="utf-8")
    script_path.chmod(0o755)

    report = [
        "# Pythia observational model/config sweep plan",
        "",
        "This plan evaluates the same H2-ready slice suite across Pythia-like model sizes and/or evaluation budgets. It remains observational and cannot establish causal dependency.",
        "",
        f"- slice_table: `{args.slice_table}`",
        f"- examples: `{args.examples}`",
        f"- models: `{', '.join(args.models)}`",
        f"- revisions: `{', '.join(args.revisions)}`",
        f"- max_examples_per_slice: `{', '.join(map(str, args.max_examples_per_slice))}`",
        f"- planned runs: `{len(rows)}`",
        "",
        "## Planned runs",
    ]
    for r in rows:
        report.append(f"- `{r['sweep_id']}`: model=`{r['model_name']}`, n_examples_per_slice=`{r['max_examples_per_slice']}`, output=`{r['result_dir']}`")
    report += [
        "",
        "## Interpretation rule",
        "A Pythia residual pattern becomes more thesis-useful if it persists across model size, checkpoint density, or evaluation budget. It remains observational unless pretraining or finetuning interventions are added.",
    ]
    (out / "PYTHIA_SWEEP_PLAN.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    manifest = write_manifest(
        out,
        experiment="Pythia_observational_sweep_plan",
        backend="Pythia_observational",
        code_version=args.code_version,
        input_paths={"slice_table": args.slice_table, "examples": args.examples},
        extra={"models": args.models, "revisions": args.revisions, "max_examples_per_slice": args.max_examples_per_slice, "thesis_use": args.thesis_use},
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
    print(f"Wrote Pythia sweep plan to {out}")


if __name__ == "__main__":
    main()
