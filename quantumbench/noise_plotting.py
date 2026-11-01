import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


NOISE_ORDER = ["none", "low", "medium", "high"]


def load_noise_results(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def ordered_noise_names(data: dict) -> list[str]:
    available = set(data["noise_levels"])
    ordered = [name for name in NOISE_ORDER if name in available]
    ordered.extend(sorted(available - set(ordered)))
    return ordered


def save_figure(output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close()


def plot_noise_metric(
    data: dict,
    metric_key: str,
    output_path: Path,
    ylabel: str,
    title: str,
    error_key: str | None = None,
    show_optimal_reference: bool = False,
) -> None:
    names = ordered_noise_names(data)
    summaries = [
        data["noise_levels"][name]["summary"]
        for name in names
    ]
    values = [summary[metric_key] for summary in summaries]

    plt.figure(figsize=(8, 5))

    if error_key:
        errors = [summary[error_key] for summary in summaries]
        plt.errorbar(
            names,
            values,
            yerr=errors,
            marker="o",
            capsize=4,
        )
    else:
        plt.plot(names, values, marker="o")

    if show_optimal_reference:
        plt.axhline(
            1.0,
            linestyle="--",
            color="black",
            linewidth=1,
            label="Exact classical optimum ratio",
        )
        plt.legend()

    plt.xlabel("Depolarizing-noise level")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.ylim(0.0, 1.05)
    plt.grid(alpha=0.25)
    save_figure(output_path)


def generate_noise_plots(
    data: dict,
    output_directory: Path,
) -> list[Path]:
    paths = [
        output_directory / "noise_approximation_ratio.png",
        output_directory / "noise_optimal_probability.png",
    ]

    plot_noise_metric(
        data,
        metric_key="sampled_ratio_mean",
        error_key="sampled_ratio_std",
        output_path=paths[0],
        ylabel="Mean sampled approximation ratio",
        title="QAOA solution quality under depolarizing noise",
        show_optimal_reference=True,
    )
    plot_noise_metric(
        data,
        metric_key="optimal_probability_mean",
        output_path=paths[1],
        ylabel="Mean optimal-sample probability",
        title="Optimal-solution sampling under depolarizing noise",
    )

    return paths