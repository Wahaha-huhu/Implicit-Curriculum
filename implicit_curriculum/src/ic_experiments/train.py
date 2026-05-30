from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import torch
from torch import nn

from .configs import InterventionConfig, TrainingConfig
from .data import HeldoutSets, apply_sampling_intervention, generate_batch, set_seed, task_weights_tensor
from .metrics import acquisition_times, estimate_gradient_stats, evaluate_per_task, representation_cka
from .models import build_model
from .tasks import TaskSpec, structural_design_diagnostics, task_table


def run_single_training(
    tasks: list[TaskSpec],
    config: TrainingConfig,
    intervention: InterventionConfig,
    model_name: str = "mlp",
) -> dict[str, pd.DataFrame | dict]:
    """Run one seed/condition pilot training experiment."""

    set_seed(config.seed)
    device = torch.device(config.device)
    input_dim = config.n_bits + len(tasks)
    model = build_model(
        model_name=model_name,
        input_dim=input_dim,
        hidden_dim=config.hidden_dim,
        depth=config.depth,
        dropout=config.dropout,
    ).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=config.learning_rate, weight_decay=config.weight_decay)
    criterion = nn.BCEWithLogitsLoss(reduction="mean")
    base_weights = task_weights_tensor(tasks, device=device)
    heldout = HeldoutSets(
        tasks=tasks,
        n_bits=config.n_bits,
        examples_per_task=config.eval_examples_per_task,
        seed=config.seed + 10_000,
        device=device,
    )

    eval_records: list[dict] = []
    grad_task_frames: list[pd.DataFrame] = []
    grad_cross_frames: list[pd.DataFrame] = []

    data_seen = 0
    eval_records.extend(evaluate_per_task(model, heldout, data_seen, intervention.name, config.seed))
    if config.grad_stats_every > 0:
        task_grad_df, cross_grad_df = estimate_gradient_stats(
            model=model,
            tasks=tasks,
            n_bits=config.n_bits,
            data_seen=data_seen,
            condition=intervention.name,
            seed=config.seed,
            batches_per_task=config.grad_stat_batches,
            batch_size=config.grad_stat_batch_size,
            device=device,
        )
        grad_task_frames.append(task_grad_df)
        grad_cross_frames.append(cross_grad_df)

    next_checkpoint = config.checkpoint_every
    next_grad_checkpoint = config.grad_stats_every if config.grad_stats_every > 0 else None

    while data_seen < config.max_data_seen:
        weights = apply_sampling_intervention(base_weights, tasks, intervention, data_seen)
        inputs, labels, _, _ = generate_batch(
            tasks=tasks,
            n_bits=config.n_bits,
            batch_size=config.batch_size,
            weights=weights,
            device=device,
            intervention=intervention,
            data_seen=data_seen,
        )
        optimizer.zero_grad(set_to_none=True)
        logits = model(inputs)
        loss = criterion(logits, labels)
        loss.backward()
        optimizer.step()
        data_seen += config.batch_size

        if data_seen >= next_checkpoint or data_seen >= config.max_data_seen:
            eval_records.extend(evaluate_per_task(model, heldout, data_seen, intervention.name, config.seed))
            while next_checkpoint <= data_seen:
                next_checkpoint += config.checkpoint_every

        if next_grad_checkpoint is not None and (data_seen >= next_grad_checkpoint or data_seen >= config.max_data_seen):
            task_grad_df, cross_grad_df = estimate_gradient_stats(
                model=model,
                tasks=tasks,
                n_bits=config.n_bits,
                data_seen=data_seen,
                condition=intervention.name,
                seed=config.seed,
                batches_per_task=config.grad_stat_batches,
                batch_size=config.grad_stat_batch_size,
                device=device,
            )
            grad_task_frames.append(task_grad_df)
            grad_cross_frames.append(cross_grad_df)
            while next_grad_checkpoint <= data_seen:
                next_grad_checkpoint += config.grad_stats_every

    eval_df = pd.DataFrame(eval_records)
    if not eval_df.empty and "data_seen" in eval_df.columns:
        eval_df["checkpoint_fraction"] = eval_df["data_seen"] / max(1, config.max_data_seen)
    acquisition_df = acquisition_times(
        eval_df,
        threshold=config.acquisition_threshold,
        patience=config.acquisition_patience,
        metric=config.acquisition_metric,
    )
    grad_task_df = pd.concat(grad_task_frames, ignore_index=True) if grad_task_frames else pd.DataFrame()
    grad_cross_df = pd.concat(grad_cross_frames, ignore_index=True) if grad_cross_frames else pd.DataFrame()
    for _df in (grad_task_df, grad_cross_df):
        if not _df.empty and "data_seen" in _df.columns:
            _df["checkpoint_fraction"] = _df["data_seen"] / max(1, config.max_data_seen)
    cka_df = representation_cka(
        model=model,
        tasks=tasks,
        n_bits=config.n_bits,
        examples=config.cka_examples,
        data_seen=data_seen,
        condition=intervention.name,
        seed=config.seed,
        device=device,
    )
    if not cka_df.empty and "data_seen" in cka_df.columns:
        cka_df["checkpoint_fraction"] = cka_df["data_seen"] / max(1, config.max_data_seen)

    metadata = {
        "config": config.to_dict(),
        "intervention": intervention.to_dict(),
        "model_name": model_name,
        "n_parameters": sum(p.numel() for p in model.parameters()),
        "final_data_seen": data_seen,
    }
    return {
        "eval": eval_df,
        "acquisition": acquisition_df,
        "grad_task": grad_task_df,
        "grad_cross": grad_cross_df,
        "cka": cka_df,
        "metadata": metadata,
    }


def save_pilot_outputs(
    outputs: list[dict[str, pd.DataFrame | dict]],
    tasks: list[TaskSpec],
    output_dir: str | Path,
    extra_metadata: dict | None = None,
) -> dict[str, str]:
    """Aggregate and save outputs from multiple conditions/seeds."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    frames = {
        "eval_curves": pd.concat([o["eval"] for o in outputs], ignore_index=True),
        "acquisition_times": pd.concat([o["acquisition"] for o in outputs], ignore_index=True),
        "grad_stats": pd.concat([o["grad_task"] for o in outputs], ignore_index=True),
        "grad_cross_task": pd.concat([o["grad_cross"] for o in outputs], ignore_index=True),
        "representation_cka": pd.concat([o["cka"] for o in outputs], ignore_index=True),
        "structure_table": task_table(tasks),
    }

    paths: dict[str, str] = {}
    for name, df in frames.items():
        path = output_path / f"{name}.csv"
        df.to_csv(path, index=False)
        paths[name] = str(path)

    summary = {
        "n_runs": len(outputs),
        "runs": [o["metadata"] for o in outputs],
        "structural_design_diagnostics": structural_design_diagnostics(tasks),
        "paths": paths,
    }
    if extra_metadata:
        summary.update(extra_metadata)
    summary_path = output_path / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    paths["summary"] = str(summary_path)
    return paths
