from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
import torch


DEFAULT_DOSE_MULTIPLIERS = (0.0, 0.5, 1.0, 2.0)


@dataclass(frozen=True)
class CouplingPair:
    pair_id: str
    source_task: str
    target_task: str
    pair_type: str
    filler_task: str
    source_kind: str = ""
    target_kind: str = ""
    source_op: str = ""
    target_op: str = ""
    source_frequency: float = float("nan")
    target_frequency: float = float("nan")
    source_reference_learnability: float = float("nan")
    target_reference_learnability: float = float("nan")
    surface_overlap_proxy: float = float("nan")
    formal_relation: str = "none"

    def to_row(self) -> dict[str, Any]:
        return {
            "pair_id": self.pair_id,
            "source_task": self.source_task,
            "target_task": self.target_task,
            "pair_type": self.pair_type,
            "filler_task": self.filler_task,
            "source_kind": self.source_kind,
            "target_kind": self.target_kind,
            "source_op": self.source_op,
            "target_op": self.target_op,
            "source_frequency": self.source_frequency,
            "target_frequency": self.target_frequency,
            "source_reference_learnability": self.source_reference_learnability,
            "target_reference_learnability": self.target_reference_learnability,
            "surface_overlap_proxy": self.surface_overlap_proxy,
            "formal_relation": self.formal_relation,
        }


def normalize_structure_table(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "task_name" not in out.columns:
        out["task_name"] = out.get("structure_id", pd.Series(dtype=str))
    if "structure_id" not in out.columns:
        out["structure_id"] = out["task_name"]
    if "op" not in out.columns and "operation" in out.columns:
        out["op"] = out["operation"]
    for c in ["kind", "op", "components", "control_type", "control_for"]:
        if c not in out.columns:
            out[c] = ""
    for c in ["frequency", "reference_learnability", "formal_utility"]:
        if c not in out.columns:
            out[c] = np.nan
        out[c] = pd.to_numeric(out[c], errors="coerce")
    return out


def make_coupling_pair_plan(
    structure: pd.DataFrame,
    max_pairs: int = 12,
    seed: int = 0,
    include_reverse_composition: bool = True,
) -> pd.DataFrame:
    """Construct a designed, heterogeneous ordered-pair sample for the N1 pilot.

    The plan deliberately samples broad interaction types rather than assuming an
    implicit-curriculum or compositional mechanism. Composition is one pair type;
    same-operation, same-surface/control, and unrelated pairs provide baselines.
    """

    df = normalize_structure_table(structure)
    if df.empty:
        raise ValueError("Cannot build a coupling plan from an empty structure table.")
    rng = np.random.default_rng(seed)
    rows: list[CouplingPair] = []
    names = list(df["task_name"].astype(str))

    atomics = df[df["kind"].astype(str).eq("atomic")].copy()
    composites = df[df["kind"].astype(str).eq("composite")].copy()
    surface = df[df["kind"].astype(str).str.contains("surface", na=False)].copy()
    shortcuts = df[df["kind"].astype(str).str.contains("shortcut", na=False)].copy()
    unrelated = df[df["kind"].astype(str).str.contains("unrelated", na=False)].copy()
    controls = pd.concat([surface, shortcuts, unrelated], ignore_index=True).drop_duplicates("task_name")
    if controls.empty:
        controls = df[~df["kind"].astype(str).eq("composite")].copy()

    # 1. Component -> composite pairs, and optionally the reverse direction as a
    # built-in asymmetry check. This is now a case type, not an assumed mechanism.
    for _, comp in composites.iterrows():
        comps = [x for x in str(comp.get("components", "")).split(",") if x and x != "nan"]
        for source in comps:
            if source not in set(names):
                continue
            rows.append(pair_from_names(df, source, str(comp["task_name"]), "component_to_composite", rng))
            if include_reverse_composition:
                rows.append(pair_from_names(df, str(comp["task_name"]), source, "composite_to_component_reverse", rng))

    # 2. Same-operation atomic pairs: expected to often show transfer without any
    # formal component relation.
    for op, g in atomics.groupby("op"):
        task_names = list(g["task_name"].astype(str))
        if len(task_names) < 2:
            continue
        rng.shuffle(task_names)
        for a, b in zip(task_names[::2], task_names[1::2]):
            rows.append(pair_from_names(df, a, b, "same_operation", rng))
            rows.append(pair_from_names(df, b, a, "same_operation_reverse", rng))

    # 3. Surface/control pairs: a conservative baseline for template/surface effects.
    for _, src in controls.iterrows():
        target_pool = atomics if not atomics.empty else df[df["task_name"] != src["task_name"]]
        if target_pool.empty:
            continue
        tgt = choose_matched_task(target_pool, src, forbidden={str(src["task_name"])}, rng=rng)
        if tgt:
            rows.append(pair_from_names(df, str(src["task_name"]), tgt, "control_or_surface", rng))

    # 4. Unrelated-matched pairs across different operation/kind. These estimate the
    # no-specific-interaction baseline and preserve unexpected effects as measurable residuals.
    for _, src in df.sample(frac=1.0, random_state=seed).iterrows():
        forbidden = {str(src["task_name"])}
        pool = df[(df["op"].astype(str) != str(src.get("op", ""))) & ~df["task_name"].astype(str).isin(forbidden)].copy()
        if pool.empty:
            continue
        tgt = choose_matched_task(pool, src, forbidden=forbidden, rng=rng)
        if tgt:
            rows.append(pair_from_names(df, str(src["task_name"]), tgt, "unrelated_matched", rng))
        if len(rows) >= max_pairs * 3:
            break

    # Deduplicate, then stratified-downsample by pair_type.
    dedup: dict[tuple[str, str, str], CouplingPair] = {}
    for r in rows:
        if r.source_task == r.target_task:
            continue
        dedup.setdefault((r.source_task, r.target_task, r.pair_type), r)
    plan = pd.DataFrame([r.to_row() for r in dedup.values()])
    if plan.empty:
        raise ValueError("No valid coupling pairs could be built from the structure table.")
    plan = stratified_limit(plan, max_pairs=max_pairs, seed=seed)
    plan = plan.reset_index(drop=True)
    plan["pair_index"] = np.arange(len(plan), dtype=int)
    plan["pair_id"] = [f"P{i:03d}_{sanitize(a)}__to__{sanitize(b)}" for i, (a, b) in enumerate(zip(plan["source_task"], plan["target_task"]))]
    # Put pair_id first.
    cols = ["pair_id", "pair_index"] + [c for c in plan.columns if c not in {"pair_id", "pair_index"}]
    return plan[cols]


def pair_from_names(df: pd.DataFrame, source: str, target: str, pair_type: str, rng: np.random.Generator) -> CouplingPair:
    s = df[df["task_name"].astype(str).eq(str(source))]
    t = df[df["task_name"].astype(str).eq(str(target))]
    if s.empty or t.empty:
        raise ValueError(f"Unknown pair task(s): source={source!r}, target={target!r}")
    sr = s.iloc[0]
    tr = t.iloc[0]
    filler = choose_filler(df, source=str(source), target=str(target), reference=sr, rng=rng)
    formal_relation = "none"
    target_components = {x for x in str(tr.get("components", "")).split(",") if x and x != "nan"}
    source_components = {x for x in str(sr.get("components", "")).split(",") if x and x != "nan"}
    if str(source) in target_components:
        formal_relation = "source_is_target_component"
    elif str(target) in source_components:
        formal_relation = "target_is_source_component"
    elif str(sr.get("op", "")) == str(tr.get("op", "")):
        formal_relation = "same_operation"
    return CouplingPair(
        pair_id="",
        source_task=str(source),
        target_task=str(target),
        pair_type=pair_type,
        filler_task=filler,
        source_kind=str(sr.get("kind", "")),
        target_kind=str(tr.get("kind", "")),
        source_op=str(sr.get("op", "")),
        target_op=str(tr.get("op", "")),
        source_frequency=float(sr.get("frequency", np.nan)),
        target_frequency=float(tr.get("frequency", np.nan)),
        source_reference_learnability=float(sr.get("reference_learnability", np.nan)),
        target_reference_learnability=float(tr.get("reference_learnability", np.nan)),
        surface_overlap_proxy=token_overlap_proxy(str(source), str(target)),
        formal_relation=formal_relation,
    )


def choose_filler(df: pd.DataFrame, source: str, target: str, reference: pd.Series, rng: np.random.Generator) -> str:
    forbidden = {source, target}
    pool = df[~df["task_name"].astype(str).isin(forbidden)].copy()
    # Prefer unrelated/control tasks, then different-operation atomics, but never the target.
    if "kind" in pool.columns:
        priority = pool["kind"].astype(str).str.contains("unrelated|surface|shortcut", regex=True, na=False).astype(int)
        pool["_priority"] = -priority
    else:
        pool["_priority"] = 0
    if "op" in pool.columns:
        pool["_same_op"] = pool["op"].astype(str).eq(str(reference.get("op", ""))).astype(int)
    else:
        pool["_same_op"] = 0
    return choose_matched_task(pool, reference, forbidden=forbidden, rng=rng) or str(pool.iloc[0]["task_name"])


def choose_matched_task(pool: pd.DataFrame, reference: pd.Series, forbidden: set[str], rng: np.random.Generator) -> str | None:
    cand = pool[~pool["task_name"].astype(str).isin(forbidden)].copy()
    if cand.empty:
        return None
    ref_freq = float(reference.get("frequency", np.nan))
    ref_learn = float(reference.get("reference_learnability", np.nan))
    cand["_score"] = 0.0
    if "_priority" in cand.columns:
        cand["_score"] += cand["_priority"].astype(float)
    if "_same_op" in cand.columns:
        cand["_score"] += 0.5 * cand["_same_op"].astype(float)
    if np.isfinite(ref_freq):
        cand["_score"] += (np.log(np.maximum(pd.to_numeric(cand["frequency"], errors="coerce"), 1e-12)) - np.log(max(ref_freq, 1e-12))).abs()
    if np.isfinite(ref_learn):
        cand["_score"] += 0.25 * (pd.to_numeric(cand["reference_learnability"], errors="coerce") - ref_learn).abs()
    cand = cand.sort_values(["_score", "task_name"])
    # deterministic after scoring; rng only used in future if ties need randomization.
    return str(cand.iloc[0]["task_name"])


def stratified_limit(plan: pd.DataFrame, max_pairs: int, seed: int) -> pd.DataFrame:
    if len(plan) <= max_pairs:
        return plan.copy()
    rng = np.random.default_rng(seed)
    groups = {k: g.copy() for k, g in plan.groupby("pair_type", sort=True)}
    selected = []
    # Round-robin through pair types to preserve heterogeneity.
    while len(selected) < max_pairs and groups:
        for k in list(groups):
            g = groups[k]
            if g.empty:
                groups.pop(k, None)
                continue
            idx = int(rng.integers(0, len(g)))
            selected.append(g.iloc[idx])
            groups[k] = g.drop(g.index[idx]).reset_index(drop=True)
            if len(selected) >= max_pairs:
                break
    return pd.DataFrame(selected)


def token_overlap_proxy(a: str, b: str) -> float:
    aset = {x for x in a.replace("-", "_").split("_") if x}
    bset = {x for x in b.replace("-", "_").split("_") if x}
    if not aset and not bset:
        return 0.0
    return len(aset & bset) / max(1, len(aset | bset))


def sanitize(s: str) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in str(s))[:80]


def make_dose_weights(
    base_weights: torch.Tensor,
    source_idx: int,
    target_idx: int,
    filler_idx: int,
    multiplier: float,
) -> torch.Tensor:
    """Return a fixed-budget task sampling distribution for one source-dose level.

    The target task's base weight is preserved whenever possible. Increasing the source
    displaces a matched filler first, then a non-target pool if necessary. Removing or
    lowering the source sends the freed mass to the filler. This makes the measured
    effect closer to A-specific transfer/interference than a generic data-budget effect.
    """

    weights = base_weights.clone().float()
    if source_idx < 0 or source_idx >= len(weights):
        raise IndexError(f"source_idx out of range: {source_idx}")
    if target_idx == source_idx:
        raise ValueError("source and target must be different tasks")
    filler_idx = int(filler_idx) if 0 <= int(filler_idx) < len(weights) and int(filler_idx) not in {source_idx, target_idx} else -1
    original_source = weights[source_idx].clone()
    desired_source = torch.clamp(original_source * float(multiplier), min=0.0, max=0.95)
    delta = desired_source - original_source
    weights[source_idx] = desired_source
    if abs(float(delta.item())) < 1e-12:
        return weights / weights.sum().clamp_min(1e-12)
    if delta < 0:
        # Freed mass goes into matched filler.
        if filler_idx >= 0:
            weights[filler_idx] += -delta
        else:
            pool = torch.ones_like(weights, dtype=torch.bool)
            pool[source_idx] = False
            pool[target_idx] = False
            weights[pool] += (-delta) / max(1, int(pool.sum().item()))
    else:
        remaining = float(delta.item())
        if filler_idx >= 0:
            take = min(float(weights[filler_idx].item()), remaining)
            weights[filler_idx] -= take
            remaining -= take
        if remaining > 1e-12:
            pool = torch.ones_like(weights, dtype=torch.bool)
            pool[source_idx] = False
            pool[target_idx] = False
            if filler_idx >= 0:
                pool[filler_idx] = False
            total_pool = float(weights[pool].sum().item())
            if total_pool > 1e-12:
                frac = min(1.0, remaining / total_pool)
                weights[pool] *= (1.0 - frac)
                remaining -= total_pool * frac
        if remaining > 1e-8:
            # If there is not enough unrelated mass, shrink everything except the target
            # proportionally. This is recorded in realized-frequency diagnostics downstream.
            pool = torch.ones_like(weights, dtype=torch.bool)
            pool[source_idx] = False
            pool[target_idx] = False
            total_pool = float(weights[pool].sum().item())
            if total_pool > 1e-12:
                frac = min(1.0, remaining / total_pool)
                weights[pool] *= (1.0 - frac)
    weights = torch.clamp(weights, min=0.0)
    if float(weights.sum().item()) <= 0:
        return base_weights / base_weights.sum().clamp_min(1e-12)
    return weights / weights.sum().clamp_min(1e-12)


def trapezoid_auc(x: Iterable[float], y: Iterable[float]) -> float:
    xs = np.asarray(list(x), dtype=float)
    ys = np.asarray(list(y), dtype=float)
    ok = np.isfinite(xs) & np.isfinite(ys)
    xs = xs[ok]
    ys = ys[ok]
    if len(xs) == 0:
        return float("nan")
    if len(xs) == 1:
        return float(ys[0])
    order = np.argsort(xs)
    xs = xs[order]
    ys = ys[order]
    span = float(xs[-1] - xs[0])
    if span <= 0:
        return float(np.nanmean(ys))
    return float(np.trapz(ys, xs) / span)


def linear_slope(x: Iterable[float], y: Iterable[float]) -> float:
    xs = np.asarray(list(x), dtype=float)
    ys = np.asarray(list(y), dtype=float)
    ok = np.isfinite(xs) & np.isfinite(ys)
    xs = xs[ok]
    ys = ys[ok]
    if len(xs) < 2 or float(np.var(xs)) <= 1e-12:
        return float("nan")
    return float(np.polyfit(xs, ys, deg=1)[0])


def bootstrap_ci(values: Iterable[float], n_bootstrap: int = 2000, seed: int = 0, alpha: float = 0.05) -> tuple[float, float, float]:
    arr = np.asarray([v for v in values if np.isfinite(v)], dtype=float)
    if len(arr) == 0:
        return float("nan"), float("nan"), float("nan")
    mean = float(np.mean(arr))
    if len(arr) == 1 or n_bootstrap <= 0:
        return mean, mean, mean
    rng = np.random.default_rng(seed)
    boots = np.asarray([np.mean(rng.choice(arr, size=len(arr), replace=True)) for _ in range(int(n_bootstrap))], dtype=float)
    lo, hi = np.quantile(boots, [alpha / 2, 1 - alpha / 2])
    return mean, float(lo), float(hi)
