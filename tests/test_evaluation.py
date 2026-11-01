from types import SimpleNamespace

import networkx as nx
import pytest

from quantumbench.evaluation import (
    approximation_ratio,
    evaluate_qaoa_result,
    summarize_qaoa_runs,
)


def make_triangle():
    graph = nx.Graph()
    graph.add_nodes_from(range(3))
    graph.add_weighted_edges_from([
        (0, 1, 1),
        (1, 2, 1),
        (0, 2, 1),
    ])
    return graph


def make_analysis(expected_ratio, optimal_probability):
    return {
        "expected_approximation_ratio": expected_ratio,
        "sampled_mean_approximation_ratio": expected_ratio,
        "best_sampled_approximation_ratio": expected_ratio,
        "optimal_sample_probability": optimal_probability,
    }


def test_zero_optimum_ratio():
    assert approximation_ratio(0.0, 0.0) == 1.0
    assert approximation_ratio(1.0, 0.0) == 0.0


def test_qaoa_evaluation_metrics():
    result = SimpleNamespace(
        expected_cut_value=1.5,
        sampled_mean_cut_value=1.0,
        best_sampled_value=2.0,
        shots=4,
        counts={"001": 2, "000": 2},
    )

    analysis = evaluate_qaoa_result(
        make_triangle(),
        result,
        optimal_value=2.0,
    )

    assert analysis["expected_approximation_ratio"] == 0.75
    assert analysis["sampled_mean_approximation_ratio"] == 0.5
    assert analysis["best_sampled_approximation_ratio"] == 1.0
    assert analysis["optimal_sample_probability"] == 0.5


def test_run_summary():
    runs = [
        {
            "analysis": make_analysis(0.8, 0.5),
            "qaoa": {
                "runtime_seconds": 2.0,
                "circuit_depth": 10,
            },
        },
        {
            "analysis": make_analysis(1.0, 0.75),
            "qaoa": {
                "runtime_seconds": 4.0,
                "circuit_depth": 10,
            },
        },
    ]

    summary = summarize_qaoa_runs(runs)

    assert summary["run_count"] == 2
    assert summary["expected_ratio_mean"] == pytest.approx(0.9)
    assert summary["optimal_probability_mean"] == pytest.approx(0.625)
    assert summary["runtime_seconds_mean"] == 3.0
    assert summary["circuit_depth"] == 10