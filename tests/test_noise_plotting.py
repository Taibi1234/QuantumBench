from quantumbench.noise_plotting import generate_noise_plots


def make_noise_data():
    levels = {}

    for index, name in enumerate(["none", "low", "medium", "high"]):
        levels[name] = {
            "summary": {
                "sampled_ratio_mean": 1.0 - index * 0.1,
                "sampled_ratio_std": 0.02,
                "optimal_probability_mean": 0.8 - index * 0.1,
            }
        }

    return {"noise_levels": levels}


def test_generate_noise_plots(tmp_path):
    paths = generate_noise_plots(make_noise_data(), tmp_path)

    assert len(paths) == 2

    for path in paths:
        assert path.exists()
        assert path.stat().st_size > 0