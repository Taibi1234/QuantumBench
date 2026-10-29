import networkx as nx
import pytest

from quantumbench.heuristic import solve_maxcut_heuristic
from quantumbench.instances import create_instance


def test_heuristic_solves_weighted_triangle():
    graph = nx.Graph()
    graph.add_nodes_from(range(3))
    graph.add_weighted_edges_from([
        (0, 1, 5),
        (1, 2, 1),
        (0, 2, 1),
    ])

    result = solve_maxcut_heuristic(graph, restarts=10, seed=42)

    assert result.best_value == 6.0


def test_heuristic_is_reproducible():
    instance = create_instance(8, 0.5, 44)

    first = solve_maxcut_heuristic(
        instance.graph,
        restarts=20,
        seed=42,
    )
    second = solve_maxcut_heuristic(
        instance.graph,
        restarts=20,
        seed=42,
    )

    assert first == second


def test_invalid_restart_count_is_rejected():
    instance = create_instance(4, 0.5, 11)

    with pytest.raises(ValueError):
        solve_maxcut_heuristic(
            instance.graph,
            restarts=0,
        )