from quantumbench.plotting import generate_all_plots


def make_summary(expected_ratio, probability, runtime, depth):
    return {
        "expected_ratio_mean": expected_ratio,
        "expected_ratio_std": 0.05,
        "sampled_ratio_mean": expected_ratio,
        "sampled_ratio_std": 0.05,
        "optimal_probability_mean": probability,
        "best_sampled_ratio": expected_ratio,
        "runtime_seconds_mean": runtime,
        "circuit_depth": depth,
    }


def test_generate_all_plots(tmp_path):
    data = {
        "instances": [
            {
                "instance": {"instance_id": "test-instance"},
                "depths": {
                    "1": {
                        "summary": make_summary(0.8, 0.4, 1.0, 5),
                        "runs": [
                            {
                                "run_index": 0,
                                "seed": 42,
                                "qaoa": {
                                    "objective_history": [
                                        1.0,
                                        0.5,
                                        0.2,
                                    ]
                                },
                            }
                        ],
                    },
                    "2": {
                        "summary": make_summary(0.9, 0.6, 2.0, 9),
                        "runs": [],
                    },
                },
            }
        ]
    }

    paths = generate_all_plots(
        data,
        output_directory=tmp_path,
        convergence_instance="test-instance",
        convergence_reps=1,
    )

    assert len(paths) == 4

    for path in paths:
        assert path.exists()
        assert path.stat().st_size > 0