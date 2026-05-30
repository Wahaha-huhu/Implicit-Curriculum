from __future__ import annotations

import argparse
from pathlib import Path

from ic_experiments.configs import InterventionConfig, TrainingConfig
from ic_experiments.tasks import build_pilot_tasks
from ic_experiments.train import run_single_training, save_pilot_outputs


def default_conditions() -> dict[str, InterventionConfig]:
    """Condition registry for the minimum decisive pilot.

    A = hypothesized component task. U = unrelated matched-control task.
    The U conditions are not perfect gradient-matched controls yet; they are
    first-pass data-budget matched controls. More exact controls will be added in
    the next implementation step.
    """

    return {
        "baseline": InterventionConfig(name="baseline", kind="none"),
        "upweight_A": InterventionConfig(
            name="upweight_A",
            kind="upweight",
            task_name="A_bit0",
            multiplier=3.0,
            start_data_seen=0,
        ),
        "upweight_U_matched": InterventionConfig(
            name="upweight_U_matched",
            kind="upweight",
            task_name="U_unrelated_xor910",
            matched_control_for="upweight_A",
            multiplier=3.0,
            start_data_seen=0,
        ),
        "corrupt_A": InterventionConfig(
            name="corrupt_A",
            kind="corrupt",
            task_name="A_bit0",
            corrupt_prob=0.35,
            start_data_seen=0,
        ),
        "corrupt_U_matched": InterventionConfig(
            name="corrupt_U_matched",
            kind="corrupt",
            task_name="U_unrelated_xor910",
            matched_control_for="corrupt_A",
            corrupt_prob=0.35,
            start_data_seen=0,
        ),
        "delay_A": InterventionConfig(
            name="delay_A",
            kind="delay",
            task_name="A_bit0",
            start_data_seen=0,
            end_data_seen=5_000,
        ),
        "delay_U_matched": InterventionConfig(
            name="delay_U_matched",
            kind="delay",
            task_name="U_unrelated_xor910",
            matched_control_for="delay_A",
            start_data_seen=0,
            end_data_seen=5_000,
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the minimum decisive implicit-curriculum pilot.")
    parser.add_argument("--output-dir", type=Path, default=Path("results/pilot"))
    parser.add_argument("--seeds", type=int, nargs="+", default=[0])
    parser.add_argument("--conditions", type=str, nargs="+", default=["baseline", "upweight_A", "upweight_U_matched", "corrupt_A", "corrupt_U_matched", "delay_A", "delay_U_matched"])
    parser.add_argument("--max-data-seen", type=int, default=20_000)
    parser.add_argument("--checkpoint-every", type=int, default=1_000)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--learning-rate", type=float, default=2e-3)
    parser.add_argument("--hidden-dim", type=int, default=128)
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--weight-decay", type=float, default=0.0)
    parser.add_argument("--dropout", type=float, default=0.0)
    parser.add_argument("--eval-examples-per-task", type=int, default=2048)
    parser.add_argument("--grad-stats-every", type=int, default=5_000)
    parser.add_argument("--grad-stat-batches", type=int, default=4)
    parser.add_argument("--grad-stat-batch-size", type=int, default=128)
    parser.add_argument("--cka-examples", type=int, default=512)
    parser.add_argument("--acquisition-threshold", type=float, default=0.90)
    parser.add_argument("--acquisition-patience", type=int, default=2)
    parser.add_argument("--acquisition-metric", type=str, default="balanced_accuracy")
    parser.add_argument("--device", type=str, default="cpu")
    parser.add_argument("--model", type=str, default="mlp")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    tasks = build_pilot_tasks()
    registry = default_conditions()
    missing = [name for name in args.conditions if name not in registry]
    if missing:
        raise SystemExit(f"Unknown conditions: {missing}. Available: {sorted(registry)}")

    outputs = []
    for seed in args.seeds:
        for condition_name in args.conditions:
            intervention = registry[condition_name]
            # Scale default delay windows to the requested run length: delay the
            # first quarter of training unless the user edited the registry.
            if intervention.kind == "delay" and intervention.end_data_seen == 5_000:
                intervention = InterventionConfig(**{**intervention.to_dict(), "end_data_seen": max(args.batch_size, args.max_data_seen // 4)})

            config = TrainingConfig(
                seed=seed,
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
                acquisition_metric=args.acquisition_metric,
                grad_stats_every=args.grad_stats_every,
                grad_stat_batches=args.grad_stat_batches,
                grad_stat_batch_size=args.grad_stat_batch_size,
                cka_examples=args.cka_examples,
                device=args.device,
                output_dir=args.output_dir,
            )
            print(f"Running condition={condition_name} seed={seed}")
            outputs.append(run_single_training(tasks, config, intervention, model_name=args.model))

    paths = save_pilot_outputs(
        outputs=outputs,
        tasks=tasks,
        output_dir=args.output_dir,
        extra_metadata={"conditions": args.conditions, "seeds": args.seeds},
    )
    print("Saved outputs:")
    for key, path in paths.items():
        print(f"  {key}: {path}")


if __name__ == "__main__":
    main()
