from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

from ic_experiments.run_management import append_registry, write_manifest


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _load_slices(path: Path) -> list[dict[str, Any]]:
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _score_choice(model: Any, tokenizer: Any, prompt: str, choice: str, device: str) -> float:
    import torch

    prompt_ids = tokenizer(prompt, return_tensors="pt", add_special_tokens=False).input_ids.to(device)
    choice_ids = tokenizer(choice, return_tensors="pt", add_special_tokens=False).input_ids.to(device)
    input_ids = torch.cat([prompt_ids, choice_ids], dim=1)
    with torch.no_grad():
        logits = model(input_ids).logits
        logp = torch.log_softmax(logits, dim=-1)
    # log prob for choice tokens; token t is predicted by previous position.
    start = prompt_ids.shape[1]
    total = 0.0
    for j in range(choice_ids.shape[1]):
        pos = start + j - 1
        tok = int(choice_ids[0, j])
        total += float(logp[0, pos, tok].detach().cpu())
    return total


def _evaluate_model(model_name: str, revision: str | None, examples: list[dict[str, Any]], device: str, max_examples_per_slice: int | None) -> list[dict[str, Any]]:
    try:
        import torch  # noqa: F401
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except Exception as e:
        raise RuntimeError("run_pythia_observational_pilot requires torch and transformers. Install them or run only slice generation/analysis.") from e

    tok = AutoTokenizer.from_pretrained(model_name, revision=revision, trust_remote_code=False)
    model = AutoModelForCausalLM.from_pretrained(model_name, revision=revision, trust_remote_code=False)
    model.to(device)
    model.eval()

    counts: dict[str, int] = {}
    rows = []
    for ex in examples:
        sid = ex["slice_id"]
        counts[sid] = counts.get(sid, 0) + 1
        if max_examples_per_slice is not None and counts[sid] > max_examples_per_slice:
            continue
        choices = list(ex.get("choices") or [" A", " B", " C", " D"])
        scores = [_score_choice(model, tok, ex["prompt"], ch, device) for ch in choices]
        pred_i = int(np.argmax(scores))
        correct_i = choices.index(ex["correct_choice"])
        sorted_scores = sorted(scores, reverse=True)
        top_margin = float(sorted_scores[0] - sorted_scores[1]) if len(sorted_scores) > 1 else 0.0
        correct_score = float(scores[correct_i])
        best_incorrect = max(float(s) for j, s in enumerate(scores) if j != correct_i) if len(scores) > 1 else float("nan")
        correct_margin = correct_score - best_incorrect if math.isfinite(best_incorrect) else 0.0
        # Rank 1 means the correct option is top-scored. Ties are treated optimistically.
        correct_rank = 1 + sum(float(s) > correct_score for j, s in enumerate(scores) if j != correct_i)
        rows.append({
            "slice_id": sid,
            "correct": int(pred_i == correct_i),
            "logprob_correct": correct_score,
            "logprob_pred": float(scores[pred_i]),
            "logprob_margin": top_margin,
            "correct_margin": float(correct_margin),
            "correct_rank": int(correct_rank),
            "correct_mrr": float(1.0 / correct_rank),
            "n_choices": len(choices),
        })
    return rows


def _aggregate(rows: list[dict[str, Any]], model_name: str, revision: str, checkpoint_index: int, data_seen_proxy: float) -> list[dict[str, Any]]:
    by: dict[str, list[dict[str, Any]]] = {}
    for r in rows:
        by.setdefault(r["slice_id"], []).append(r)
    out = []
    for sid, rs in by.items():
        out.append({
            "model_name": model_name,
            "revision": revision,
            "checkpoint_index": checkpoint_index,
            "data_seen_proxy": data_seen_proxy,
            "slice_id": sid,
            "accuracy": float(np.mean([r["correct"] for r in rs])),
            "mean_logprob_correct": float(np.mean([r["logprob_correct"] for r in rs])),
            "mean_logprob_margin": float(np.mean([r["logprob_margin"] for r in rs])),
            "mean_correct_margin": float(np.mean([r.get("correct_margin", float("nan")) for r in rs])),
            "mean_correct_rank": float(np.mean([r.get("correct_rank", float("nan")) for r in rs])),
            "mean_correct_mrr": float(np.mean([r.get("correct_mrr", float("nan")) for r in rs])),
            "n_examples": len(rs),
        })
    return out


def main() -> None:
    p = argparse.ArgumentParser(description="Evaluate checkpointed causal LMs on the observational slice suite.")
    p.add_argument("--slice-table", required=True)
    p.add_argument("--examples", required=True)
    p.add_argument("--output-dir", default="results/pythia_observational_pilot_v24")
    p.add_argument("--model-name", default="EleutherAI/pythia-70m")
    p.add_argument("--revisions", nargs="+", default=["step0", "step1000", "step10000", "step143000"], help="HF revisions/checkpoints to evaluate, e.g. step1000")
    p.add_argument("--data-seen-proxies", nargs="*", type=float, default=None, help="Optional numeric x-axis values matching revisions.")
    p.add_argument("--device", default="cuda")
    p.add_argument("--max-examples-per-slice", type=int, default=64)
    p.add_argument("--code-version", default="v2.4")
    p.add_argument("--archive-root", default="results/archive")
    p.add_argument("--thesis-use", default="diagnostic")
    args = p.parse_args()

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    examples = _read_jsonl(Path(args.examples))
    slices = _load_slices(Path(args.slice_table))

    if args.data_seen_proxies and len(args.data_seen_proxies) != len(args.revisions):
        raise ValueError("--data-seen-proxies must have the same length as --revisions")
    proxies = args.data_seen_proxies or list(range(len(args.revisions)))

    all_rows = []
    for i, rev in enumerate(args.revisions):
        eval_rows = _evaluate_model(args.model_name, rev, examples, args.device, args.max_examples_per_slice)
        all_rows.extend(_aggregate(eval_rows, args.model_name, rev, i, float(proxies[i])))

    with (out / "pythia_eval_curves.csv").open("w", newline="", encoding="utf-8") as f:
        fieldnames = ["model_name", "revision", "checkpoint_index", "data_seen_proxy", "slice_id", "accuracy", "mean_logprob_correct", "mean_logprob_margin", "mean_correct_margin", "mean_correct_rank", "mean_correct_mrr", "n_examples"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)
    # Copy slice table for analysis portability.
    with (out / "pythia_slice_table.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(slices[0].keys()))
        writer.writeheader()
        writer.writerows(slices)

    report = f"""# Pythia observational pilot run\n\n- model: `{args.model_name}`\n- revisions: `{', '.join(args.revisions)}`\n- slices: `{len(slices)}`\n- examples evaluated per slice/checkpoint: `{args.max_examples_per_slice}`\n\nThis is observational checkpoint evaluation. It can test H1/H2-like signatures but cannot establish causal dependency.\n"""
    (out / "pythia_observational_pilot_report.md").write_text(report, encoding="utf-8")
    manifest = write_manifest(
        out,
        experiment="Pythia_observational_pilot",
        backend="Pythia_observational",
        code_version=args.code_version,
        input_paths={"slice_table": args.slice_table, "examples": args.examples},
        extra={"model_name": args.model_name, "revisions": args.revisions, "thesis_use": args.thesis_use},
    )
    append_registry(Path(args.archive_root) / "results_registry.csv", {
        "run_id": manifest["run_id"],
        "code_version": args.code_version,
        "experiment": manifest["experiment"],
        "backend": manifest["backend"],
        "output_path": str(out),
        "status": "created",
        "thesis_use": args.thesis_use,
        "created_at_utc": manifest["created_at_utc"],
    })
    print(f"Wrote Pythia observational pilot outputs to {out}")


if __name__ == "__main__":
    main()
