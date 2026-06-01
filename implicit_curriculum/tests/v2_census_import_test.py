def test_v2_census_modules_import():
    import ic_experiments.census  # noqa: F401
    import ic_experiments.experiments.make_b1_v2_preregistration  # noqa: F401
    import ic_experiments.experiments.make_b1_causal_census_plan  # noqa: F401
    import ic_experiments.experiments.run_b1_causal_census  # noqa: F401
    import ic_experiments.experiments.analyze_b1_causal_census_verdicts  # noqa: F401
    import ic_experiments.experiments.analyze_b1_alignment_predicts_census_verdict  # noqa: F401
