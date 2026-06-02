from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

from ic_experiments.backends.sequence_dsl import SequenceDSLConfig, generate_sequence_dsl_family
from ic_experiments.coupling import DEFAULT_DOSE_MULTIPLIERS, make_coupling_pair_plan
from ic_experiments.run_management import write_manifest


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Create an N1 cross-task coupling pilot plan for B1 Sequence DSL.")
    p.add_argument("--output-dir", type=Path, default=Path("results/b1_coupling_pilot_plan"))
    p.add_argument("--structure-table", type=Path, default=None, help="Existing B1 structure_table.csv. If omitted, a fresh family is generated.")
    p.add_argument("--max-pairs", type=int, default=12)
    p.add_argument("--pair-seed", type=int, default=0)
    p.add_argument("--dose-multipliers", type=float, nargs="+", default=list(DEFAULT_DOSE_MULTIPLIERS))
    p.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    p.add_argument("--no-reverse-composition", action="store_true")
    # Fresh-family options.
    p.add_argument("--family-seed", type=int, default=0)
    p.add_argument("--vocab-content", type=int, default=32)
    p.add_argument("--input-len", type=int, default=6)
    p.add_argument("--n-atomic", type=int, default=8)
    p.add_argument("--n-composite", type=int, default=6)
    p.add_argument("--n-shortcut-controls", type=int, default=2)
    p.add_argument("--n-surface-controls", type=int, default=2)
    p.add_argument("--n-unrelated-controls", type=int, default=4)
    p.add_argument("--frequency-mode", type=str, default="zipf", choices=["zipf", "uniform"])
    p.add_argument("--zipf-alpha", type=float, default=1.05)
    p.add_argument("--write-run-script", action="store_true")
    p.add_argument("--run-output-dir", type=Path, default=Path("results/b1_coupling_pilot"))
    p.add_argument("--device", type=str, default="cuda")
    p.add_argument("--max-data-seen", type=int, default=120_000)
    p.add_argument("--batch-size", type=int, default=256)
    p.add_argument("--n-checkpoints", type=int, default=60)
    p.add_argument("--eval-examples-per-task", type=int, default=256)
    p.add_argument("--code-version", type=str, default="n1.0")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    if args.structure_table is not None:
        structure = pd.read_csv(args.structure_table)
        source_path = str(args.structure_table)
    else:
        cfg = SequenceDSLConfig(
            vocab_content=args.vocab_content,
            input_len=args.input_len,
            n_atomic=args.n_atomic,
            n_composite=args.n_composite,
            n_shortcut_controls=args.n_shortcut_controls,
            n_surface_controls=args.n_surface_controls,
            n_unrelated_controls=args.n_unrelated_controls,
            frequency_mode=args.frequency_mode,
            zipf_alpha=args.zipf_alpha,
            seed=args.family_seed,
        )
        family = generate_sequence_dsl_family(cfg)
        structure = family.structure_table()
        source_path = str(out / "structure_table.csv")
        (out / "generated_family_metadata.json").write_text(json.dumps(family.metadata(), indent=2), encoding="utf-8")
    structure.to_csv(out / "structure_table.csv", index=False)

    pair_plan = make_coupling_pair_plan(
        structure,
        max_pairs=args.max_pairs,
        seed=args.pair_seed,
        include_reverse_composition=not args.no_reverse_composition,
    )
    pair_plan.to_csv(out / "b1_coupling_pair_plan.csv", index=False)

    rows = []
    for _, pair in pair_plan.iterrows():
        for mult in args.dose_multipliers:
            for seed in args.seeds:
                rows.append(
                    {
                        "pair_id": pair["pair_id"],
                        "pair_index": int(pair["pair_index"]),
                        "source_task": pair["source_task"],
                        "target_task": pair["target_task"],
                        "pair_type": pair["pair_type"],
                        "filler_task": pair["filler_task"],
                        "source_multiplier": float(mult),
                        "condition": f"source_x{float(mult):g}",
                        "seed": int(seed),
                    }
                )
    run_plan = pd.DataFrame(rows)
    run_plan.to_csv(out / "b1_coupling_run_plan.csv", index=False)

    report = render_report(args, pair_plan, run_plan, source_path)
    (out / "b1_coupling_pilot_plan_report.md").write_text(report, encoding="utf-8")
    summary = {
        "experiment": "N1_B1_cross_task_coupling_pilot_plan",
        "source_structure_table": source_path,
        "n_pairs": int(len(pair_plan)),
        "n_run_rows": int(len(run_plan)),
        "dose_multipliers": [float(x) for x in args.dose_multipliers],
        "seeds": [int(s) for s in args.seeds],
        "paths": {
            "structure_table": str(out / "structure_table.csv"),
            "pair_plan": str(out / "b1_coupling_pair_plan.csv"),
            "run_plan": str(out / "b1_coupling_run_plan.csv"),
        },
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    if args.write_run_script:
        script = recommended_commands(args, out)
        script_path = out / "recommended_b1_coupling_pilot_commands.sh"
        script_path.write_text(script, encoding="utf-8")
        script_path.chmod(0o755)

    write_manifest(
        out,
        experiment="N1_B1_cross_task_coupling_pilot_plan",
        backend="B1_sequence_dsl",
        code_version=args.code_version,
        run_id="b1_coupling_pilot_plan",
        command=sys.argv,
        input_paths={"structure_table": source_path},
        extra={"max_pairs": args.max_pairs, "dose_multipliers": [float(x) for x in args.dose_multipliers], "seeds": args.seeds},
    )

    print("Saved B1 coupling pilot plan outputs:")
    for name in ["structure_table.csv", "b1_coupling_pair_plan.csv", "b1_coupling_run_plan.csv", "b1_coupling_pilot_plan_report.md", "summary.json", "run_manifest.json"]:
        print(f"  {out / name}")


def render_report(args: argparse.Namespace, pair_plan: pd.DataFrame, run_plan: pd.DataFrame, source_path: str) -> str:
    lines = [
        "# B1 N1 cross-task coupling pilot plan",
        "",
        "This is the first pilot for the positive-mechanism reframe: measure whether early training-dynamics coupling predicts directly measured cross-task transfer/interference.",
        "",
        "## Inputs",
        f"- structure table: `{source_path}`",
        f"- pairs: `{len(pair_plan)}`",
        f"- run rows: `{len(run_plan)}`",
        f"- dose multipliers: `{', '.join(map(str, args.dose_multipliers))}`",
        f"- seeds: `{', '.join(map(str, args.seeds))}`",
        "",
        "## Pair-type coverage",
    ]
    for pair_type, n in pair_plan["pair_type"].value_counts().sort_index().items():
        lines.append(f"- `{pair_type}`: `{int(n)}`")
    lines.extend(["", "## Planned pairs"])
    for _, r in pair_plan.iterrows():
        lines.append(f"- `{r['pair_id']}`: `{r['source_task']}` → `{r['target_task']}` ({r['pair_type']}), filler=`{r['filler_task']}`")
    lines.extend(
        [
            "",
            "## Interpretation discipline",
            "This plan does not assume ordered learning, quanta, or composition. It creates a heterogeneous pair set so that the runner can measure a continuous interaction effect I(A→B) and validate early gradient/representation coupling against that effect.",
        ]
    )
    return "\n".join(lines)


def recommended_commands(args: argparse.Namespace, out: Path) -> str:
    return f"""#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH=${{PYTHONPATH:-$(pwd)/src}}
python -m ic_experiments.experiments.run_b1_coupling_pilot \\
  --structure-table {out / 'structure_table.csv'} \\
  --pair-plan {out / 'b1_coupling_pair_plan.csv'} \\
  --output-dir {args.run_output_dir} \\
  --seeds {' '.join(map(str, args.seeds))} \\
  --dose-multipliers {' '.join(map(str, args.dose_multipliers))} \\
  --device {args.device} \\
  --max-data-seen {args.max_data_seen} \\
  --batch-size {args.batch_size} \\
  --n-checkpoints {args.n_checkpoints} \\
  --eval-examples-per-task {args.eval_examples_per_task} \\
  --skip-existing

python -m ic_experiments.experiments.analyze_b1_coupling_pilot \\
  --result-dir {args.run_output_dir} \\
  --output-dir {args.run_output_dir}_analysis
"""


if __name__ == "__main__":
    main()
