from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
import torch
from torch import nn

from .data import make_task_conditioned_inputs
from .tasks import TaskSpec, labels_for_task


@dataclass(frozen=True)
class AcquisitionConfig:
    threshold: float = 0.90
    patience: int = 2
    metric: str = "balanced_accuracy"


@torch.no_grad()
def evaluate_per_task(
    model: nn.Module,
    heldout,
    data_seen: int,
    condition: str,
    seed: int,
) -> list[dict]:
    model.eval()
    criterion = nn.BCEWithLogitsLoss(reduction="mean")
    records: list[dict] = []
    for task_idx, task in enumerate(heldout.tasks):
        inputs, labels = heldout.inputs_labels_for_task(task_idx)
        logits = model(inputs)
        loss = float(criterion(logits, labels).item())
        probs = torch.sigmoid(logits)
        preds = (probs >= 0.5).float()
        acc = float((preds == labels).float().mean().item())
        pos_mask = labels == 1
        neg_mask = labels == 0
        pos_acc = float((preds[pos_mask] == labels[pos_mask]).float().mean().item()) if bool(pos_mask.any()) else float("nan")
        neg_acc = float((preds[neg_mask] == labels[neg_mask]).float().mean().item()) if bool(neg_mask.any()) else float("nan")
        if pos_mask.any() and neg_mask.any():
            balanced_acc = 0.5 * (pos_acc + neg_acc)
        else:
            balanced_acc = acc
        records.append(
            {
                "condition": condition,
                "seed": seed,
                "data_seen": data_seen,
                "task_name": task.name,
                "kind": task.kind,
                "loss": loss,
                "accuracy": acc,
                "balanced_accuracy": balanced_acc,
                "pos_accuracy": pos_acc,
                "neg_accuracy": neg_acc,
            }
        )
    model.train()
    return records


def acquisition_times(eval_df: pd.DataFrame, threshold: float = 0.90, patience: int = 2, metric: str = "balanced_accuracy") -> pd.DataFrame:
    """First sustained threshold crossing by condition/seed/task.

    Returns NaN when a task does not cross the threshold.
    """

    rows: list[dict] = []
    group_cols = ["condition", "seed", "task_name", "kind"]
    for keys, g in eval_df.sort_values("data_seen").groupby(group_cols):
        condition, seed, task_name, kind = keys
        if metric not in g.columns:
            raise ValueError(f"Metric {metric!r} not present in eval dataframe columns {list(g.columns)}")
        acc = g[metric].to_numpy()
        times = g["data_seen"].to_numpy()
        acquired_at = np.nan
        for i in range(0, len(acc) - patience + 1):
            if np.all(acc[i : i + patience] >= threshold):
                acquired_at = float(times[i])
                break
        rows.append(
            {
                "condition": condition,
                "seed": int(seed),
                "task_name": task_name,
                "kind": kind,
                "acquired_at": acquired_at,
                "threshold": threshold,
                "patience": patience,
                "metric": metric,
                "final_metric": float(acc[-1]) if len(acc) else np.nan,
                "final_accuracy": float(g["accuracy"].to_numpy()[-1]) if len(g) else np.nan,
                "final_balanced_accuracy": float(g["balanced_accuracy"].to_numpy()[-1]) if len(g) else np.nan,
            }
        )
    return pd.DataFrame(rows)


def flatten_current_grads(model: nn.Module) -> torch.Tensor:
    chunks = []
    for p in model.parameters():
        if p.grad is None:
            chunks.append(torch.zeros(p.numel(), device=next(model.parameters()).device))
        else:
            chunks.append(p.grad.detach().flatten())
    return torch.cat(chunks)


def cosine(a: torch.Tensor, b: torch.Tensor, eps: float = 1e-12) -> float:
    denom = torch.linalg.norm(a) * torch.linalg.norm(b)
    if float(denom) < eps:
        return float("nan")
    return float(torch.dot(a, b).item() / (float(denom.item()) + eps))


def estimate_gradient_stats(
    model: nn.Module,
    tasks: list[TaskSpec],
    n_bits: int,
    data_seen: int,
    condition: str,
    seed: int,
    batches_per_task: int = 4,
    batch_size: int = 128,
    device: str | torch.device = "cpu",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Estimate task gradient diagnostics on fresh batches.

    The estimator is intentionally lightweight and noisy. It is useful for pilot
    diagnostics; the full experiment should increase batches and add confidence
    intervals.
    """

    model.train()
    criterion = nn.BCEWithLogitsLoss(reduction="mean")
    tasks_by_name = {t.name: t for t in tasks}
    per_task_grads: dict[str, list[torch.Tensor]] = {t.name: [] for t in tasks}

    for task_idx, task in enumerate(tasks):
        for _ in range(batches_per_task):
            bits = torch.randint(0, 2, (batch_size, n_bits), dtype=torch.float32, device=device)
            task_ids = torch.full((batch_size,), task_idx, dtype=torch.long, device=device)
            inputs = make_task_conditioned_inputs(bits, task_ids, len(tasks))
            labels = labels_for_task(task, bits, tasks_by_name)
            model.zero_grad(set_to_none=True)
            logits = model(inputs)
            loss = criterion(logits, labels)
            loss.backward()
            per_task_grads[task.name].append(flatten_current_grads(model).detach().cpu())

    task_rows = []
    mean_grads: dict[str, torch.Tensor] = {}
    for task in tasks:
        grads = torch.stack(per_task_grads[task.name], dim=0)
        mean_grad = grads.mean(dim=0)
        mean_grads[task.name] = mean_grad
        centered = grads - mean_grad.unsqueeze(0)
        norm = float(torch.linalg.norm(mean_grad).item())
        noise = float(torch.sqrt((centered.pow(2).sum(dim=1)).mean()).item())
        snr = norm / (noise + 1e-12)
        pairwise = []
        for i in range(len(grads)):
            for j in range(i + 1, len(grads)):
                pairwise.append(cosine(grads[i], grads[j]))
        within_alignment = float(np.nanmean(pairwise)) if pairwise else np.nan
        task_rows.append(
            {
                "condition": condition,
                "seed": seed,
                "data_seen": data_seen,
                "task_name": task.name,
                "kind": task.kind,
                "grad_mean_norm": norm,
                "grad_noise_rms": noise,
                "grad_snr": snr,
                "within_task_grad_alignment": within_alignment,
            }
        )

    cross_rows = []
    for t1 in tasks:
        for t2 in tasks:
            cross_rows.append(
                {
                    "condition": condition,
                    "seed": seed,
                    "data_seen": data_seen,
                    "task_i": t1.name,
                    "task_j": t2.name,
                    "grad_cosine_mean": cosine(mean_grads[t1.name], mean_grads[t2.name]),
                }
            )
    return pd.DataFrame(task_rows), pd.DataFrame(cross_rows)


@torch.no_grad()
def representation_cka(
    model: nn.Module,
    tasks: list[TaskSpec],
    n_bits: int,
    examples: int,
    data_seen: int,
    condition: str,
    seed: int,
    device: str | torch.device = "cpu",
) -> pd.DataFrame:
    """Linear CKA between hidden states for task-conditioned views of same bits."""

    model.eval()
    bits = torch.randint(0, 2, (examples, n_bits), dtype=torch.float32, device=device)
    hidden_by_task: dict[str, torch.Tensor] = {}
    for task_idx, task in enumerate(tasks):
        task_ids = torch.full((examples,), task_idx, dtype=torch.long, device=device)
        inputs = make_task_conditioned_inputs(bits, task_ids, len(tasks))
        _, hidden = model(inputs, return_hidden=True)
        hidden_by_task[task.name] = hidden.detach().cpu()

    rows = []
    for ti in tasks:
        for tj in tasks:
            rows.append(
                {
                    "condition": condition,
                    "seed": seed,
                    "data_seen": data_seen,
                    "task_i": ti.name,
                    "task_j": tj.name,
                    "linear_cka": linear_cka(hidden_by_task[ti.name], hidden_by_task[tj.name]),
                }
            )
    model.train()
    return pd.DataFrame(rows)


def linear_cka(x: torch.Tensor, y: torch.Tensor, eps: float = 1e-12) -> float:
    x = x.float() - x.float().mean(dim=0, keepdim=True)
    y = y.float() - y.float().mean(dim=0, keepdim=True)
    xty = x.T @ y
    numerator = torch.linalg.norm(xty, ord="fro").pow(2)
    denominator = torch.linalg.norm(x.T @ x, ord="fro") * torch.linalg.norm(y.T @ y, ord="fro")
    return float((numerator / (denominator + eps)).item())
