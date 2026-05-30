from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable

import numpy as np
import pandas as pd
import torch


@dataclass(frozen=True)
class TaskSpec:
    """A labeled sub-task in the controlled mixed distribution.

    Attributes
    ----------
    name:
        Stable task identifier.
    kind:
        atomic, composite, shortcut, surface_control, or unrelated.
    op:
        Operation used to generate labels. Component operations recursively call
        other TaskSpecs; bit operations read raw input bits directly.
    bits:
        Raw bit indices used by bit-level operations.
    components:
        Formal component tasks used by composite or shortcut structures.
    frequency:
        Mixture rate before normalization.
    reference_learnability:
        Ex ante difficulty proxy. In this first pilot this is hand-specified by
        computation depth; later versions should support DSL-MDL and single-task
        sample-complexity measurement.
    formal_utility:
        Filled in after the task family is built.
    description:
        Human-readable role in the pilot.
    """

    name: str
    kind: str
    op: str
    bits: tuple[int, ...] = ()
    components: tuple[str, ...] = ()
    frequency: float = 1.0
    reference_learnability: float = 1.0
    formal_utility: float = 0.0
    description: str = ""


def _xor_float(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    return ((a.long() ^ b.long()).float())


def _eq_float(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    return (a.long() == b.long()).float()


def labels_for_task(
    task: TaskSpec,
    bits: torch.Tensor,
    tasks_by_name: dict[str, TaskSpec],
    _stack: tuple[str, ...] = (),
) -> torch.Tensor:
    """Return binary labels for a task and raw Bernoulli bit matrix.

    Parameters
    ----------
    task:
        Task to evaluate.
    bits:
        Tensor of shape [batch, n_bits], values in {0, 1}.
    tasks_by_name:
        Lookup table for recursive component definitions.
    _stack:
        Internal recursion guard.
    """

    if task.name in _stack:
        raise ValueError(f"Cycle detected in task graph: {_stack + (task.name,)}")

    op = task.op
    if op == "bit":
        return bits[:, task.bits[0]].float()
    if op == "not_bit":
        return 1.0 - bits[:, task.bits[0]].float()
    if op == "xor2":
        return _xor_float(bits[:, task.bits[0]], bits[:, task.bits[1]])
    if op == "eq2":
        return _eq_float(bits[:, task.bits[0]], bits[:, task.bits[1]])
    if op == "and_bits":
        return (bits[:, task.bits[0]].long() & bits[:, task.bits[1]].long()).float()
    if op == "or_bits":
        return (bits[:, task.bits[0]].long() | bits[:, task.bits[1]].long()).float()
    if op == "and_components":
        a = labels_for_task(tasks_by_name[task.components[0]], bits, tasks_by_name, _stack + (task.name,))
        b = labels_for_task(tasks_by_name[task.components[1]], bits, tasks_by_name, _stack + (task.name,))
        return (a.long() & b.long()).float()
    if op == "or_components":
        a = labels_for_task(tasks_by_name[task.components[0]], bits, tasks_by_name, _stack + (task.name,))
        b = labels_for_task(tasks_by_name[task.components[1]], bits, tasks_by_name, _stack + (task.name,))
        return (a.long() | b.long()).float()
    if op == "xor_components":
        a = labels_for_task(tasks_by_name[task.components[0]], bits, tasks_by_name, _stack + (task.name,))
        b = labels_for_task(tasks_by_name[task.components[1]], bits, tasks_by_name, _stack + (task.name,))
        return _xor_float(a, b)
    if op == "shortcut_bit":
        # Formally declares a component but the label is available from a direct
        # shortcut bit. This is a negative control for symbolic-dependency claims.
        return bits[:, task.bits[0]].float()
    if op == "surface_control":
        # Shares the same input surface as all other tasks but is semantically
        # unrelated. Later sequence variants should implement stronger surface
        # matching via token overlap.
        return _xor_float(bits[:, task.bits[0]], bits[:, task.bits[1]])

    raise ValueError(f"Unknown task op: {op}")


def build_pilot_tasks() -> list[TaskSpec]:
    """Construct the minimum decisive pilot task family.

    This first family intentionally has simple Boolean tasks. It is meant to
    validate the pipeline and reveal failure modes, not to carry the final paper.
    """

    raw = [
        TaskSpec(
            name="A_bit0",
            kind="atomic",
            op="bit",
            bits=(0,),
            frequency=0.20,
            reference_learnability=1.0,
            description="Atomic component A: read bit 0.",
        ),
        TaskSpec(
            name="B_bit1",
            kind="atomic",
            op="bit",
            bits=(1,),
            frequency=0.14,
            reference_learnability=1.0,
            description="Atomic component B: read bit 1.",
        ),
        TaskSpec(
            name="C_xor23",
            kind="atomic",
            op="xor2",
            bits=(2, 3),
            frequency=0.10,
            reference_learnability=2.0,
            description="Atomic component C: XOR of bits 2 and 3.",
        ),
        TaskSpec(
            name="D_eq45",
            kind="atomic",
            op="eq2",
            bits=(4, 5),
            frequency=0.08,
            reference_learnability=2.0,
            description="Atomic component D: equality of bits 4 and 5.",
        ),
        TaskSpec(
            name="AB_and",
            kind="composite",
            op="and_components",
            components=("A_bit0", "B_bit1"),
            frequency=0.14,
            reference_learnability=2.0,
            description="Composite C1: formal AND of components A and B.",
        ),
        TaskSpec(
            name="AC_xor",
            kind="composite",
            op="xor_components",
            components=("A_bit0", "C_xor23"),
            frequency=0.10,
            reference_learnability=3.0,
            description="Composite C2: formal XOR of components A and C.",
        ),
        TaskSpec(
            name="A_shortcut_bit6",
            kind="shortcut",
            op="shortcut_bit",
            bits=(6,),
            components=("A_bit0",),
            frequency=0.08,
            reference_learnability=1.0,
            description="Negative control: formally references A, but label is shortcut bit 6.",
        ),
        TaskSpec(
            name="surface_control_78",
            kind="surface_control",
            op="surface_control",
            bits=(7, 8),
            frequency=0.08,
            reference_learnability=2.0,
            description="Surface/control task without formal dependency.",
        ),
        TaskSpec(
            name="U_unrelated_xor910",
            kind="unrelated",
            op="xor2",
            bits=(9, 10),
            frequency=0.08,
            reference_learnability=2.0,
            description="Unrelated matched-control task.",
        ),
    ]

    total = sum(t.frequency for t in raw)
    normalized = [replace(t, frequency=t.frequency / total) for t in raw]
    utilities = compute_formal_utilities(normalized)
    return [replace(t, formal_utility=utilities[t.name]) for t in normalized]


def compute_formal_utilities(tasks: Iterable[TaskSpec]) -> dict[str, float]:
    tasks = list(tasks)
    utilities = {t.name: 0.0 for t in tasks}
    for t in tasks:
        for component in t.components:
            utilities[component] = utilities.get(component, 0.0) + t.frequency
    return utilities


def task_table(tasks: list[TaskSpec]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "task_name": t.name,
                "kind": t.kind,
                "op": t.op,
                "bits": ",".join(map(str, t.bits)),
                "components": ",".join(t.components),
                "frequency": t.frequency,
                "reference_learnability": t.reference_learnability,
                "formal_utility": t.formal_utility,
                "description": t.description,
            }
            for t in tasks
        ]
    )


def structural_design_diagnostics(tasks: list[TaskSpec]) -> dict[str, float]:
    """Basic identifiability diagnostics for the current task family.

    This is a lightweight first pass. The full H1/H2 implementation should add
    VIF-targeted task generation, nonlinear design diagnostics, and simulated
    recovery gates.
    """

    df = task_table(tasks)
    x = df[["frequency", "reference_learnability", "formal_utility"]].to_numpy(dtype=float)
    x_centered = x - x.mean(axis=0, keepdims=True)
    corr = np.corrcoef(x_centered.T)
    cond = float(np.linalg.cond(np.column_stack([np.ones(len(x)), x])))

    out: dict[str, float] = {"design_condition_number": cond}
    names = ["frequency", "reference_learnability", "formal_utility"]
    for i, ni in enumerate(names):
        for j, nj in enumerate(names):
            if i < j:
                out[f"pearson_{ni}__{nj}"] = float(corr[i, j])
    out.update(_vif_dict(x, names))
    return out


def _vif_dict(x: np.ndarray, names: list[str]) -> dict[str, float]:
    out = {}
    for i, name in enumerate(names):
        y = x[:, i]
        other = np.delete(x, i, axis=1)
        design = np.column_stack([np.ones(len(y)), other])
        beta, *_ = np.linalg.lstsq(design, y, rcond=None)
        pred = design @ beta
        ss_res = float(((y - pred) ** 2).sum())
        ss_tot = float(((y - y.mean()) ** 2).sum())
        r2 = 1.0 - ss_res / max(ss_tot, 1e-12)
        out[f"vif_{name}"] = float(1.0 / max(1.0 - r2, 1e-12))
    return out
