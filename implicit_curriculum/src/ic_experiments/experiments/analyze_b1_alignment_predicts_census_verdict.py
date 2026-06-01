from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from ic_experiments.census import auc_score, leave_group_out_auc
from ic_experiments.run_management import append_registry, write_manifest


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Test whether early mediator alignment predicts B1 v2 causal-census verdicts.")
    p.add_argument("--census-verdicts", type=Path, required=True, help="b1_v2_causal_census_pair_verdicts.csv")
    p.add_argument("--mediator-pair-role-summary", type=Path, required=True)
    p.add_argument("--mediator-contrast-summary", type=Path, default=None)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--positive-verdict", type=str, default="exact_component_dependency")
    p.add_argument("--family-column", type=str, default="family_id")
    p.add_argument("--code-version", type=str, default="v3.2")
    p.add_argument("--archive-root", type=Path, default=None)
    p.add_argument("--thesis-use", type=str, default="candidate")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    verdicts = pd.read_csv(args.census_verdicts)
    roles = pd.read_csv(args.mediator_pair_role_summary)
    contrasts = pd.read_csv(args.mediator_contrast_summary) if args.mediator_contrast_summary and args.mediator_contrast_summary.exists() else pd.DataFrame()
    features = build_alignment_features(roles, contrasts)
    joined = normalize_and_join(verdicts, features)
    if joined.empty:
        raise ValueError("No overlapping component/composite pairs between census verdicts and mediator summaries.")
    joined["label_exact_dependency"] = (joined["verdict"].astype(str) == args.positive_verdict).astype(int)
    score_cols = [
        c for c in [
            "exact_gradient_cosine", "exact_minus_same_operation_gradient_cosine", "exact_minus_different_operation_gradient_cosine",
            "min_exact_minus_control_gradient_cosine", "exact_linear_cka", "min_exact_minus_control_linear_cka",
        ]
        if c in joined.columns
    ]
    auc_rows = []
    for col in score_cols:
        auc_rows.append({
            "score": col,
            "n_rows": int(joined[col].notna().sum()),
            "auc": auc_score(joined["label_exact_dependency"].to_numpy(), joined[col].to_numpy()),
        })
    auc_df = pd.DataFrame(auc_rows).sort_values("auc", ascending=False) if auc_rows else pd.DataFrame()
    if args.family_column in joined.columns and score_cols:
        logo = []
        for col in score_cols:
            g = leave_group_out_auc(joined, label_col="label_exact_dependency", score_col=col, group_col=args.family_column)
            if not g.empty:
                g.insert(0, "score", col)
                logo.append(g)
        logo_df = pd.concat(logo, ignore_index=True) if logo else pd.DataFrame()
    else:
        logo_df = pd.DataFrame()
    joined.to_csv(args.output_dir / "b1_v2_alignment_verdict_features.csv", index=False)
    auc_df.to_csv(args.output_dir / "b1_v2_alignment_verdict_auc.csv", index=False)
    logo_df.to_csv(args.output_dir / "b1_v2_alignment_leave_family_out_auc.csv", index=False)
    (args.output_dir / "b1_v2_alignment_predicts_verdict_report.md").write_text(render_report(joined, auc_df, logo_df, args), encoding="utf-8")
    manifest = write_manifest(
        args.output_dir,
        experiment="B1_v2_alignment_predicts_census_verdict",
        backend="B1_sequence_dsl",
        code_version=args.code_version,
        run_id="b1_v2_alignment_predicts_census_verdict",
        command=sys.argv,
        input_paths={
            "census_verdicts": str(args.census_verdicts),
            "mediator_pair_role_summary": str(args.mediator_pair_role_summary),
            "mediator_contrast_summary": str(args.mediator_contrast_summary or ""),
        },
        extra={"thesis_use": args.thesis_use, "positive_verdict": args.positive_verdict},
    )
    if args.archive_root is not None:
        append_registry(args.archive_root / "results_registry.csv", {
            "run_id": manifest["run_id"], "code_version": args.code_version, "git_sha": manifest["git_sha"],
            "experiment": manifest["experiment"], "backend": manifest["backend"], "output_path": str(args.output_dir),
            "status": "analyzed", "thesis_use": args.thesis_use, "created_at_utc": manifest["created_at_utc"],
        })
    print("Saved B1 v2 alignment→verdict outputs:")
    for name in ["b1_v2_alignment_predicts_verdict_report.md", "b1_v2_alignment_verdict_features.csv", "b1_v2_alignment_verdict_auc.csv", "b1_v2_alignment_leave_family_out_auc.csv", "run_manifest.json"]:
        print(f"  {args.output_dir / name}")


def build_alignment_features(roles: pd.DataFrame, contrasts: pd.DataFrame) -> pd.DataFrame:
    role_features = []
    group_cols = ["component", "composite"]
    for (component, composite), g in roles.groupby(group_cols, dropna=False):
        d = {"component": component, "composite": composite}
        by_role = {str(r["source_role"]): r for _, r in g.iterrows()}
        exact = by_role.get("exact_component")
        if exact is not None:
            d["exact_gradient_cosine"] = safe_float(exact.get("mean_gradient_cosine"))
            d["exact_linear_cka"] = safe_float(exact.get("mean_linear_cka"))
            d["exact_source_gradient_norm"] = safe_float(exact.get("mean_source_gradient_norm"))
        deltas_gc = []
        deltas_cka = []
        for role, short in [
            ("same_operation_control", "same_operation"),
            ("different_operation_control", "different_operation"),
            ("fake_component_control", "fake_component"),
            ("surface_control", "surface"),
        ]:
            ctrl = by_role.get(role)
            if exact is not None and ctrl is not None:
                dg = safe_float(exact.get("mean_gradient_cosine")) - safe_float(ctrl.get("mean_gradient_cosine"))
                dc = safe_float(exact.get("mean_linear_cka")) - safe_float(ctrl.get("mean_linear_cka"))
                d[f"exact_minus_{short}_gradient_cosine"] = dg
                d[f"exact_minus_{short}_linear_cka"] = dc
                if np.isfinite(dg):
                    deltas_gc.append(dg)
                if np.isfinite(dc):
                    deltas_cka.append(dc)
        d["min_exact_minus_control_gradient_cosine"] = min(deltas_gc) if deltas_gc else np.nan
        d["mean_exact_minus_control_gradient_cosine"] = float(np.mean(deltas_gc)) if deltas_gc else np.nan
        d["min_exact_minus_control_linear_cka"] = min(deltas_cka) if deltas_cka else np.nan
        d["mean_exact_minus_control_linear_cka"] = float(np.mean(deltas_cka)) if deltas_cka else np.nan
        role_features.append(d)
    out = pd.DataFrame(role_features)
    if not contrasts.empty:
        c = contrasts.copy()
        ren = {}
        for col in c.columns:
            lc = col.lower()
            if lc == "delta_gradient_cosine":
                ren[col] = "contrast_delta_gradient_cosine"
            elif lc == "delta_linear_cka":
                ren[col] = "contrast_delta_linear_cka"
        c = c.rename(columns=ren)
        rows = []
        for (component, composite), g in c.groupby(["component", "composite"], dropna=False):
            rows.append({
                "component": component,
                "composite": composite,
                "contrast_min_delta_gradient_cosine": safe_float(pd.to_numeric(g.get("contrast_delta_gradient_cosine", pd.Series(dtype=float)), errors="coerce").min()),
                "contrast_mean_delta_gradient_cosine": safe_float(pd.to_numeric(g.get("contrast_delta_gradient_cosine", pd.Series(dtype=float)), errors="coerce").mean()),
                "contrast_min_delta_linear_cka": safe_float(pd.to_numeric(g.get("contrast_delta_linear_cka", pd.Series(dtype=float)), errors="coerce").min()),
                "contrast_mean_delta_linear_cka": safe_float(pd.to_numeric(g.get("contrast_delta_linear_cka", pd.Series(dtype=float)), errors="coerce").mean()),
            })
        cfeat = pd.DataFrame(rows)
        out = out.merge(cfeat, on=["component", "composite"], how="outer")
    return out


def normalize_and_join(verdicts: pd.DataFrame, features: pd.DataFrame) -> pd.DataFrame:
    v = verdicts.copy()
    aliases = {"component_id": "component", "composite_id": "composite"}
    for old, new in aliases.items():
        if old in v.columns and new not in v.columns:
            v[new] = v[old]
    if "component" not in v.columns or "composite" not in v.columns:
        raise ValueError(f"Verdicts must contain component/composite columns; columns={list(v.columns)}")
    joined = v.merge(features, on=["component", "composite"], how="inner")
    return joined


def render_report(joined: pd.DataFrame, auc_df: pd.DataFrame, logo_df: pd.DataFrame, args: argparse.Namespace) -> str:
    n_pos = int(joined["label_exact_dependency"].sum()) if "label_exact_dependency" in joined else 0
    lines = [
        "# B1 v2 alignment predicts causal verdict",
        "",
        "This analysis treats the causal-census verdict as ground truth and tests whether early mediator features, especially exact component→composite gradient alignment, predict exact-component dependency.",
        "",
        f"Joined pairs: `{len(joined)}`; positive verdict `{args.positive_verdict}`: `{n_pos}`.",
        "",
        "## AUC by score",
    ]
    if auc_df.empty:
        lines.append("No AUC scores were computable, usually because only one verdict class is present or no mediator features overlap.")
    else:
        for _, r in auc_df.iterrows():
            auc = r["auc"]
            auc_text = "nan" if pd.isna(auc) else f"{float(auc):.3f}"
            lines.append(f"- `{r['score']}`: AUC={auc_text} (n={int(r['n_rows'])})")
    lines += ["", "## Leave-family-out check"]
    if logo_df.empty:
        lines.append("No leave-family-out AUC was available; add a family column to the census plan/verdict table for this stronger generalization check.")
    else:
        for _, r in logo_df.iterrows():
            auc = r["auc"]
            auc_text = "nan" if pd.isna(auc) else f"{float(auc):.3f}"
            lines.append(f"- `{r['score']}` held out `{r['held_out_group']}`: AUC={auc_text} (n={int(r['n_rows'])})")
    lines += [
        "",
        "## Interpretation boundary",
        "A high AUC supports gradient alignment as a cheap leading indicator of the expensive intervention verdict. It does not replace the intervention census; it is validated against it.",
    ]
    return "\n".join(lines)


def safe_float(x) -> float:
    try:
        return float(x)
    except Exception:
        return float("nan")


if __name__ == "__main__":
    main()
