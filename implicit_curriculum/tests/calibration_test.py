from __future__ import annotations

from pathlib import Path

import pandas as pd

from ic_experiments.calibration import CalibrationCriteria, acquisition_summary_from_times, choose_component_and_controls_from_calibration, family_calibration_summary
from ic_experiments.design import DesignCriteria
from ic_experiments.neural_design import NeuralDesignConfig, generate_neural_task_family


def main() -> None:
    family = generate_neural_task_family(NeuralDesignConfig(n_atomic=6, n_composite=4, n_shortcut_controls=1, n_surface_controls=1, n_unrelated_controls=1, n_bits=24, seed=2, max_attempts=1000, criteria=DesignCriteria(min_rows=13)))
    assert family.passed, family.diagnostics
    rows = []
    for seed in [0, 1, 2]:
        for task in family.tasks:
            acquired = 1000.0 if task.kind in {"atomic", "composite"} else float("nan")
            rows.append({"condition": "baseline", "seed": seed, "task_name": task.name, "kind": task.kind, "acquired_at": acquired, "final_balanced_accuracy": 0.95 if acquired == acquired else 0.6})
    acq = pd.DataFrame(rows)
    structure = pd.DataFrame([
        {"task_name": t.name, "kind": t.kind, "op": t.op, "bits": ",".join(map(str, t.bits)), "components": ",".join(t.components), "frequency": t.frequency, "reference_learnability": t.reference_learnability, "formal_utility": t.formal_utility, "description": t.description}
        for t in family.tasks
    ])
    summary = acquisition_summary_from_times(acq, structure)
    chosen = choose_component_and_controls_from_calibration(family.tasks, summary, CalibrationCriteria(min_usable_composites_for_component=1))
    assert chosen["component"]
    assert chosen["composites"]
    fam_summary = family_calibration_summary(family.tasks, summary, CalibrationCriteria(min_usable_composites_for_component=1, target_max_mean_acquisition_rate=1.0))
    assert "mean_acquisition_rate" in fam_summary
    print("calibration test passed")


if __name__ == "__main__":
    main()
