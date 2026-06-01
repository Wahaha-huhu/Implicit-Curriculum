import pandas as pd

from ic_experiments.census import build_causal_census_plan, classify_pair_verdict, VerdictConfig


def test_build_causal_census_plan_from_formal_graph():
    structure = pd.DataFrame([
        {"task_name": "A00_copy", "structure_id": "A00_copy", "kind": "atomic", "op": "copy", "components": "", "frequency": 0.1, "reference_learnability": 1.0, "formal_utility": 1.0},
        {"task_name": "A01_copy", "structure_id": "A01_copy", "kind": "atomic", "op": "copy", "components": "", "frequency": 0.1, "reference_learnability": 1.0, "formal_utility": 1.0},
        {"task_name": "A02_reverse", "structure_id": "A02_reverse", "kind": "atomic", "op": "reverse", "components": "", "frequency": 0.1, "reference_learnability": 2.0, "formal_utility": 1.0},
        {"task_name": "C00_copy_then_reverse", "structure_id": "C00_copy_then_reverse", "kind": "composite", "op": "copy_then_reverse", "components": "A00_copy,A02_reverse", "frequency": 0.05, "reference_learnability": 3.0, "formal_utility": 0.0},
        {"task_name": "K00_shortcut", "structure_id": "K00_shortcut", "kind": "shortcut", "op": "shortcut_identity", "components": "A00_copy", "control_type": "shortcut_no_reuse", "frequency": 0.1, "reference_learnability": 1.0, "formal_utility": 0.0},
        {"task_name": "S00_surface", "structure_id": "S00_surface", "kind": "surface_control", "op": "surface_rotate", "components": "", "control_type": "surface_overlap_no_dependency", "frequency": 0.1, "reference_learnability": 1.0, "formal_utility": 0.0},
        {"task_name": "U00_unrelated", "structure_id": "U00_unrelated", "kind": "unrelated", "op": "reverse", "components": "", "control_type": "unrelated_matched", "frequency": 0.1, "reference_learnability": 2.0, "formal_utility": 0.0},
    ])
    plan = build_causal_census_plan(structure, max_pairs=1)
    assert len(plan) == 1
    assert plan.iloc[0]["component"] == "A00_copy"
    assert plan.iloc[0]["composite"] == "C00_copy_then_reverse"
    assert "same_operation_control" in plan.columns


def test_classify_pair_verdict_exact_dependency():
    pair = {"component": "A", "composite": "C"}
    contrasts = pd.DataFrame([
        {"manipulation": "upweight", "control_type": "same_operation", "time_expected_direction_rate": 1.0, "signed_censored_time_effect_mean": 10.0, "time_sign_pvalue": 0.03, "n_paired_seeds": 8, "exact_acquisition_rate": 0.5, "exact_final_metric_mean": 0.8},
        {"manipulation": "upweight", "control_type": "different_operation", "time_expected_direction_rate": 1.0, "signed_censored_time_effect_mean": 11.0, "time_sign_pvalue": 0.03, "n_paired_seeds": 8, "exact_acquisition_rate": 0.5, "exact_final_metric_mean": 0.8},
        {"manipulation": "upweight", "control_type": "fake_component", "time_expected_direction_rate": 0.75, "signed_censored_time_effect_mean": 5.0, "time_sign_pvalue": 0.08, "n_paired_seeds": 8, "exact_acquisition_rate": 0.5, "exact_final_metric_mean": 0.8},
        {"manipulation": "upweight", "control_type": "surface", "time_expected_direction_rate": 0.75, "signed_censored_time_effect_mean": 4.0, "time_sign_pvalue": 0.08, "n_paired_seeds": 8, "exact_acquisition_rate": 0.5, "exact_final_metric_mean": 0.8},
    ])
    verdict = classify_pair_verdict(pair, contrasts, VerdictConfig(alpha=0.1))
    assert verdict["verdict"] == "exact_component_dependency"
