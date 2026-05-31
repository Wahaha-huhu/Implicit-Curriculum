from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path
from typing import Any, Callable

from ic_experiments.run_management import append_registry, write_manifest

LETTERS = ["A", "B", "C", "D"]


def _dedup(items: list[str]) -> list[str]:
    out: list[str] = []
    for x in items:
        x = str(x)
        if x not in out:
            out.append(x)
    return out


def _choices(correct: str, wrongs: list[str], rng: random.Random) -> tuple[list[str], int]:
    pool = _dedup([str(correct)] + [str(w) for w in wrongs if str(w) != str(correct)])
    # Fill with simple placeholders if a generator accidentally produced duplicates.
    fillers = ["none", "unknown", "both", "neither", "yes", "no", "maybe", "0", "1", "2", "3", "4"]
    for f in fillers:
        if len(pool) >= 4:
            break
        if f not in pool:
            pool.append(f)
    opts = pool[:4]
    rng.shuffle(opts)
    return opts, opts.index(str(correct))


def _mc_prompt(question: str, opts: list[str]) -> str:
    body = " ".join(f"{LETTERS[i]}) {opt}" for i, opt in enumerate(opts))
    return f"Question: {question}\nChoices: {body}\nAnswer:"


def _letter(idx: int) -> str:
    return " " + LETTERS[idx]


def _example(slice_id: str, question: str, correct: str, wrongs: list[str], rng: random.Random) -> dict[str, Any]:
    opts, idx = _choices(correct, wrongs, rng)
    return {
        "slice_id": slice_id,
        "prompt": _mc_prompt(question, opts),
        "choices": [" A", " B", " C", " D"],
        "correct_choice": _letter(idx),
        "target_text": str(correct),
    }


def _slice(slice_id: str, kind: str, family: str, operation: str, depth: int, freq: float, learn: float, util: float, components: str = "", control_type: str = "", answer_entropy: float = 1.0, prompt_family: str | None = None) -> dict[str, Any]:
    return {
        "slice_id": slice_id,
        "kind": kind,
        "family": family,
        "prompt_family": prompt_family or family,
        "operation_type": operation,
        "composition_depth": depth,
        "frequency_proxy": freq,
        "reference_learnability": learn,
        "formal_utility": util,
        "answer_entropy_proxy": answer_entropy,
        "component_ids": components,
        "control_type": control_type,
    }


def build_h2_ready_suite(seed: int, n_per_slice: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rng = random.Random(seed)
    slices: list[dict[str, Any]] = []
    generators: list[tuple[str, Callable[[random.Random], dict[str, Any]]]] = []

    def add(meta: dict[str, Any], gen: Callable[[random.Random], dict[str, Any]]) -> None:
        slices.append(meta)
        generators.append((meta["slice_id"], gen))

    colors = ["red", "blue", "green", "yellow"]
    animals = ["cat", "dog", "bird", "fish"]
    names = ["Mia", "Leo", "Ava", "Noah"]
    objects = ["key", "coin", "book", "map"]
    words = ["red", "blue", "cat", "dog", "sun", "moon"]

    # Arithmetic atomics.
    def gen_add(r: random.Random) -> dict[str, Any]:
        a, b = r.randint(0, 4), r.randint(0, 4)
        c = a + b
        return _example("arith_add_small", f"What is {a} plus {b}?", str(c), [c + 1, max(0, c - 1), c + 2], r)

    def gen_sub(r: random.Random) -> dict[str, Any]:
        a, b = r.randint(0, 8), r.randint(0, 4)
        if b > a:
            a, b = b, a
        c = a - b
        return _example("arith_sub_small", f"What is {a} minus {b}?", str(c), [c + 1, max(0, c - 1), c + 2], r)

    def gen_compare(r: random.Random) -> dict[str, Any]:
        a, b = r.randint(0, 9), r.randint(0, 9)
        ans = "yes" if a > b else "no"
        return _example("arith_compare", f"Is {a} greater than {b}?", ans, ["no" if ans == "yes" else "yes", "maybe", "unknown"], r)

    def gen_even(r: random.Random) -> dict[str, Any]:
        a = r.randint(0, 12)
        ans = "yes" if a % 2 == 0 else "no"
        return _example("arith_even", f"Is {a} even?", ans, ["no" if ans == "yes" else "yes", "maybe", "unknown"], r)

    def gen_max(r: random.Random) -> dict[str, Any]:
        a, b = r.randint(0, 9), r.randint(0, 9)
        ans = str(max(a, b))
        return _example("arith_max2", f"Which number is larger: {a} or {b}?", ans, [min(a, b), a + b, abs(a - b)], r)

    def gen_min(r: random.Random) -> dict[str, Any]:
        a, b = r.randint(0, 9), r.randint(0, 9)
        ans = str(min(a, b))
        return _example("arith_min2", f"Which number is smaller: {a} or {b}?", ans, [max(a, b), a + b, abs(a - b)], r)

    add(_slice("arith_add_small", "atomic", "arithmetic", "addition", 1, 0.90, 0.20, 0.8), gen_add)
    add(_slice("arith_sub_small", "atomic", "arithmetic", "subtraction", 1, 0.75, 0.35, 0.5), gen_sub)
    add(_slice("arith_compare", "atomic", "arithmetic", "comparison", 1, 0.85, 0.20, 0.8), gen_compare)
    add(_slice("arith_even", "atomic", "arithmetic", "parity", 1, 0.65, 0.40, 0.5), gen_even)
    add(_slice("arith_max2", "atomic", "arithmetic", "max", 1, 0.55, 0.45, 0.4), gen_max)
    add(_slice("arith_min2", "atomic", "arithmetic", "min", 1, 0.55, 0.45, 0.4), gen_min)

    # String atomics.
    def gen_copy(r: random.Random) -> dict[str, Any]:
        w = r.choice(words)
        return _example("word_copy", f"Copy this word: {w}", w, [x for x in words if x != w][:5], r)

    def gen_first(r: random.Random) -> dict[str, Any]:
        seq = r.sample(words, 3)
        return _example("word_first", f"What is the first word in: {' '.join(seq)}?", seq[0], [seq[1], seq[2], r.choice(words)], r)

    def gen_last(r: random.Random) -> dict[str, Any]:
        seq = r.sample(words, 3)
        return _example("word_last", f"What is the last word in: {' '.join(seq)}?", seq[-1], [seq[0], seq[1], r.choice(words)], r)

    def gen_reverse2(r: random.Random) -> dict[str, Any]:
        seq = r.sample(animals, 2)
        ans = " ".join(reversed(seq))
        return _example("word_reverse2", f"Reverse these two words: {' '.join(seq)}", ans, [" ".join(seq), f"{seq[0]} {seq[0]}", f"{seq[1]} {seq[1]}"], r)

    def gen_same(r: random.Random) -> dict[str, Any]:
        same = r.random() < 0.5
        a = r.choice(words)
        b = a if same else r.choice([w for w in words if w != a])
        ans = "yes" if same else "no"
        return _example("word_same", f"Are the two words the same: {a} {b}?", ans, ["no" if ans == "yes" else "yes", "maybe", "unknown"], r)

    add(_slice("word_copy", "atomic", "string", "copy", 1, 0.80, 0.25, 0.8), gen_copy)
    add(_slice("word_first", "atomic", "string", "first", 1, 0.75, 0.30, 0.6), gen_first)
    add(_slice("word_last", "atomic", "string", "last", 1, 0.70, 0.30, 0.6), gen_last)
    add(_slice("word_reverse2", "atomic", "string", "reverse", 1, 0.55, 0.50, 0.8), gen_reverse2)
    add(_slice("word_same", "atomic", "string", "same_compare", 1, 0.60, 0.35, 0.5), gen_same)

    # Retrieval / semantic / syntax atomics.
    def gen_retrieve_obj(r: random.Random) -> dict[str, Any]:
        vals = r.sample(objects, len(names))
        kv = dict(zip(names, vals))
        q = r.choice(names)
        ctx = "; ".join(f"{n} has {o}" for n, o in kv.items())
        return _example("retrieval_object", f"{ctx}. What does {q} have?", kv[q], [o for o in objects if o != kv[q]], r)

    def gen_retrieve_num(r: random.Random) -> dict[str, Any]:
        kv = {n: r.randint(0, 6) for n in names}
        q = r.choice(names)
        ctx = "; ".join(f"{n} has number {v}" for n, v in kv.items())
        return _example("retrieval_number", f"{ctx}. What number does {q} have?", str(kv[q]), [kv[q] + 1, max(0, kv[q] - 1), 9], r)

    def gen_color_lookup(r: random.Random) -> dict[str, Any]:
        obj = r.choice(objects)
        color = r.choice(colors)
        return _example("semantic_color_lookup", f"The {obj} is {color}. What color is the {obj}?", color, [c for c in colors if c != color], r)

    def gen_animal_class(r: random.Random) -> dict[str, Any]:
        animal = r.choice(animals)
        ans = "animal"
        return _example("semantic_animal_class", f"A {animal} is what kind of thing?", ans, ["color", "number", "object"], r)

    def gen_plural(r: random.Random) -> dict[str, Any]:
        plural = r.random() < 0.5
        noun = r.choice(["cat", "dog", "bird"])
        subj = noun + "s" if plural else noun
        ans = "are" if plural else "is"
        return _example("syntax_is_are", f"Choose the verb: The {subj} ___ here.", ans, ["is" if ans == "are" else "are", "was", "be"], r)

    add(_slice("retrieval_object", "atomic", "retrieval", "retrieve_object", 1, 0.60, 0.50, 0.8), gen_retrieve_obj)
    add(_slice("retrieval_number", "atomic", "retrieval", "retrieve_number", 1, 0.55, 0.55, 0.8), gen_retrieve_num)
    add(_slice("semantic_color_lookup", "atomic", "semantic", "color_lookup", 1, 0.70, 0.25, 0.4), gen_color_lookup)
    add(_slice("semantic_animal_class", "atomic", "semantic", "category", 1, 0.75, 0.20, 0.3), gen_animal_class)
    add(_slice("syntax_is_are", "atomic", "syntax", "agreement", 1, 0.75, 0.35, 0.4), gen_plural)

    # Composites.
    def gen_add_compare(r: random.Random) -> dict[str, Any]:
        a, b, c = r.randint(0, 4), r.randint(0, 4), r.randint(0, 8)
        ans = "yes" if a + b > c else "no"
        return _example("comp_add_then_compare", f"Is {a} plus {b} greater than {c}?", ans, ["no" if ans == "yes" else "yes", "maybe", "unknown"], r)

    def gen_sub_compare(r: random.Random) -> dict[str, Any]:
        a, b, c = r.randint(0, 8), r.randint(0, 4), r.randint(0, 6)
        if b > a:
            a, b = b, a
        ans = "yes" if a - b > c else "no"
        return _example("comp_sub_then_compare", f"Is {a} minus {b} greater than {c}?", ans, ["no" if ans == "yes" else "yes", "maybe", "unknown"], r)

    def gen_add_even(r: random.Random) -> dict[str, Any]:
        a, b = r.randint(0, 5), r.randint(0, 5)
        ans = "yes" if (a + b) % 2 == 0 else "no"
        return _example("comp_add_then_even", f"Is {a} plus {b} even?", ans, ["no" if ans == "yes" else "yes", "maybe", "unknown"], r)

    def gen_max_compare(r: random.Random) -> dict[str, Any]:
        a, b, c = r.randint(0, 9), r.randint(0, 9), r.randint(0, 9)
        ans = "yes" if max(a, b) > c else "no"
        return _example("comp_max_then_compare", f"Is the larger of {a} and {b} greater than {c}?", ans, ["no" if ans == "yes" else "yes", "maybe", "unknown"], r)

    def gen_retrieve_compare(r: random.Random) -> dict[str, Any]:
        kv = {n: r.randint(0, 6) for n in names}
        q = r.choice(names)
        t = r.randint(0, 6)
        ctx = "; ".join(f"{n} has number {v}" for n, v in kv.items())
        ans = "yes" if kv[q] > t else "no"
        return _example("comp_retrieve_then_compare", f"{ctx}. Is {q}'s number greater than {t}?", ans, ["no" if ans == "yes" else "yes", "maybe", "unknown"], r)

    def gen_retrieve_color(r: random.Random) -> dict[str, Any]:
        obj = r.choice(objects)
        color = r.choice(colors)
        holder = r.choice(names)
        return _example("comp_retrieve_then_color", f"{holder} has the {obj}. The {obj} is {color}. What color is {holder}'s thing?", color, [c for c in colors if c != color], r)

    def gen_reverse_first(r: random.Random) -> dict[str, Any]:
        seq = r.sample(words, 3)
        rev = list(reversed(seq))
        return _example("comp_reverse_then_first", f"Reverse this list, then give the first word: {' '.join(seq)}", rev[0], [rev[1], rev[2], seq[0]], r)

    def gen_reverse_last(r: random.Random) -> dict[str, Any]:
        seq = r.sample(words, 3)
        rev = list(reversed(seq))
        return _example("comp_reverse_then_last", f"Reverse this list, then give the last word: {' '.join(seq)}", rev[-1], [rev[0], rev[1], seq[-1]], r)

    def gen_first_same(r: random.Random) -> dict[str, Any]:
        seq1 = r.sample(words, 3)
        seq2 = r.sample(words, 3)
        ans = "yes" if seq1[0] == seq2[0] else "no"
        return _example("comp_first_then_same", f"Are the first words the same: {' '.join(seq1)} / {' '.join(seq2)}?", ans, ["no" if ans == "yes" else "yes", "maybe", "unknown"], r)

    def gen_reverse_same(r: random.Random) -> dict[str, Any]:
        seq = r.sample(words, 3)
        rev = list(reversed(seq))
        ans = "yes" if rev[0] == seq[-1] else "no"  # Usually yes by construction.
        return _example("comp_reverse_then_same", f"After reversing {' '.join(seq)}, is the first word {seq[-1]}?", ans, ["no" if ans == "yes" else "yes", "maybe", "unknown"], r)

    add(_slice("comp_add_then_compare", "composite", "arithmetic", "add_then_compare", 2, 0.40, 0.55, 0.0, "arith_add_small;arith_compare"), gen_add_compare)
    add(_slice("comp_sub_then_compare", "composite", "arithmetic", "sub_then_compare", 2, 0.35, 0.65, 0.0, "arith_sub_small;arith_compare"), gen_sub_compare)
    add(_slice("comp_add_then_even", "composite", "arithmetic", "add_then_parity", 2, 0.35, 0.60, 0.0, "arith_add_small;arith_even"), gen_add_even)
    add(_slice("comp_max_then_compare", "composite", "arithmetic", "max_then_compare", 2, 0.30, 0.70, 0.0, "arith_max2;arith_compare"), gen_max_compare)
    add(_slice("comp_retrieve_then_compare", "composite", "retrieval", "retrieve_then_compare", 2, 0.30, 0.80, 0.0, "retrieval_number;arith_compare"), gen_retrieve_compare)
    add(_slice("comp_retrieve_then_color", "composite", "retrieval", "retrieve_then_color", 2, 0.35, 0.65, 0.0, "retrieval_object;semantic_color_lookup"), gen_retrieve_color)
    add(_slice("comp_reverse_then_first", "composite", "string", "reverse_then_first", 2, 0.30, 0.65, 0.0, "word_reverse2;word_first"), gen_reverse_first)
    add(_slice("comp_reverse_then_last", "composite", "string", "reverse_then_last", 2, 0.30, 0.65, 0.0, "word_reverse2;word_last"), gen_reverse_last)
    add(_slice("comp_first_then_same", "composite", "string", "first_then_same", 2, 0.35, 0.55, 0.0, "word_first;word_same"), gen_first_same)
    add(_slice("comp_reverse_then_same", "composite", "string", "reverse_then_same", 2, 0.25, 0.75, 0.0, "word_reverse2;word_same"), gen_reverse_same)

    # Surface / operation-family controls.
    def gen_num_surface(r: random.Random) -> dict[str, Any]:
        color = r.choice(colors)
        return _example("ctrl_number_surface", f"Ignore numbers {r.randint(0,9)} and {r.randint(0,9)}. The color word is {color}. What color word appears?", color, [c for c in colors if c != color], r)

    def gen_word_surface(r: random.Random) -> dict[str, Any]:
        animal = r.choice(animals)
        return _example("ctrl_word_surface", f"The visible animal word is {animal}. Which animal word is visible?", animal, [a for a in animals if a != animal], r)

    def gen_retrieval_surface(r: random.Random) -> dict[str, Any]:
        name = r.choice(names)
        obj = r.choice(objects)
        return _example("ctrl_retrieval_surface", f"{name} appears with the word {obj}. Which object word appears?", obj, [o for o in objects if o != obj], r)

    add(_slice("ctrl_number_surface", "surface_control", "surface", "number_surface", 1, 0.50, 0.30, 0.0, "", "surface"), gen_num_surface)
    add(_slice("ctrl_word_surface", "surface_control", "surface", "word_surface", 1, 0.50, 0.30, 0.0, "", "surface"), gen_word_surface)
    add(_slice("ctrl_retrieval_surface", "surface_control", "surface", "retrieval_surface", 1, 0.45, 0.35, 0.0, "", "surface"), gen_retrieval_surface)

    examples: list[dict[str, Any]] = []
    for _, gen in generators:
        for _ in range(n_per_slice):
            examples.append(gen(rng))
    return slices, examples


def main() -> None:
    p = argparse.ArgumentParser(description="Create an H2-ready Pythia observational slice suite with many atomic/composite slices.")
    p.add_argument("--output-dir", default="results/pythia_h2_ready_slice_suite_v27")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--n-per-slice", type=int, default=64)
    p.add_argument("--code-version", default="v2.7")
    p.add_argument("--archive-root", default="results/archive")
    p.add_argument("--thesis-use", default="diagnostic")
    args = p.parse_args()

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    slices, examples = build_h2_ready_suite(args.seed, args.n_per_slice)

    with (out / "pythia_slice_table.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(slices[0].keys()))
        writer.writeheader()
        writer.writerows(slices)
    with (out / "pythia_slice_examples.jsonl").open("w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex, sort_keys=True) + "\n")

    n_atomic = sum(1 for s in slices if s["kind"] == "atomic")
    n_comp = sum(1 for s in slices if s["kind"] == "composite")
    n_ctrl = sum(1 for s in slices if "control" in s["kind"])
    report = [
        "# Pythia H2-ready observational slice suite",
        "",
        "This suite expands the Pythia bridge so primitive-to-composite residual analysis has enough atomic slices to fit a non-degenerate predictor.",
        "",
        f"- total slices: `{len(slices)}`",
        f"- atomic slices: `{n_atomic}`",
        f"- composite slices: `{n_comp}`",
        f"- control slices: `{n_ctrl}`",
        f"- examples: `{len(examples)}`",
        f"- examples per slice: `{args.n_per_slice}`",
        "",
        "## Claim boundary",
        "This suite supports observational H1/H2-style signatures only. It cannot establish causal dependency because Pythia pretraining is not intervened on.",
    ]
    (out / "pythia_h2_ready_slice_suite_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    manifest = write_manifest(
        out,
        experiment="Pythia_H2_ready_slice_suite_generation",
        backend="Pythia_observational",
        code_version=args.code_version,
        input_paths={},
        extra={"n_slices": len(slices), "n_atomic": n_atomic, "n_composites": n_comp, "n_controls": n_ctrl, "n_examples": len(examples), "thesis_use": args.thesis_use},
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
    print(f"Wrote Pythia H2-ready slice suite to {out}")


if __name__ == "__main__":
    main()
