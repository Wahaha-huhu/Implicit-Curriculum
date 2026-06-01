def test_final_experiment_state_import():
    import ic_experiments.experiments.make_final_experiment_state as m
    assert hasattr(m, "main")
