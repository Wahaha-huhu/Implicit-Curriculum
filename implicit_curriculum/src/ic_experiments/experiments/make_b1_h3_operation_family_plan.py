from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from ic_experiments.backends.sequence_dsl import SequenceDSLConfig, load_sequence_family
from ic_experiments.experiments.run_b1_h3_interventions import choose_control, choose_operation_control


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Create a B1 H3 operation-family control plan from H2 pair selection.")
    p.add_argument("--structure-table", type=Path, required=True)
    p.add_argument("--pair-selection", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, default=Path("results/b1_h3_operation_family_plan"))
    p.add_argument("--top-composites", type=int, default=1)
    p.add_argument("--components-per-composite", type=int, default=2)
    p.add_argument("--vocab-content", type=int, default=32)
    p.add_argument("--input-len", type=int, default=6)
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
    pairs = pairs.sort_values(["positive_rate", "mean_residual_log_time"], ascending=[False, False])
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
    plan.to_csv(args.output_dir / "h3_operation_family_plan.csv", index=False)
    (args.output_dir / "h3_operation_family_plan_report.md").write_text(render_report(plan, args), encoding="utf-8")
    print(f"Saved H3 operation-family plan to {args.output_dir}")
    print(f"  {args.output_dir / 'h3_operation_family_plan.csv'}")
    print(f"  {args.output_dir / 'h3_operation_family_plan_report.md'}")


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
        "",
        "## Planned pairs",
    ]
    for i, r in plan.iterrows():
        lines.append(
            f"- row `{i}`: `{r['component']}` → `{r['composite']}`; "
            f"same-op=`{r['same_operation_control']}`, diff-op=`{r['different_operation_control']}`, "
            f"fake=`{r['fake_component_control']}`, surface=`{r['surface_control']}`"
        )
    lines += [
        "",
        "## Recommended condition set",
        "`baseline upweight_component upweight_same_operation_unrelated upweight_different_operation_matched upweight_fake_component upweight_surface_control delay_component delay_same_operation_unrelated delay_different_operation_matched corrupt_component corrupt_same_operation_unrelated corrupt_different_operation_matched`",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
