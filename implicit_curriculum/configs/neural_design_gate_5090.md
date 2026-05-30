# v0.3 neural design gate command

```bash
PYTHONPATH=src python -m ic_experiments.experiments.run_neural_design_gate \
  --output-dir results/neural_design_gate \
  --seed 0 \
  --n-atomic 12 \
  --n-composite 8 \
  --n-shortcut-controls 4 \
  --n-surface-controls 4 \
  --n-unrelated-controls 4 \
  --n-bits 48 \
  --max-attempts 10000
```
