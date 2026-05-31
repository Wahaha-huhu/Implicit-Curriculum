import importlib


def test_pythia_calibration_imports():
    importlib.import_module('ic_experiments.experiments.analyze_pythia_threshold_sensitivity')
    importlib.import_module('ic_experiments.experiments.make_pythia_easy_slice_suite')
