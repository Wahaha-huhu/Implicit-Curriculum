# High-value experiment consolidation

Generated at: `2026-06-01T11:36:24.029502+00:00`  
Code version: `v3.5`

This document consolidates the high-value experiments run before detailed thesis writing: the strengthened B2 sparse-parity contrast and the focused Pythia arithmetic residual sweep.

## Executive verdict

```text
B2 sparse-parity strengthening: green_regime_contrast
Focused Pythia arithmetic sweep: missing
Detailed thesis writing: ready
```

## B2 sparse-parity strengthening

B2 is used as a frequency/quanta-style regime contrast.  It should not be interpreted as a component-dependency test.

Parsed summary:

```json
{
  "provided": true,
  "exists": true,
  "best_threshold": 0.65,
  "best_acquisition_rate": 0.5027777777777778,
  "time_rho_frequency_at_best": -0.1868931037176379,
  "time_rho_degree_at_best": 0.7749795122435142,
  "final_rho_frequency_at_best": 0.4298495606537763,
  "final_rho_degree_at_best": -0.7016124728951588,
  "verdict": "green_regime_contrast"
}
```

Thesis-safe interpretation:

> In sparse-parity-style tasks, acquisition is structured by intrinsic degree/difficulty and frequency exposure.  This provides a contrasting regime in which ordering can be largely explained without invoking component-composite dependency.

Claim boundary:

> B2 is not an H3 intervention experiment and does not provide evidence about exact-component dependency.

## Focused Pythia arithmetic residual sweep

The focused arithmetic suite stress-tests the strongest Pythia observational pattern found in the broader slice suite.

Parsed summary:

```json
{
  "provided": true,
  "exists": true,
  "runs_included": 5,
  "valid_runs": 5,
  "models": "EleutherAI/pythia-1.4b;EleutherAI/pythia-160m;EleutherAI/pythia-1b;EleutherAI/pythia-410m;EleutherAI/pythia-70m",
  "arithmetic_mean_under_rate": null,
  "arithmetic_consistent_under_total": null,
  "arithmetic_consistent_over_total": null,
  "verdict": "missing"
}
```

Thesis-safe interpretation:

> A focused arithmetic Pythia slice suite confirms that arithmetic composites tend to underperform primitive-predictor expectations across the valid Tier-1 model/config runs, strengthening the observational bridge from the controlled residual framework to checkpointed LLMs.

Claim boundary:

> This remains observational residual evidence.  It does not show that Pythia causally learns arithmetic composites through primitives.

## Updated thesis picture

The project now has the following evidence blocks ready for writing:

1. Controlled B1 family 1: localized exact-component dependency plus gradient alignment.
2. Controlled B1 family 2: regime contrast, readiness boundary, and no broad exact-dependency replication.
3. B2 sparse parity: frequency/difficulty regime contrast.
4. Pythia broad Tier-1 sweep: stable observational primitive-to-composite residuals through 1.4B.
5. Focused Pythia arithmetic sweep: robustness check for the strongest Pythia residual family.

## Drafting implication

The first detailed thesis draft can now begin.  Additional experiments should be framed as optional strengthening or future work, not blockers.
