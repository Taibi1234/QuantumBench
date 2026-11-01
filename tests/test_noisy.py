import networkx as nx
import pytest

from quantumbench.noisy import (
    build_depolarizing_noise_model,
    evaluate_noisy_qaoa,
)
from quantumbench.qaoa import solve_qaoa_ideal


def make_triangle():
    graph = nx.Graph()
    graph.add_nodes_from(range(3))
    graph.add_weighted_edges_from([
        (0, 1, 1),
        (1, 2, 1),
        (0, 2, 1),
    ])
    return graph


def optimized_triangle_parameters():
    result = solve_qaoa_ideal(
        make_triangle(),
        reps=1,
        shots=64,
        seed=42,
        maxiter=20,
    )
    return result.optimal_parameters


def test_zero_noise_simulation():
    result = evaluate_noisy_qaoa(
        make_triangle(),
        optimal_parameters=optimized_triangle_parameters(),
        reps=1,
        one_qubit_error=0.0,
        two_qubit_error=0.0,
        shots=64,
        seed=42,
    )

    assert sum(result.counts.values()) == 64
    assert 0.0 <= result.sampled_mean_cut_value <= 2.0
    assert 0.0 <= result.best_sampled_value <= 2.0


def test_noisy_simulation_is_reproducible():
    parameters = optimized_triangle_parameters()

    first = evaluate_noisy_qaoa(
        make_triangle(),
        optimal_parameters=parameters,
        reps=1,
        one_qubit_error=0.005,
        two_qubit_error=0.03,
        shots=64,
        seed=42,
    )
    second = evaluate_noisy_qaoa(
        make_triangle(),
        optimal_parameters=parameters,
        reps=1,
        one_qubit_error=0.005,
        two_qubit_error=0.03,
        shots=64,
        seed=42,
    )

    assert first.counts == second.counts
    assert first.sampled_mean_cut_value == pytest.approx(
        second.sampled_mean_cut_value
    )


def test_invalid_noise_rate_is_rejected():
    with pytest.raises(ValueError):
        build_depolarizing_noise_model(
            one_qubit_error=-0.1,
            two_qubit_error=0.0,
        )