import importlib


def test_cross_family_claims_imports():
    mod = importlib.import_module("ic_experiments.experiments.analyze_b1_cross_family_claims")
    assert hasattr(mod, "main")
