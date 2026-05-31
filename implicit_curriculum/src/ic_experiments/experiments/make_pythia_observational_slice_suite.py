from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from pathlib import Path
from typing import Any

from ic_experiments.run_management import append_registry, write_manifest


def _choices(correct: str, wrongs: list[str], rng: random.Random) -> tuple[list[str], int]:
    opts = [correct] + wrongs
    rng.shuffle(opts)
    return opts, opts.index(correct)


def _mc_prompt(question: str, opts: list[str]) -> str:
    letters = ["A", "B", "C", "D"]
    body = " ".join(f"{letters[i]}) {opt}" for i, opt in enumerate(opts))
    return f"Question: {question}\nChoices: {body}\nAnswer:"


def _letter(idx: int) -> str:
    return " " + ["A", "B", "C", "D"][idx]


def build_examples(seed: int, n_per_slice: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rng = random.Random(seed)
    slices: list[dict[str, Any]] = []
    examples: list[dict[str, Any]] = []

    def add_slice(slice_id: str, kind: str, family: str, operation: str, depth: int, freq: float, learn: float, util: float, components: str = "", control_type: str = ""):
        slices.append({
            "slice_id": slice_id,
            "kind": kind,
            "family": family,
            "operation_type": operation,
            "composition_depth": depth,
            "frequency_proxy": freq,
            "reference_learnability": learn,
            "formal_utility": util,
            "component_ids": components,
            "control_type": control_type,
        })

    add_slice("arith_add_1d", "atomic", "arithmetic", "addition", 1, 0.85, 0.25, 0.8)
    add_slice("arith_compare_1d", "atomic", "arithmetic", "comparison", 1, 0.70, 0.20, 0.6)
    add_slice("arith_add_then_compare", "composite", "arithmetic", "add_then_compare", 2, 0.35, 0.65, 0.0, "arith_add_1d;arith_compare_1d")
    add_slice("arith_surface_control", "surface_control", "arithmetic", "surface_numbers", 1, 0.35, 0.35, 0.0, "", "surface")
    add_slice("syntax_local_agreement", "atomic", "syntax", "agreement", 1, 0.75, 0.30, 0.7)
    add_slice("syntax_distractor_agreement", "composite", "syntax", "agreement_with_distractor", 2, 0.40, 0.70, 0.0, "syntax_local_agreement")
    add_slice("retrieval_kv", "atomic", "retrieval", "retrieve", 1, 0.60, 0.45, 0.7)
    add_slice("retrieval_then_compare", "composite", "retrieval", "retrieve_then_compare", 2, 0.30, 0.80, 0.0, "retrieval_kv;arith_compare_1d")
    add_slice("string_copy", "atomic", "string", "copy", 1, 0.65, 0.30, 0.7)
    add_slice("string_reverse", "atomic", "string", "reverse", 1, 0.50, 0.55, 0.7)
    add_slice("string_reverse_then_copy", "composite", "string", "reverse_then_copy", 2, 0.25, 0.85, 0.0, "string_reverse;string_copy")
    add_slice("string_surface_control", "surface_control", "string", "surface_tokens", 1, 0.25, 0.40, 0.0, "", "surface")

    colors = ["red", "blue", "green", "yellow"]
    animals = ["cat", "dog", "bird", "fish"]
    names = ["Mia", "Leo", "Ava", "Noah"]
    objects = ["key", "coin", "book", "map"]

    for _ in range(n_per_slice):
        # arithmetic add
        a, b = rng.randint(0, 8), rng.randint(0, 8)
        correct = str(a + b)
        wrongs = [str(a + b + d) for d in [1, -1, 2] if a + b + d >= 0]
        while len(wrongs) < 3:
            wrongs.append(str(rng.randint(0, 18)))
        opts, idx = _choices(correct, wrongs[:3], rng)
        examples.append({"slice_id": "arith_add_1d", "prompt": _mc_prompt(f"What is {a} plus {b}?", opts), "choices": [" A", " B", " C", " D"], "correct_choice": _letter(idx), "target_text": correct})

        # compare
        x, y = rng.randint(0, 9), rng.randint(0, 9)
        correct = "yes" if x > y else "no"
        opts, idx = _choices(correct, ["no" if correct == "yes" else "yes", "maybe", "unknown"], rng)
        examples.append({"slice_id": "arith_compare_1d", "prompt": _mc_prompt(f"Is {x} greater than {y}?", opts), "choices": [" A", " B", " C", " D"], "correct_choice": _letter(idx), "target_text": correct})

        # add then compare
        a, b, c = rng.randint(0, 6), rng.randint(0, 6), rng.randint(0, 12)
        correct = "yes" if a + b > c else "no"
        opts, idx = _choices(correct, ["no" if correct == "yes" else "yes", "maybe", "unknown"], rng)
        examples.append({"slice_id": "arith_add_then_compare", "prompt": _mc_prompt(f"Is {a} plus {b} greater than {c}?", opts), "choices": [" A", " B", " C", " D"], "correct_choice": _letter(idx), "target_text": correct})

        # arithmetic surface control: mention numbers but ask color fact from prompt.
        color = rng.choice(colors)
        opts, idx = _choices(color, [c for c in colors if c != color][:3], rng)
        examples.append({"slice_id": "arith_surface_control", "prompt": _mc_prompt(f"Ignore the numbers {rng.randint(0,9)} and {rng.randint(0,9)}. The stated color is {color}. What is the color?", opts), "choices": [" A", " B", " C", " D"], "correct_choice": _letter(idx), "target_text": color})

        # syntax local agreement
        noun = rng.choice(["cat", "dog", "bird"])
        verb = rng.choice(["runs", "sleeps", "jumps"])
        opts, idx = _choices(verb, ["run", "sleep", "jump"], rng)
        examples.append({"slice_id": "syntax_local_agreement", "prompt": _mc_prompt(f"Choose the grammatical verb: The {noun} ___ .", opts), "choices": [" A", " B", " C", " D"], "correct_choice": _letter(idx), "target_text": verb})

        # syntax distractor agreement
        noun = rng.choice(["cat", "dog", "bird"])
        distractor = rng.choice(["dogs", "cats", "birds"])
        verb = rng.choice(["runs", "sleeps", "jumps"])
        opts, idx = _choices(verb, ["run", "sleep", "jump"], rng)
        examples.append({"slice_id": "syntax_distractor_agreement", "prompt": _mc_prompt(f"Choose the grammatical verb: The {noun} near the {distractor} ___ .", opts), "choices": [" A", " B", " C", " D"], "correct_choice": _letter(idx), "target_text": verb})

        # retrieval
        kv = dict(zip(names, rng.sample(objects, len(names))))
        q = rng.choice(names)
        correct = kv[q]
        opts, idx = _choices(correct, [o for o in objects if o != correct][:3], rng)
        context = "; ".join(f"{k} has {v}" for k, v in kv.items())
        examples.append({"slice_id": "retrieval_kv", "prompt": _mc_prompt(f"{context}. What does {q} have?", opts), "choices": [" A", " B", " C", " D"], "correct_choice": _letter(idx), "target_text": correct})

        # retrieval then compare
        kvn = {name: rng.randint(0, 9) for name in names}
        q = rng.choice(names)
        t = rng.randint(0, 9)
        correct = "yes" if kvn[q] > t else "no"
        opts, idx = _choices(correct, ["no" if correct == "yes" else "yes", "maybe", "unknown"], rng)
        context = "; ".join(f"{k} has number {v}" for k, v in kvn.items())
        examples.append({"slice_id": "retrieval_then_compare", "prompt": _mc_prompt(f"{context}. Is {q}'s number greater than {t}?", opts), "choices": [" A", " B", " C", " D"], "correct_choice": _letter(idx), "target_text": correct})

        # strings with MC sequence options as joined tokens
        seq = rng.sample(animals, 3)
        correct = " ".join(seq)
        wrong_pool = [" ".join(rng.sample(animals, 3)) for _ in range(8)]
        wrongs = []
        for w in wrong_pool:
            if w != correct and w not in wrongs:
                wrongs.append(w)
            if len(wrongs) == 3:
                break
        opts, idx = _choices(correct, wrongs, rng)
        examples.append({"slice_id": "string_copy", "prompt": _mc_prompt(f"Copy the sequence: {' '.join(seq)}", opts), "choices": [" A", " B", " C", " D"], "correct_choice": _letter(idx), "target_text": correct})

        rev = list(reversed(seq))
        correct = " ".join(rev)
        wrong_pool = [" ".join(rng.sample(animals, 3)) for _ in range(8)]
        wrongs = []
        for w in wrong_pool:
            if w != correct and w not in wrongs:
                wrongs.append(w)
            if len(wrongs) == 3:
                break
        opts, idx = _choices(correct, wrongs, rng)
        examples.append({"slice_id": "string_reverse", "prompt": _mc_prompt(f"Reverse the sequence: {' '.join(seq)}", opts), "choices": [" A", " B", " C", " D"], "correct_choice": _letter(idx), "target_text": correct})

        # reverse then copy is intentionally a composite phrasing (copy the reversed sequence)
        opts, idx = _choices(correct, wrongs, rng)
        examples.append({"slice_id": "string_reverse_then_copy", "prompt": _mc_prompt(f"First reverse the sequence, then repeat it: {' '.join(seq)}", opts), "choices": [" A", " B", " C", " D"], "correct_choice": _letter(idx), "target_text": correct})

        # string surface control
        animal = rng.choice(animals)
        opts, idx = _choices(animal, [a for a in animals if a != animal][:3], rng)
        examples.append({"slice_id": "string_surface_control", "prompt": _mc_prompt(f"The visible animal token is {animal}. Which animal token is visible?", opts), "choices": [" A", " B", " C", " D"], "correct_choice": _letter(idx), "target_text": animal})

    return slices, examples


def main() -> None:
    p = argparse.ArgumentParser(description="Create a small Pythia-style observational slice suite.")
    p.add_argument("--output-dir", default="results/pythia_slice_suite_v24")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--n-per-slice", type=int, default=64)
    p.add_argument("--code-version", default="v2.4")
    p.add_argument("--archive-root", default="results/archive")
    p.add_argument("--thesis-use", default="diagnostic")
    args = p.parse_args()

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    slices, examples = build_examples(args.seed, args.n_per_slice)

    with (out / "pythia_slice_table.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(slices[0].keys()))
        writer.writeheader()
        writer.writerows(slices)
    with (out / "pythia_slice_examples.jsonl").open("w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex, sort_keys=True) + "\n")

    report = f"""# Pythia-style observational slice suite\n\nThis suite is a small observational bridge from the controlled B1 experiments to checkpointed language models. It is not a causal intervention benchmark.\n\n- slices: `{len(slices)}`\n- examples: `{len(examples)}`\n- examples per slice: `{args.n_per_slice}`\n\n## Design\n\nThe suite contains atomic, composite, and surface-control behavioral slices across arithmetic, syntax, retrieval, and string-operation families. Each example is multiple-choice so checkpoint evaluation can use choice log probabilities rather than generation.\n\n## Claim boundary\n\nThis suite can support H1/H2-style observational signatures: acquisition order, predictor correlations, and primitive-to-composite residuals. It cannot support H3 causal dependency because model pretraining is not intervened on.\n"""
    (out / "pythia_slice_suite_report.md").write_text(report, encoding="utf-8")

    manifest = write_manifest(
        out,
        experiment="Pythia_observational_slice_suite",
        backend="Pythia_observational",
        code_version=args.code_version,
        input_paths={},
        extra={"n_slices": len(slices), "n_examples": len(examples), "thesis_use": args.thesis_use},
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

    print(f"Wrote Pythia observational slice suite to {out}")


if __name__ == "__main__":
    main()
