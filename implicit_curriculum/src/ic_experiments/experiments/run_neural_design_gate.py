from __future__ import annotations

import argparse
from pathlib import Path

from ic_experiments.design import DesignCriteria
from ic_experiments.neural_design import NeuralDesignConfig, generate_neural_task_family, save_neural_family


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate a VIF-targeted concrete neural task family.")
    p.add_argument("--output-dir", type=Path, default=Path("results/neural_design_gate"))
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--n-atomic", type=int, default=12)
    p.add_argument("--n-composite", type=int, default=8)
    p.add_argument("--n-shortcut-controls", type=int, default=4)
    p.add_argument("--n-surface-controls", type=int, default=4)
    p.add_argument("--n-unrelated-controls", type=int, default=4)
    p.add_argument("--n-bits", type=int, default=48)
    p.add_argument("--frequency-low", type=float, default=0.01)
    p.add_argument("--frequency-high", type=float, default=0.12)
    p.add_argument("--max-attempts", type=int, default=10000)
    p.add_argument("--max-vif", type=float, default=5.0)
    p.add_argument("--max-abs-pearson", type=float, default=0.70)
    p.add_argument("--max-abs-spearman", type=float, default=0.75)
    p.add_argument("--max-condition-number", type=float, default=50.0)
    p.add_argument("--include-xor-composites", action="store_true")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    criteria = DesignCriteria(
        max_vif=args.max_vif,
        max_abs_pearson=args.max_abs_pearson,
        max_abs_spearman=args.max_abs_spearman,
        max_condition_number=args.max_condition_number,
        min_rows=args.n_atomic + args.n_composite + args.n_shortcut_controls + args.n_surface_controls + args.n_unrelated_controls,
    )
    config = NeuralDesignConfig(
        n_atomic=args.n_atomic,
        n_composite=args.n_composite,
        n_shortcut_controls=args.n_shortcut_controls,
        n_surface_controls=args.n_surface_controls,
        n_unrelated_controls=args.n_unrelated_controls,
        n_bits=args.n_bits,
        frequency_low=args.frequency_low,
        frequency_high=args.frequency_high,
        seed=args.seed,
        max_attempts=args.max_attempts,
        include_xor_composites=args.include_xor_composites,
        criteria=criteria,
    )
    result = generate_neural_task_family(config)
    paths = save_neural_family(result, args.output_dir)
    print(f"passed={result.passed} attempts_used={result.attempts_used}")
    print("Saved outputs:")
    for k, v in paths.items():
        print(f"  {k}: {v}")
    if not result.passed:
        raise SystemExit("Neural design gate did not pass. Inspect neural_design_report.md and adjust generation criteria.")


if __name__ == "__main__":
    main()
