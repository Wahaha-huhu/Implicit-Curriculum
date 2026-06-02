
def test_n1_coupling_modules_import():
    import ic_experiments.coupling  # noqa: F401
    import ic_experiments.experiments.make_b1_coupling_pilot_plan  # noqa: F401
    import ic_experiments.experiments.run_b1_coupling_pilot  # noqa: F401
    import ic_experiments.experiments.analyze_b1_coupling_pilot  # noqa: F401
