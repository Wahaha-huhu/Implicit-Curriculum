from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path
from typing import Any

from ic_experiments.run_management import append_registry, write_manifest


def _choices(correct: str, wrongs: list[str], rng: random.Random) -> tuple[list[str], int]:
    opts = [correct] + wrongs
    # Deduplicate while preserving order.
    dedup = []
    for x in opts:
        if x not in dedup:
            dedup.append(x)
    opts = dedup[:4]
    rng.shuffle(opts)
    return opts, opts.index(correct)


def _mc_prompt(question: str, opts: list[str]) -> str:
    letters = ["A", "B", "C", "D"]
    body = " ".join(f"{letters[i]}) {opt}" for i, opt in enumerate(opts))
    return f"Question: {question}\nChoices: {body}\nAnswer:"


def _letter(idx: int) -> str:
    return " " + ["A", "B", "C", "D"][idx]


def build_easy_examples(seed: int, n_per_slice: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rng = random.Random(seed)
    slices = [
        {"slice_id": "easy_add_1d", "kind": "atomic", "family": "arithmetic", "operation_type": "addition", "composition_depth": 1, "frequency_proxy": 0.9, "reference_learnability": 0.2, "formal_utility": 0.8, "component_ids": "", "control_type": ""},
        {"slice_id": "easy_compare_1d", "kind": "atomic", "family": "arithmetic", "operation_type": "comparison", "composition_depth": 1, "frequency_proxy": 0.8, "reference_learnability": 0.2, "formal_utility": 0.8, "component_ids": "", "control_type": ""},
        {"slice_id": "easy_add_then_compare", "kind": "composite", "family": "arithmetic", "operation_type": "add_then_compare", "composition_depth": 2, "frequency_proxy": 0.4, "reference_learnability": 0.5, "formal_utility": 0.0, "component_ids": "easy_add_1d;easy_compare_1d", "control_type": ""},
        {"slice_id": "easy_copy_word", "kind": "atomic", "family": "string", "operation_type": "copy", "composition_depth": 1, "frequency_proxy": 0.75, "reference_learnability": 0.25, "formal_utility": 0.7, "component_ids": "", "control_type": ""},
        {"slice_id": "easy_reverse_two_words", "kind": "atomic", "family": "string", "operation_type": "reverse", "composition_depth": 1, "frequency_proxy": 0.55, "reference_learnability": 0.45, "formal_utility": 0.7, "component_ids": "", "control_type": ""},
        {"slice_id": "easy_reverse_then_copy", "kind": "composite", "family": "string", "operation_type": "reverse_then_copy", "composition_depth": 2, "frequency_proxy": 0.3, "reference_learnability": 0.65, "formal_utility": 0.0, "component_ids": "easy_reverse_two_words;easy_copy_word", "control_type": ""},
        {"slice_id": "easy_color_surface", "kind": "surface_control", "family": "surface", "operation_type": "surface_color", "composition_depth": 1, "frequency_proxy": 0.5, "reference_learnability": 0.25, "formal_utility": 0.0, "component_ids": "", "control_type": "surface"},
        {"slice_id": "easy_animals_surface", "kind": "surface_control", "family": "surface", "operation_type": "surface_animal", "composition_depth": 1, "frequency_proxy": 0.5, "reference_learnability": 0.25, "formal_utility": 0.0, "component_ids": "", "control_type": "surface"},
    ]
    examples: list[dict[str, Any]] = []
    colors = ["red", "blue", "green", "yellow"]
    animals = ["cat", "dog", "bird", "fish"]
    words = ["red", "blue", "cat", "dog"]
    for _ in range(n_per_slice):
        a, b = rng.randint(0, 4), rng.randint(0, 4)
        correct = str(a + b)
        opts, idx = _choices(correct, [str(a + b + 1), str(max(0, a + b - 1)), str(a + b + 2)], rng)
        examples.append({"slice_id": "easy_add_1d", "prompt": _mc_prompt(f"What is {a} plus {b}?", opts), "choices": [" A", " B", " C", " D"], "correct_choice": _letter(idx), "target_text": correct})

        x, y = rng.randint(0, 5), rng.randint(0, 5)
        correct = "yes" if x > y else "no"
        opts, idx = _choices(correct, ["no" if correct == "yes" else "yes", "maybe", "unknown"], rng)
        examples.append({"slice_id": "easy_compare_1d", "prompt": _mc_prompt(f"Is {x} greater than {y}?", opts), "choices": [" A", " B", " C", " D"], "correct_choice": _letter(idx), "target_text": correct})

        a, b, c = rng.randint(0, 3), rng.randint(0, 3), rng.randint(0, 6)
        correct = "yes" if a + b > c else "no"
        opts, idx = _choices(correct, ["no" if correct == "yes" else "yes", "maybe", "unknown"], rng)
        examples.append({"slice_id": "easy_add_then_compare", "prompt": _mc_prompt(f"Is {a} plus {b} greater than {c}?", opts), "choices": [" A", " B", " C", " D"], "correct_choice": _letter(idx), "target_text": correct})

        word = rng.choice(words)
        opts, idx = _choices(word, [w for w in words if w != word], rng)
        examples.append({"slice_id": "easy_copy_word", "prompt": _mc_prompt(f"Copy this word: {word}", opts), "choices": [" A", " B", " C", " D"], "correct_choice": _letter(idx), "target_text": word})

        pair = rng.sample(animals, 2)
        correct = " ".join(reversed(pair))
        wrongs = [" ".join(pair), f"{pair[0]} {pair[0]}", f"{pair[1]} {pair[1]}"]
        opts, idx = _choices(correct, wrongs, rng)
        examples.append({"slice_id": "easy_reverse_two_words", "prompt": _mc_prompt(f"Reverse these two words: {' '.join(pair)}", opts), "choices": [" A", " B", " C", " D"], "correct_choice": _letter(idx), "target_text": correct})

        opts, idx = _choices(correct, wrongs, rng)
        examples.append({"slice_id": "easy_reverse_then_copy", "prompt": _mc_prompt(f"First reverse, then copy these words: {' '.join(pair)}", opts), "choices": [" A", " B", " C", " D"], "correct_choice": _letter(idx), "target_text": correct})

        color = rng.choice(colors)
        opts, idx = _choices(color, [c for c in colors if c != color], rng)
        examples.append({"slice_id": "easy_color_surface", "prompt": _mc_prompt(f"The color is {color}. What color is stated?", opts), "choices": [" A", " B", " C", " D"], "correct_choice": _letter(idx), "target_text": color})

        animal = rng.choice(animals)
        opts, idx = _choices(animal, [a for a in animals if a != animal], rng)
        examples.append({"slice_id": "easy_animals_surface", "prompt": _mc_prompt(f"The animal is {animal}. What animal is stated?", opts), "choices": [" A", " B", " C", " D"], "correct_choice": _letter(idx), "target_text": animal})
    return slices, examples


def main() -> None:
    p = argparse.ArgumentParser(description="Create an easier Pythia observational slice suite for calibration.")
    p.add_argument("--output-dir", default="results/pythia_easy_slice_suite_v25")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--n-per-slice", type=int, default=64)
    p.add_argument("--code-version", default="v2.5")
    p.add_argument("--archive-root", default="results/archive")
    p.add_argument("--thesis-use", default="diagnostic")
    args = p.parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    slices, examples = build_easy_examples(args.seed, args.n_per_slice)
    with (out / "pythia_slice_table.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(slices[0].keys()))
        writer.writeheader()
        writer.writerows(slices)
    with (out / "pythia_slice_examples.jsonl").open("w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex) + "\n")
    report = [
        "# Easy Pythia observational slice suite",
        "",
        f"- slices: `{len(slices)}`",
        f"- examples: `{len(examples)}`",
        "",
        "This suite is intentionally easier than the standard bridge suite. It is for calibration only: use it to find a measurable checkpoint/slice regime before making observational H1/H2 comparisons.",
    ]
    (out / "pythia_easy_slice_suite_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    manifest = write_manifest(
        out,
        experiment="Pythia_easy_slice_suite_generation",
        backend="Pythia_observational",
        code_version=args.code_version,
        input_paths={},
        extra={"n_per_slice": args.n_per_slice, "thesis_use": args.thesis_use},
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
    print(f"Wrote easy Pythia slice suite to {out}")


if __name__ == "__main__":
    main()
