from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Literal


InterventionKind = Literal["none", "upweight", "corrupt", "delay"]


@dataclass(frozen=True)
class InterventionConfig:
    """Training-distribution or label intervention for one task.

    The intervention is deliberately simple in this first implementation pass.
    More exact gradient-matched and model-state interventions should be added
    after the pilot infrastructure is validated.
    """

    name: str = "baseline"
    kind: InterventionKind = "none"
    task_name: str | None = None
    matched_control_for: str | None = None
    start_data_seen: int = 0
    end_data_seen: int | None = None
    multiplier: float = 2.0
    corrupt_prob: float = 0.25

    def is_active(self, data_seen: int) -> bool:
        if self.kind == "none":
            return False
        if data_seen < self.start_data_seen:
            return False
        if self.end_data_seen is not None and data_seen >= self.end_data_seen:
            return False
        return True

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class TrainingConfig:
    """Configuration for a single pilot training run."""

    seed: int = 0
    n_bits: int = 12
    batch_size: int = 128
    max_data_seen: int = 20_000
    checkpoint_every: int = 1_000
    learning_rate: float = 2e-3
    weight_decay: float = 0.0
    hidden_dim: int = 128
    depth: int = 2
    dropout: float = 0.0
    eval_examples_per_task: int = 2_048
    acquisition_threshold: float = 0.90
    acquisition_patience: int = 2
    acquisition_metric: str = "balanced_accuracy"
    grad_stats_every: int = 5_000
    grad_stat_batches: int = 4
    grad_stat_batch_size: int = 128
    cka_examples: int = 512
    device: str = "cpu"
    output_dir: Path = field(default_factory=lambda: Path("results/pilot"))

    def to_dict(self) -> dict:
        d = asdict(self)
        d["output_dir"] = str(self.output_dir)
        return d
