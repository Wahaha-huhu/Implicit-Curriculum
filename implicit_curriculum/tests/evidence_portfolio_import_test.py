import importlib

for name in [
    'ic_experiments.experiments.analyze_thesis_portfolio',
    'ic_experiments.experiments.make_b1_comprehensive_experiment_plan',
]:
    importlib.import_module(name)
print('evidence portfolio import test passed')
