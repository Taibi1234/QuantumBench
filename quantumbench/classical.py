from dataclasses import dataclass
from itertools import product

import networkx as nx

from quantumbench.graphs import validate_graph


@dataclass(frozen=True)
class ExactMaxCutResult:
    optimal_value: float
    optimal_assignments: list[tuple[int, ...]]
    evaluated_assignments: int


def cut_value(graph: nx.Graph, assignment: list[int] | tuple[int, ...]) -> float:
    validate_graph(graph)

    if len(assignment) != len(graph):
        raise ValueError("Assignment must contain one bit per graph node.")

    if any(bit not in (0, 1) for bit in assignment):
        raise ValueError("Every assignment value must be either 0 or 1.")

    value = 0.0

    for source, target, data in graph.edges(data=True):
        if assignment[source] != assignment[target]:
            value += float(data.get("weight", 1))

    return value


def solve_maxcut_exact(graph: nx.Graph) -> ExactMaxCutResult:
    validate_graph(graph)

    node_count = len(graph)

    if node_count == 0:
        return ExactMaxCutResult(
            optimal_value=0.0,
            optimal_assignments=[tuple()],
            evaluated_assignments=1,
        )

    optimal_value = -1.0
    optimal_assignments = []
    evaluated_assignments = 0

    # Fixing the first bit to zero removes complementary duplicate solutions.
    for remaining_bits in product((0, 1), repeat=node_count - 1):
        assignment = (0,) + remaining_bits
        value = cut_value(graph, assignment)
        evaluated_assignments += 1

        if value > optimal_value:
            optimal_value = value
            optimal_assignments = [assignment]
        elif value == optimal_value:
            optimal_assignments.append(assignment)

    return ExactMaxCutResult(
        optimal_value=optimal_value,
        optimal_assignments=optimal_assignments,
        evaluated_assignments=evaluated_assignments,
    )