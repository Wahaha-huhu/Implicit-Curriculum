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
    fillers = ["yes", "no", "maybe", "unknown", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
    for f in fillers:
        if len(pool) >= 4:
            break
        if f not in pool:
            pool.append(f)
    opts = pool[:4]
    rng.shuffle(opts)
    return opts, opts.index(str(correct))


def _prompt(question: str, opts: list[str]) -> str:
    return "Question: " + question + "\nChoices: " + " ".join(f"{LETTERS[i]}) {o}" for i, o in enumerate(opts)) + "\nAnswer:"


def _example(slice_id: str, question: str, correct: str | int, wrongs: list[str | int], rng: random.Random) -> dict[str, Any]:
    opts, idx = _choices(str(correct), [str(w) for w in wrongs], rng)
    return {
        "slice_id": slice_id,
        "prompt": _prompt(question, opts),
        "choices": [" A", " B", " C", " D"],
        "correct_choice": " " + LETTERS[idx],
        "target_text": str(correct),
    }


def _slice(slice_id: str, kind: str, operation: str, depth: int, freq: float, learn: float, util: float, components: str = "", control_type: str = "", entropy: float = 1.0) -> dict[str, Any]:
    return {
        "slice_id": slice_id,
        "kind": kind,
        "family": "arithmetic" if kind != "surface_control" else "surface",
        "prompt_family": "arithmetic",
        "operation_type": operation,
        "composition_depth": depth,
        "frequency_proxy": freq,
        "reference_learnability": learn,
        "formal_utility": util,
        "answer_entropy_proxy": entropy,
        "component_ids": components,
        "control_type": control_type,
    }


def build_suite(seed: int, n_per_slice: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rng = random.Random(seed)
    slices: list[dict[str, Any]] = []
    gens: list[tuple[str, Callable[[random.Random], dict[str, Any]]]] = []

    def add(meta: dict[str, Any], gen: Callable[[random.Random], dict[str, Any]]) -> None:
        slices.append(meta)
        gens.append((meta["slice_id"], gen))

    # Atomic arithmetic primitives.
    def add_small(r: random.Random) -> dict[str, Any]:
        a, b = r.randint(0, 5), r.randint(0, 5); c = a + b
        return _example("arith_add_small", f"What is {a} plus {b}?", c, [c+1, max(0,c-1), c+2], r)

    def add_large(r: random.Random) -> dict[str, Any]:
        a, b = r.randint(5, 14), r.randint(5, 14); c = a + b
        return _example("arith_add_large", f"What is {a} plus {b}?", c, [c+1, c-1, c+2], r)

    def sub_small(r: random.Random) -> dict[str, Any]:
        a, b = r.randint(0, 12), r.randint(0, 6)
        if b > a: a, b = b, a
        c = a - b
        return _example("arith_sub_small", f"What is {a} minus {b}?", c, [c+1, max(0,c-1), c+2], r)

    def compare_gt(r: random.Random) -> dict[str, Any]:
        a, b = r.randint(0, 18), r.randint(0, 18); ans = "yes" if a > b else "no"
        return _example("arith_compare_gt", f"Is {a} greater than {b}?", ans, ["no" if ans=="yes" else "yes", "maybe", "unknown"], r)

    def compare_lt(r: random.Random) -> dict[str, Any]:
        a, b = r.randint(0, 18), r.randint(0, 18); ans = "yes" if a < b else "no"
        return _example("arith_compare_lt", f"Is {a} less than {b}?", ans, ["no" if ans=="yes" else "yes", "maybe", "unknown"], r)

    def even(r: random.Random) -> dict[str, Any]:
        a = r.randint(0, 24); ans = "yes" if a % 2 == 0 else "no"
        return _example("arith_even", f"Is {a} even?", ans, ["no" if ans=="yes" else "yes", "maybe", "unknown"], r)

    def odd(r: random.Random) -> dict[str, Any]:
        a = r.randint(0, 24); ans = "yes" if a % 2 == 1 else "no"
        return _example("arith_odd", f"Is {a} odd?", ans, ["no" if ans=="yes" else "yes", "maybe", "unknown"], r)

    def max2(r: random.Random) -> dict[str, Any]:
        a, b = r.randint(0, 18), r.randint(0, 18); ans = max(a,b)
        return _example("arith_max2", f"Which number is larger: {a} or {b}?", ans, [min(a,b), a+b, abs(a-b)], r)

    def min2(r: random.Random) -> dict[str, Any]:
        a, b = r.randint(0, 18), r.randint(0, 18); ans = min(a,b)
        return _example("arith_min2", f"Which number is smaller: {a} or {b}?", ans, [max(a,b), a+b, abs(a-b)], r)

    def double(r: random.Random) -> dict[str, Any]:
        a = r.randint(0, 12); c = 2*a
        return _example("arith_double", f"What is double {a}?", c, [c+1, max(0,c-2), a], r)

    def diff_abs(r: random.Random) -> dict[str, Any]:
        a, b = r.randint(0, 18), r.randint(0, 18); c = abs(a-b)
        return _example("arith_absdiff", f"What is the difference between {a} and {b}?", c, [c+1, max(0,c-1), a+b], r)

    def equals(r: random.Random) -> dict[str, Any]:
        same = r.random() < 0.5; a = r.randint(0, 12); b = a if same else r.choice([x for x in range(13) if x != a]); ans = "yes" if same else "no"
        return _example("arith_equals", f"Is {a} equal to {b}?", ans, ["no" if ans=="yes" else "yes", "maybe", "unknown"], r)

    atomics = [
        ("arith_add_small", "addition_small", .90, .20, .9, add_small),
        ("arith_add_large", "addition_large", .65, .45, .6, add_large),
        ("arith_sub_small", "subtraction", .75, .35, .7, sub_small),
        ("arith_compare_gt", "comparison_gt", .85, .20, .9, compare_gt),
        ("arith_compare_lt", "comparison_lt", .80, .25, .6, compare_lt),
        ("arith_even", "parity_even", .70, .35, .7, even),
        ("arith_odd", "parity_odd", .65, .40, .5, odd),
        ("arith_max2", "max", .60, .45, .7, max2),
        ("arith_min2", "min", .60, .45, .5, min2),
        ("arith_double", "double", .65, .35, .5, double),
        ("arith_absdiff", "absolute_difference", .50, .60, .4, diff_abs),
        ("arith_equals", "equality", .75, .25, .4, equals),
    ]
    for sid, op, freq, learn, util, gen in atomics:
        add(_slice(sid, "atomic", op, 1, freq, learn, util), gen)

    # Composites.
    def comp_add_gt(r: random.Random) -> dict[str, Any]:
        a,b,c = r.randint(0,6), r.randint(0,6), r.randint(0,12); ans = "yes" if a+b > c else "no"
        return _example("comp_add_then_compare_gt", f"Is {a} plus {b} greater than {c}?", ans, ["no" if ans=="yes" else "yes", "maybe", "unknown"], r)

    def comp_add_lt(r: random.Random) -> dict[str, Any]:
        a,b,c = r.randint(0,6), r.randint(0,6), r.randint(0,12); ans = "yes" if a+b < c else "no"
        return _example("comp_add_then_compare_lt", f"Is {a} plus {b} less than {c}?", ans, ["no" if ans=="yes" else "yes", "maybe", "unknown"], r)

    def comp_sub_gt(r: random.Random) -> dict[str, Any]:
        a,b,c = r.randint(0,14), r.randint(0,8), r.randint(0,10)
        if b > a: a,b = b,a
        ans = "yes" if a-b > c else "no"
        return _example("comp_sub_then_compare_gt", f"Is {a} minus {b} greater than {c}?", ans, ["no" if ans=="yes" else "yes", "maybe", "unknown"], r)

    def comp_add_even(r: random.Random) -> dict[str, Any]:
        a,b = r.randint(0,8), r.randint(0,8); ans = "yes" if (a+b)%2==0 else "no"
        return _example("comp_add_then_even", f"Is {a} plus {b} even?", ans, ["no" if ans=="yes" else "yes", "maybe", "unknown"], r)

    def comp_sub_odd(r: random.Random) -> dict[str, Any]:
        a,b = r.randint(0,14), r.randint(0,8)
        if b > a: a,b = b,a
        ans = "yes" if (a-b)%2==1 else "no"
        return _example("comp_sub_then_odd", f"Is {a} minus {b} odd?", ans, ["no" if ans=="yes" else "yes", "maybe", "unknown"], r)

    def comp_max_gt(r: random.Random) -> dict[str, Any]:
        a,b,c = r.randint(0,18), r.randint(0,18), r.randint(0,18); ans = "yes" if max(a,b)>c else "no"
        return _example("comp_max_then_compare_gt", f"Is the larger of {a} and {b} greater than {c}?", ans, ["no" if ans=="yes" else "yes", "maybe", "unknown"], r)

    def comp_min_lt(r: random.Random) -> dict[str, Any]:
        a,b,c = r.randint(0,18), r.randint(0,18), r.randint(0,18); ans = "yes" if min(a,b)<c else "no"
        return _example("comp_min_then_compare_lt", f"Is the smaller of {a} and {b} less than {c}?", ans, ["no" if ans=="yes" else "yes", "maybe", "unknown"], r)

    def comp_double_gt(r: random.Random) -> dict[str, Any]:
        a,c = r.randint(0,10), r.randint(0,20); ans = "yes" if 2*a > c else "no"
        return _example("comp_double_then_compare_gt", f"Is double {a} greater than {c}?", ans, ["no" if ans=="yes" else "yes", "maybe", "unknown"], r)

    def comp_abs_even(r: random.Random) -> dict[str, Any]:
        a,b = r.randint(0,18), r.randint(0,18); ans = "yes" if abs(a-b)%2==0 else "no"
        return _example("comp_absdiff_then_even", f"Is the difference between {a} and {b} even?", ans, ["no" if ans=="yes" else "yes", "maybe", "unknown"], r)

    def comp_add_eq(r: random.Random) -> dict[str, Any]:
        a,b,c = r.randint(0,6), r.randint(0,6), r.randint(0,12); ans = "yes" if a+b == c else "no"
        return _example("comp_add_then_equals", f"Is {a} plus {b} equal to {c}?", ans, ["no" if ans=="yes" else "yes", "maybe", "unknown"], r)

    comps = [
        ("comp_add_then_compare_gt", "add_then_compare_gt", "arith_add_small;arith_compare_gt", .40, .55, comp_add_gt),
        ("comp_add_then_compare_lt", "add_then_compare_lt", "arith_add_small;arith_compare_lt", .38, .58, comp_add_lt),
        ("comp_sub_then_compare_gt", "sub_then_compare_gt", "arith_sub_small;arith_compare_gt", .35, .65, comp_sub_gt),
        ("comp_add_then_even", "add_then_even", "arith_add_small;arith_even", .35, .60, comp_add_even),
        ("comp_sub_then_odd", "sub_then_odd", "arith_sub_small;arith_odd", .32, .68, comp_sub_odd),
        ("comp_max_then_compare_gt", "max_then_compare_gt", "arith_max2;arith_compare_gt", .30, .70, comp_max_gt),
        ("comp_min_then_compare_lt", "min_then_compare_lt", "arith_min2;arith_compare_lt", .30, .70, comp_min_lt),
        ("comp_double_then_compare_gt", "double_then_compare_gt", "arith_double;arith_compare_gt", .32, .65, comp_double_gt),
        ("comp_absdiff_then_even", "absdiff_then_even", "arith_absdiff;arith_even", .28, .75, comp_abs_even),
        ("comp_add_then_equals", "add_then_equals", "arith_add_small;arith_equals", .30, .70, comp_add_eq),
    ]
    for sid, op, components, freq, learn, gen in comps:
        add(_slice(sid, "composite", op, 2, freq, learn, 0.0, components), gen)

    # Surface controls with arithmetic-looking prompts but direct reading.
    def ctrl_digit(r: random.Random) -> dict[str, Any]:
        n = r.randint(0,9)
        return _example("ctrl_arith_digit_surface", f"Ignore the equation. The answer digit shown is {n}. Which digit is shown?", n, [n+1, max(0,n-1), 9], r)

    def ctrl_word(r: random.Random) -> dict[str, Any]:
        word = r.choice(["plus", "minus", "greater", "even"])
        return _example("ctrl_arith_word_surface", f"The visible math word is {word}. Which word is visible?", word, [w for w in ["plus", "minus", "greater", "even"] if w != word], r)

    add(_slice("ctrl_arith_digit_surface", "surface_control", "digit_surface", 1, .50, .30, 0.0, "", "surface"), ctrl_digit)
    add(_slice("ctrl_arith_word_surface", "surface_control", "word_surface", 1, .50, .30, 0.0, "", "surface"), ctrl_word)

    examples: list[dict[str, Any]] = []
    for _, gen in gens:
        for _ in range(n_per_slice):
            examples.append(gen(rng))
    return slices, examples


def main() -> None:
    p = argparse.ArgumentParser(description="Create a focused arithmetic Pythia observational suite for robustness testing of arithmetic residual underperformance.")
    p.add_argument("--output-dir", default="results/pythia_arithmetic_slice_suite_v34")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--n-per-slice", type=int, default=64)
    p.add_argument("--code-version", default="v3.4")
    p.add_argument("--archive-root", default="results/archive")
    p.add_argument("--thesis-use", default="diagnostic")
    args = p.parse_args()

    out = Path(args.output_dir); out.mkdir(parents=True, exist_ok=True)
    slices, examples = build_suite(args.seed, args.n_per_slice)
    with (out / "pythia_slice_table.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(slices[0].keys()))
        writer.writeheader(); writer.writerows(slices)
    with (out / "pythia_slice_examples.jsonl").open("w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex, sort_keys=True) + "\n")
    n_atomic = sum(s["kind"] == "atomic" for s in slices)
    n_comp = sum(s["kind"] == "composite" for s in slices)
    n_ctrl = sum("control" in s["kind"] for s in slices)
    report = [
        "# Pythia focused arithmetic slice suite",
        "",
        "This suite stress-tests the strongest Pythia observational pattern found so far: arithmetic composite underperformance relative to primitive-predictor expectations.",
        "",
        f"- total slices: `{len(slices)}`",
        f"- atomic slices: `{n_atomic}`",
        f"- composite slices: `{n_comp}`",
        f"- control slices: `{n_ctrl}`",
        f"- examples: `{len(examples)}`",
        f"- examples per slice: `{args.n_per_slice}`",
        "",
        "## Claim boundary",
        "This suite is observational. It can test robustness of Pythia arithmetic residual signatures, but it cannot establish causal dependency.",
    ]
    (out / "pythia_arithmetic_slice_suite_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    manifest = write_manifest(out, experiment="Pythia_focused_arithmetic_slice_suite_generation", backend="Pythia_observational", code_version=args.code_version, input_paths={}, extra={"n_slices": len(slices), "n_atomic": n_atomic, "n_composites": n_comp, "n_controls": n_ctrl, "n_examples": len(examples), "thesis_use": args.thesis_use})
    append_registry(Path(args.archive_root) / "results_registry.csv", {"run_id": manifest["run_id"], "code_version": args.code_version, "experiment": manifest["experiment"], "backend": manifest["backend"], "output_path": str(out), "status": "created", "thesis_use": args.thesis_use, "created_at_utc": manifest["created_at_utc"]})
    print(f"Wrote focused arithmetic Pythia slice suite to {out}")


if __name__ == "__main__":
    main()
