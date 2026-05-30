from __future__ import annotations

import argparse
import json
from pathlib import Path

from ic_experiments.configs import InterventionConfig, TrainingConfig
from ic_experiments.neural_design import (
    NeuralDesignConfig,
    choose_default_component_and_controls,
    generate_neural_task_family,
    load_neural_family,
    save_neural_family,
)
from ic_experiments.train import run_single_training, save_pilot_outputs


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run a first H1-style ordering pilot on a generated neural task family.")
    p.add_argument("--output-dir", type=Path, default=Path("results/h1_ordering_pilot"))
    p.add_argument("--structure-table", type=Path, default=None, help="Optional structure_table.csv from run_neural_design_gate or run_calibrated_neural_design.")
    p.add_argument("--chosen-component-file", type=Path, default=None, help="Optional chosen_component_and_controls.json from run_calibrated_neural_design.")
    p.add_argument("--family-seed", type=int, default=0)
    p.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    p.add_argument("--conditions", type=str, nargs="+", default=["baseline"])
    p.add_argument("--n-atomic", type=int, default=12)
    p.add_argument("--n-composite", type=int, default=8)
    p.add_argument("--n-shortcut-controls", type=int, default=4)
    p.add_argument("--n-surface-controls", type=int, default=4)
    p.add_argument("--n-unrelated-controls", type=int, default=4)
    p.add_argument("--n-bits", type=int, default=48)
    p.add_argument("--max-data-seen", type=int, default=60_000)
    p.add_argument("--checkpoint-every", type=int, default=2_000)
    p.add_argument("--batch-size", type=int, default=256)
    p.add_argument("--learning-rate", type=float, default=2e-3)
    p.add_argument("--hidden-dim", type=int, default=256)
    p.add_argument("--depth", type=int, default=2)
    p.add_argument("--weight-decay", type=float, default=0.0)
    p.add_argument("--dropout", type=float, default=0.0)
    p.add_argument("--eval-examples-per-task", type=int, default=2048)
    p.add_argument("--grad-stats-every", type=int, default=20_000)
    p.add_argument("--grad-stat-batches", type=int, default=4)
    p.add_argument("--grad-stat-batch-size", type=int, default=128)
    p.add_argument("--cka-examples", type=int, default=512)
    p.add_argument("--acquisition-threshold", type=float, default=0.90)
    p.add_argument("--acquisition-patience", type=int, default=2)
    p.add_argument("--device", type=str, default="cpu")
    p.add_argument("--model", type=str, default="mlp")
    return p.parse_args()


def generated_conditions(component: str, unrelated: str, fake: str, surface: str, max_data_seen: int, batch_size: int) -> dict[str, InterventionConfig]:
    delay_end = max(batch_size, max_data_seen // 4)
    return {
        "baseline": InterventionConfig(name="baseline", kind="none"),
        "upweight_component": InterventionConfig(name="upweight_component", kind="upweight", task_name=component, multiplier=3.0),
        "upweight_unrelated_matched": InterventionConfig(name="upweight_unrelated_matched", kind="upweight", task_name=unrelated, matched_control_for="upweight_component", multiplier=3.0),
        "upweight_fake_component": InterventionConfig(name="upweight_fake_component", kind="upweight", task_name=fake, matched_control_for="upweight_component", multiplier=3.0),
        "upweight_surface_control": InterventionConfig(name="upweight_surface_control", kind="upweight", task_name=surface, matched_control_for="upweight_component", multiplier=3.0),
        "corrupt_component": InterventionConfig(name="corrupt_component", kind="corrupt", task_name=component, corrupt_prob=0.35),
        "corrupt_unrelated_matched": InterventionConfig(name="corrupt_unrelated_matched", kind="corrupt", task_name=unrelated, matched_control_for="corrupt_component", corrupt_prob=0.35),
        "delay_component": InterventionConfig(name="delay_component", kind="delay", task_name=component, end_data_seen=delay_end),
        "delay_unrelated_matched": InterventionConfig(name="delay_unrelated_matched", kind="delay", task_name=unrelated, matched_control_for="delay_component", end_data_seen=delay_end),
    }


def main() -> None:
    args = parse_args()
    if args.structure_table is not None:
        tasks = load_neural_family(args.structure_table)
        design_metadata = {"loaded_structure_table": str(args.structure_table)}
    else:
        family = generate_neural_task_family(
            NeuralDesignConfig(
                n_atomic=args.n_atomic,
                n_composite=args.n_composite,
                n_shortcut_controls=args.n_shortcut_controls,
                n_surface_controls=args.n_surface_controls,
                n_unrelated_controls=args.n_unrelated_controls,
                n_bits=args.n_bits,
                seed=args.family_seed,
            )
        )
        tasks = family.tasks
        design_dir = args.output_dir / "generated_family"
        save_neural_family(family, design_dir)
        design_metadata = family.metadata()
        if not family.passed:
            raise SystemExit("Generated neural family did not pass design criteria; run run_neural_design_gate for diagnostics.")

    chosen = _load_chosen_component(args.chosen_component_file, args.structure_table, tasks)
    registry = generated_conditions(
        component=str(chosen["component"]),
        unrelated=str(chosen["unrelated_control"]),
        fake=str(chosen["fake_component_control"]),
        surface=str(chosen["surface_control"]),
        max_data_seen=args.max_data_seen,
        batch_size=args.batch_size,
    )
    missing = [c for c in args.conditions if c not in registry]
    if missing:
        raise SystemExit(f"Unknown conditions {missing}. Available: {sorted(registry)}")

    outputs = []
    for seed in args.seeds:
        for condition in args.conditions:
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
                dropout=args.dropout,
                eval_examples_per_task=args.eval_examples_per_task,
                acquisition_threshold=args.acquisition_threshold,
                acquisition_patience=args.acquisition_patience,
                grad_stats_every=args.grad_stats_every,
                grad_stat_batches=args.grad_stat_batches,
                grad_stat_batch_size=args.grad_stat_batch_size,
                cka_examples=args.cka_examples,
                device=args.device,
                output_dir=args.output_dir,
            )
            print(f"Running generated family condition={condition} seed={seed}")
            outputs.append(run_single_training(tasks, cfg, registry[condition], model_name=args.model))

    paths = save_pilot_outputs(
        outputs,
        tasks,
        args.output_dir,
        extra_metadata={
            "family": design_metadata,
            "chosen_component_and_controls": chosen,
            "conditions": args.conditions,
            "seeds": args.seeds,
        },
    )
    print("Saved outputs:")
    for k, v in paths.items():
        print(f"  {k}: {v}")
    print("Chosen component/control set:")
    print(chosen)


def _load_chosen_component(path: Path | None, structure_table: Path | None, tasks) -> dict:
    candidates = []
    if path is not None:
        candidates.append(path)
    if structure_table is not None:
        candidates.append(structure_table.parent / "chosen_component_and_controls.json")
    for candidate in candidates:
        if candidate.exists():
            try:
                return json.loads(candidate.read_text(encoding="utf-8"))
            except Exception:
                pass
    return choose_default_component_and_controls(tasks)


if __name__ == "__main__":
    main()
