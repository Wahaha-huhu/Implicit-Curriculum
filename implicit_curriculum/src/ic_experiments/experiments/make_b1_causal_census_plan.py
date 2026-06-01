from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from ic_experiments.backends.sequence_dsl import SequenceDSLConfig, load_sequence_family
from ic_experiments.census import (
    CONDITION_SETS,
    build_causal_census_plan,
    render_causal_census_plan_report,
    render_causal_census_run_script,
)
from ic_experiments.run_management import append_registry, write_manifest


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Create the B1 v2 causal-census plan from a structure table and optional H3-readiness table.")
    p.add_argument("--structure-table", type=Path, required=True)
    p.add_argument("--ready-pair-selection", type=Path, default=None, help="Optional h3_ready_pair_selection.csv; if omitted, all formal component→composite pairs are listed.")
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--ready-only", action="store_true")
    p.add_argument("--allow-not-ready", action="store_true")
    p.add_argument("--min-readiness-score", type=float, default=None)
    p.add_argument("--max-pairs", type=int, default=None)
    p.add_argument("--include-composites", nargs="*", default=None)
    p.add_argument("--exclude-composites", nargs="*", default=None)
    p.add_argument("--vocab-content", type=int, default=32)
    p.add_argument("--input-len", type=int, default=6)
    p.add_argument("--write-run-script", action="store_true")
    p.add_argument("--condition-set", choices=sorted(CONDITION_SETS), default="full")
    p.add_argument("--run-output-prefix", type=str, default="results/b1_v2_causal_census")
    p.add_argument("--seeds", nargs="*", default=[str(i) for i in range(10)])
    p.add_argument("--max-data-seen", type=int, default=250000)
    p.add_argument("--batch-size", type=int, default=256)
    p.add_argument("--n-checkpoints", type=int, default=100)
    p.add_argument("--eval-examples-per-task", type=int, default=512)
    p.add_argument("--d-model", type=int, default=128)
    p.add_argument("--n-layers", type=int, default=2)
    p.add_argument("--n-heads", type=int, default=4)
    p.add_argument("--d-mlp", type=int, default=512)
    p.add_argument("--device", type=str, default="cuda")
    p.add_argument("--pretrain-data-seen", type=int, default=50000)
    p.add_argument("--code-version", type=str, default="v3.2")
    p.add_argument("--archive-root", type=Path, default=None)
    p.add_argument("--thesis-use", type=str, default="preregistered")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    cfg = SequenceDSLConfig(vocab_content=args.vocab_content, input_len=args.input_len)
    family = load_sequence_family(args.structure_table, cfg)
    structure = family.structure_table()
    ready = pd.read_csv(args.ready_pair_selection) if args.ready_pair_selection and args.ready_pair_selection.exists() else None
    plan = build_causal_census_plan(
        structure,
        ready,
        ready_only=args.ready_only,
        allow_not_ready=args.allow_not_ready,
        min_readiness_score=args.min_readiness_score,
        max_pairs=args.max_pairs,
        include_composites=args.include_composites,
        exclude_composites=args.exclude_composites,
    )
    if plan.empty:
        raise ValueError("No causal-census rows selected. Relax readiness filters or inspect the pair-selection table.")
    plan.to_csv(args.output_dir / "b1_v2_causal_census_plan.csv", index=False)
    # Compatibility aliases for existing H3 runner/plan tooling.
    plan.to_csv(args.output_dir / "h3_operation_family_plan.csv", index=False)
    (args.output_dir / "b1_v2_causal_census_plan_report.md").write_text(
        render_causal_census_plan_report(plan, structure_path=str(args.structure_table), ready_path=str(args.ready_pair_selection or ""), condition_set=args.condition_set),
        encoding="utf-8",
    )
    if args.write_run_script:
        script = render_causal_census_run_script(
            plan,
            structure_table=str(args.structure_table),
            output_prefix=args.run_output_prefix,
            condition_set=args.condition_set,
            seeds=args.seeds,
            max_data_seen=args.max_data_seen,
            batch_size=args.batch_size,
            n_checkpoints=args.n_checkpoints,
            eval_examples_per_task=args.eval_examples_per_task,
            d_model=args.d_model,
            n_layers=args.n_layers,
            n_heads=args.n_heads,
            d_mlp=args.d_mlp,
            device=args.device,
            pretrain_data_seen=args.pretrain_data_seen,
            code_version=args.code_version,
            archive_root=str(args.archive_root) if args.archive_root else None,
            thesis_use=args.thesis_use,
        )
        path = args.output_dir / "recommended_causal_census_commands.sh"
        path.write_text(script, encoding="utf-8")
        path.chmod(0o755)
    manifest = write_manifest(
        args.output_dir,
        experiment="B1_v2_causal_census_plan",
        backend="B1_sequence_dsl",
        code_version=args.code_version,
        run_id="b1_v2_causal_census_plan",
        command=sys.argv,
        input_paths={"structure_table": str(args.structure_table), "ready_pair_selection": str(args.ready_pair_selection or "")},
        extra={"condition_set": args.condition_set, "thesis_use": args.thesis_use, "ready_only": args.ready_only},
    )
    if args.archive_root is not None:
        append_registry(args.archive_root / "results_registry.csv", {
            "run_id": manifest["run_id"], "code_version": args.code_version, "git_sha": manifest["git_sha"],
            "experiment": manifest["experiment"], "backend": manifest["backend"], "output_path": str(args.output_dir),
            "status": "planned", "thesis_use": args.thesis_use, "created_at_utc": manifest["created_at_utc"],
        })
    print("Saved B1 v2 causal-census plan outputs:")
    for name in ["b1_v2_causal_census_plan_report.md", "b1_v2_causal_census_plan.csv", "h3_operation_family_plan.csv", "recommended_causal_census_commands.sh", "run_manifest.json"]:
        p = args.output_dir / name
        if p.exists():
            print(f"  {p}")


if __name__ == "__main__":
    main()
