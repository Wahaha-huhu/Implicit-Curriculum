def test_import_all_model_sweep_plan():
    import ic_experiments.experiments.make_pythia_all_model_sweep_plan as m
    assert hasattr(m, "main")
