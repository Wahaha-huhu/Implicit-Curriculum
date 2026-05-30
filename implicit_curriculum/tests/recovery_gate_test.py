from __future__ import annotations

from ic_experiments.design import DesignCriteria, PropertyDesignConfig, passes_design_criteria, sample_property_design
from ic_experiments.recovery import RecoveryConfig, run_recovery_suite


def main() -> None:
    criteria = DesignCriteria(max_vif=5.0, max_abs_pearson=0.75, max_abs_spearman=0.75, max_condition_number=75.0, min_rows=10)
    prop_config = PropertyDesignConfig(n_atomic=6, n_composite=4, seed=123, criteria=criteria, max_attempts=2000)
    design, diag = sample_property_design(prop_config)
    assert len(design) == 10
    assert passes_design_criteria(diag, criteria), diag

    recovery = run_recovery_suite(RecoveryConfig(seed=123, n_replicates=2, n_folds=3, property_design=prop_config))
    assert not recovery["verdict"].empty
    verdict = recovery["verdict"].set_index("true_mechanism")
    assert verdict.loc["frequency_only", "selected_frequency_only_rate"] >= 0.5
    assert verdict.loc["three_factor", "selected_three_factor_rate"] >= 0.5
    assert verdict.loc["dependency_gated", "positive_residual_rate"] >= 0.5
    print("recovery gate smoke test passed")


if __name__ == "__main__":
    main()
