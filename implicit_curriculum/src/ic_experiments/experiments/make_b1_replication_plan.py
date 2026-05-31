from __future__ import annotations

import argparse
from pathlib import Path
from textwrap import dedent

import pandas as pd

from ic_experiments.run_management import write_manifest, append_registry


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Create a reproducible B1 second-family replication plan and ready-to-run command script."
    )
    p.add_argument("--output-dir", type=Path, default=Path("results/b1_replication_plan_v20"))
    p.add_argument("--family-id", type=str, default="family_replication_01")
    p.add_argument("--candidate-seeds", type=int, nargs="+", default=list(range(20, 30)))
    p.add_argument("--calibration-seeds", type=int, nargs="+", default=[0, 1, 2])
    p.add_argument("--sweep-seeds", type=int, nargs="+", default=list(range(10)))
    p.add_argument("--h3-seeds", type=int, nargs="+", default=list(range(10)))
    p.add_argument("--configs", nargs="+", default=["base", "lr_low", "lr_high", "wd_zero", "batch_small", "batch_large"])
    p.add_argument("--vocab-content", type=int, default=32)
    p.add_argument("--input-len", type=int, default=6)
    p.add_argument("--calibration-max-data-seen", type=int, default=200_000)
    p.add_argument("--sweep-max-data-seen", type=int, default=250_000)
    p.add_argument("--batch-size", type=int, default=256)
    p.add_argument("--learning-rate", type=float, default=5e-4)
    p.add_argument("--weight-decay", type=float, default=0.1)
    p.add_argument("--n-checkpoints", type=int, default=100)
    p.add_argument("--eval-examples-per-task", type=int, default=512)
    p.add_argument("--d-model", type=int, default=128)
    p.add_argument("--n-layers", type=int, default=2)
    p.add_argument("--n-heads", type=int, default=4)
    p.add_argument("--d-mlp", type=int, default=512)
    p.add_argument("--device", type=str, default="cuda")
    p.add_argument("--top-composites", type=int, default=1)
    p.add_argument("--components-per-composite", type=int, default=2)
    p.add_argument("--condition-set", choices=["standard", "strong"], default="strong")
    p.add_argument("--code-version", type=str, default="v2.0")
    p.add_argument("--archive-root", type=Path, default=Path("results/archive"))
    p.add_argument("--thesis-use", type=str, default="candidate")
    return p.parse_args()


def _join(values: list[int] | list[str]) -> str:
    return " ".join(str(v) for v in values)


def main() -> None:
    args = parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    base = f"results/{args.family_id}"
    dirs = {
        "calibration": f"{base}/sequence_dsl_calibration",
        "h1": f"{base}/b1_h1_shared_sweep",
        "h3_plan": f"{base}/b1_h3_plan",
        "h3_prefix": f"{base}/b1_h3",
        "mediator": f"{base}/b1_mediator_h3_pairs",
    }

    rows = [
        {
            "stage": "1_calibration",
            "command": "run_sequence_dsl_calibration",
            "output_dir": dirs["calibration"],
            "success_gate": "calibration passes; token acquisition nonzero/non-saturated; composite coverage sufficient",
            "claim_role": "validates this replication family as a trainable B1 substrate",
        },
        {
            "stage": "2_h1_shared_sweep",
            "command": "run_b1_h1_shared_sweep + analyze_b1_h1_shared_sweep",
            "output_dir": dirs["h1"],
            "success_gate": "learnability positive and frequency expected-direction in true/atomic strata across configs",
            "claim_role": "tests whether H1 sign stability replicates in a new family",
        },
        {
            "stage": "3_h2_predictor_residuals",
            "command": "analyze_b1_h2_predictor_ladder",
            "output_dir": dirs["h1"],
            "success_gate": "simple atomic predictors beat permutation and select structured composite residuals",
            "claim_role": "tests whether residual-based candidate selection replicates",
        },
        {
            "stage": "4_h3_plan",
            "command": "make_b1_h3_operation_family_plan",
            "output_dir": dirs["h3_plan"],
            "success_gate": "at least one high-residual composite with controls selected",
            "claim_role": "pre-registers pair-specific H3 replication targets",
        },
        {
            "stage": "5_h3_interventions",
            "command": "recommended_h3_commands.sh",
            "output_dir": dirs["h3_prefix"] + "_row*",
            "success_gate": "exact component beats same/different controls under pretrain and/or corruption",
            "claim_role": "tests whether localized exact-component sensitivity recurs",
        },
        {
            "stage": "6_optional_mediators",
            "command": "run_b1_mediator_diagnostics + analyze_b1_mediator_diagnostics",
            "output_dir": dirs["mediator"],
            "success_gate": "positive H3 pairs show stronger exact-component early gradient coupling than controls",
            "claim_role": "tests whether mediator pattern replicates",
        },
    ]
    plan_df = pd.DataFrame(rows)
    plan_df.to_csv(out / "b1_replication_plan.csv", index=False)

    script = make_script(args, dirs)
    script_path = out / "recommended_replication_commands.sh"
    script_path.write_text(script, encoding="utf-8")
    script_path.chmod(0o755)

    report = make_report(args, rows, dirs)
    (out / "B1_REPLICATION_PLAN.md").write_text(report, encoding="utf-8")

    manifest = write_manifest(
        out,
        experiment="B1_second_family_replication_plan",
        backend="B1_sequence_dsl",
        code_version=args.code_version,
        run_id=f"{args.family_id}_replication_plan",
        command=None,
        input_paths={},
        extra={
            "family_id": args.family_id,
            "candidate_seeds": args.candidate_seeds,
            "calibration_seeds": args.calibration_seeds,
            "sweep_seeds": args.sweep_seeds,
            "h3_seeds": args.h3_seeds,
            "thesis_use": args.thesis_use,
        },
    )
    if args.archive_root:
        append_registry(
            args.archive_root / "results_registry.csv",
            {
                "run_id": manifest["run_id"],
                "code_version": args.code_version,
                "git_sha": manifest["git_sha"],
                "experiment": manifest["experiment"],
                "backend": manifest["backend"],
                "output_path": str(out),
                "status": "planned",
                "thesis_use": args.thesis_use,
                "created_at_utc": manifest["created_at_utc"],
            },
        )
    print(f"Wrote {out / 'B1_REPLICATION_PLAN.md'}")
    print(f"Wrote {script_path}")


def make_script(args: argparse.Namespace, dirs: dict[str, str]) -> str:
    candidate_seeds = _join(args.candidate_seeds)
    calibration_seeds = _join(args.calibration_seeds)
    sweep_seeds = _join(args.sweep_seeds)
    h3_seeds = _join(args.h3_seeds)
    configs = _join(args.configs)
    return dedent(f"""\
    #!/usr/bin/env bash
    set -euo pipefail

    # B1 second-family replication pipeline generated by make_b1_replication_plan.py.
    # Run sections one at a time. Inspect each report before continuing to the next stage.

    FAMILY_ID={args.family_id}
    CALIB_DIR={dirs['calibration']}
    H1_DIR={dirs['h1']}
    H3_PLAN_DIR={dirs['h3_plan']}
    H3_PREFIX={dirs['h3_prefix']}
    MEDIATOR_DIR={dirs['mediator']}

    echo "[1/5] Calibrating second B1 family: ${{FAMILY_ID}}"
    PYTHONPATH=src python -m ic_experiments.experiments.run_sequence_dsl_calibration \
      --output-dir ${{CALIB_DIR}} \
      --candidate-seeds {candidate_seeds} \
      --calibration-seeds {calibration_seeds} \
      --vocab-content {args.vocab_content} \
      --input-len {args.input_len} \
      --max-data-seen {args.calibration_max_data_seen} \
      --batch-size {args.batch_size} \
      --learning-rate {args.learning_rate} \
      --weight-decay {args.weight_decay} \
      --device {args.device}

    echo "Inspect ${{CALIB_DIR}}/sequence_dsl_calibration_report.md before continuing."

    echo "[2/5] Running B1 H1 shared sweep on replicated family"
    PYTHONPATH=src python -m ic_experiments.experiments.run_b1_h1_shared_sweep \
      --output-dir ${{H1_DIR}} \
      --structure-table ${{CALIB_DIR}}/structure_table.csv \
      --seeds {sweep_seeds} \
      --configs {configs} \
      --max-data-seen {args.sweep_max_data_seen} \
      --batch-size {args.batch_size} \
      --learning-rate {args.learning_rate} \
      --weight-decay {args.weight_decay} \
      --n-checkpoints {args.n_checkpoints} \
      --eval-examples-per-task {args.eval_examples_per_task} \
      --d-model {args.d_model} \
      --n-layers {args.n_layers} \
      --n-heads {args.n_heads} \
      --d-mlp {args.d_mlp} \
      --vocab-content {args.vocab_content} \
      --input-len {args.input_len} \
      --device {args.device} \
      --skip-existing

    PYTHONPATH=src python -m ic_experiments.experiments.analyze_b1_h1_shared_sweep \
      --result-dir ${{H1_DIR}}

    echo "[3/5] Running H2 predictor ladder / residual selection on replicated family"
    PYTHONPATH=src python -m ic_experiments.experiments.analyze_b1_h2_predictor_ladder \
      --result-dir ${{H1_DIR}} \
      --metric-family token_accuracy \
      --threshold 0.7 \
      --n-permutations 100 \
      --code-version {args.code_version} \
      --archive-root {args.archive_root} \
      --thesis-use {args.thesis_use}

    echo "[4/5] Planning H3 operation-family controls for replicated family"
    PYTHONPATH=src python -m ic_experiments.experiments.make_b1_h3_operation_family_plan \
      --structure-table ${{H1_DIR}}/structure_table.csv \
      --pair-selection ${{H1_DIR}}/h2_pair_selection.csv \
      --output-dir ${{H3_PLAN_DIR}} \
      --top-composites {args.top_composites} \
      --components-per-composite {args.components_per_composite} \
      --write-run-script \
      --condition-set {args.condition_set} \
      --run-output-prefix ${{H3_PREFIX}} \
      --seeds {h3_seeds} \
      --max-data-seen {args.sweep_max_data_seen} \
      --batch-size {args.batch_size} \
      --n-checkpoints {args.n_checkpoints} \
      --eval-examples-per-task {args.eval_examples_per_task} \
      --d-model {args.d_model} \
      --n-layers {args.n_layers} \
      --n-heads {args.n_heads} \
      --d-mlp {args.d_mlp} \
      --device {args.device} \
      --code-version {args.code_version} \
      --archive-root {args.archive_root} \
      --thesis-use {args.thesis_use}

    echo "Inspect ${{H3_PLAN_DIR}}/h3_operation_family_plan_report.md, then run:"
    echo "bash ${{H3_PLAN_DIR}}/recommended_h3_commands.sh"

    # After H3 rows finish, create an evidence matrix manually by listing the generated row directories, e.g.:
    # PYTHONPATH=src python -m ic_experiments.experiments.analyze_b1_h3_evidence_matrix \
    #   --row-dirs ${{H3_PREFIX}}_row0_* ${{H3_PREFIX}}_row1_* \
    #   --output-dir results/${{FAMILY_ID}}/b1_h3_evidence_matrix \
    #   --code-version {args.code_version} \
    #   --archive-root {args.archive_root} \
    #   --thesis-use {args.thesis_use}
    """)


def make_report(args: argparse.Namespace, rows: list[dict], dirs: dict[str, str]) -> str:
    return f"""# B1 Second-Family Replication Plan

This plan is designed to test whether the current localized dependency result is specific to the first generated B1 family or recurs in a new controlled sequence-transformer family.

## Family

- family_id: `{args.family_id}`
- candidate seeds: `{_join(args.candidate_seeds)}`
- calibration seeds: `{_join(args.calibration_seeds)}`
- H1 sweep seeds: `{_join(args.sweep_seeds)}`
- H3 seeds: `{_join(args.h3_seeds)}`
- configs: `{_join(args.configs)}`

## Outputs

| Stage | Output directory | Claim role |
|---|---|---|
""" + "\n".join(
        f"| {r['stage']} | `{r['output_dir']}` | {r['claim_role']} |" for r in rows
    ) + f"""

## Success criteria

A strong replication would show:

1. calibration passes with nonzero/non-saturated acquisition;
2. H1 signs replicate, especially positive reference-learnability timing effect;
3. H2 selects structured composite residuals beyond the atomic parallel null;
4. at least one H3 pair shows exact-component sensitivity beyond same-operation and different-operation controls;
5. if mediator diagnostics are run, H3-positive pairs show stronger early gradient coupling than controls.

A negative or mixed replication is still useful: it would support the current thesis boundary that exact dependency is localized and heterogeneous, not universal.

## Ready-to-run script

Run sections in:

```bash
bash {dirs.get('plan_dir', 'results/...')}/recommended_replication_commands.sh
```

The actual script is written to `recommended_replication_commands.sh` in this plan directory.
"""


if __name__ == "__main__":
    main()
