import numpy as np
import pandas as pd

from ic_experiments.experiments.analyze_b1_coupling_pilot import (
    DEFAULT_BASELINE_COLUMNS,
    correlation_row,
    residualized_predictor_correlations,
)


class Args:
    primary_outcome = "mean_slope_target_auc_token_accuracy"
    baseline_columns = DEFAULT_BASELINE_COLUMNS
    categorical_baselines = []
    min_pairs_for_categorical = 30


def test_residualized_predictor_correlations_controls_baseline_columns():
    df = pd.DataFrame(
        {
            "pair_id": [f"p{i}" for i in range(8)],
            "mean_slope_target_auc_token_accuracy": np.linspace(-1, 1, 8),
            "mean_gradient_cosine": np.linspace(-1, 1, 8),
            "source_frequency": np.linspace(0.1, 0.8, 8),
            "target_frequency": np.linspace(0.8, 0.1, 8),
            "source_reference_learnability": np.ones(8),
            "target_reference_learnability": np.linspace(1.0, 2.0, 8),
            "surface_overlap_proxy": np.zeros(8),
        }
    )
    out = residualized_predictor_correlations(df, Args())
    assert not out.empty
    assert "baseline_columns" in out.columns


def test_correlation_row_reports_n_pairs():
    df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 3, 5]})
    row = correlation_row(df, "x", "y", "test")
    assert row["n_pairs"] == 3
    assert row["pearson_r"] > 0.99
