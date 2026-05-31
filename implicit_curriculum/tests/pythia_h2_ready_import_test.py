from ic_experiments.experiments import make_pythia_h2_ready_slice_suite, analyze_pythia_h2_readiness


def test_imports():
    assert make_pythia_h2_ready_slice_suite is not None
    assert analyze_pythia_h2_readiness is not None
