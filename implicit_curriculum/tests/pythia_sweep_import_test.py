def test_import_pythia_sweep_modules():
    import ic_experiments.experiments.make_pythia_sweep_plan as plan
    import ic_experiments.experiments.analyze_pythia_sweep_synthesis as synth
    assert plan is not None
    assert synth is not None
