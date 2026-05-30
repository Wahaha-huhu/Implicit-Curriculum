from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def get_git_sha(cwd: Path | None = None) -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(cwd or Path.cwd()), text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "unknown"


def get_git_status(cwd: Path | None = None) -> str:
    try:
        return subprocess.check_output(["git", "status", "--short"], cwd=str(cwd or Path.cwd()), text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "unknown"


def infer_run_id(experiment: str, code_version: str = "unknown", suffix: str | None = None) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    clean_exp = _clean(experiment)
    clean_ver = _clean(code_version)
    parts = [stamp, clean_ver, clean_exp]
    if suffix:
        parts.append(_clean(suffix))
    return "_".join(p for p in parts if p)


def _clean(text: str) -> str:
    return "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in str(text)).strip("_")


def write_manifest(
    output_dir: Path,
    *,
    experiment: str,
    backend: str | None = None,
    code_version: str = "unknown",
    run_id: str | None = None,
    command: Iterable[str] | None = None,
    input_paths: dict[str, str] | None = None,
    extra: dict[str, Any] | None = None,
    git_root: Path | None = None,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    cmd = list(command) if command is not None else sys.argv
    manifest: dict[str, Any] = {
        "run_id": run_id or output_dir.name,
        "experiment": experiment,
        "backend": backend,
        "code_version": code_version,
        "created_at_utc": utc_now_iso(),
        "output_dir": str(output_dir),
        "command": " ".join(str(x) for x in cmd),
        "argv": [str(x) for x in cmd],
        "git_sha": get_git_sha(git_root),
        "git_status_short": get_git_status(git_root),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "input_paths": input_paths or {},
    }
    if extra:
        manifest.update(extra)
    (output_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "command.txt").write_text(manifest["command"] + "\n", encoding="utf-8")
    (output_dir / "git_commit.txt").write_text(str(manifest["git_sha"]) + "\n", encoding="utf-8")
    return manifest


def append_registry(registry_path: Path, record: dict[str, Any]) -> None:
    import csv

    registry_path.parent.mkdir(parents=True, exist_ok=True)
    flat = {k: _jsonish(v) for k, v in record.items()}
    exists = registry_path.exists()
    old_fields: list[str] = []
    if exists:
        with registry_path.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            old_fields = list(reader.fieldnames or [])
    fields = list(dict.fromkeys(old_fields + list(flat.keys())))
    rows: list[dict[str, Any]] = []
    if exists:
        with registry_path.open("r", newline="", encoding="utf-8") as f:
            rows.extend(csv.DictReader(f))
    rows.append(flat)
    with registry_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def _jsonish(v: Any) -> str | int | float | bool | None:
    if isinstance(v, (str, int, float, bool)) or v is None:
        return v
    try:
        return json.dumps(v, sort_keys=True)
    except TypeError:
        return str(v)


def archive_existing_result(
    source_dir: Path,
    archive_root: Path,
    *,
    experiment: str,
    code_version: str = "unknown",
    run_id: str | None = None,
    thesis_use: str = "candidate",
    copy: bool = True,
    overwrite: bool = False,
    registry_name: str = "results_registry.csv",
) -> Path:
    """Copy or move an existing result directory into an immutable archive path.

    This is useful for preserving outputs before later versions overwrite `results/latest`.
    """
    if not source_dir.exists():
        raise FileNotFoundError(source_dir)
    run_id = run_id or infer_run_id(experiment, code_version, source_dir.name)
    dest = archive_root / _clean(code_version) / _clean(experiment) / _clean(run_id)
    if dest.exists():
        if not overwrite:
            raise FileExistsError(f"Archive destination already exists: {dest}")
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if copy:
        shutil.copytree(source_dir, dest)
    else:
        shutil.move(str(source_dir), str(dest))
    manifest = write_manifest(
        dest,
        experiment=experiment,
        backend=None,
        code_version=code_version,
        run_id=run_id,
        command=["archive_existing_result", str(source_dir), str(dest)],
        extra={"archived_from": str(source_dir), "thesis_use": thesis_use},
    )
    append_registry(
        archive_root / registry_name,
        {
            "run_id": manifest["run_id"],
            "code_version": code_version,
            "git_sha": manifest["git_sha"],
            "experiment": experiment,
            "backend": manifest.get("backend") or "",
            "output_path": str(dest),
            "status": "archived",
            "thesis_use": thesis_use,
            "created_at_utc": manifest["created_at_utc"],
        },
    )
    return dest
