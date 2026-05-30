from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
from torch import nn

from ic_experiments.backends.base import StructureSpec, structure_specs_to_frame
from ic_experiments.design import DesignCriteria, design_diagnostics, passes_design_criteria

PAD, BOS, SEP, EOS = 0, 1, 2, 3
CONTENT_OFFSET = 4


@dataclass(frozen=True)
class SequenceTaskSpec:
    structure_id: str
    kind: str
    op: str
    frequency: float
    reference_learnability: float
    formal_utility: float = 0.0
    components: tuple[str, ...] = ()
    offset: int = 1
    control_for: str | None = None
    control_type: str | None = None
    description: str = ""


@dataclass(frozen=True)
class SequenceDSLConfig:
    """Primary B1 sequence-DSL substrate skeleton.

    This backend is closer to LLM pretraining than the Boolean sandbox: examples
    are token sequences and the model is trained by target-token cross entropy.
    The first version is intentionally small and smoke-testable; later versions
    should add retrieval, modular arithmetic, richer control packets, and full
    gradient/representation mediators.
    """

    vocab_content: int = 64
    input_len: int = 8
    n_atomic: int = 8
    n_composite: int = 6
    n_shortcut_controls: int = 2
    n_surface_controls: int = 2
    n_unrelated_controls: int = 2
    frequency_mode: str = "zipf"
    zipf_alpha: float = 1.05
    seed: int = 0
    criteria: DesignCriteria = DesignCriteria(min_rows=12, max_abs_pearson=0.75, max_abs_spearman=0.80)

    @property
    def vocab_size(self) -> int:
        return self.vocab_content + CONTENT_OFFSET

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["criteria"] = asdict(self.criteria)
        d["vocab_size"] = self.vocab_size
        return d


@dataclass(frozen=True)
class SequenceDSLFamily:
    tasks: list[SequenceTaskSpec]
    diagnostics: dict[str, float | bool]
    passed: bool
    config: SequenceDSLConfig

    @property
    def name(self) -> str:
        return "B1_sequence_dsl"

    def structure_table(self) -> pd.DataFrame:
        return sequence_task_table(self.tasks, backend=self.name)

    def generic_structure_table(self) -> pd.DataFrame:
        specs = [
            StructureSpec(
                structure_id=t.structure_id,
                backend=self.name,
                kind=t.kind,
                operation=t.op,
                frequency=t.frequency,
                reference_learnability=t.reference_learnability,
                formal_utility=t.formal_utility,
                components=t.components,
                control_for=t.control_for,
                control_type=t.control_type,
                metadata={"offset": t.offset, "description": t.description},
            )
            for t in self.tasks
        ]
        return structure_specs_to_frame(specs)

    def metadata(self) -> dict[str, Any]:
        return {"backend": self.name, "config": self.config.to_dict(), "diagnostics": self.diagnostics, "passed": self.passed}


def sequence_task_table(tasks: list[SequenceTaskSpec], backend: str = "B1_sequence_dsl") -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "structure_id": t.structure_id,
                "task_name": t.structure_id,
                "backend": backend,
                "kind": t.kind,
                "op": t.op,
                "components": ",".join(t.components),
                "frequency": t.frequency,
                "reference_learnability": t.reference_learnability,
                "formal_utility": t.formal_utility,
                "control_for": t.control_for or "",
                "control_type": t.control_type or "",
                "offset": t.offset,
                "description": t.description,
            }
            for t in tasks
        ]
    )


def generate_sequence_dsl_family(config: SequenceDSLConfig) -> SequenceDSLFamily:
    rng = np.random.default_rng(config.seed)
    tasks: list[SequenceTaskSpec] = []
    atom_ops = ["copy", "reverse", "substitute"]
    for i in range(config.n_atomic):
        op = atom_ops[i % len(atom_ops)]
        offset = int(rng.integers(1, min(7, config.vocab_content)))
        learn = {"copy": 1.0, "substitute": 1.5, "reverse": 2.0}[op]
        tasks.append(
            SequenceTaskSpec(
                structure_id=f"A{i:02d}_{op}",
                kind="atomic",
                op=op,
                frequency=1.0,
                reference_learnability=learn,
                offset=offset,
                description=f"Atomic sequence DSL task: {op}.",
            )
        )
    atomic_ids = [t.structure_id for t in tasks]
    # Bias composites to pair a transform with copy/reverse/substitute so they are
    # learnable enough for pilots but still formally compositional.
    comp_ops = ["reverse_then_substitute", "substitute_then_reverse", "copy_then_substitute"]
    for j in range(config.n_composite):
        c1, c2 = rng.choice(len(atomic_ids), size=2, replace=False)
        op = comp_ops[j % len(comp_ops)]
        offset = int(rng.integers(1, min(7, config.vocab_content)))
        tasks.append(
            SequenceTaskSpec(
                structure_id=f"C{j:02d}_{op}_{c1:02d}_{c2:02d}",
                kind="composite",
                op=op,
                components=(atomic_ids[int(c1)], atomic_ids[int(c2)]),
                frequency=1.0,
                reference_learnability=3.0,
                offset=offset,
                description=f"Composite sequence DSL task: {op}.",
            )
        )
    for k in range(config.n_shortcut_controls):
        comp = str(rng.choice(atomic_ids))
        tasks.append(
            SequenceTaskSpec(
                structure_id=f"K{k:02d}_shortcut_for_{comp}",
                kind="shortcut",
                op="shortcut_identity",
                components=(comp,),
                frequency=1.0,
                reference_learnability=1.0,
                control_for=comp,
                control_type="shortcut_no_reuse",
                description="Formal component listed, but output is direct identity shortcut.",
            )
        )
    for k in range(config.n_surface_controls):
        tasks.append(
            SequenceTaskSpec(
                structure_id=f"S{k:02d}_surface_rotate",
                kind="surface_control",
                op="surface_rotate",
                frequency=1.0,
                reference_learnability=2.0,
                control_type="surface_overlap_no_dependency",
                offset=int(rng.integers(1, config.input_len)),
                description="Shares sequence surface but target is unrelated rotation.",
            )
        )
    for k in range(config.n_unrelated_controls):
        tasks.append(
            SequenceTaskSpec(
                structure_id=f"U{k:02d}_unrelated_substitute",
                kind="unrelated",
                op="substitute",
                frequency=1.0,
                reference_learnability=1.5,
                control_type="unrelated_matched",
                offset=int(rng.integers(1, min(7, config.vocab_content))),
                description="Unrelated matched-control pool.",
            )
        )
    freqs = _frequencies(len(tasks), config)
    rng.shuffle(freqs)
    tasks = [replace(t, frequency=float(freqs[i])) for i, t in enumerate(tasks)]
    utilities = _formal_utilities(tasks)
    tasks = [replace(t, formal_utility=utilities[t.structure_id]) for t in tasks]
    # Shuffle frequency once more within kind to reduce frequency/utility coupling.
    tasks = _shuffle_freqs_within_kind(tasks, rng)
    df = sequence_task_table(tasks)
    diag = design_diagnostics(df)
    passed = passes_design_criteria(diag, config.criteria)
    diag = dict(diag)
    diag["passed"] = bool(passed)
    diag["n_tasks"] = float(len(tasks))
    return SequenceDSLFamily(tasks=tasks, diagnostics=diag, passed=passed, config=config)


def save_sequence_dsl_family(family: SequenceDSLFamily, output_dir: str | Path) -> dict[str, str]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    paths = {
        "structure_table": str(output / "structure_table.csv"),
        "generic_structure_table": str(output / "generic_structure_table.csv"),
        "design_diagnostics": str(output / "design_diagnostics.csv"),
        "summary": str(output / "summary.json"),
        "report": str(output / "sequence_dsl_report.md"),
    }
    family.structure_table().to_csv(paths["structure_table"], index=False)
    family.generic_structure_table().to_csv(paths["generic_structure_table"], index=False)
    pd.DataFrame([family.diagnostics]).to_csv(paths["design_diagnostics"], index=False)
    import json

    summary = family.metadata()
    summary["paths"] = paths
    Path(paths["summary"]).write_text(json.dumps(summary, indent=2), encoding="utf-8")
    Path(paths["report"]).write_text(_render_report(family), encoding="utf-8")
    return paths


def load_sequence_family(path: str | Path, config: SequenceDSLConfig | None = None) -> SequenceDSLFamily:
    df = pd.read_csv(path)
    tasks = []
    for row in df.to_dict(orient="records"):
        comps = tuple(x for x in str(row.get("components", "")).split(",") if x and x != "nan")
        tasks.append(
            SequenceTaskSpec(
                structure_id=str(row.get("structure_id", row.get("task_name"))),
                kind=str(row["kind"]),
                op=str(row["op"]),
                frequency=float(row["frequency"]),
                reference_learnability=float(row["reference_learnability"]),
                formal_utility=float(row.get("formal_utility", 0.0)),
                components=comps,
                offset=int(row.get("offset", 1)),
                control_for=str(row.get("control_for", "")) or None,
                control_type=str(row.get("control_type", "")) or None,
                description=str(row.get("description", "")),
            )
        )
    cfg = config or SequenceDSLConfig()
    diag = design_diagnostics(sequence_task_table(tasks))
    return SequenceDSLFamily(tasks=tasks, diagnostics=diag, passed=passes_design_criteria(diag, cfg.criteria), config=cfg)


def target_for_task(task: SequenceTaskSpec, x: torch.Tensor, vocab_content: int, tasks_by_id: dict[str, SequenceTaskSpec]) -> torch.Tensor:
    """Return target tokens for input content-token tensor x [batch, input_len]."""
    op = task.op
    if op == "copy" or op == "shortcut_identity":
        return x.clone()
    if op == "reverse":
        return torch.flip(x, dims=[1])
    if op == "substitute":
        return _substitute(x, task.offset, vocab_content)
    if op == "surface_rotate":
        shift = int(task.offset) % x.shape[1]
        return torch.roll(x, shifts=shift, dims=1)
    if op == "reverse_then_substitute":
        return _substitute(torch.flip(x, dims=[1]), task.offset, vocab_content)
    if op == "substitute_then_reverse":
        return torch.flip(_substitute(x, task.offset, vocab_content), dims=[1])
    if op == "copy_then_substitute":
        return _substitute(x, task.offset, vocab_content)
    raise ValueError(f"Unknown sequence op: {op}")


def make_lm_batch(
    tasks: list[SequenceTaskSpec],
    config: SequenceDSLConfig,
    batch_size: int,
    device: str | torch.device,
    weights: torch.Tensor | None = None,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    device = torch.device(device)
    n_tasks = len(tasks)
    if weights is None:
        weights = torch.tensor([t.frequency for t in tasks], dtype=torch.float32, device=device)
        weights = weights / weights.sum()
    task_ids = torch.multinomial(weights, num_samples=batch_size, replacement=True)
    x = torch.randint(CONTENT_OFFSET, config.vocab_size, (batch_size, config.input_len), dtype=torch.long, device=device)
    tokens = torch.full((batch_size, 1 + config.input_len + 1 + config.input_len), PAD, dtype=torch.long, device=device)
    labels = torch.full_like(tokens, -100)
    tasks_by_id = {t.structure_id: t for t in tasks}
    tokens[:, 0] = BOS
    tokens[:, 1 : 1 + config.input_len] = x
    sep_pos = 1 + config.input_len
    tokens[:, sep_pos] = SEP
    for idx, task in enumerate(tasks):
        mask = task_ids == idx
        if mask.any():
            y = target_for_task(task, x[mask], config.vocab_content, tasks_by_id)
            # Inputs after SEP contain previous target tokens; the label at SEP
            # predicts y[0], then subsequent positions predict y[1:].
            start = sep_pos
            labels[mask, start : start + config.input_len] = y
            tokens[mask, start + 1 : start + config.input_len] = y[:, :-1]
    return tokens, labels, task_ids


class CausalTransformerLM(nn.Module):
    def __init__(self, vocab_size: int, max_seq_len: int, d_model: int = 128, n_layers: int = 2, n_heads: int = 4, d_mlp: int = 512, dropout: float = 0.0):
        super().__init__()
        self.token_emb = nn.Embedding(vocab_size, d_model)
        self.pos_emb = nn.Embedding(max_seq_len, d_model)
        layer = nn.TransformerEncoderLayer(d_model=d_model, nhead=n_heads, dim_feedforward=d_mlp, dropout=dropout, batch_first=True, activation="gelu")
        self.blocks = nn.TransformerEncoder(layer, num_layers=n_layers)
        self.ln = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, vocab_size, bias=False)
        self.max_seq_len = max_seq_len

    def forward(self, tokens: torch.Tensor, return_hidden: bool = False):
        b, t = tokens.shape
        pos = torch.arange(t, device=tokens.device).unsqueeze(0).expand(b, t)
        h = self.token_emb(tokens) + self.pos_emb(pos)
        mask = torch.triu(torch.ones(t, t, device=tokens.device, dtype=torch.bool), diagonal=1)
        h = self.blocks(h, mask=mask)
        h = self.ln(h)
        logits = self.head(h)
        if return_hidden:
            return logits, h
        return logits


def evaluate_sequence_per_task(model: nn.Module, tasks: list[SequenceTaskSpec], config: SequenceDSLConfig, examples_per_task: int, data_seen: int, condition: str, seed: int, device: str | torch.device) -> list[dict[str, Any]]:
    model.eval()
    device = torch.device(device)
    criterion = nn.CrossEntropyLoss(ignore_index=-100)
    rows: list[dict[str, Any]] = []
    with torch.no_grad():
        for task_idx, task in enumerate(tasks):
            weights = torch.zeros(len(tasks), device=device)
            weights[task_idx] = 1.0
            tokens, labels, _ = make_lm_batch(tasks, config, examples_per_task, device, weights)
            logits = model(tokens)
            loss = criterion(logits.reshape(-1, logits.size(-1)), labels.reshape(-1)).item()
            pred = logits.argmax(dim=-1)
            mask = labels != -100
            token_acc = (pred[mask] == labels[mask]).float().mean().item()
            per_ex = ((pred == labels) | ~mask).all(dim=1).float().mean().item()
            rows.append(
                {
                    "condition": condition,
                    "seed": seed,
                    "data_seen": data_seen,
                    "task_name": task.structure_id,
                    "kind": task.kind,
                    "loss": float(loss),
                    "token_accuracy": float(token_acc),
                    "exact_match": float(per_ex),
                    "balanced_accuracy": float(per_ex),
                    "accuracy": float(per_ex),
                }
            )
    model.train()
    return rows


def _substitute(x: torch.Tensor, offset: int, vocab_content: int) -> torch.Tensor:
    content = x - CONTENT_OFFSET
    return ((content + int(offset)) % vocab_content) + CONTENT_OFFSET


def _frequencies(n: int, config: SequenceDSLConfig) -> np.ndarray:
    if config.frequency_mode == "uniform":
        return np.ones(n, dtype=float) / n
    ranks = np.arange(1, n + 1, dtype=float)
    w = ranks ** (-config.zipf_alpha)
    return w / w.sum()


def _formal_utilities(tasks: list[SequenceTaskSpec]) -> dict[str, float]:
    util = {t.structure_id: 0.0 for t in tasks}
    for t in tasks:
        if t.kind != "composite":
            continue
        for c in t.components:
            util[c] = util.get(c, 0.0) + t.frequency
    return util


def _shuffle_freqs_within_kind(tasks: list[SequenceTaskSpec], rng: np.random.Generator) -> list[SequenceTaskSpec]:
    out = list(tasks)
    for kind in sorted({t.kind for t in tasks}):
        idx = [i for i, t in enumerate(tasks) if t.kind == kind]
        freqs = [tasks[i].frequency for i in idx]
        rng.shuffle(freqs)
        for i, f in zip(idx, freqs):
            out[i] = replace(out[i], frequency=float(f))
    total = sum(t.frequency for t in out)
    out = [replace(t, frequency=t.frequency / total) for t in out]
    util = _formal_utilities(out)
    return [replace(t, formal_utility=util[t.structure_id]) for t in out]


def _render_report(family: SequenceDSLFamily) -> str:
    diag = family.diagnostics
    return "\n".join(
        [
            "# Sequence DSL backend report",
            "",
            "This is B1: the primary controlled sequence/transformer substrate skeleton.",
            "The current implementation is a smoke-testable version of the stronger operational design.",
            "",
            f"Passed design diagnostics: **{family.passed}**",
            f"n_tasks: `{len(family.tasks)}`",
            f"vocab_size: `{family.config.vocab_size}`",
            f"input_len: `{family.config.input_len}`",
            "",
            "## Key diagnostics",
            f"- design_condition_number: `{float(diag['design_condition_number']):.4g}`",
            f"- vif_frequency: `{float(diag['vif_frequency']):.4g}`",
            f"- vif_reference_learnability: `{float(diag['vif_reference_learnability']):.4g}`",
            f"- vif_formal_utility: `{float(diag['vif_formal_utility']):.4g}`",
            "",
            "## Interpretation",
            "This backend is now the preferred target for the main controlled experiments. B0 Boolean remains a debugging sandbox; B2 sparse parity is the quanta-comparable baseline.",
        ]
    )
