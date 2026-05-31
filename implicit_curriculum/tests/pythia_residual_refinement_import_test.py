def test_pythia_residual_refinement_import():
    import ic_experiments.experiments.analyze_pythia_residual_refinement as mod
    assert hasattr(mod, "main")
