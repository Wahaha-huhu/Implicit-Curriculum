from __future__ import annotations

import argparse
import csv
from pathlib import Path

from ic_experiments.run_management import append_registry, write_manifest


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def main() -> None:
    p = argparse.ArgumentParser(description="Write a prioritized plan for high-value experiments before thesis drafting.")
    p.add_argument("--output-dir", default="results/high_value_experiment_plan_v34")
    p.add_argument("--code-version", default="v3.4")
    p.add_argument("--archive-root", default="results/archive")
    p.add_argument("--thesis-use", default="candidate")
    args = p.parse_args()
    out = Path(args.output_dir); out.mkdir(parents=True, exist_ok=True)

    rows = [
        {"priority": 1, "experiment": "B2 sparse-parity strengthening", "goal": "Make the frequency/quanta contrast credible", "status_target": "GREEN if nontrivial coverage and plausible frequency/degree signs", "compute": "moderate GPU/CPU"},
        {"priority": 2, "experiment": "Focused Pythia arithmetic residual suite", "goal": "Stress-test the strongest Pythia residual family", "status_target": "GREEN if arithmetic underperformance persists through 70M-1.4B", "compute": "reuse Pythia sweep runner"},
        {"priority": 3, "experiment": "Stronger mediator diagnostics", "goal": "Deepen mechanism for A02->C06 beyond global gradient cosine", "status_target": "GREEN if layer/parameter-block gradients separate positive from controls", "compute": "moderate"},
        {"priority": 4, "experiment": "Third B1 H3-ready family", "goal": "Test whether localized exact dependency recurs", "status_target": "GREEN if another exact-component H3 positive pair appears", "compute": "high"},
    ]
    with (out / "high_value_experiment_plan.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader(); writer.writerows(rows)

    readme = """
# High-value experiment plan before thesis drafting

The core thesis is already draft-ready, but these experiments provide stronger justification before writing.

## Priority 1 — B2 sparse-parity strengthening
Purpose: provide a clean frequency/quanta-style contrast. B2 is not a dependency test; it is a regime contrast.

## Priority 2 — Focused Pythia arithmetic residual suite
Purpose: stress-test the strongest Pythia observation: arithmetic composite underperformance relative to primitive-predictor expectations.

## Priority 3 — Stronger mediator diagnostics
Purpose: deepen the mechanism around the controlled positive pair A02_substitute -> C06.

## Priority 4 — Third B1 H3-ready family
Purpose: strongest but most expensive controlled replication of localized exact dependency.

Recommended order: run B2 strengthening and focused Pythia arithmetic first. Then decide whether to spend more compute on mediator diagnostics or a third B1 family.
"""
    _write(out / "HIGH_VALUE_EXPERIMENT_PLAN.md", readme)

    b2_script = """#!/usr/bin/env bash
set -euo pipefail

PYTHONPATH=src python -m ic_experiments.experiments.run_sparse_parity_pilot \
  --output-dir results/b2_sparse_parity_strengthened_v34 \
  --family-seed 0 \
  --seeds 0 1 2 3 4 5 6 7 8 9 \
  --n-bits 40 \
  --n-tasks 36 \
  --degrees 1 2 3 \
  --frequency-mode zipf \
  --zipf-alpha 1.1 \
  --max-data-seen 1000000 \
  --checkpoint-every 10000 \
  --batch-size 1024 \
  --learning-rate 0.002 \
  --hidden-dim 512 \
  --depth 3 \
  --eval-examples-per-task 4096 \
  --device cuda

PYTHONPATH=src python -m ic_experiments.experiments.analyze_sparse_parity_pilot \
  --result-dir results/b2_sparse_parity_strengthened_v34 \
  --thresholds 0.65 0.75 0.85 0.90 \
  --metric balanced_accuracy \
  --patience 2

PYTHONPATH=src python -m ic_experiments.experiments.analyze_b2_strengthening_synthesis \
  --run-dirs results/b2_sparse_parity_strengthened_v34 \
  --output-dir results/b2_strengthening_synthesis_v34 \
  --code-version v3.4 \
  --archive-root results/archive \
  --thesis-use candidate
"""
    _write(out / "run_b2_strengthening_v34.sh", b2_script)
    (out / "run_b2_strengthening_v34.sh").chmod(0o755)

    pythia_script = """#!/usr/bin/env bash
set -euo pipefail

PYTHONPATH=src python -m ic_experiments.experiments.make_pythia_focused_arithmetic_slice_suite \
  --output-dir results/pythia_arithmetic_slice_suite_v34 \
  --n-per-slice 64 \
  --code-version v3.4 \
  --archive-root results/archive \
  --thesis-use diagnostic

PYTHONPATH=src python -m ic_experiments.experiments.make_pythia_sweep_plan \
  --slice-table results/pythia_arithmetic_slice_suite_v34/pythia_slice_table.csv \
  --examples results/pythia_arithmetic_slice_suite_v34/pythia_slice_examples.jsonl \
  --output-dir results/pythia_arithmetic_sweep_plan_v34 \
  --run-root results/pythia_arithmetic_model_sweep_v34 \
  --models EleutherAI/pythia-70m EleutherAI/pythia-160m EleutherAI/pythia-410m EleutherAI/pythia-1b EleutherAI/pythia-1.4b \
  --revisions step0 step1000 step10000 step143000 \
  --max-examples-per-slice 64 \
  --device cuda \
  --code-version v3.4 \
  --archive-root results/archive \
  --thesis-use diagnostic

bash results/pythia_arithmetic_sweep_plan_v34/recommended_pythia_sweep_commands.sh

PYTHONPATH=src python -m ic_experiments.experiments.analyze_pythia_sweep_synthesis \
  --run-dirs \
    results/pythia_arithmetic_model_sweep_v34/pythia-70m_n64 \
    results/pythia_arithmetic_model_sweep_v34/pythia-160m_n64 \
    results/pythia_arithmetic_model_sweep_v34/pythia-410m_n64 \
    results/pythia_arithmetic_model_sweep_v34/pythia-1b_n64 \
    results/pythia_arithmetic_model_sweep_v34/pythia-1.4b_n64 \
  --output-dir results/pythia_arithmetic_sweep_synthesis_v34 \
  --code-version v3.4 \
  --archive-root results/archive \
  --thesis-use candidate
"""
    _write(out / "run_pythia_arithmetic_sweep_v34.sh", pythia_script)
    (out / "run_pythia_arithmetic_sweep_v34.sh").chmod(0o755)

    manifest = write_manifest(out, experiment="High_value_experiment_plan", backend="meta", code_version=args.code_version, input_paths={}, extra={"thesis_use": args.thesis_use})
    append_registry(Path(args.archive_root) / "results_registry.csv", {"run_id": manifest["run_id"], "code_version": args.code_version, "experiment": manifest["experiment"], "backend": manifest["backend"], "output_path": str(out), "status": "created", "thesis_use": args.thesis_use, "created_at_utc": manifest["created_at_utc"]})
    print(f"Wrote high-value experiment plan to {out}")


if __name__ == "__main__":
    main()
