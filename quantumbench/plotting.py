import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np


def load_depth_results(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def available_depths(data: dict) -> list[int]:
    depths = {
        int(depth)
        for instance in data["instances"]
        for depth in instance["depths"]
    }
    return sorted(depths)


def save_figure(output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close()


def plot_instance_metric(
    data: dict,
    metric_key: str,
    output_path: Path,
    ylabel: str,
    title: str,
    error_key: str | None = None,
) -> None:
    plt.figure(figsize=(9, 5))

    for instance_result in data["instances"]:
        instance_id = instance_result["instance"]["instance_id"]
        depth_mapping = instance_result["depths"]
        depths = sorted(int(depth) for depth in depth_mapping)
        summaries = [
            depth_mapping[str(depth)]["summary"]
            for depth in depths
        ]
        values = [summary[metric_key] for summary in summaries]

        if error_key:
            errors = [summary[error_key] for summary in summaries]
            plt.errorbar(
                depths,
                values,
                yerr=errors,
                marker="o",
                capsize=3,
                label=instance_id,
            )
        else:
            plt.plot(
                depths,
                values,
                marker="o",
                label=instance_id,
            )

    plt.xlabel("QAOA depth (p)")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(available_depths(data))
    plt.ylim(0.0, 1.05)
    plt.grid(alpha=0.25)
    plt.legend(fontsize=8)
    save_figure(output_path)


def plot_runtime_and_circuit_depth(
    data: dict,
    output_path: Path,
) -> None:
    depths = available_depths(data)
    mean_runtimes = []
    mean_circuit_depths = []

    for depth in depths:
        summaries = [
            instance["depths"][str(depth)]["summary"]
            for instance in data["instances"]
            if str(depth) in instance["depths"]
        ]
        mean_runtimes.append(
            np.mean([
                summary["runtime_seconds_mean"]
                for summary in summaries
            ])
        )
        mean_circuit_depths.append(
            np.mean([
                summary["circuit_depth"]
                for summary in summaries
            ])
        )

    figure, axes = plt.subplots(1, 2, figsize=(11, 4))

    axes[0].plot(depths, mean_runtimes, marker="o")
    axes[0].set_xlabel("QAOA depth (p)")
    axes[0].set_ylabel("Mean runtime (seconds)")
    axes[0].set_title("Runtime across benchmark instances")
    axes[0].set_xticks(depths)
    axes[0].grid(alpha=0.25)

    axes[1].plot(depths, mean_circuit_depths, marker="o")
    axes[1].set_xlabel("QAOA depth (p)")
    axes[1].set_ylabel("Mean circuit depth")
    axes[1].set_title("Circuit depth across benchmark instances")
    axes[1].set_xticks(depths)
    axes[1].grid(alpha=0.25)

    figure.tight_layout()
    save_figure(output_path)


def plot_convergence(
    data: dict,
    instance_id: str,
    reps: int,
    output_path: Path,
) -> None:
    instance_result = next(
        (
            instance
            for instance in data["instances"]
            if instance["instance"]["instance_id"] == instance_id
        ),
        None,
    )

    if instance_result is None:
        raise ValueError(f"Unknown instance: {instance_id}")

    depth_result = instance_result["depths"].get(str(reps))

    if depth_result is None:
        raise ValueError(
            f"Instance {instance_id} has no result for p={reps}."
        )

    plt.figure(figsize=(8, 5))

    for run in depth_result["runs"]:
        history = run["qaoa"]["objective_history"]
        plt.plot(
            range(1, len(history) + 1),
            history,
            label=f"Run {run['run_index']} (seed={run['seed']})",
        )

    plt.xlabel("Objective evaluation")
    plt.ylabel("Expected cost Hamiltonian value")
    plt.title(f"QAOA convergence: {instance_id}, p={reps}")
    plt.grid(alpha=0.25)
    plt.legend(fontsize=8)
    save_figure(output_path)


def generate_all_plots(
    data: dict,
    output_directory: Path,
    convergence_instance: str,
    convergence_reps: int,
) -> list[Path]:
    paths = [
        output_directory / "approximation_ratio_by_depth.png",
        output_directory / "optimal_probability_by_depth.png",
        output_directory / "runtime_and_circuit_depth.png",
        output_directory / "qaoa_convergence.png",
    ]

    plot_instance_metric(
        data,
        metric_key="expected_ratio_mean",
        error_key="expected_ratio_std",
        output_path=paths[0],
        ylabel="Expected approximation ratio",
        title="QAOA solution quality versus depth",
    )
    plot_instance_metric(
        data,
        metric_key="optimal_probability_mean",
        output_path=paths[1],
        ylabel="Mean optimal-sample probability",
        title="Optimal-solution sampling versus depth",
    )
    plot_runtime_and_circuit_depth(data, paths[2])
    plot_convergence(
        data,
        instance_id=convergence_instance,
        reps=convergence_reps,
        output_path=paths[3],
    )

    return paths