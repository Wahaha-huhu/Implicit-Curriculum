def test_pythia_sweep_consolidation_import():
    import ic_experiments.experiments.consolidate_pythia_sweep_evidence as mod
    assert hasattr(mod, "main")
