from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import pandas as pd

from ic_experiments.census import CONDITION_SETS, slug
from ic_experiments.run_management import append_registry, write_manifest


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run B1 v2 causal-census H3 intervention rows by wrapping the existing pair-specific H3 runner.")
    p.add_argument("--census-plan", type=Path, required=True)
    p.add_argument("--structure-table", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--row-indices", type=int, nargs="*", default=None, help="Optional subset of census_row indices to run.")
    p.add_argument("--condition-set", choices=sorted(CONDITION_SETS), default="full")
    p.add_argument("--conditions", nargs="*", default=None, help="Override the condition set with explicit conditions.")
    p.add_argument("--seeds", type=int, nargs="+", default=list(range(10)))
    p.add_argument("--max-data-seen", type=int, default=250000)
    p.add_argument("--batch-size", type=int, default=256)
    p.add_argument("--learning-rate", type=float, default=5e-4)
    p.add_argument("--weight-decay", type=float, default=0.1)
    p.add_argument("--warmup-frac", type=float, default=0.05)
    p.add_argument("--n-checkpoints", type=int, default=100)
    p.add_argument("--eval-examples-per-task", type=int, default=512)
    p.add_argument("--d-model", type=int, default=128)
    p.add_argument("--n-layers", type=int, default=2)
    p.add_argument("--n-heads", type=int, default=4)
    p.add_argument("--d-mlp", type=int, default=512)
    p.add_argument("--device", type=str, default="cuda")
    p.add_argument("--pretrain-data-seen", type=int, default=50000)
    p.add_argument("--metric-family", type=str, default="token_accuracy")
    p.add_argument("--threshold", type=float, default=0.7)
    p.add_argument("--patience", type=int, default=2)
    p.add_argument("--skip-existing", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--code-version", type=str, default="v3.2")
    p.add_argument("--archive-root", type=Path, default=None)
    p.add_argument("--thesis-use", type=str, default="candidate")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    plan = pd.read_csv(args.census_plan)
    if args.row_indices is not None and len(args.row_indices) > 0:
        plan = plan[plan["census_row"].astype(int).isin(args.row_indices)].copy()
    if plan.empty:
        raise ValueError("No census rows to run.")
    conditions = args.conditions or CONDITION_SETS[args.condition_set]
    index_rows = []
    for _, r in plan.iterrows():
        out = args.output_dir / f"row{int(r['census_row']):03d}_{slug(r['pair_id'])}"
        index_rows.append({
            "census_row": int(r["census_row"]),
            "pair_id": r["pair_id"],
            "component": r["component"],
            "composite": r["composite"],
            "result_dir": str(out),
            "status": "pending",
        })
        run_cmd = [
            sys.executable, "-m", "ic_experiments.experiments.run_b1_h3_interventions",
            "--output-dir", str(out),
            "--structure-table", str(args.structure_table),
            "--component", str(r["component"]),
            "--composite", str(r["composite"]),
            "--same-operation-control", str(r.get("same_operation_control", "")),
            "--different-operation-control", str(r.get("different_operation_control", "")),
            "--fake-component-control", str(r.get("fake_component_control", "")),
            "--surface-control", str(r.get("surface_control", "")),
            "--unrelated-control", str(r.get("unrelated_control", "")),
            "--conditions", *conditions,
            "--seeds", *[str(s) for s in args.seeds],
            "--max-data-seen", str(args.max_data_seen),
            "--batch-size", str(args.batch_size),
            "--learning-rate", str(args.learning_rate),
            "--weight-decay", str(args.weight_decay),
            "--warmup-frac", str(args.warmup_frac),
            "--n-checkpoints", str(args.n_checkpoints),
            "--eval-examples-per-task", str(args.eval_examples_per_task),
            "--d-model", str(args.d_model),
            "--n-layers", str(args.n_layers),
            "--n-heads", str(args.n_heads),
            "--d-mlp", str(args.d_mlp),
            "--device", args.device,
            "--pretrain-data-seen", str(args.pretrain_data_seen),
            "--code-version", args.code_version,
            "--thesis-use", args.thesis_use,
        ]
        if args.skip_existing:
            run_cmd.append("--skip-existing")
        if args.archive_root is not None:
            run_cmd.extend(["--archive-root", str(args.archive_root)])
        analyze_cmd = [
            sys.executable, "-m", "ic_experiments.experiments.analyze_b1_h3_interventions",
            "--result-dir", str(out),
            "--metric-family", args.metric_family,
            "--threshold", str(args.threshold),
            "--patience", str(args.patience),
            "--code-version", args.code_version,
            "--thesis-use", args.thesis_use,
        ]
        if args.archive_root is not None:
            analyze_cmd.extend(["--archive-root", str(args.archive_root)])
        print("[census-run]", " ".join(run_cmd))
        if not args.dry_run:
            subprocess.run(run_cmd, check=True)
        print("[census-analyze]", " ".join(analyze_cmd))
        if not args.dry_run:
            subprocess.run(analyze_cmd, check=True)
        index_rows[-1]["status"] = "dry_run" if args.dry_run else "completed"
    pd.DataFrame(index_rows).to_csv(args.output_dir / "b1_v2_causal_census_run_index.csv", index=False)
    manifest = write_manifest(
        args.output_dir,
        experiment="B1_v2_causal_census_run",
        backend="B1_sequence_dsl",
        code_version=args.code_version,
        run_id="b1_v2_causal_census_run",
        command=sys.argv,
        input_paths={"census_plan": str(args.census_plan), "structure_table": str(args.structure_table)},
        extra={"condition_set": args.condition_set, "conditions": conditions, "thesis_use": args.thesis_use, "dry_run": args.dry_run},
    )
    if args.archive_root is not None:
        append_registry(args.archive_root / "results_registry.csv", {
            "run_id": manifest["run_id"], "code_version": args.code_version, "git_sha": manifest["git_sha"],
            "experiment": manifest["experiment"], "backend": manifest["backend"], "output_path": str(args.output_dir),
            "status": "dry_run" if args.dry_run else "completed", "thesis_use": args.thesis_use, "created_at_utc": manifest["created_at_utc"],
        })
    print("Saved census run index:")
    print(f"  {args.output_dir / 'b1_v2_causal_census_run_index.csv'}")


if __name__ == "__main__":
    main()
