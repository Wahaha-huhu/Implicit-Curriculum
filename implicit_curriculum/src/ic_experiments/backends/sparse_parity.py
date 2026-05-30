from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from pathlib import Path

import numpy as np
import pandas as pd

from ic_experiments.backends.base import StructureSpec, structure_specs_to_frame
from ic_experiments.design import DesignCriteria, design_diagnostics, passes_design_criteria
from ic_experiments.neural_design import save_neural_family
from ic_experiments.tasks import TaskSpec, task_table


@dataclass(frozen=True)
class SparseParityConfig:
    """Quanta-comparable multitask sparse parity backend.

    Each structure is a parity of a fixed sparse subset of input bits. Frequency is
    controlled directly. Degree is a reference-learnability knob. This backend is
    intentionally close to the quantization-model toy, so frequency-only outcomes
    here are interpretable as a baseline rather than a failure.
    """

    n_bits: int = 40
    n_tasks: int = 24
    degrees: tuple[int, ...] = (3, 5)
    frequency_mode: str = "zipf"  # zipf or uniform
    zipf_alpha: float = 1.1
    seed: int = 0
    criteria: DesignCriteria = DesignCriteria(min_rows=16, max_abs_pearson=0.75, max_abs_spearman=0.80)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["criteria"] = asdict(self.criteria)
        return d


@dataclass(frozen=True)
class SparseParityFamily:
    tasks: list[TaskSpec]
    specs: list[StructureSpec]
    diagnostics: dict[str, float | bool]
    passed: bool
    config: SparseParityConfig

    @property
    def name(self) -> str:
        return "B2_sparse_parity"

    def structure_table(self) -> pd.DataFrame:
        # Preserve the old TaskSpec columns so existing MLP training commands can
        # load the table, while also adding backend-agnostic columns.
        df = task_table(self.tasks)
        df["backend"] = self.name
        df["structure_id"] = df["task_name"]
        df["control_type"] = ""
        df["control_for"] = ""
        return df

    def generic_structure_table(self) -> pd.DataFrame:
        return structure_specs_to_frame(self.specs)

    def metadata(self) -> dict:
        return {
            "backend": self.name,
            "config": self.config.to_dict(),
            "diagnostics": self.diagnostics,
            "passed": self.passed,
        }


def generate_sparse_parity_family(config: SparseParityConfig) -> SparseParityFamily:
    rng = np.random.default_rng(config.seed)
    if not config.degrees:
        raise ValueError("At least one parity degree is required")
    tasks: list[TaskSpec] = []
    used: set[tuple[int, ...]] = set()
    freqs = _frequencies(config)
    degree_schedule = list(config.degrees) * int(np.ceil(config.n_tasks / len(config.degrees)))
    degree_schedule = degree_schedule[: config.n_tasks]
    rng.shuffle(degree_schedule)

    for i, degree in enumerate(degree_schedule):
        for _ in range(2000):
            bits = tuple(sorted(int(x) for x in rng.choice(config.n_bits, size=degree, replace=False)))
            if bits not in used:
                used.add(bits)
                break
        else:
            bits = tuple(sorted(int(x) for x in rng.choice(config.n_bits, size=degree, replace=False)))
        tasks.append(
            TaskSpec(
                name=f"P{i:02d}_parity_d{degree}_{'_'.join(map(str, bits))}",
                kind="atomic",
                op="parity_bits",
                bits=bits,
                frequency=float(freqs[i]),
                reference_learnability=float(degree),
                formal_utility=0.0,
                description=f"Sparse parity task {i}: parity over {degree} bits.",
            )
        )
    # frequency table can become correlated with degree by chance; shuffle until
    # diagnostics pass, or return the best shuffled attempt.
    best_tasks = tasks
    best_diag = _diagnostics(tasks)
    best_score = _score(best_diag, config.criteria)
    passed = passes_design_criteria(best_diag, config.criteria)
    for _ in range(500):
        shuffled_freqs = list(freqs)
        rng.shuffle(shuffled_freqs)
        candidate = [replace(t, frequency=float(shuffled_freqs[j])) for j, t in enumerate(tasks)]
        diag = _diagnostics(candidate)
        score = _score(diag, config.criteria)
        if score < best_score:
            best_tasks, best_diag, best_score = candidate, diag, score
        if passes_design_criteria(diag, config.criteria):
            best_tasks, best_diag, passed = candidate, diag, True
            break
    specs = [
        StructureSpec(
            structure_id=t.name,
            backend="B2_sparse_parity",
            kind=t.kind,
            operation=t.op,
            frequency=t.frequency,
            reference_learnability=t.reference_learnability,
            formal_utility=t.formal_utility,
            components=t.components,
            metadata={"bits": ",".join(map(str, t.bits)), "degree": len(t.bits)},
        )
        for t in best_tasks
    ]
    best_diag = dict(best_diag)
    best_diag["passed"] = bool(passed)
    best_diag["n_tasks"] = float(len(best_tasks))
    return SparseParityFamily(tasks=best_tasks, specs=specs, diagnostics=best_diag, passed=bool(passed), config=config)


def save_sparse_parity_family(family: SparseParityFamily, output_dir: str | Path) -> dict[str, str]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    paths = {
        "structure_table": str(output / "structure_table.csv"),
        "generic_structure_table": str(output / "generic_structure_table.csv"),
        "design_diagnostics": str(output / "design_diagnostics.csv"),
        "summary": str(output / "summary.json"),
        "report": str(output / "sparse_parity_report.md"),
    }
    family.structure_table().to_csv(paths["structure_table"], index=False)
    family.generic_structure_table().to_csv(paths["generic_structure_table"], index=False)
    pd.DataFrame([family.diagnostics]).to_csv(paths["design_diagnostics"], index=False)
    import json

    summary = family.metadata()
    summary["paths"] = paths
    Path(paths["summary"]).write_text(json.dumps(summary, indent=2), encoding="utf-8")
    Path(paths["report"]).write_text(_render_sparse_report(family), encoding="utf-8")
    return paths


def _frequencies(config: SparseParityConfig) -> np.ndarray:
    if config.frequency_mode == "uniform":
        return np.ones(config.n_tasks, dtype=float) / config.n_tasks
    if config.frequency_mode != "zipf":
        raise ValueError("frequency_mode must be 'zipf' or 'uniform'")
    ranks = np.arange(1, config.n_tasks + 1, dtype=float)
    weights = ranks ** (-config.zipf_alpha)
    return weights / weights.sum()


def _diagnostics(tasks: list[TaskSpec]) -> dict[str, float | bool]:
    # B2 has no formal utility by default; separate utility effects are
    # deliberately non-identifiable in this baseline. Diagnose the dimensions
    # that should be identifiable: frequency and parity degree.
    df = task_table(tasks)
    diag = design_diagnostics(df, columns=["frequency", "reference_learnability"])
    diag["formal_utility_identifiable"] = False
    diag["vif_formal_utility"] = float("nan")
    return diag


def _score(diag: dict[str, float | bool], criteria: DesignCriteria) -> float:
    score = max(0.0, float(diag["design_condition_number"]) / criteria.max_condition_number - 1.0)
    for k, v in diag.items():
        if k.startswith("vif_"):
            score += max(0.0, float(v) / criteria.max_vif - 1.0)
        elif k.startswith("pearson_"):
            if not np.isfinite(float(v)):
                continue
            score += max(0.0, abs(float(v)) / criteria.max_abs_pearson - 1.0)
        elif k.startswith("spearman_"):
            if not np.isfinite(float(v)):
                continue
            score += max(0.0, abs(float(v)) / criteria.max_abs_spearman - 1.0)
    return score


def _render_sparse_report(family: SparseParityFamily) -> str:
    diag = family.diagnostics
    return "\n".join(
        [
            "# Sparse parity backend report",
            "",
            "This is B2: a quanta-comparable multitask sparse-parity backend.",
            "It is intended as a baseline where frequency and parity degree should dominate acquisition timing.",
            "",
            f"Passed design diagnostics: **{family.passed}**",
            f"n_tasks: `{len(family.tasks)}`",
            f"n_bits: `{family.config.n_bits}`",
            f"frequency_mode: `{family.config.frequency_mode}`",
            f"degrees: `{family.config.degrees}`",
            "",
            "## Key diagnostics",
            f"- design_condition_number: `{float(diag['design_condition_number']):.4g}`",
            f"- vif_frequency: `{float(diag['vif_frequency']):.4g}`",
            f"- vif_reference_learnability: `{float(diag['vif_reference_learnability']):.4g}`",
            "- formal_utility: `not identifiable / absent in B2 baseline`",
            "",
            "## How to use",
            "Use `structure_table.csv` with the existing `run_h1_ordering_pilot` command and `--model mlp`.",
            "This backend has no formal composites by default, so it is for H1/H2/quanta-baseline checks rather than H3 dependency claims.",
        ]
    )
