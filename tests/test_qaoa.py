import networkx as nx
import numpy as np
import pytest

from quantumbench.qaoa import (
    bitstring_to_assignment,
    build_maxcut_hamiltonian,
    solve_qaoa_ideal,
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


def test_hamiltonian_ground_energy():
    hamiltonian = build_maxcut_hamiltonian(make_triangle())
    eigenvalues = np.linalg.eigvalsh(hamiltonian.to_matrix())

    # H = 0.5(Z0Z1 + Z1Z2 + Z0Z2), whose ground energy is -0.5.
    assert eigenvalues[0] == pytest.approx(-0.5)


def test_bitstring_conversion():
    assert bitstring_to_assignment("100") == (0, 0, 1)
    assert bitstring_to_assignment("011") == (1, 1, 0)


def test_ideal_qaoa_produces_valid_results():
    result = solve_qaoa_ideal(
        make_triangle(),
        reps=1,
        shots=128,
        seed=42,
        maxiter=40,
    )

    assert sum(result.counts.values()) == 128
    assert 0.0 <= result.expected_cut_value <= 2.0
    assert 0.0 <= result.best_sampled_value <= 2.0
    assert result.circuit_depth > 0
    assert len(result.objective_history) > 0


def test_ideal_qaoa_is_reproducible():
    first = solve_qaoa_ideal(
        make_triangle(),
        reps=1,
        shots=64,
        seed=42,
        maxiter=20,
    )
    second = solve_qaoa_ideal(
        make_triangle(),
        reps=1,
        shots=64,
        seed=42,
        maxiter=20,
    )

    assert first.counts == second.counts
    assert first.optimal_parameters == pytest.approx(
        second.optimal_parameters
    )
    assert first.expected_cut_value == pytest.approx(
        second.expected_cut_value
    )