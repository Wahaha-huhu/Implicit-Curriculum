import importlib


def test_first_stage_summary_import():
    mod = importlib.import_module("ic_experiments.experiments.make_first_stage_experiment_summary")
    assert hasattr(mod, "main")
