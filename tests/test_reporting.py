import pytest

from quantumbench.reporting import (
    build_experiment_summary,
    summary_to_markdown,
)


def make_depth_summary(expected_ratio):
    return {
        "expected_ratio_mean": expected_ratio,
        "optimal_probability_mean": expected_ratio,
        "runtime_seconds_mean": 1.0,
        "circuit_depth": 5,
    }


def test_experiment_summary():
    depth_data = {
        "instances": [
            {
                "depths": {
                    "1": {"summary": make_depth_summary(0.8)},
                    "2": {"summary": make_depth_summary(0.9)},
                }
            }
        ]
    }
    noise_data = {
        "exact": {"optimal_value": 10.0},
        "ideal_optimization": {
            "analysis": {
                "expected_approximation_ratio": 0.9,
                "optimal_sample_probability": 0.5,
            }
        },
        "noise_levels": {
            "none": {
                "one_qubit_error": 0.0,
                "two_qubit_error": 0.0,
                "summary": {
                    "sampled_ratio_mean": 0.9,
                    "sampled_ratio_std": 0.02,
                    "optimal_probability_mean": 0.5,
                },
            }
        },
    }

    summary = build_experiment_summary(depth_data, noise_data)
    markdown = summary_to_markdown(summary)

    assert summary["best_depth_by_mean_expected_ratio"] == 2
    assert summary["depth_study"][1]["expected_ratio_mean"] == (
        pytest.approx(0.8)
    )
    assert "# QuantumBench experimental summary" in markdown
    assert "No quantum advantage is claimed." in markdown