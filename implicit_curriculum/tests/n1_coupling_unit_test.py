import torch

from ic_experiments.backends.sequence_dsl import SequenceDSLConfig, generate_sequence_dsl_family
from ic_experiments.coupling import make_coupling_pair_plan, make_dose_weights, linear_slope


def test_make_coupling_pair_plan_has_expected_columns():
    family = generate_sequence_dsl_family(SequenceDSLConfig(vocab_content=16, input_len=4, n_unrelated_controls=3, seed=3))
    plan = make_coupling_pair_plan(family.structure_table(), max_pairs=8, seed=0)
    assert not plan.empty
    for col in ["pair_id", "source_task", "target_task", "filler_task", "pair_type"]:
        assert col in plan.columns
    assert (plan["source_task"] != plan["target_task"]).all()


def test_make_dose_weights_preserves_sum_and_target_weight():
    base = torch.tensor([0.2, 0.3, 0.1, 0.4])
    weights = make_dose_weights(base, source_idx=0, target_idx=1, filler_idx=2, multiplier=0.0)
    assert torch.isclose(weights.sum(), torch.tensor(1.0))
    assert torch.isclose(weights[1], base[1])
    assert weights[0] < base[0]
    assert weights[2] > base[2]


def test_linear_slope_basic():
    assert abs(linear_slope([0, 1, 2], [1, 3, 5]) - 2.0) < 1e-6
