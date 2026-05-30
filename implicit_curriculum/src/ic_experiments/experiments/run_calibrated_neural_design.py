from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from ic_experiments.calibration import (
    CalibrationCriteria,
    acquisition_summary_from_times,
    choose_component_and_controls_from_calibration,
    family_calibration_summary,
    save_calibration_report,
)
from ic_experiments.configs import InterventionConfig, TrainingConfig
from ic_experiments.design import DesignCriteria
from ic_experiments.neural_design import NeuralDesignConfig, generate_neural_task_family, save_neural_family
from ic_experiments.train import run_single_training, save_pilot_outputs


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate neural task families and select one that passes design and acquisition-coverage calibration.")
    p.add_argument("--output-dir", type=Path, default=Path("results/calibrated_neural_design"))
    p.add_argument("--candidate-seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    p.add_argument("--calibration-seeds", type=int, nargs="+", default=[0, 1])
    p.add_argument("--n-atomic", type=int, default=12)
    p.add_argument("--n-composite", type=int, default=10)
    p.add_argument("--n-shortcut-controls", type=int, default=4)
    p.add_argument("--n-surface-controls", type=int, default=4)
    p.add_argument("--n-unrelated-controls", type=int, default=4)
    p.add_argument("--n-bits", type=int, default=48)
    p.add_argument("--max-attempts", type=int, default=10000)
    p.add_argument("--frequency-low", type=float, default=0.01)
    p.add_argument("--frequency-high", type=float, default=0.18)
    p.add_argument("--max-data-seen", type=int, default=120000)
    p.add_argument("--checkpoint-every", type=int, default=2000)
    p.add_argument("--batch-size", type=int, default=512)
    p.add_argument("--learning-rate", type=float, default=2e-3)
    p.add_argument("--hidden-dim", type=int, default=256)
    p.add_argument("--depth", type=int, default=2)
    p.add_argument("--weight-decay", type=float, default=0.0)
    p.add_argument("--eval-examples-per-task", type=int, default=2048)
    p.add_argument("--acquisition-threshold", type=float, default=0.90)
    p.add_argument("--acquisition-patience", type=int, default=2)
    p.add_argument("--device", type=str, default="cpu")
    p.add_argument("--model", type=str, default="mlp")
    p.add_argument("--target-min-mean-acq-rate", type=float, default=0.45)
    p.add_argument("--target-max-mean-acq-rate", type=float, default=0.85)
    p.add_argument("--min-usable-composites", type=int, default=3)
    p.add_argument("--usable-composite-min-rate", type=float, default=0.30)
    p.add_argument("--usable-composite-max-rate", type=float, default=0.95)
    p.add_argument("--keep-all-candidate-runs", action="store_true", help="Keep full candidate eval/acquisition outputs instead of only summaries.")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    criteria = CalibrationCriteria(
        target_min_mean_acquisition_rate=args.target_min_mean_acq_rate,
        target_max_mean_acquisition_rate=args.target_max_mean_acq_rate,
        min_usable_composites_for_component=args.min_usable_composites,
        usable_composite_min_rate=args.usable_composite_min_rate,
        usable_composite_max_rate=args.usable_composite_max_rate,
    )

    candidate_rows = []
    selected_payload: dict | None = None
    best_payload: dict | None = None
    best_score = float("-inf")

    for candidate_seed in args.candidate_seeds:
        family = generate_neural_task_family(
            NeuralDesignConfig(
                n_atomic=args.n_atomic,
                n_composite=args.n_composite,
                n_shortcut_controls=args.n_shortcut_controls,
                n_surface_controls=args.n_surface_controls,
                n_unrelated_controls=args.n_unrelated_controls,
                n_bits=args.n_bits,
                frequency_low=args.frequency_low,
                frequency_high=args.frequency_high,
                seed=candidate_seed,
                max_attempts=args.max_attempts,
                criteria=DesignCriteria(min_rows=args.n_atomic + args.n_composite + args.n_shortcut_controls + args.n_surface_controls + args.n_unrelated_controls),
            )
        )
        candidate_dir = args.output_dir / f"candidate_seed_{candidate_seed}"
        save_neural_family(family, candidate_dir)
        if not family.passed:
            row = {"candidate_seed": candidate_seed, "design_passed": False, "passed": False, "reason": "design_failed"}
            candidate_rows.append(row)
            continue

        outputs = []
        for seed in args.calibration_seeds:
            cfg = TrainingConfig(
                seed=seed,
                n_bits=args.n_bits,
                batch_size=args.batch_size,
                max_data_seen=args.max_data_seen,
                checkpoint_every=args.checkpoint_every,
                learning_rate=args.learning_rate,
                weight_decay=args.weight_decay,
                hidden_dim=args.hidden_dim,
                depth=args.depth,
                eval_examples_per_task=args.eval_examples_per_task,
                acquisition_threshold=args.acquisition_threshold,
                acquisition_patience=args.acquisition_patience,
                grad_stats_every=0,
                cka_examples=128,
                device=args.device,
                output_dir=candidate_dir,
            )
            print(f"Calibrating candidate_seed={candidate_seed} training_seed={seed}")
            outputs.append(run_single_training(family.tasks, cfg, InterventionConfig(name="baseline", kind="none"), model_name=args.model))

        paths = save_pilot_outputs(
            outputs,
            family.tasks,
            candidate_dir,
            extra_metadata={"candidate_seed": candidate_seed, "calibration_seeds": args.calibration_seeds, "calibration_criteria": criteria.to_dict()},
        )
        acq = pd.read_csv(paths["acquisition_times"])
        structure = pd.read_csv(paths["structure_table"])
        acq_summary = acquisition_summary_from_times(acq, structure)
        acq_summary.to_csv(candidate_dir / "calibration_acquisition_summary.csv", index=False)
        chosen = choose_component_and_controls_from_calibration(family.tasks, acq_summary, criteria)
        summary = family_calibration_summary(family.tasks, acq_summary, criteria)
        summary["candidate_seed"] = int(candidate_seed)
        row = {
            "candidate_seed": candidate_seed,
            "design_passed": True,
            **summary,
        }
        candidate_rows.append(row)
        score = float(summary.get("mean_acquisition_rate", 0.0)) + 0.25 * float(summary.get("n_usable_composites", 0))
        payload = {"family": family, "candidate_dir": candidate_dir, "acq_summary": acq_summary, "chosen": chosen, "summary": summary, "paths": paths}
        if score > best_score:
            best_score = score
            best_payload = payload
        if bool(summary.get("passed", False)) and selected_payload is None:
            selected_payload = payload
            if not args.keep_all_candidate_runs:
                # We can stop early once a candidate passes, because the gate is
                # meant to find a usable design rather than optimize scientifically.
                break

    candidate_table = pd.DataFrame(candidate_rows)
    candidate_table.to_csv(args.output_dir / "candidate_calibration_summary.csv", index=False)
    payload = selected_payload or best_payload
    if payload is None:
        raise SystemExit("No design-passing candidates were available.")

    selected_dir = args.output_dir / "selected_family"
    selected_dir.mkdir(parents=True, exist_ok=True)
    save_neural_family(payload["family"], selected_dir)
    payload["acq_summary"].to_csv(selected_dir / "calibration_acquisition_summary.csv", index=False)
    (selected_dir / "chosen_component_and_controls.json").write_text(json.dumps(payload["chosen"], indent=2), encoding="utf-8")

    # Convenience copies at the output root for subsequent commands.
    pd.read_csv(selected_dir / "structure_table.csv").to_csv(args.output_dir / "structure_table.csv", index=False)
    pd.read_csv(selected_dir / "design_diagnostics.csv").to_csv(args.output_dir / "design_diagnostics.csv", index=False)
    payload["acq_summary"].to_csv(args.output_dir / "calibration_acquisition_summary.csv", index=False)
    (args.output_dir / "chosen_component_and_controls.json").write_text(json.dumps(payload["chosen"], indent=2), encoding="utf-8")

    selected_summary = {
        "selected_candidate_seed": int(payload["summary"].get("candidate_seed", -1)) if "candidate_seed" in payload["summary"] else None,
        "selected_passed": bool(payload["summary"].get("passed", False)),
        "selected_summary": payload["summary"],
        "chosen_component_and_controls": payload["chosen"],
        "criteria": criteria.to_dict(),
        "args": {k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()},
    }
    (args.output_dir / "summary.json").write_text(json.dumps(selected_summary, indent=2), encoding="utf-8")
    save_calibration_report(args.output_dir, candidate_table, {**payload["summary"], **payload["chosen"]}, criteria)

    print("Saved calibrated design outputs:")
    for name in ["structure_table.csv", "design_diagnostics.csv", "calibration_acquisition_summary.csv", "chosen_component_and_controls.json", "candidate_calibration_summary.csv", "calibrated_neural_design_report.md"]:
        print(f"  {name}: {args.output_dir / name}")
    if not bool(payload["summary"].get("passed", False)):
        print("WARNING: no candidate fully passed calibration; selected best available family for diagnosis.")


if __name__ == "__main__":
    main()
