from ic_experiments.experiments import run_b1_h1_shared_sweep, analyze_b1_h1_shared_sweep


def test_b1_h1_modules_import():
    assert hasattr(run_b1_h1_shared_sweep, 'main')
    assert hasattr(analyze_b1_h1_shared_sweep, 'main')
