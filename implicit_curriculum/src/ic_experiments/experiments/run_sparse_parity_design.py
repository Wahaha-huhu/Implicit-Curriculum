from __future__ import annotations

import argparse
from pathlib import Path

from ic_experiments.backends.sparse_parity import SparseParityConfig, generate_sparse_parity_family, save_sparse_parity_family


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate B2 sparse-parity/quanta-baseline task family.")
    p.add_argument("--output-dir", type=Path, default=Path("results/sparse_parity_design"))
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--n-bits", type=int, default=40)
    p.add_argument("--n-tasks", type=int, default=24)
    p.add_argument("--degrees", type=int, nargs="+", default=[3, 5])
    p.add_argument("--frequency-mode", type=str, choices=["zipf", "uniform"], default="zipf")
    p.add_argument("--zipf-alpha", type=float, default=1.1)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    family = generate_sparse_parity_family(
        SparseParityConfig(
            n_bits=args.n_bits,
            n_tasks=args.n_tasks,
            degrees=tuple(args.degrees),
            frequency_mode=args.frequency_mode,
            zipf_alpha=args.zipf_alpha,
            seed=args.seed,
        )
    )
    paths = save_sparse_parity_family(family, args.output_dir)
    print(f"Generated sparse-parity family: passed={family.passed}")
    for k, v in paths.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
