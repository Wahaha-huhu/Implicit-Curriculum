from __future__ import annotations

import argparse
from pathlib import Path

from ic_experiments.run_management import archive_existing_result


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Archive an existing result directory into results/archive/<version>/<experiment>/<run_id>.")
    p.add_argument("--source-dir", type=Path, required=True)
    p.add_argument("--archive-root", type=Path, default=Path("results/archive"))
    p.add_argument("--experiment", type=str, required=True)
    p.add_argument("--code-version", type=str, default="unknown")
    p.add_argument("--run-id", type=str, default=None)
    p.add_argument("--thesis-use", type=str, default="candidate", choices=["candidate", "debug", "main", "discard"])
    p.add_argument("--move", action="store_true", help="Move instead of copy.")
    p.add_argument("--overwrite", action="store_true")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    dest = archive_existing_result(
        args.source_dir,
        args.archive_root,
        experiment=args.experiment,
        code_version=args.code_version,
        run_id=args.run_id,
        thesis_use=args.thesis_use,
        copy=not args.move,
        overwrite=args.overwrite,
    )
    print(f"Archived result to {dest}")


if __name__ == "__main__":
    main()
