from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from ic_experiments.backends.sequence_dsl import SequenceDSLConfig, load_sequence_family
from ic_experiments.experiments.run_b1_h3_interventions import choose_control, choose_operation_control

STANDARD_CONDITIONS = (
    "baseline upweight_component upweight_same_operation_unrelated upweight_different_operation_matched "
    "upweight_fake_component upweight_surface_control delay_component delay_same_operation_unrelated "
    "delay_different_operation_matched corrupt_component corrupt_same_operation_unrelated "
    "corrupt_different_operation_matched"
)

STRONG_CONDITIONS = (
    "baseline pretrain_component pretrain_same_operation_unrelated pretrain_different_operation_matched "
    "corrupt_component_strong corrupt_same_operation_unrelated_strong corrupt_different_operation_matched_strong "
    "delay_component_strong delay_same_operation_unrelated_strong delay_different_operation_matched_strong"
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Create a B1 H3 operation-family control plan from H2 pair selection.")
    p.add_argument("--structure-table", type=Path, required=True)
    p.add_argument("--pair-selection", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, default=Path("results/b1_h3_operation_family_plan"))
    p.add_argument("--top-composites", type=int, default=1)
    p.add_argument("--components-per-composite", type=int, default=2)
    p.add_argument("--include-composites", nargs="*", default=None, help="Optional explicit composite ids to include, overriding top-composites selection.")
    p.add_argument("--exclude-composites", nargs="*", default=None, help="Composite ids to exclude before ranking.")
    p.add_argument("--min-positive-rate", type=float, default=None, help="Optional minimum H2 positive residual rate.")
    p.add_argument("--min-residual", type=float, default=None, help="Optional minimum mean residual log-time.")
    p.add_argument("--vocab-content", type=int, default=32)
    p.add_argument("--input-len", type=int, default=6)
    p.add_argument("--write-run-script", action="store_true", help="Write recommended_h3_commands.sh for every planned row.")
    p.add_argument("--run-output-prefix", type=str, default="results/b1_h3_followup", help="Prefix used in generated run commands.")
    p.add_argument("--condition-set", choices=["standard", "strong"], default="strong", help="Condition set used in generated run commands.")
    p.add_argument("--seeds", nargs="*", default=[str(i) for i in range(10)], help="Seeds for generated run commands.")
    p.add_argument("--max-data-seen", type=int, default=250000)
    p.add_argument("--batch-size", type=int, default=256)
    p.add_argument("--n-checkpoints", type=int, default=100)
    p.add_argument("--eval-examples-per-task", type=int, default=512)
    p.add_argument("--d-model", type=int, default=128)
    p.add_argument("--n-layers", type=int, default=2)
    p.add_argument("--n-heads", type=int, default=4)
    p.add_argument("--d-mlp", type=int, default=512)
    p.add_argument("--device", type=str, default="cuda")
    p.add_argument("--code-version", type=str, default="v1.5")
    p.add_argument("--archive-root", type=str, default="results/archive")
    p.add_argument("--thesis-use", type=str, default="candidate")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    cfg = SequenceDSLConfig(vocab_content=args.vocab_content, input_len=args.input_len)
    family = load_sequence_family(args.structure_table, cfg)
    structure = family.structure_table()
    pairs = pd.read_csv(args.pair_selection)
    if pairs.empty:
        raise ValueError(f"Empty pair-selection file: {args.pair_selection}")
    pairs = normalize_pair_columns(pairs)
    pairs = filter_pairs(pairs, args)
    pairs = pairs.sort_values(["positive_rate", "mean_residual_log_time"], ascending=[False, False])
    if args.include_composites:
        selected_composites = list(dict.fromkeys(args.include_composites))
    else:
        selected_composites = list(dict.fromkeys(pairs["composite"].tolist()))[: args.top_composites]
    rows = []
    for composite in selected_composites:
        comp_pairs = pairs[pairs["composite"] == composite].head(args.components_per_composite)
        for _, r in comp_pairs.iterrows():
            component = str(r["component"])
            row = build_plan_row(structure, component, composite)
            row["source_mean_residual_log_time"] = float(r.get("mean_residual_log_time", r.get("residual_log_time", float("nan"))))
            row["source_positive_rate"] = float(r.get("positive_rate", float("nan")))
            rows.append(row)
    plan = pd.DataFrame(rows)
    if plan.empty:
        raise ValueError("No H3 plan rows selected. Try relaxing filters or checking include/exclude composite ids.")
    plan.to_csv(args.output_dir / "h3_operation_family_plan.csv", index=False)
    (args.output_dir / "h3_operation_family_plan_report.md").write_text(render_report(plan, args), encoding="utf-8")
    if args.write_run_script:
        script = render_run_script(plan, args)
        path = args.output_dir / "recommended_h3_commands.sh"
        path.write_text(script, encoding="utf-8")
        path.chmod(0o755)
    print(f"Saved H3 operation-family plan to {args.output_dir}")
    print(f"  {args.output_dir / 'h3_operation_family_plan.csv'}")
    print(f"  {args.output_dir / 'h3_operation_family_plan_report.md'}")
    if args.write_run_script:
        print(f"  {args.output_dir / 'recommended_h3_commands.sh'}")


def filter_pairs(pairs: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    out = pairs.copy()
    if args.exclude_composites:
        out = out[~out["composite"].isin(args.exclude_composites)].copy()
    if args.include_composites:
        out = out[out["composite"].isin(args.include_composites)].copy()
    if args.min_positive_rate is not None:
        out = out[out["positive_rate"] >= args.min_positive_rate].copy()
    if args.min_residual is not None:
        out = out[out["mean_residual_log_time"] >= args.min_residual].copy()
    return out


def normalize_pair_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "component" not in out.columns and "component_id" in out.columns:
        out["component"] = out["component_id"]
    if "composite" not in out.columns:
        for c in ["composite_id", "task_name"]:
            if c in out.columns:
                out["composite"] = out[c]
                break
    needed = {"component", "composite"}
    missing = needed - set(out.columns)
    if missing:
        raise ValueError(f"Pair selection is missing columns {missing}; columns={list(out.columns)}")
    if "positive_rate" not in out.columns:
        if "positive_residual_rate" in out.columns:
            out["positive_rate"] = out["positive_residual_rate"]
        else:
            out["positive_rate"] = 0.0
    if "mean_residual_log_time" not in out.columns:
        if "residual_log_time" in out.columns:
            out["mean_residual_log_time"] = out["residual_log_time"]
        else:
            out["mean_residual_log_time"] = 0.0
    return out


def build_plan_row(structure: pd.DataFrame, component: str, composite: str) -> dict[str, str | float]:
    same = choose_operation_control(structure, component, composite, same_operation=True)
    diff = choose_operation_control(structure, component, composite, same_operation=False)
    fake = choose_control(structure, "shortcut", component)
    surface = choose_control(structure, "surface_control", component)
    return {
        "component": component,
        "composite": composite,
        "unrelated_control": same or "",
        "same_operation_control": same or "",
        "different_operation_control": diff or "",
        "fake_component_control": fake or "",
        "surface_control": surface or "",
    }


def render_report(plan: pd.DataFrame, args: argparse.Namespace) -> str:
    lines = [
        "# B1 H3 operation-family control plan",
        "",
        "This plan sharpens H3 by separating exact-component effects from operation-family transfer.",
        "Each row can be passed to `run_b1_h3_interventions` using `--plan-file ... --plan-index N`.",
        "",
        f"- source pair_selection: `{args.pair_selection}`",
        f"- n planned pairs: `{len(plan)}`",
        f"- include_composites: `{args.include_composites}`",
        f"- exclude_composites: `{args.exclude_composites}`",
        f"- condition_set_for_script: `{args.condition_set}`",
        "",
        "## Planned pairs",
    ]
    for i, r in plan.iterrows():
        lines.append(
            f"- row `{i}`: `{r['component']}` → `{r['composite']}`; "
            f"same-op=`{r['same_operation_control']}`, diff-op=`{r['different_operation_control']}`, "
            f"fake=`{r['fake_component_control']}`, surface=`{r['surface_control']}`, "
            f"source residual={float(r.get('source_mean_residual_log_time', float('nan'))):.3f}, "
            f"positive-rate={float(r.get('source_positive_rate', float('nan'))):.3f}"
        )
    lines += [
        "",
        "## Recommended standard condition set",
        f"`{STANDARD_CONDITIONS}`",
        "",
        "## Recommended strong condition set",
        f"`{STRONG_CONDITIONS}`",
        "",
        "## Interpretation rule",
        "Exact-component dependency requires the exact component to beat same-operation and different-operation controls. If exact and same-operation controls move the composite similarly, interpret the effect as operation-family transfer rather than exact dependency.",
    ]
    return "\n".join(lines)


def render_run_script(plan: pd.DataFrame, args: argparse.Namespace) -> str:
    conditions = STRONG_CONDITIONS if args.condition_set == "strong" else STANDARD_CONDITIONS
    seeds = " ".join(str(s) for s in args.seeds)
    lines = ["#!/usr/bin/env bash", "set -euo pipefail", ""]
    for i, r in plan.iterrows():
        safe_comp = str(r["composite"]).replace("/", "_")
        safe_component = str(r["component"]).replace("/", "_")
        out = f"{args.run_output_prefix}_row{i}_{safe_component}_to_{safe_comp}_{args.condition_set}"
        lines.append(f"# Row {i}: {r['component']} -> {r['composite']}")
        lines.append(
            "PYTHONPATH=src python -m ic_experiments.experiments.run_b1_h3_interventions "
            f"--output-dir {out} "
            f"--structure-table {args.structure_table} "
            f"--plan-file {args.output_dir / 'h3_operation_family_plan.csv'} "
            f"--plan-index {i} "
            f"--seeds {seeds} "
            f"--conditions {conditions} "
            "--pretrain-data-seen 50000 --strong-corrupt-prob 0.50 --strong-delay-fraction 0.60 "
            f"--max-data-seen {args.max_data_seen} --batch-size {args.batch_size} --n-checkpoints {args.n_checkpoints} "
            f"--eval-examples-per-task {args.eval_examples_per_task} --d-model {args.d_model} --n-layers {args.n_layers} "
            f"--n-heads {args.n_heads} --d-mlp {args.d_mlp} --vocab-content {args.vocab_content} --input-len {args.input_len} "
            f"--device {args.device} --code-version {args.code_version} --archive-root {args.archive_root} --thesis-use {args.thesis_use}"
        )
        lines.append(
            "PYTHONPATH=src python -m ic_experiments.experiments.analyze_b1_h3_interventions "
            f"--result-dir {out} --metric-family token_accuracy --threshold 0.7 "
            f"--code-version {args.code_version} --archive-root {args.archive_root} --thesis-use {args.thesis_use}"
        )
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
