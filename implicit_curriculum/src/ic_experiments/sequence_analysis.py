from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import torch

from ic_experiments.backends.sequence_dsl import CONTENT_OFFSET, SequenceDSLConfig, SequenceDSLFamily, SequenceTaskSpec, target_for_task


def spearman(x: pd.Series, y: pd.Series) -> float:
    tmp = pd.DataFrame({"x": x, "y": y}).replace([np.inf, -np.inf], np.nan).dropna()
    if len(tmp) < 3 or tmp["x"].nunique() < 2 or tmp["y"].nunique() < 2:
        return np.nan
    return float(tmp["x"].rank().corr(tmp["y"].rank()))


def sequence_difficulty_table(
    family: SequenceDSLFamily,
    n_probe_examples: int = 2048,
    seed: int = 0,
) -> pd.DataFrame:
    """Compute pre-training difficulty/entropy descriptors for B1 sequence tasks.

    These are analysis covariates, not learned metrics. They help separate
    frequency effects from operation type, output entropy, target length, and
    trivial token baselines.
    """
    cfg = family.config
    g = torch.Generator(device="cpu")
    g.manual_seed(seed)
    x = torch.randint(CONTENT_OFFSET, cfg.vocab_size, (n_probe_examples, cfg.input_len), dtype=torch.long, generator=g)
    tasks_by_id = {t.structure_id: t for t in family.tasks}
    rows: list[dict] = []
    for task in family.tasks:
        y = target_for_task(task, x, cfg.vocab_content, tasks_by_id).cpu().numpy()
        x_np = x.cpu().numpy()
        pos_entropies = []
        pos_majority = []
        for pos in range(y.shape[1]):
            vals, counts = np.unique(y[:, pos], return_counts=True)
            p = counts.astype(float) / counts.sum()
            ent = float(-(p * np.log2(np.maximum(p, 1e-12))).sum())
            pos_entropies.append(ent)
            pos_majority.append(float(p.max()))
        copy_fraction = float((y == x_np).mean())
        rows.append(
            {
                "task_name": task.structure_id,
                "structure_id": task.structure_id,
                "kind": task.kind,
                "op": task.op,
                "operation_type": task.op,
                "frequency": task.frequency,
                "reference_learnability": task.reference_learnability,
                "formal_utility": task.formal_utility,
                "n_components": len(task.components),
                "composition_depth": _composition_depth(task, tasks_by_id),
                "target_length": cfg.input_len,
                "input_length": cfg.input_len,
                "output_entropy": float(np.mean(pos_entropies)),
                "positionwise_entropy_mean": float(np.mean(pos_entropies)),
                "positionwise_entropy_min": float(np.min(pos_entropies)),
                "positionwise_entropy_max": float(np.max(pos_entropies)),
                "random_baseline_token_accuracy": float(np.mean(pos_majority)),
                "copy_fraction": copy_fraction,
                "control_type": task.control_type or "",
                "control_for": task.control_for or "",
                "components": ",".join(task.components),
            }
        )
    return pd.DataFrame(rows)


def _composition_depth(task: SequenceTaskSpec, tasks_by_id: dict[str, SequenceTaskSpec], stack: tuple[str, ...] = ()) -> int:
    if task.structure_id in stack:
        return 0
    if not task.components:
        return 1
    depths = []
    for c in task.components:
        child = tasks_by_id.get(c)
        if child is not None:
            depths.append(_composition_depth(child, tasks_by_id, stack + (task.structure_id,)))
    return 1 + (max(depths) if depths else 0)


def make_config_table(args, backend: str, n_parameters: int | None = None) -> pd.DataFrame:
    d = vars(args).copy() if hasattr(args, "__dict__") else dict(args)
    for key, value in list(d.items()):
        if isinstance(value, Path):
            d[key] = str(value)
        elif isinstance(value, (list, tuple)):
            d[key] = ",".join(str(x) for x in value)
    d["backend"] = backend
    if n_parameters is not None:
        d["n_parameters"] = int(n_parameters)
    return pd.DataFrame([d])


def make_checkpoint_table(checkpoints: Iterable[int], max_data_seen: int, seeds: Iterable[int], condition: str = "baseline") -> pd.DataFrame:
    rows = []
    values = [0] + sorted(set(int(c) for c in checkpoints))
    for seed in seeds:
        for idx, data_seen in enumerate(values):
            rows.append(
                {
                    "condition": condition,
                    "seed": int(seed),
                    "checkpoint_index": idx,
                    "data_seen": int(data_seen),
                    "checkpoint_fraction": float(data_seen) / max(1, max_data_seen),
                }
            )
    return pd.DataFrame(rows)


def final_metrics(eval_df: pd.DataFrame) -> pd.DataFrame:
    if eval_df.empty:
        return pd.DataFrame()
    key_cols = ["condition", "seed", "task_name", "kind"]
    cols = [c for c in eval_df.columns if c in key_cols or c in ["loss", "token_accuracy", "exact_match", "accuracy", "balanced_accuracy", "data_seen", "checkpoint_fraction"]]
    return eval_df.sort_values("data_seen").groupby(key_cols, as_index=False).tail(1)[cols]


def frequency_realization_table(count_rows: list[dict], structure: pd.DataFrame, max_data_seen: int, input_len: int) -> pd.DataFrame:
    if not count_rows:
        return pd.DataFrame()
    counts = pd.DataFrame(count_rows)
    # Aggregate because a runner may append per checkpoint or per seed.
    group_cols = ["condition", "seed", "task_name"]
    agg = counts.groupby(group_cols, as_index=False).agg(realized_sample_count=("realized_sample_count", "sum"))
    total = agg.groupby(["condition", "seed"])["realized_sample_count"].transform("sum")
    agg["realized_sample_fraction"] = agg["realized_sample_count"] / total.replace(0, np.nan)
    agg["realized_target_token_count"] = agg["realized_sample_count"] * int(input_len)
    total_tokens = agg.groupby(["condition", "seed"])["realized_target_token_count"].transform("sum")
    agg["effective_loss_weight"] = agg["realized_target_token_count"] / total_tokens.replace(0, np.nan)
    meta_cols = [c for c in ["task_name", "frequency", "kind", "op", "reference_learnability", "formal_utility"] if c in structure.columns]
    if meta_cols:
        meta = structure[meta_cols].drop_duplicates("task_name")
        agg = agg.merge(meta, on="task_name", how="left")
    agg["intended_frequency"] = agg.get("frequency", np.nan)
    agg["frequency_error"] = agg["realized_sample_fraction"] - agg["intended_frequency"]
    agg["target_data_seen"] = int(max_data_seen)
    return agg


def realization_summary(realized: pd.DataFrame) -> pd.DataFrame:
    if realized.empty:
        return pd.DataFrame()
    rows = []
    for (condition, seed), g in realized.groupby(["condition", "seed"]):
        rows.append(
            {
                "condition": condition,
                "seed": int(seed),
                "n_tasks": int(g["task_name"].nunique()),
                "total_samples": int(g["realized_sample_count"].sum()),
                "mae_frequency": float(g["frequency_error"].abs().mean()),
                "max_abs_frequency_error": float(g["frequency_error"].abs().max()),
                "spearman_intended_realized": spearman(g["intended_frequency"], g["realized_sample_fraction"]),
            }
        )
    return pd.DataFrame(rows)



def _merge_missing_metadata(df: pd.DataFrame, meta: pd.DataFrame) -> pd.DataFrame:
    """Attach task metadata without creating duplicate *_meta columns.

    Some analyzers enrich acquisition/final tables before calling the shared
    stratified summary. Re-merging the full metadata table can trigger pandas
    MergeError when columns such as ``kind`` and ``kind_meta`` already coexist.
    This helper only merges metadata columns that are absent from ``df`` and
    fills missing values in existing columns from temporary metadata columns.
    """
    if df.empty or meta.empty or "task_name" not in df.columns or "task_name" not in meta.columns:
        return df

    out = df.copy()
    # Remove stale helper columns from previous merges. They are never used as
    # authoritative metadata and can collide with pandas suffix generation.
    stale_cols = [c for c in out.columns if c.endswith("_meta")]
    if stale_cols:
        out = out.drop(columns=stale_cols)

    wanted_cols = [c for c in meta.columns if c != "task_name"]
    missing_cols = [c for c in wanted_cols if c not in out.columns]

    # For existing metadata columns, fill nulls from the authoritative table.
    existing_cols = [c for c in wanted_cols if c in out.columns]
    if existing_cols:
        fill = meta[["task_name"] + existing_cols].drop_duplicates("task_name")
        tmp = out.merge(fill, on="task_name", how="left", suffixes=("", "__fill"))
        for c in existing_cols:
            fc = f"{c}__fill"
            if fc in tmp.columns:
                tmp[c] = tmp[c].where(tmp[c].notna(), tmp[fc])
                tmp = tmp.drop(columns=[fc])
        out = tmp

    if missing_cols:
        out = out.merge(meta[["task_name"] + missing_cols].drop_duplicates("task_name"), on="task_name", how="left")
    return out


def stratified_ordering_summary(
    acq_df: pd.DataFrame,
    final_df: pd.DataFrame,
    structure: pd.DataFrame,
    metric_family: str,
    threshold: float,
) -> pd.DataFrame:
    if structure.empty or acq_df.empty:
        return pd.DataFrame()
    meta_cols = [c for c in ["task_name", "frequency", "reference_learnability", "formal_utility", "kind", "op", "operation_type", "target_length", "control_type"] if c in structure.columns]
    meta = structure[meta_cols].drop_duplicates("task_name")
    acq = acq_df[(acq_df.get("metric_family") == metric_family) & (acq_df.get("analysis_threshold") == threshold)].copy()
    if acq.empty:
        return pd.DataFrame()
    acq = _merge_missing_metadata(acq, meta)
    final = _merge_missing_metadata(final_df.copy(), meta)
    metric_col = metric_family if metric_family in final.columns else ("token_accuracy" if metric_family == "token_accuracy" else "exact_match")
    strata: list[tuple[str, pd.DataFrame, pd.DataFrame]] = []
    base_acq = acq[acq["condition"] == "baseline"].copy()
    base_final = final[final["condition"] == "baseline"].copy()
    strata.append(("all", base_acq, base_final))
    true_kinds = {"atomic", "composite"}
    strata.append(("true_tasks_atomic_composite", base_acq[base_acq["kind"].isin(true_kinds)], base_final[base_final["kind"].isin(true_kinds)]))
    for kind in sorted(k for k in base_acq["kind"].dropna().unique()):
        strata.append((f"kind={kind}", base_acq[base_acq["kind"] == kind], base_final[base_final["kind"] == kind]))
    if "op" in base_acq.columns:
        for op in sorted(o for o in base_acq["op"].dropna().unique()):
            strata.append((f"op={op}", base_acq[base_acq["op"] == op], base_final[base_final["op"] == op]))
    if "target_length" in base_acq.columns:
        for tl in sorted(t for t in base_acq["target_length"].dropna().unique()):
            strata.append((f"target_length={tl}", base_acq[base_acq["target_length"] == tl], base_final[base_final["target_length"] == tl]))
    rows = []
    for name, g, f in strata:
        if len(g) == 0:
            continue
        rows.append(
            {
                "metric_family": metric_family,
                "threshold": float(threshold),
                "stratum": name,
                "n": int(len(g)),
                "n_tasks": int(g["task_name"].nunique()),
                "acquisition_rate": float(g["acquired_at"].notna().mean()),
                "time_spearman_frequency": spearman(g.get("frequency", pd.Series(dtype=float)), g["acquired_at"]),
                "time_spearman_reference_learnability": spearman(g.get("reference_learnability", pd.Series(dtype=float)), g["acquired_at"]),
                "time_spearman_formal_utility": spearman(g.get("formal_utility", pd.Series(dtype=float)), g["acquired_at"]),
                "final_spearman_frequency": spearman(f.get("frequency", pd.Series(dtype=float)), f[metric_col] if metric_col in f else pd.Series(dtype=float)),
                "final_spearman_reference_learnability": spearman(f.get("reference_learnability", pd.Series(dtype=float)), f[metric_col] if metric_col in f else pd.Series(dtype=float)),
                "final_spearman_formal_utility": spearman(f.get("formal_utility", pd.Series(dtype=float)), f[metric_col] if metric_col in f else pd.Series(dtype=float)),
            }
        )
    return pd.DataFrame(rows)
