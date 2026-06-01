def test_high_value_consolidation_import():
    import ic_experiments.experiments.consolidate_high_value_experiment_evidence as mod
    assert hasattr(mod, "main")
