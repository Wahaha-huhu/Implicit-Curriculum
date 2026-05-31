import importlib


def test_pythia_observational_imports():
    importlib.import_module("ic_experiments.experiments.make_pythia_observational_slice_suite")
    importlib.import_module("ic_experiments.experiments.run_pythia_observational_pilot")
    importlib.import_module("ic_experiments.experiments.analyze_pythia_observational_pilot")
