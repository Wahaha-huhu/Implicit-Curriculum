from __future__ import annotations

from pathlib import Path

from ic_experiments.design import DesignCriteria
from ic_experiments.neural_design import NeuralDesignConfig, generate_neural_task_family, save_neural_family, choose_default_component_and_controls


def main() -> None:
    result = generate_neural_task_family(
        NeuralDesignConfig(
            n_atomic=8,
            n_composite=4,
            n_shortcut_controls=2,
            n_surface_controls=2,
            n_unrelated_controls=2,
            n_bits=32,
            seed=0,
            max_attempts=1000,
            criteria=DesignCriteria(min_rows=18),
        )
    )
    assert result.passed, result.diagnostics
    assert len(result.tasks) == 18
    chosen = choose_default_component_and_controls(result.tasks)
    assert chosen["component"]
    assert chosen["composites"]
    paths = save_neural_family(result, Path("/tmp/ic_neural_design_test"))
    assert Path(paths["structure_table"]).exists()
    print("neural design gate test passed")


if __name__ == "__main__":
    main()
