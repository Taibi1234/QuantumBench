import networkx as nx
import pytest

from quantumbench.classical import cut_value, solve_maxcut_exact
from quantumbench.graphs import generate_weighted_graph


def make_graph(edges):
    graph = nx.Graph()
    graph.add_nodes_from(range(3))
    graph.add_weighted_edges_from(edges)
    return graph


def test_triangle_maxcut():
    graph = make_graph([
        (0, 1, 1),
        (1, 2, 1),
        (0, 2, 1),
    ])

    result = solve_maxcut_exact(graph)

    assert result.optimal_value == 2.0
    assert result.optimal_assignments == [
        (0, 0, 1),
        (0, 1, 0),
        (0, 1, 1),
    ]
    assert result.evaluated_assignments == 4


def test_weighted_triangle_maxcut():
    graph = make_graph([
        (0, 1, 5),
        (1, 2, 1),
        (0, 2, 1),
    ])

    result = solve_maxcut_exact(graph)

    assert result.optimal_value == 6.0
    assert result.optimal_assignments == [
        (0, 1, 0),
        (0, 1, 1),
    ]


def test_cut_value():
    graph = make_graph([
        (0, 1, 5),
        (1, 2, 1),
        (0, 2, 1),
    ])

    assert cut_value(graph, (0, 1, 0)) == 6.0
    assert cut_value(graph, (0, 0, 0)) == 0.0


def test_reproducible_graph_generation():
    first = generate_weighted_graph(8, 0.5, 42)
    second = generate_weighted_graph(8, 0.5, 42)

    first_edges = [
        (source, target, data["weight"])
        for source, target, data in first.edges(data=True)
    ]
    second_edges = [
        (source, target, data["weight"])
        for source, target, data in second.edges(data=True)
    ]

    assert first_edges == second_edges


def test_invalid_assignment_length_is_rejected():
    graph = make_graph([(0, 1, 1)])

    with pytest.raises(ValueError):
        cut_value(graph, (0, 1))


def test_invalid_assignment_bit_is_rejected():
    graph = make_graph([(0, 1, 1)])

    with pytest.raises(ValueError):
        cut_value(graph, (0, 2, 0))