from __future__ import annotations

import argparse
from pathlib import Path

from ic_experiments.backends.sequence_dsl import SequenceDSLConfig, generate_sequence_dsl_family, save_sequence_dsl_family


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate B1 sequence-DSL/transformer task family.")
    p.add_argument("--output-dir", type=Path, default=Path("results/sequence_dsl_design"))
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--vocab-content", type=int, default=64)
    p.add_argument("--input-len", type=int, default=8)
    p.add_argument("--n-atomic", type=int, default=8)
    p.add_argument("--n-composite", type=int, default=6)
    p.add_argument("--n-shortcut-controls", type=int, default=2)
    p.add_argument("--n-surface-controls", type=int, default=2)
    p.add_argument("--n-unrelated-controls", type=int, default=2)
    p.add_argument("--frequency-mode", choices=["zipf", "uniform"], default="zipf")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    family = generate_sequence_dsl_family(
        SequenceDSLConfig(
            vocab_content=args.vocab_content,
            input_len=args.input_len,
            n_atomic=args.n_atomic,
            n_composite=args.n_composite,
            n_shortcut_controls=args.n_shortcut_controls,
            n_surface_controls=args.n_surface_controls,
            n_unrelated_controls=args.n_unrelated_controls,
            frequency_mode=args.frequency_mode,
            seed=args.seed,
        )
    )
    paths = save_sequence_dsl_family(family, args.output_dir)
    print(f"Generated sequence-DSL family: passed={family.passed}")
    for k, v in paths.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
