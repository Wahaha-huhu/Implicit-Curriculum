from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from ic_experiments.metrics import acquisition_times
from ic_experiments.run_management import append_registry, write_manifest
from ic_experiments.sequence_analysis import final_metrics


CONTRAST_SPECS = [
    # Legacy exact-vs-unrelated contrast; in v1.1 unrelated_control defaults to same-operation unrelated.
    ("upweight_component", "upweight_unrelated_matched", "earlier", "exact_vs_legacy_unrelated"),
    ("upweight_component", "upweight_same_operation_unrelated", "earlier", "exact_vs_same_operation"),
    ("upweight_component", "upweight_different_operation_matched", "earlier", "exact_vs_different_operation"),
    ("upweight_component", "upweight_fake_component", "earlier", "exact_vs_fake_component"),
    ("upweight_component", "upweight_surface_control", "earlier", "exact_vs_surface"),
    ("upweight_same_operation_unrelated", "upweight_different_operation_matched", "earlier", "operation_family_vs_different_operation"),
    ("corrupt_component", "corrupt_unrelated_matched", "later", "exact_corrupt_vs_legacy_unrelated"),
    ("corrupt_component", "corrupt_same_operation_unrelated", "later", "exact_corrupt_vs_same_operation"),
    ("corrupt_component", "corrupt_different_operation_matched", "later", "exact_corrupt_vs_different_operation"),
    ("delay_component", "delay_unrelated_matched", "later", "exact_delay_vs_legacy_unrelated"),
    ("delay_component", "delay_same_operation_unrelated", "later", "exact_delay_vs_same_operation"),
    ("delay_component", "delay_different_operation_matched", "later", "exact_delay_vs_different_operation"),
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Analyze B1 H3 pair-specific intervention runs.")
    p.add_argument("--result-dir", type=Path, required=True)
    p.add_argument("--metric-family", type=str, default="token_accuracy")
    p.add_argument("--threshold", type=float, default=0.7)
    p.add_argument("--patience", type=int, default=2)
    p.add_argument("--code-version", type=str, default="v1.1")
    p.add_argument("--run-id", type=str, default=None)
    p.add_argument("--archive-root", type=Path, default=None)
    p.add_argument("--thesis-use", type=str, default="candidate")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    result_dir = args.result_dir
    eval_df = pd.read_csv(result_dir / "eval_curves.csv")
    pair = load_pair(result_dir)
    acq = load_or_compute_acq(result_dir, eval_df, args.metric_family, args.threshold, args.patience)
    final = final_metrics(eval_df)
    final.to_csv(result_dir / "h3_final_metrics.csv", index=False)
    acq_prepared = prepare_acq(acq, eval_df, args.metric_family, args.threshold)
    acq_prepared.to_csv(result_dir / "h3_acquisition_times.csv", index=False)

    contrasts = intervention_contrasts(acq_prepared, final, pair, args.metric_family)
    contrasts.to_csv(result_dir / "h3_intervention_contrasts.csv", index=False)

    pair_summary = summarize_pair(acq_prepared, final, contrasts, pair, args.metric_family)
    pair_summary.to_csv(result_dir / "h3_pair_summary.csv", index=False)

    report = make_report(pair, acq_prepared, final, contrasts, pair_summary, args.metric_family, args.threshold)
    (result_dir / "h3_analysis_report.md").write_text(report, encoding="utf-8")

    manifest = write_manifest(
        result_dir,
        experiment="B1_H3_pair_specific_intervention_analysis",
        backend="B1_sequence_dsl",
        code_version=args.code_version,
        run_id=args.run_id or f"h3_analysis_{pair['component']}_to_{pair['composite']}",
        command=sys.argv,
        input_paths={"result_dir": str(result_dir)},
        extra={"pair": pair, "metric_family": args.metric_family, "threshold": args.threshold, "thesis_use": args.thesis_use},
    )
    if args.archive_root is not None:
        append_registry(
            args.archive_root / "results_registry.csv",
            {
                "run_id": manifest["run_id"],
                "code_version": args.code_version,
                "git_sha": manifest["git_sha"],
                "experiment": manifest["experiment"],
                "backend": manifest["backend"],
                "output_path": str(result_dir),
                "status": "analyzed",
                "thesis_use": args.thesis_use,
                "created_at_utc": manifest["created_at_utc"],
            },
        )

    print("Saved B1 H3 analysis outputs:")
    for name in ["h3_analysis_report.md", "h3_intervention_contrasts.csv", "h3_pair_summary.csv", "h3_acquisition_times.csv", "h3_final_metrics.csv", "run_manifest.json"]:
        print(f"  {result_dir / name}")


def load_pair(result_dir: Path) -> dict[str, str]:
    path = result_dir / "h3_pair_config.csv"
    if path.exists():
        df = pd.read_csv(path)
        if not df.empty:
            return {k: str(v) for k, v in df.iloc[0].to_dict().items() if str(v) != "nan"}
    summary = result_dir / "summary.json"
    if summary.exists():
        data = json.loads(summary.read_text(encoding="utf-8"))
        if "pair" in data:
            return {k: str(v) for k, v in data["pair"].items()}
    raise FileNotFoundError("Could not find h3_pair_config.csv or summary.json with pair information.")


def load_or_compute_acq(result_dir: Path, eval_df: pd.DataFrame, metric_family: str, threshold: float, patience: int) -> pd.DataFrame:
    # Recompute to make sure analysis threshold is respected even if quick table differs.
    acq = acquisition_times(eval_df, threshold=threshold, patience=patience, metric=metric_family)
    acq["metric_family"] = metric_family
    acq["analysis_threshold"] = float(threshold)
    return acq


def prepare_acq(acq: pd.DataFrame, eval_df: pd.DataFrame, metric_family: str, threshold: float) -> pd.DataFrame:
    max_by = eval_df.groupby(["condition", "seed"], as_index=False)["data_seen"].max().rename(columns={"data_seen": "max_data_seen"})
    out = acq.merge(max_by, on=["condition", "seed"], how="left")
    out["censored_acquired_at"] = out["acquired_at"].fillna(out["max_data_seen"])
    out["is_censored"] = out["acquired_at"].isna()
    out["metric_family"] = metric_family
    out["analysis_threshold"] = threshold
    return out


def intervention_contrasts(acq: pd.DataFrame, final: pd.DataFrame, pair: dict[str, str], metric_family: str) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    composite = pair["composite"]
    for left, right, expected, contrast_type in CONTRAST_SPECS:
        if left not in set(acq["condition"]) or right not in set(acq["condition"]):
            continue
        left_acq = acq[(acq["condition"] == left) & (acq["task_name"] == composite)][["seed", "acquired_at", "censored_acquired_at", "is_censored"]].rename(
            columns={"acquired_at": "left_acquired_at", "censored_acquired_at": "left_censored_acquired_at", "is_censored": "left_is_censored"}
        )
        right_acq = acq[(acq["condition"] == right) & (acq["task_name"] == composite)][["seed", "acquired_at", "censored_acquired_at", "is_censored"]].rename(
            columns={"acquired_at": "right_acquired_at", "censored_acquired_at": "right_censored_acquired_at", "is_censored": "right_is_censored"}
        )
        merged = left_acq.merge(right_acq, on="seed", how="inner")
        left_final = _final_metric(final, left, composite, metric_family, "left")
        right_final = _final_metric(final, right, composite, metric_family, "right")
        merged = merged.merge(left_final, on="seed", how="left").merge(right_final, on="seed", how="left")
        if merged.empty:
            rows.append(empty_contrast(left, right, expected, composite, contrast_type))
            continue
        both = merged[merged["left_acquired_at"].notna() & merged["right_acquired_at"].notna()].copy()
        strict_delta = both["left_acquired_at"] - both["right_acquired_at"] if not both.empty else pd.Series(dtype=float)
        censored_delta = merged["left_censored_acquired_at"] - merged["right_censored_acquired_at"]
        final_delta = merged["left_final_metric"] - merged["right_final_metric"]
        if expected == "earlier":
            strict_expected = strict_delta < 0
            censored_expected = censored_delta < 0
            final_expected = final_delta > 0
        else:
            strict_expected = strict_delta > 0
            censored_expected = censored_delta > 0
            final_expected = final_delta < 0
        rows.append({
            "composite": composite,
            "left_condition": left,
            "right_condition": right,
            "expected_direction": expected,
            "contrast_type": contrast_type,
            "n_paired_seeds": int(len(merged)),
            "n_strict_paired_acquired": int(len(both)),
            "left_acquisition_rate": float(merged["left_acquired_at"].notna().mean()),
            "right_acquisition_rate": float(merged["right_acquired_at"].notna().mean()),
            "strict_delta_acquired_at_mean": float(strict_delta.mean()) if len(strict_delta) else np.nan,
            "strict_expected_direction_rate": float(strict_expected.mean()) if len(strict_delta) else np.nan,
            "censored_delta_acquired_at_mean": float(censored_delta.mean()),
            "censored_expected_direction_rate": float(censored_expected.mean()),
            "final_metric_delta_mean": float(final_delta.mean()),
            "final_metric_expected_direction_rate": float(final_expected.mean()),
            "left_final_metric_mean": float(merged["left_final_metric"].mean()),
            "right_final_metric_mean": float(merged["right_final_metric"].mean()),
        })
    return pd.DataFrame(rows)


def _final_metric(final: pd.DataFrame, condition: str, task_name: str, metric_family: str, prefix: str) -> pd.DataFrame:
    col = metric_family if metric_family in final.columns else "token_accuracy"
    out = final[(final["condition"] == condition) & (final["task_name"] == task_name)][["seed", col]].copy()
    return out.rename(columns={col: f"{prefix}_final_metric"})


def empty_contrast(left: str, right: str, expected: str, composite: str, contrast_type: str = "") -> dict[str, Any]:
    return {
        "composite": composite,
        "left_condition": left,
        "right_condition": right,
        "expected_direction": expected,
        "contrast_type": contrast_type,
        "n_paired_seeds": 0,
        "n_strict_paired_acquired": 0,
        "left_acquisition_rate": np.nan,
        "right_acquisition_rate": np.nan,
        "strict_delta_acquired_at_mean": np.nan,
        "strict_expected_direction_rate": np.nan,
        "censored_delta_acquired_at_mean": np.nan,
        "censored_expected_direction_rate": np.nan,
        "final_metric_delta_mean": np.nan,
        "final_metric_expected_direction_rate": np.nan,
    }


def summarize_pair(acq: pd.DataFrame, final: pd.DataFrame, contrasts: pd.DataFrame, pair: dict[str, str], metric_family: str) -> pd.DataFrame:
    task_keys = ["component", "composite", "unrelated_control", "same_operation_control", "different_operation_control", "fake_component_control", "surface_control"]
    tasks = []
    for key in task_keys:
        value = pair.get(key)
        if value and value not in tasks:
            tasks.append(value)
    rows = []
    for condition in sorted(acq["condition"].unique()):
        for task in tasks:
            g = acq[(acq["condition"] == condition) & (acq["task_name"] == task)]
            f = final[(final["condition"] == condition) & (final["task_name"] == task)]
            rows.append({
                "condition": condition,
                "task_name": task,
                "role": _role(task, pair),
                "acquisition_rate": float(g["acquired_at"].notna().mean()) if not g.empty else np.nan,
                "mean_censored_acquired_at": float(g["censored_acquired_at"].mean()) if not g.empty else np.nan,
                "mean_final_metric": float(f[metric_family].mean()) if not f.empty and metric_family in f.columns else np.nan,
            })
    summary = pd.DataFrame(rows)
    # Attach simple aggregate contrast quality as repeated columns for convenience.
    if not contrasts.empty:
        summary["mean_censored_expected_direction_rate"] = float(contrasts["censored_expected_direction_rate"].mean())
        summary["mean_final_expected_direction_rate"] = float(contrasts["final_metric_expected_direction_rate"].mean())
    return summary


def _role(task: str, pair: dict[str, str]) -> str:
    for k, v in pair.items():
        if task == v:
            return k
    return "other"


def make_report(pair: dict[str, str], acq: pd.DataFrame, final: pd.DataFrame, contrasts: pd.DataFrame, pair_summary: pd.DataFrame, metric_family: str, threshold: float) -> str:
    lines = [
        "# B1 H3 pair-specific intervention analysis",
        "",
        "This is an H3 pilot analysis. It tests whether component interventions move the selected composite beyond matched control interventions. It is causal only within this controlled training setup and remains a pilot until replicated across more pairs/families.",
        "",
        f"Primary metric: `{metric_family}` threshold `{threshold}`.",
        "",
        "## Pair",
        f"- component: `{pair['component']}`",
        f"- composite: `{pair['composite']}`",
        f"- unrelated_control: `{pair.get('unrelated_control', '')}`",
        f"- same_operation_control: `{pair.get('same_operation_control', '')}`",
        f"- different_operation_control: `{pair.get('different_operation_control', '')}`",
        f"- fake_component_control: `{pair.get('fake_component_control', '')}`",
        f"- surface_control: `{pair.get('surface_control', '')}`",
        "",
        "## Composite acquisition by condition",
    ]
    comp = pair["composite"]
    comp_rows = pair_summary[pair_summary["task_name"] == comp]
    for _, r in comp_rows.iterrows():
        lines.append(
            f"- `{r['condition']}`: acq={r['acquisition_rate']:.3f}, mean censored time={r['mean_censored_acquired_at']:.1f}, final={r['mean_final_metric']:.3f}"
        )
    lines += ["", "## Intervention contrasts"]
    if contrasts.empty:
        lines.append("No intervention contrasts available.")
    else:
        for _, r in contrasts.iterrows():
            lines.append(
                f"- `{r['contrast_type']}`: `{r['left_condition']}` vs `{r['right_condition']}` ({r['expected_direction']}): "
                f"strict Δ={_fmt(r['strict_delta_acquired_at_mean'])} (n={int(r['n_strict_paired_acquired'])}), "
                f"censored Δ={_fmt(r['censored_delta_acquired_at_mean'])}, "
                f"censored-rate={_fmt(r['censored_expected_direction_rate'])}, "
                f"Δfinal={_fmt(r['final_metric_delta_mean'])}"
            )
    if not contrasts.empty:
        mean_censored = contrasts["censored_expected_direction_rate"].mean()
        mean_final = contrasts["final_metric_expected_direction_rate"].mean()
        exact_same = contrasts[contrasts.get("contrast_type", pd.Series(dtype=str)).astype(str).str.contains("same_operation", na=False)]
        exact_diff = contrasts[contrasts.get("contrast_type", pd.Series(dtype=str)).astype(str).str.contains("different_operation", na=False)]
        lines += [
            "",
            "## Decision aid",
            f"- mean censored expected-direction rate: `{mean_censored:.3f}`",
            f"- mean final-metric expected-direction rate: `{mean_final:.3f}`",
        ]
        if not exact_same.empty:
            lines.append(f"- exact-vs-same-operation censored expected-direction rate: `{exact_same['censored_expected_direction_rate'].mean():.3f}`")
        if not exact_diff.empty:
            lines.append(f"- exact/different-operation censored expected-direction rate: `{exact_diff['censored_expected_direction_rate'].mean():.3f}`")
        lines += [
            "",
            "GREEN for exact-component dependency requires exact-component interventions to beat same-operation, different-operation, fake, and surface controls. If component and same-operation controls both help similarly, interpret the result as operation-family transfer rather than exact dependency.",
        ]
    return "\n".join(lines)


def _fmt(x: Any) -> str:
    try:
        if pd.isna(x):
            return "nan"
        return f"{float(x):.3f}"
    except Exception:
        return str(x)


if __name__ == "__main__":
    main()
