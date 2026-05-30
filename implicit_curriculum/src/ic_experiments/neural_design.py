from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from pathlib import Path

import numpy as np
import pandas as pd

from .design import DesignCriteria, design_diagnostics, passes_design_criteria
from .tasks import TaskSpec, compute_formal_utilities, task_table


@dataclass(frozen=True)
class NeuralDesignConfig:
    """Configuration for generated neural task families.

    The generator searches over concrete Boolean task families until the realized
    structural properties are sufficiently decorrelated. Unlike the synthetic
    recovery gate, this returns actual trainable TaskSpec objects.
    """

    n_atomic: int = 12
    n_composite: int = 8
    n_shortcut_controls: int = 4
    n_surface_controls: int = 4
    n_unrelated_controls: int = 4
    n_bits: int = 48
    frequency_low: float = 0.01
    frequency_high: float = 0.12
    seed: int = 0
    max_attempts: int = 10_000
    include_xor_composites: bool = False
    criteria: DesignCriteria = DesignCriteria(min_rows=24, max_abs_pearson=0.70, max_abs_spearman=0.75)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["criteria"] = asdict(self.criteria)
        return d


ATOM_OPS = ("bit", "not_bit", "and_bits", "or_bits", "xor2", "eq2")
EASY_ATOM_OPS = ("bit", "not_bit")
MEDIUM_ATOM_OPS = ("and_bits", "or_bits", "eq2")
HARD_ATOM_OPS = ("xor2",)


@dataclass(frozen=True)
class NeuralFamilyResult:
    tasks: list[TaskSpec]
    diagnostics: dict[str, float | bool]
    attempts_used: int
    passed: bool
    config: NeuralDesignConfig

    def metadata(self) -> dict:
        return {
            "config": self.config.to_dict(),
            "diagnostics": self.diagnostics,
            "attempts_used": self.attempts_used,
            "passed": self.passed,
        }


def generate_neural_task_family(config: NeuralDesignConfig) -> NeuralFamilyResult:
    """Generate a concrete task family with decorrelated realized properties."""

    rng = np.random.default_rng(config.seed)
    best_tasks: list[TaskSpec] | None = None
    best_diag: dict[str, float | bool] | None = None
    best_score = float("inf")
    best_attempt = 0

    for attempt in range(1, config.max_attempts + 1):
        tasks = _sample_family_once(config, rng, attempt)
        diagnostics = neural_family_diagnostics(tasks)
        score = _neural_design_score(diagnostics, config.criteria)
        if score < best_score:
            best_score = score
            best_tasks = tasks
            best_diag = dict(diagnostics)
            best_attempt = attempt
        if passes_design_criteria(diagnostics, config.criteria):
            diagnostics = dict(diagnostics)
            diagnostics["attempts_used"] = float(attempt)
            diagnostics["passed"] = True
            return NeuralFamilyResult(tasks=tasks, diagnostics=diagnostics, attempts_used=attempt, passed=True, config=config)

    assert best_tasks is not None and best_diag is not None
    best_diag = dict(best_diag)
    best_diag["attempts_used"] = float(best_attempt)
    best_diag["passed"] = False
    return NeuralFamilyResult(tasks=best_tasks, diagnostics=best_diag, attempts_used=best_attempt, passed=False, config=config)


def _sample_family_once(config: NeuralDesignConfig, rng: np.random.Generator, attempt: int) -> list[TaskSpec]:
    used_bit_pairs: set[tuple[int, ...]] = set()
    tasks: list[TaskSpec] = []

    # Mix easy/medium/hard atomics so reference learnability is not degenerate.
    op_schedule: list[str] = []
    n_easy = max(2, config.n_atomic // 3)
    n_medium = max(2, config.n_atomic // 3)
    n_hard = max(1, config.n_atomic - n_easy - n_medium)
    op_schedule.extend(rng.choice(EASY_ATOM_OPS, size=n_easy, replace=True).tolist())
    op_schedule.extend(rng.choice(MEDIUM_ATOM_OPS, size=n_medium, replace=True).tolist())
    op_schedule.extend(rng.choice(HARD_ATOM_OPS, size=n_hard, replace=True).tolist())
    rng.shuffle(op_schedule)

    for i, op in enumerate(op_schedule[: config.n_atomic]):
        bits = _fresh_bits_for_op(op, config.n_bits, rng, used_bit_pairs)
        tasks.append(
            TaskSpec(
                name=f"A{i:02d}_{op}_{'_'.join(map(str, bits))}",
                kind="atomic",
                op=op,
                bits=bits,
                frequency=_sample_frequency(config, rng),
                reference_learnability=_reference_learnability(op),
                description=f"Generated atomic task {i}: {op} on bits {bits}.",
            )
        )

    atomic_names = [t.name for t in tasks]
    composite_ops = ["and_components", "or_components"]
    if config.include_xor_composites:
        composite_ops.append("xor_components")

    # Encourage utility decorrelation by choosing components according to random
    # latent component propensity rather than their own frequency.
    component_propensity = rng.gamma(shape=1.2, scale=1.0, size=len(atomic_names))
    component_propensity = component_propensity / component_propensity.sum()
    for j in range(config.n_composite):
        c1, c2 = rng.choice(len(atomic_names), size=2, replace=False, p=component_propensity)
        op = str(rng.choice(composite_ops))
        # Keep XOR composites rare unless explicitly included because v0.2 showed
        # XOR-style composites can become too hard for clean dependency tests.
        learn = 1.0 + max(tasks[int(c1)].reference_learnability, tasks[int(c2)].reference_learnability)
        if op == "xor_components":
            learn += 1.0
        tasks.append(
            TaskSpec(
                name=f"C{j:02d}_{op.replace('_components','')}_{c1:02d}_{c2:02d}",
                kind="composite",
                op=op,
                components=(atomic_names[int(c1)], atomic_names[int(c2)]),
                frequency=_sample_frequency(config, rng),
                reference_learnability=float(learn),
                description=f"Generated composite task {j}: {op} over atomics {c1} and {c2}.",
            )
        )

    # Shortcut/no-reuse controls: formally list a component, but label comes from a
    # fresh bit. They should not be counted as true utility edges by downstream
    # analysis, so utility is recomputed with include_kinds=(composite,) below.
    for k in range(config.n_shortcut_controls):
        comp_idx = int(rng.choice(len(atomic_names), p=component_propensity))
        bit = _fresh_single_bit(config.n_bits, rng, used_bit_pairs)
        tasks.append(
            TaskSpec(
                name=f"K{k:02d}_shortcut_for_{comp_idx:02d}_bit{bit}",
                kind="shortcut",
                op="shortcut_bit",
                bits=(bit,),
                components=(atomic_names[comp_idx],),
                frequency=_sample_frequency(config, rng),
                reference_learnability=1.0,
                description="Symbolic-dependency/no-reuse negative control: formal component but direct shortcut label.",
            )
        )

    for k in range(config.n_surface_controls):
        bits = _fresh_bits_for_op("xor2", config.n_bits, rng, used_bit_pairs)
        tasks.append(
            TaskSpec(
                name=f"S{k:02d}_surface_xor_{bits[0]}_{bits[1]}",
                kind="surface_control",
                op="surface_control",
                bits=bits,
                frequency=_sample_frequency(config, rng),
                reference_learnability=2.0,
                description="Surface-overlap/no-dependency control.",
            )
        )

    unrelated_ops = ("xor2", "eq2", "and_bits", "or_bits")
    for k in range(config.n_unrelated_controls):
        op = str(rng.choice(unrelated_ops))
        bits = _fresh_bits_for_op(op, config.n_bits, rng, used_bit_pairs)
        tasks.append(
            TaskSpec(
                name=f"U{k:02d}_{op}_{bits[0]}_{bits[1]}",
                kind="unrelated",
                op=op,
                bits=bits,
                frequency=_sample_frequency(config, rng),
                reference_learnability=_reference_learnability(op),
                description="Unrelated frequency/learnability-matched control pool.",
            )
        )

    # Normalize frequencies and compute true formal utility from actual composites
    # only. Shortcut controls intentionally do not contribute to utility.
    total = sum(t.frequency for t in tasks)
    tasks = [replace(t, frequency=t.frequency / total) for t in tasks]
    utilities = compute_formal_utilities_for_kinds(tasks, include_kinds=("composite",))
    tasks = [replace(t, formal_utility=utilities[t.name]) for t in tasks]

    # To make some high-utility atomics not automatically high-frequency, randomly
    # shuffle frequencies within kind after utility is assigned on some attempts.
    # This preserves the task graph while helping the search pass decorrelation.
    if attempt % 2 == 0:
        tasks = _shuffle_frequencies_within_kind(tasks, rng)
    return tasks


def compute_formal_utilities_for_kinds(tasks: list[TaskSpec], include_kinds: tuple[str, ...] = ("composite",)) -> dict[str, float]:
    utilities = {t.name: 0.0 for t in tasks}
    for t in tasks:
        if t.kind not in include_kinds:
            continue
        for component in t.components:
            utilities[component] = utilities.get(component, 0.0) + t.frequency
    return utilities


def neural_family_diagnostics(tasks: list[TaskSpec]) -> dict[str, float | bool]:
    df = task_table(tasks)
    diag = design_diagnostics(df)
    diag["n_tasks"] = float(len(tasks))
    diag["n_atomic"] = float((df["kind"] == "atomic").sum())
    diag["n_composite"] = float((df["kind"] == "composite").sum())
    diag["n_controls"] = float((~df["kind"].isin(["atomic", "composite"])).sum())
    diag["frequency_sum"] = float(df["frequency"].sum())
    diag["utility_nonzero_rate"] = float((df["formal_utility"] > 0).mean())
    return diag


def save_neural_family(result: NeuralFamilyResult, output_dir: str | Path) -> dict[str, str]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    paths = {
        "structure_table": str(output_path / "structure_table.csv"),
        "design_diagnostics": str(output_path / "design_diagnostics.csv"),
        "summary": str(output_path / "summary.json"),
        "report": str(output_path / "neural_design_report.md"),
    }
    task_table(result.tasks).to_csv(paths["structure_table"], index=False)
    pd.DataFrame([result.diagnostics]).to_csv(paths["design_diagnostics"], index=False)
    import json

    summary = result.metadata()
    summary["paths"] = paths
    Path(paths["summary"]).write_text(json.dumps(summary, indent=2), encoding="utf-8")
    Path(paths["report"]).write_text(_render_report(result), encoding="utf-8")
    return paths


def load_neural_family(path: str | Path) -> list[TaskSpec]:
    df = pd.read_csv(path)
    tasks: list[TaskSpec] = []
    for row in df.to_dict(orient="records"):
        bits = tuple(int(x) for x in str(row.get("bits", "")).split(",") if x != "" and x != "nan")
        components = tuple(x for x in str(row.get("components", "")).split(",") if x != "" and x != "nan")
        tasks.append(
            TaskSpec(
                name=str(row["task_name"]),
                kind=str(row["kind"]),
                op=str(row["op"]),
                bits=bits,
                components=components,
                frequency=float(row["frequency"]),
                reference_learnability=float(row["reference_learnability"]),
                formal_utility=float(row["formal_utility"]),
                description=str(row.get("description", "")),
            )
        )
    return tasks


def choose_default_component_and_controls(tasks: list[TaskSpec]) -> dict[str, str | list[str]]:
    """Choose a high-utility component, composites using it, and matched controls."""

    df = task_table(tasks)
    atomics = df[df["kind"] == "atomic"].copy()
    if atomics.empty:
        raise ValueError("No atomic tasks in family")
    # For intervention pilots, prefer a component that is both useful and likely
    # to be learnable. The ordering/H2 analyses still use all tasks; this choice
    # only selects a stable target for causal pilot diagnostics.
    learnable = atomics[atomics["reference_learnability"] <= 2.0].copy()
    candidates = learnable if not learnable.empty else atomics
    candidates = candidates.sort_values(["formal_utility", "reference_learnability", "frequency"], ascending=[False, True, False])
    component = str(candidates.iloc[0]["task_name"])
    composites = [t.name for t in tasks if t.kind == "composite" and component in t.components]
    if not composites:
        # Fall back to the highest-utility component with at least one composite.
        for _, row in atomics.sort_values(["formal_utility", "reference_learnability"], ascending=[False, True]).iterrows():
            maybe = str(row["task_name"])
            maybe_comps = [t.name for t in tasks if t.kind == "composite" and maybe in t.components]
            if maybe_comps:
                component = maybe
                composites = maybe_comps
                break
    if not composites:
        composites = [t.name for t in tasks if t.kind == "composite"][:2]
    component_row = atomics[atomics["task_name"] == component].iloc[0]
    component_freq = float(component_row["frequency"])
    component_learn = float(component_row["reference_learnability"])

    controls = df[df["kind"].isin(["unrelated", "surface_control", "shortcut"])].copy()
    controls["match_distance"] = (np.log(controls["frequency"] + 1e-12) - np.log(component_freq + 1e-12)).abs() + 0.25 * (controls["reference_learnability"] - component_learn).abs()
    unrelated = controls[controls["kind"] == "unrelated"].sort_values("match_distance")
    fake = controls[controls["kind"] == "shortcut"].sort_values("match_distance")
    surface = controls[controls["kind"] == "surface_control"].sort_values("match_distance")
    return {
        "component": component,
        "composites": composites[:3],
        "unrelated_control": str(unrelated.iloc[0]["task_name"]) if not unrelated.empty else str(controls.iloc[0]["task_name"]),
        "fake_component_control": str(fake.iloc[0]["task_name"]) if not fake.empty else str(controls.iloc[0]["task_name"]),
        "surface_control": str(surface.iloc[0]["task_name"]) if not surface.empty else str(controls.iloc[0]["task_name"]),
    }


def _sample_frequency(config: NeuralDesignConfig, rng: np.random.Generator) -> float:
    return float(np.exp(rng.uniform(np.log(config.frequency_low), np.log(config.frequency_high))))


def _reference_learnability(op: str) -> float:
    if op in {"bit", "not_bit", "shortcut_bit"}:
        return 1.0
    if op in {"and_bits", "or_bits", "eq2"}:
        return 2.0
    if op in {"xor2", "surface_control"}:
        return 2.5
    if op in {"and_components", "or_components"}:
        return 3.0
    if op == "xor_components":
        return 4.0
    return 2.0


def _fresh_single_bit(n_bits: int, rng: np.random.Generator, used: set[tuple[int, ...]]) -> int:
    for _ in range(1000):
        bit = int(rng.integers(0, n_bits))
        key = (bit,)
        if key not in used:
            used.add(key)
            return bit
    bit = int(rng.integers(0, n_bits))
    used.add((bit,))
    return bit


def _fresh_bits_for_op(op: str, n_bits: int, rng: np.random.Generator, used: set[tuple[int, ...]]) -> tuple[int, ...]:
    if op in {"bit", "not_bit", "shortcut_bit"}:
        return (_fresh_single_bit(n_bits, rng, used),)
    for _ in range(1000):
        a, b = rng.choice(n_bits, size=2, replace=False)
        key = tuple(sorted((int(a), int(b))))
        if key not in used:
            used.add(key)
            return (int(a), int(b))
    a, b = rng.choice(n_bits, size=2, replace=False)
    return (int(a), int(b))


def _shuffle_frequencies_within_kind(tasks: list[TaskSpec], rng: np.random.Generator) -> list[TaskSpec]:
    new_tasks = list(tasks)
    for kind in sorted({t.kind for t in tasks}):
        idx = [i for i, t in enumerate(tasks) if t.kind == kind]
        freqs = [tasks[i].frequency for i in idx]
        rng.shuffle(freqs)
        for i, freq in zip(idx, freqs):
            new_tasks[i] = replace(new_tasks[i], frequency=float(freq))
    total = sum(t.frequency for t in new_tasks)
    new_tasks = [replace(t, frequency=t.frequency / total) for t in new_tasks]
    utilities = compute_formal_utilities_for_kinds(new_tasks, include_kinds=("composite",))
    return [replace(t, formal_utility=utilities[t.name]) for t in new_tasks]


def _neural_design_score(diag: dict[str, float | bool], criteria: DesignCriteria) -> float:
    score = max(0.0, float(diag["design_condition_number"]) / criteria.max_condition_number - 1.0)
    for key, value in diag.items():
        if key.startswith("vif_"):
            score += max(0.0, float(value) / criteria.max_vif - 1.0)
        elif key.startswith("pearson_"):
            score += max(0.0, abs(float(value)) / criteria.max_abs_pearson - 1.0)
        elif key.startswith("spearman_"):
            score += max(0.0, abs(float(value)) / criteria.max_abs_spearman - 1.0)
    # Prefer nontrivial utility coverage.
    score += max(0.0, 0.15 - float(diag.get("utility_nonzero_rate", 0.0)))
    return score


def _render_report(result: NeuralFamilyResult) -> str:
    diag = result.diagnostics
    lines = [
        "# Neural design gate report",
        "",
        "This gate generates an actual trainable Boolean task family and checks whether realized structural properties are identifiable enough for H1/H2-style neural experiments.",
        "",
        f"Passed: **{bool(result.passed)}**",
        f"Attempts used: `{result.attempts_used}`",
        "",
        "## Key diagnostics",
        "",
        f"- n_tasks: `{int(diag.get('n_tasks', len(result.tasks)))}`",
        f"- design_condition_number: `{float(diag['design_condition_number']):.4g}`",
        f"- vif_frequency: `{float(diag['vif_frequency']):.4g}`",
        f"- vif_reference_learnability: `{float(diag['vif_reference_learnability']):.4g}`",
        f"- vif_formal_utility: `{float(diag['vif_formal_utility']):.4g}`",
        f"- max_abs_pearson: `{max(abs(float(v)) for k, v in diag.items() if k.startswith('pearson_')):.4g}`",
        f"- max_abs_spearman: `{max(abs(float(v)) for k, v in diag.items() if k.startswith('spearman_')):.4g}`",
        "",
        "## Interpretation",
        "",
        "If this gate passes, the generated neural family is suitable for a first ordering pilot. It does not yet prove that neural acquisition follows the intended structural predictors; it only licenses fitting them without obvious collinearity failure.",
    ]
    return "\n".join(lines)
