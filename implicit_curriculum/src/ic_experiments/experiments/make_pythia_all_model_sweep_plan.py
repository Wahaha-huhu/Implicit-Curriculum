"""Generate tiered Pythia all-model observational sweep plans.

This helper wraps the existing Pythia observational runner/analyzers into a
set of tiered scripts. It is intentionally conservative: large models are
planned as smoke runs by default and can be promoted to full runs after they
succeed.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import shlex
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd


@dataclass(frozen=True)
class Tier:
    tier_id: str
    models: list[str]
    revisions: list[str]
    max_examples_per_slice: int
    device: str
    note: str


def _quote(x: str) -> str:
    return shlex.quote(str(x))


def _safe_model_id(model: str) -> str:
    return model.split("/")[-1].replace(".", "p")


def _run_dir(run_root: Path, model: str, max_examples: int) -> Path:
    return run_root / f"{_safe_model_id(model)}_n{max_examples}"


def _cmd(parts: Iterable[str]) -> str:
    return " ".join(_quote(p) for p in parts)


def _write_script(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    path.chmod(0o755)


def _git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--slice-table", required=True)
    p.add_argument("--examples", required=True)
    p.add_argument("--output-dir", default="results/pythia_all_model_sweep_plan_v32")
    p.add_argument("--run-root", default="results/pythia_model_sweep_v32")
    p.add_argument("--device", default="cuda")
    p.add_argument("--code-version", default="v3.2")
    p.add_argument("--archive-root", default="results/archive")
    p.add_argument("--thesis-use", default="diagnostic")

    p.add_argument(
        "--small-full-models",
        nargs="*",
        default=["EleutherAI/pythia-1b", "EleutherAI/pythia-1.4b"],
        help="Models to run at n=64 on a 4090/A100 after smoke succeeds.",
    )
    p.add_argument(
        "--large-smoke-models",
        nargs="*",
        default=["EleutherAI/pythia-2.8b", "EleutherAI/pythia-6.9b", "EleutherAI/pythia-12b"],
        help="Large models to run as n=16 smoke, usually on A100.",
    )
    p.add_argument(
        "--small-full-revisions",
        nargs="*",
        default=["step0", "step1000", "step10000", "step143000"],
    )
    p.add_argument(
        "--large-smoke-revisions",
        nargs="*",
        default=["step0", "step10000", "step143000"],
    )
    p.add_argument("--small-full-examples", type=int, default=64)
    p.add_argument("--large-smoke-examples", type=int, default=16)
    p.add_argument(
        "--existing-run-dirs",
        nargs="*",
        default=[
            "results/pythia_model_sweep_v30/pythia-70m_n64",
            "results/pythia_model_sweep_v30/pythia-160m_n64",
            "results/pythia_model_sweep_v31_410m/pythia-410m_n64",
            "results/pythia_model_sweep_v31_mid_smoke/pythia-1b_n16",
            "results/pythia_model_sweep_v31_mid_smoke/pythia-1.4b_n16",
        ],
        help="Already completed run directories to include in the all-scale synthesis script.",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    run_root = Path(args.run_root)
    run_root.mkdir(parents=True, exist_ok=True)

    tiers = [
        Tier(
            tier_id="mid_full_n64",
            models=list(args.small_full_models),
            revisions=list(args.small_full_revisions),
            max_examples_per_slice=args.small_full_examples,
            device=args.device,
            note="Upgrade 1B/1.4B from smoke to full n=64 evaluation.",
        ),
        Tier(
            tier_id="large_smoke_n16",
            models=list(args.large_smoke_models),
            revisions=list(args.large_smoke_revisions),
            max_examples_per_slice=args.large_smoke_examples,
            device=args.device,
            note="A100-preferred large-model smoke run before full evaluation.",
        ),
    ]

    rows: list[dict] = []
    for tier in tiers:
        for model in tier.models:
            rd = _run_dir(run_root, model, tier.max_examples_per_slice)
            rows.append(
                {
                    "tier_id": tier.tier_id,
                    "model": model,
                    "run_dir": str(rd),
                    "max_examples_per_slice": tier.max_examples_per_slice,
                    "revisions": " ".join(tier.revisions),
                    "device": tier.device,
                    "note": tier.note,
                }
            )

    plan = pd.DataFrame(rows)
    plan.to_csv(out / "pythia_all_model_sweep_plan.csv", index=False)

    # Per-tier scripts.
    tier_script_paths: list[Path] = []
    for tier in tiers:
        script = out / f"run_{tier.tier_id}.sh"
        tier_script_paths.append(script)
        lines = ["#!/usr/bin/env bash", "set -euo pipefail", ""]
        for model in tier.models:
            rd = _run_dir(run_root, model, tier.max_examples_per_slice)
            lines += [
                f"echo '=== Running {model} ({tier.tier_id}) ==='",
                _cmd(
                    [
                        "PYTHONPATH=src",
                        "python",
                        "-m",
                        "ic_experiments.experiments.run_pythia_observational_pilot",
                        "--slice-table",
                        args.slice_table,
                        "--examples",
                        args.examples,
                        "--output-dir",
                        str(rd),
                        "--model-name",
                        model,
                        "--revisions",
                        *tier.revisions,
                        "--max-examples-per-slice",
                        str(tier.max_examples_per_slice),
                        "--device",
                        tier.device,
                        "--code-version",
                        args.code_version,
                        "--archive-root",
                        args.archive_root,
                        "--thesis-use",
                        args.thesis_use,
                    ]
                ).replace(_quote("PYTHONPATH=src") + " ", "PYTHONPATH=src "),
                _cmd(
                    [
                        "PYTHONPATH=src",
                        "python",
                        "-m",
                        "ic_experiments.experiments.analyze_pythia_h2_readiness",
                        "--result-dir",
                        str(rd),
                        "--code-version",
                        args.code_version,
                        "--archive-root",
                        args.archive_root,
                        "--thesis-use",
                        args.thesis_use,
                    ]
                ).replace(_quote("PYTHONPATH=src") + " ", "PYTHONPATH=src "),
                _cmd(
                    [
                        "PYTHONPATH=src",
                        "python",
                        "-m",
                        "ic_experiments.experiments.analyze_pythia_continuous_scores",
                        "--result-dir",
                        str(rd),
                        "--code-version",
                        args.code_version,
                        "--archive-root",
                        args.archive_root,
                        "--thesis-use",
                        args.thesis_use,
                    ]
                ).replace(_quote("PYTHONPATH=src") + " ", "PYTHONPATH=src "),
                _cmd(
                    [
                        "PYTHONPATH=src",
                        "python",
                        "-m",
                        "ic_experiments.experiments.analyze_pythia_residual_refinement",
                        "--result-dir",
                        str(rd),
                        "--code-version",
                        args.code_version,
                        "--archive-root",
                        args.archive_root,
                        "--thesis-use",
                        args.thesis_use,
                    ]
                ).replace(_quote("PYTHONPATH=src") + " ", "PYTHONPATH=src "),
                "",
            ]
        _write_script(script, lines)

    # Synthesis scripts.
    planned_mid_dirs = [str(_run_dir(run_root, m, args.small_full_examples)) for m in args.small_full_models]
    planned_large_dirs = [str(_run_dir(run_root, m, args.large_smoke_examples)) for m in args.large_smoke_models]
    all_dirs = list(args.existing_run_dirs) + planned_mid_dirs + planned_large_dirs

    synth_lines = ["#!/usr/bin/env bash", "set -euo pipefail", ""]
    synth_lines += [
        "echo '=== Synthesizing mid full n64 runs ==='",
        _cmd(
            [
                "PYTHONPATH=src",
                "python",
                "-m",
                "ic_experiments.experiments.analyze_pythia_sweep_synthesis",
                "--run-dirs",
                *planned_mid_dirs,
                "--output-dir",
                str(out / "synthesis_mid_full_n64"),
                "--code-version",
                args.code_version,
                "--archive-root",
                args.archive_root,
                "--thesis-use",
                args.thesis_use,
            ]
        ).replace(_quote("PYTHONPATH=src") + " ", "PYTHONPATH=src "),
        "",
        "echo '=== Synthesizing large smoke n16 runs ==='",
        _cmd(
            [
                "PYTHONPATH=src",
                "python",
                "-m",
                "ic_experiments.experiments.analyze_pythia_sweep_synthesis",
                "--run-dirs",
                *planned_large_dirs,
                "--output-dir",
                str(out / "synthesis_large_smoke_n16"),
                "--code-version",
                args.code_version,
                "--archive-root",
                args.archive_root,
                "--thesis-use",
                args.thesis_use,
            ]
        ).replace(_quote("PYTHONPATH=src") + " ", "PYTHONPATH=src "),
        "",
        "echo '=== Synthesizing all available/planned runs ==='",
        _cmd(
            [
                "PYTHONPATH=src",
                "python",
                "-m",
                "ic_experiments.experiments.analyze_pythia_sweep_synthesis",
                "--run-dirs",
                *all_dirs,
                "--output-dir",
                str(out / "synthesis_all_available"),
                "--code-version",
                args.code_version,
                "--archive-root",
                args.archive_root,
                "--thesis-use",
                args.thesis_use,
            ]
        ).replace(_quote("PYTHONPATH=src") + " ", "PYTHONPATH=src "),
    ]
    synth_script = out / "recommended_pythia_all_model_synthesis.sh"
    _write_script(synth_script, synth_lines)

    # Master script does not automatically run large smoke after mid full; user may run tiers manually.
    master_lines = ["#!/usr/bin/env bash", "set -euo pipefail", ""]
    master_lines += [f"echo 'Run tiers manually. Suggested order:'"]
    for script in tier_script_paths:
        master_lines.append(f"echo '  bash {script}'")
    master_lines.append(f"echo 'Then synthesize: bash {synth_script}'")
    _write_script(out / "recommended_order.sh", master_lines)

    report = f"""# Pythia all-model tiered sweep plan

This plan extends the existing 70M/160M/410M and 1B/1.4B smoke evidence toward a broader model-scale sweep. It remains observational: stable residuals across model scale strengthen the bridge result, but they do not establish causal dependency.

## Tier scripts

- `{tier_script_paths[0]}`: full n={args.small_full_examples} run for `{', '.join(args.small_full_models)}`.
- `{tier_script_paths[1]}`: large-model smoke n={args.large_smoke_examples} run for `{', '.join(args.large_smoke_models)}`.
- `{synth_script}`: synthesize mid-full, large-smoke, and all available runs.

## Suggested execution order

1. Run mid-full n=64 for 1B and 1.4B on the 4090 if feasible.
2. Synthesize all available runs to replace smoke evidence with full n=64 evidence for 1B/1.4B.
3. Move to A100 for the large-smoke tier: 2.8B, 6.9B, and 12B.
4. Only promote a large model to n=64 if its smoke run is H2-ready and residual refinement succeeds.

## Expected feedback files

For each synthesis directory, send:

- `PYTHIA_SWEEP_SYNTHESIS.md`
- `pythia_sweep_run_summary.csv`
- `pythia_sweep_residual_stability.csv`
- `pythia_sweep_family_stability.csv`

## Claim boundary

A stable residual across model/config sweeps is stronger observational evidence than a single-run residual, but it is still not causal evidence. Use it to motivate controlled follow-ups or more focused mechanistic probes, not to claim exact-component dependency in Pythia.
"""
    (out / "PYTHIA_ALL_MODEL_SWEEP_PLAN.md").write_text(report, encoding="utf-8")

    manifest = {
        "experiment": "Pythia_all_model_tiered_sweep_plan",
        "backend": "Pythia_observational",
        "code_version": args.code_version,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "git_sha": _git_sha(),
        "output_dir": str(out),
        "run_root": str(run_root),
        "slice_table": args.slice_table,
        "examples": args.examples,
        "n_planned_runs": len(plan),
        "tiers": [t.__dict__ for t in tiers],
        "thesis_use": args.thesis_use,
    }
    (out / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote Pythia all-model tiered sweep plan to {out}")


if __name__ == "__main__":
    main()
