from __future__ import annotations

import argparse
from pathlib import Path

from ic_experiments.backends.sparse_parity import SparseParityConfig, generate_sparse_parity_family, save_sparse_parity_family
from ic_experiments.configs import InterventionConfig, TrainingConfig
from ic_experiments.experiments.analyze_sparse_parity_pilot import main as _unused  # noqa: F401; keeps module import checked
from ic_experiments.neural_design import load_neural_family
from ic_experiments.train import run_single_training, save_pilot_outputs


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run B2 sparse-parity pilot with B2-appropriate defaults.")
    p.add_argument("--output-dir", type=Path, default=Path("results/sparse_parity_pilot_v06"))
    p.add_argument("--structure-table", type=Path, default=None)
    p.add_argument("--family-seed", type=int, default=0)
    p.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    p.add_argument("--n-bits", type=int, default=40)
    p.add_argument("--n-tasks", type=int, default=24)
    p.add_argument("--degrees", type=int, nargs="+", default=[2, 3])
    p.add_argument("--frequency-mode", type=str, default="zipf", choices=["zipf", "uniform"])
    p.add_argument("--zipf-alpha", type=float, default=1.1)
    p.add_argument("--max-data-seen", type=int, default=500_000)
    p.add_argument("--checkpoint-every", type=int, default=5_000)
    p.add_argument("--batch-size", type=int, default=1024)
    p.add_argument("--learning-rate", type=float, default=2e-3)
    p.add_argument("--hidden-dim", type=int, default=512)
    p.add_argument("--depth", type=int, default=3)
    p.add_argument("--weight-decay", type=float, default=0.0)
    p.add_argument("--dropout", type=float, default=0.0)
    p.add_argument("--eval-examples-per-task", type=int, default=4096)
    p.add_argument("--grad-stats-every", type=int, default=0, help="Set >0 to log expensive gradient stats; off by default for B2 calibration.")
    p.add_argument("--grad-stat-batches", type=int, default=4)
    p.add_argument("--grad-stat-batch-size", type=int, default=128)
    p.add_argument("--cka-examples", type=int, default=0, help="Set >0 to log CKA; off by default for B2 calibration.")
    p.add_argument("--acquisition-threshold", type=float, default=0.85)
    p.add_argument("--acquisition-patience", type=int, default=2)
    p.add_argument("--device", type=str, default="cpu")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    if args.structure_table is None:
        family = generate_sparse_parity_family(
            SparseParityConfig(
                n_bits=args.n_bits,
                n_tasks=args.n_tasks,
                degrees=tuple(args.degrees),
                frequency_mode=args.frequency_mode,
                zipf_alpha=args.zipf_alpha,
                seed=args.family_seed,
            )
        )
        save_sparse_parity_family(family, args.output_dir / "design")
        tasks = family.tasks
        structure_table = args.output_dir / "design" / "structure_table.csv"
    else:
        tasks = load_neural_family(args.structure_table)
        structure_table = args.structure_table

    outputs = []
    baseline = InterventionConfig(name="baseline", kind="none")
    for seed in args.seeds:
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
        print(f"Running sparse parity seed={seed}")
        outputs.append(run_single_training(tasks, cfg, baseline, model_name="mlp"))

    paths = save_pilot_outputs(
        outputs,
        tasks,
        args.output_dir,
        extra_metadata={
            "backend": "B2_sparse_parity",
            "structure_table_source": str(structure_table),
            "seeds": args.seeds,
            "degrees": args.degrees,
            "note": "Use analyze_sparse_parity_pilot; generic H1 analyzer has component/control assumptions not used by B2.",
        },
    )
    print("Saved sparse parity pilot outputs:")
    for k, v in paths.items():
        print(f"  {k}: {v}")
    print("Next: PYTHONPATH=src python -m ic_experiments.experiments.analyze_sparse_parity_pilot --result-dir", args.output_dir)


if __name__ == "__main__":
    main()
