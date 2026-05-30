from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Protocol

import pandas as pd


@dataclass(frozen=True)
class StructureSpec:
    """Backend-agnostic description of a trainable/evaluable structure.

    This is the shared metadata layer used by B0/B1/B2 backends. Backends may
    have richer internal task objects, but every experiment should export this
    schema so downstream H1/H2/H3 analyses can be reused.
    """

    structure_id: str
    backend: str
    kind: str
    frequency: float
    reference_learnability: float
    formal_utility: float = 0.0
    components: tuple[str, ...] = ()
    control_for: str | None = None
    control_type: str | None = None
    operation: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_row(self) -> dict[str, Any]:
        row = asdict(self)
        row["components"] = ",".join(self.components)
        for key, value in self.metadata.items():
            row[f"meta_{key}"] = value
        row.pop("metadata")
        return row


class Backend(Protocol):
    """Minimal interface every experimental substrate should implement."""

    name: str

    def structure_table(self) -> pd.DataFrame:
        ...

    def metadata(self) -> dict[str, Any]:
        ...


def structure_specs_to_frame(specs: list[StructureSpec]) -> pd.DataFrame:
    return pd.DataFrame([s.to_row() for s in specs])


def write_backend_manifest(output_dir: str | Path, backend: Backend, extra: dict[str, Any] | None = None) -> dict[str, str]:
    """Write backend-agnostic metadata files."""

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    table_path = output / "structure_table.csv"
    backend.structure_table().to_csv(table_path, index=False)
    manifest = backend.metadata()
    if extra:
        manifest.update(extra)
    manifest_path = output / "backend_manifest.json"
    import json

    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return {"structure_table": str(table_path), "backend_manifest": str(manifest_path)}
