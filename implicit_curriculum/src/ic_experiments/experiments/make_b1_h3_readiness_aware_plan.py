from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

from ic_experiments.backends.sequence_dsl import SequenceDSLConfig, load_sequence_family
from ic_experiments.experiments.make_b1_h3_operation_family_plan import (
    STRONG_CONDITIONS,
    STANDARD_CONDITIONS,
    build_plan_row,
    render_run_script,
)
from ic_experiments.run_management import append_registry, write_manifest


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Create an H3 operation-family plan from H3-readiness-selected pairs.")
    p.add_argument("--structure-table", type=Path, required=True)
    p.add_argument("--ready-pair-selection", type=Path, required=True, help="h3_ready_pair_selection.csv from select_b1_h3_ready_candidates")
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--ready-only", action="store_true", help="Use only rows marked h3_ready=True.")
    p.add_argument("--allow-not-ready", action="store_true", help="Allow fallback to top non-ready rows if no ready rows exist.")
    p.add_argument("--min-readiness-score", type=float, default=None)
    p.add_argument("--top-composites", type=int, default=1)
    p.add_argument("--components-per-composite", type=int, default=2)
    p.add_argument("--vocab-content", type=int, default=32)
    p.add_argument("--input-len", type=int, default=6)
    p.add_argument("--write-run-script", action="store_true")
    p.add_argument("--run-output-prefix", type=str, default="results/b1_h3_ready")
    p.add_argument("--condition-set", choices=["standard", "strong"], default="strong")
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
    p.add_argument("--code-version", type=str, default="v2.2")
    p.add_argument("--archive-root", type=Path, default=None)
    p.add_argument("--thesis-use", type=str, default="candidate")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    cfg = SequenceDSLConfig(vocab_content=args.vocab_content, input_len=args.input_len)
    family = load_sequence_family(args.structure_table, cfg)
    structure = family.structure_table()
    pairs = pd.read_csv(args.ready_pair_selection)
    pairs = normalize_ready_pairs(pairs)
    original_n = len(pairs)
    if args.ready_only and "h3_ready" in pairs.columns:
        ready = pairs[pairs["h3_ready"].astype(str).str.lower().isin(["true", "1", "yes"])].copy()
        if not ready.empty or not args.allow_not_ready:
            pairs = ready
    if args.min_readiness_score is not None and "h3_readiness_score" in pairs.columns:
        pairs = pairs[pairs["h3_readiness_score"] >= args.min_readiness_score].copy()
    if pairs.empty:
        raise ValueError(
            "No readiness-selected pairs remain after filtering. Rerun with --allow-not-ready, relax readiness thresholds, or inspect h3_readiness_report.md."
        )
    pairs = pairs.sort_values(score_columns(pairs), ascending=[False] * len(score_columns(pairs)))
    selected_composites = list(dict.fromkeys(pairs["composite"].astype(str).tolist()))[: args.top_composites]
    rows = []
    for composite in selected_composites:
        comp_pairs = pairs[pairs["composite"].astype(str) == composite].head(args.components_per_composite)
        for _, r in comp_pairs.iterrows():
            component = str(r["component"])
            row = build_plan_row(structure, component, str(composite))
            for col in [
                "h3_ready", "h3_readiness_score", "mean_final_metric", "max_residual_log_time",
                "residual_log_time", "positive_rate", "acq_rate_t0p3", "acq_rate_t0p4", "acq_rate_t0p5", "acq_rate_t0p6", "acq_rate_t0p7",
            ]:
                if col in r.index:
                    row[f"source_{col}"] = r[col]
            rows.append(row)
    plan = pd.DataFrame(rows)
    plan.to_csv(args.output_dir / "h3_readiness_aware_plan.csv", index=False)
    # Also write with the standard name so existing H3 runner can use --plan-file directly.
    plan.to_csv(args.output_dir / "h3_operation_family_plan.csv", index=False)
    report = render_report(args, plan, original_n, len(pairs), selected_composites)
    (args.output_dir / "h3_readiness_aware_plan_report.md").write_text(report, encoding="utf-8")
    (args.output_dir / "h3_operation_family_plan_report.md").write_text(report, encoding="utf-8")
    if args.write_run_script:
        shim = argparse.Namespace(**vars(args))
        # render_run_script expects output_dir, structure_table, condition_set, seeds, etc.
        script = render_run_script(plan, shim)
        path = args.output_dir / "recommended_h3_commands.sh"
        path.write_text(script, encoding="utf-8")
        path.chmod(0o755)
    manifest = write_manifest(
        args.output_dir,
        experiment="B1_H3_readiness_aware_plan",
        backend="B1_sequence_dsl",
        code_version=args.code_version,
        run_id="b1_h3_readiness_aware_plan",
        command=sys.argv,
        input_paths={"structure_table": str(args.structure_table), "ready_pair_selection": str(args.ready_pair_selection)},
        extra={"thesis_use": args.thesis_use, "ready_only": args.ready_only, "allow_not_ready": args.allow_not_ready},
    )
    if args.archive_root is not None:
        append_registry(args.archive_root / "results_registry.csv", {
            "run_id": manifest["run_id"], "code_version": args.code_version, "git_sha": manifest["git_sha"],
            "experiment": manifest["experiment"], "backend": manifest["backend"], "output_path": str(args.output_dir),
            "status": "planned", "thesis_use": args.thesis_use, "created_at_utc": manifest["created_at_utc"],
        })
    print("Saved readiness-aware H3 plan:")
    for name in ["h3_readiness_aware_plan_report.md", "h3_readiness_aware_plan.csv", "recommended_h3_commands.sh", "run_manifest.json"]:
        p = args.output_dir / name
        if p.exists():
            print(f"  {p}")


def normalize_ready_pairs(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    aliases = {
        "component_id": "component",
        "component_task": "component",
        "composite_id": "composite",
        "composite_task": "composite",
        "task_name": "composite",
    }
    for old, new in aliases.items():
        if old in out.columns and new not in out.columns:
            out[new] = out[old]
    for col in ["component", "composite"]:
        if col not in out.columns:
            raise ValueError(f"Readiness pair selection must contain {col!r}; columns={list(out.columns)}")
    if "h3_readiness_score" not in out.columns:
        out["h3_readiness_score"] = 0.0
    if "h3_ready" not in out.columns:
        out["h3_ready"] = False
    return out


def score_columns(df: pd.DataFrame) -> list[str]:
    cols = [c for c in ["h3_ready", "h3_readiness_score", "max_residual_log_time", "residual_log_time", "positive_rate"] if c in df.columns]
    return cols or ["component"]


def render_report(args: argparse.Namespace, plan: pd.DataFrame, original_n: int, filtered_n: int, selected_composites: list[str]) -> str:
    conditions = STRONG_CONDITIONS if args.condition_set == "strong" else STANDARD_CONDITIONS
    lines = [
        "# B1 H3 readiness-aware operation-family plan",
        "",
        "This plan is generated from the H3-readiness selector, not from residual magnitude alone. It is meant to avoid the family-2 failure mode where the largest residual composites were too hard for useful intervention contrasts.",
        "",
        f"- ready pair selection: `{args.ready_pair_selection}`",
        f"- input rows: `{original_n}`",
        f"- rows after filtering: `{filtered_n}`",
        f"- planned rows: `{len(plan)}`",
        f"- selected composites: `{', '.join(selected_composites)}`",
        f"- condition set: `{args.condition_set}`",
        "",
        "## Planned pairs",
    ]
    for i, r in plan.iterrows():
        score = r.get("source_h3_readiness_score", float("nan"))
        ready = r.get("source_h3_ready", "")
        final = r.get("source_mean_final_metric", float("nan"))
        residual = r.get("source_max_residual_log_time", r.get("source_residual_log_time", float("nan")))
        lines.append(
            f"- row `{i}`: `{r['component']}` → `{r['composite']}`; same-op=`{r['same_operation_control']}`, "
            f"diff-op=`{r['different_operation_control']}`, ready=`{ready}`, score={_fmt(score)}, residual={_fmt(residual)}, final={_fmt(final)}"
        )
    lines += [
        "",
        "## Recommended condition set",
        f"`{conditions}`",
        "",
        "## Interpretation rule",
        "A readiness-aware plan can still produce negative H3 results. Its purpose is only to ensure the candidate is measurable enough that a negative result is informative rather than a hard-composite failure.",
    ]
    return "\n".join(lines)


def _fmt(x) -> str:
    try:
        return f"{float(x):.3f}"
    except Exception:
        return str(x)


if __name__ == "__main__":
    main()
