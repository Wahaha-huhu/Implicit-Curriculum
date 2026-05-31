# Cross-Family Synthesis Plan

Once at least one replication family has H1/H2/H3 outputs, create a registry file with one row per family:

```csv
family_id,h1_report,h2_report,h3_matrix,mediator_report
family_original,results/b1_h1_shared_sweep_v08/b1_h1_analysis_report.md,results/b1_h1_shared_sweep_v08/h2_analysis_report.md,results/b1_h3_evidence_matrix_v16/h3_pair_evidence_matrix.csv,results/b1_mediator_h3_pairs_v18/mediator_analysis_report.md
family_replication_01,results/family_replication_01/b1_h1_shared_sweep/b1_h1_analysis_report.md,results/family_replication_01/b1_h1_shared_sweep/h2_analysis_report.md,results/family_replication_01/b1_h3_evidence_matrix/h3_pair_evidence_matrix.csv,
```

Then run:

```bash
PYTHONPATH=src python -m ic_experiments.experiments.analyze_b1_cross_family_synthesis \
  --family-registry thesis_evidence/tables/b1_family_registry.csv \
  --output-dir results/b1_cross_family_synthesis_v20 \
  --code-version v2.0
```

The output decides which claims are single-family pilot evidence and which are cross-family supported.
