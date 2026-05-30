from __future__ import annotations

from pathlib import Path

from ic_experiments.configs import InterventionConfig, TrainingConfig
from ic_experiments.tasks import build_pilot_tasks, structural_design_diagnostics
from ic_experiments.train import run_single_training, save_pilot_outputs


def main() -> None:
    tasks = build_pilot_tasks()
    assert abs(sum(t.frequency for t in tasks) - 1.0) < 1e-6
    diagnostics = structural_design_diagnostics(tasks)
    assert "design_condition_number" in diagnostics

    config = TrainingConfig(
        seed=0,
        max_data_seen=256,
        checkpoint_every=128,
        batch_size=32,
        hidden_dim=32,
        depth=1,
        eval_examples_per_task=128,
        grad_stats_every=256,
        grad_stat_batches=2,
        grad_stat_batch_size=32,
        cka_examples=64,
        output_dir=Path("/tmp/ic_smoke"),
    )
    output = run_single_training(tasks, config, InterventionConfig(name="baseline", kind="none"))
    assert not output["eval"].empty
    assert not output["acquisition"].empty
    paths = save_pilot_outputs([output], tasks, "/tmp/ic_smoke")
    assert Path(paths["summary"]).exists()
    print("smoke test passed")


if __name__ == "__main__":
    main()
