import math

import networkx as nx
import numpy as np

from quantumbench.classical import cut_value
from quantumbench.qaoa import bitstring_to_assignment


def approximation_ratio(value: float, optimal_value: float) -> float:
    if optimal_value == 0:
        return 1.0 if value == 0 else 0.0

    return value / optimal_value


def evaluate_qaoa_result(
    graph: nx.Graph,
    result,
    optimal_value: float,
) -> dict:
    optimal_sample_count = 0

    for bitstring, count in result.counts.items():
        assignment = bitstring_to_assignment(bitstring)
        value = cut_value(graph, assignment)

        if math.isclose(value, optimal_value):
            optimal_sample_count += count

    return {
        "expected_approximation_ratio": approximation_ratio(
            result.expected_cut_value,
            optimal_value,
        ),
        "sampled_mean_approximation_ratio": approximation_ratio(
            result.sampled_mean_cut_value,
            optimal_value,
        ),
        "best_sampled_approximation_ratio": approximation_ratio(
            result.best_sampled_value,
            optimal_value,
        ),
        "optimal_sample_probability": (
            optimal_sample_count / result.shots
        ),
    }


def summarize_qaoa_runs(runs: list[dict]) -> dict:
    if not runs:
        raise ValueError("At least one QAOA run is required.")

    expected_ratios = [
        run["analysis"]["expected_approximation_ratio"]
        for run in runs
    ]
    sampled_ratios = [
        run["analysis"]["sampled_mean_approximation_ratio"]
        for run in runs
    ]
    optimal_probabilities = [
        run["analysis"]["optimal_sample_probability"]
        for run in runs
    ]
    runtimes = [
        run["qaoa"]["runtime_seconds"]
        for run in runs
    ]

    return {
        "run_count": len(runs),
        "expected_ratio_mean": float(np.mean(expected_ratios)),
        "expected_ratio_std": float(np.std(expected_ratios)),
        "sampled_ratio_mean": float(np.mean(sampled_ratios)),
        "sampled_ratio_std": float(np.std(sampled_ratios)),
        "optimal_probability_mean": float(
            np.mean(optimal_probabilities)
        ),
        "best_sampled_ratio": max(
            run["analysis"]["best_sampled_approximation_ratio"]
            for run in runs
        ),
        "runtime_seconds_mean": float(np.mean(runtimes)),
        "circuit_depth": runs[0]["qaoa"]["circuit_depth"],
    }