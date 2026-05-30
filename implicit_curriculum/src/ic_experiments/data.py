from __future__ import annotations

import torch

from .configs import InterventionConfig
from .tasks import TaskSpec, labels_for_task


def set_seed(seed: int) -> None:
    # Small pilot models run faster and more reproducibly with few CPU threads.
    try:
        torch.set_num_threads(1)
    except RuntimeError:
        pass
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def task_weights_tensor(tasks: list[TaskSpec], device: str | torch.device) -> torch.Tensor:
    weights = torch.tensor([t.frequency for t in tasks], dtype=torch.float32, device=device)
    return weights / weights.sum()


def apply_sampling_intervention(
    base_weights: torch.Tensor,
    tasks: list[TaskSpec],
    intervention: InterventionConfig,
    data_seen: int,
) -> torch.Tensor:
    weights = base_weights.clone()
    if not intervention.is_active(data_seen) or intervention.task_name is None:
        return weights / weights.sum()

    idx = task_index(tasks)[intervention.task_name]
    if intervention.kind == "upweight":
        weights[idx] = weights[idx] * intervention.multiplier
    elif intervention.kind == "delay":
        weights[idx] = 0.0
    # corrupt does not change sampling weights.

    if float(weights.sum()) <= 0:
        raise ValueError("Intervention zeroed all sampling weights.")
    return weights / weights.sum()


def task_index(tasks: list[TaskSpec]) -> dict[str, int]:
    return {t.name: i for i, t in enumerate(tasks)}


def make_task_conditioned_inputs(
    bits: torch.Tensor,
    task_ids: torch.Tensor,
    n_tasks: int,
) -> torch.Tensor:
    one_hot = torch.nn.functional.one_hot(task_ids, num_classes=n_tasks).float()
    return torch.cat([bits.float(), one_hot.to(bits.device)], dim=1)


def generate_batch(
    tasks: list[TaskSpec],
    n_bits: int,
    batch_size: int,
    weights: torch.Tensor,
    device: str | torch.device,
    intervention: InterventionConfig | None = None,
    data_seen: int = 0,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    """Sample a mixed batch.

    Returns
    -------
    inputs:
        Task-conditioned inputs, shape [batch, n_bits+n_tasks].
    labels:
        Binary labels, shape [batch].
    task_ids:
        Integer task ids, shape [batch].
    bits:
        Raw bits, shape [batch, n_bits].
    """

    n_tasks = len(tasks)
    task_ids = torch.multinomial(weights, num_samples=batch_size, replacement=True)
    bits = torch.randint(0, 2, (batch_size, n_bits), dtype=torch.float32, device=device)
    labels = torch.empty(batch_size, dtype=torch.float32, device=device)
    tasks_by_name = {t.name: t for t in tasks}

    for idx, task in enumerate(tasks):
        mask = task_ids == idx
        if mask.any():
            labels[mask] = labels_for_task(task, bits[mask], tasks_by_name)

    if intervention is not None and intervention.is_active(data_seen) and intervention.kind == "corrupt" and intervention.task_name:
        idx = task_index(tasks)[intervention.task_name]
        mask = task_ids == idx
        if mask.any():
            flip = torch.rand(int(mask.sum()), device=device) < intervention.corrupt_prob
            labels[mask] = torch.where(flip, 1.0 - labels[mask], labels[mask])

    inputs = make_task_conditioned_inputs(bits, task_ids.to(device), n_tasks)
    return inputs, labels, task_ids.to(device), bits


class HeldoutSets:
    """Fixed per-task heldout bits and labels for stable acquisition curves."""

    def __init__(self, tasks: list[TaskSpec], n_bits: int, examples_per_task: int, seed: int, device: str | torch.device):
        self.tasks = tasks
        self.n_bits = n_bits
        self.examples_per_task = examples_per_task
        self.device = torch.device(device)
        generator = torch.Generator(device="cpu")
        generator.manual_seed(seed)
        self.bits_by_task: dict[str, torch.Tensor] = {}
        self.labels_by_task: dict[str, torch.Tensor] = {}
        tasks_by_name = {t.name: t for t in tasks}
        for task in tasks:
            bits_cpu = torch.randint(0, 2, (examples_per_task, n_bits), dtype=torch.float32, generator=generator)
            bits = bits_cpu.to(self.device)
            self.bits_by_task[task.name] = bits
            self.labels_by_task[task.name] = labels_for_task(task, bits, tasks_by_name)

    def inputs_labels_for_task(self, task_idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        task = self.tasks[task_idx]
        bits = self.bits_by_task[task.name]
        task_ids = torch.full((len(bits),), task_idx, dtype=torch.long, device=bits.device)
        return make_task_conditioned_inputs(bits, task_ids, len(self.tasks)), self.labels_by_task[task.name]
