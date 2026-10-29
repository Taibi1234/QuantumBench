import random
from dataclasses import dataclass

import networkx as nx

from quantumbench.classical import cut_value
from quantumbench.graphs import validate_graph


@dataclass(frozen=True)
class HeuristicMaxCutResult:
    best_value: float
    best_assignment: tuple[int, ...]
    restarts: int
    improvement_steps: int


def flip_gain(
    graph: nx.Graph,
    assignment: list[int],
    node: int,
) -> float:
    same_side_weight = 0.0
    opposite_side_weight = 0.0

    for neighbor, data in graph[node].items():
        weight = float(data.get("weight", 1))

        if assignment[node] == assignment[neighbor]:
            same_side_weight += weight
        else:
            opposite_side_weight += weight

    return same_side_weight - opposite_side_weight


def improve_assignment(
    graph: nx.Graph,
    initial_assignment: tuple[int, ...],
) -> tuple[tuple[int, ...], float, int]:
    assignment = list(initial_assignment)
    current_value = cut_value(graph, assignment)
    improvement_steps = 0

    while True:
        gains = [
            flip_gain(graph, assignment, node)
            for node in range(len(graph))
        ]

        best_node = max(range(len(graph)), key=lambda node: gains[node])
        best_gain = gains[best_node]

        if best_gain <= 1e-12:
            break

        assignment[best_node] = 1 - assignment[best_node]
        current_value += best_gain
        improvement_steps += 1

    return tuple(assignment), current_value, improvement_steps


def solve_maxcut_heuristic(
    graph: nx.Graph,
    restarts: int = 20,
    seed: int = 42,
) -> HeuristicMaxCutResult:
    validate_graph(graph)

    if restarts < 1:
        raise ValueError("restarts must be at least one.")

    node_count = len(graph)

    if node_count == 0:
        return HeuristicMaxCutResult(
            best_value=0.0,
            best_assignment=tuple(),
            restarts=restarts,
            improvement_steps=0,
        )

    random_generator = random.Random(seed)
    starting_assignments = [tuple([0] * node_count)]

    for _ in range(restarts - 1):
        starting_assignments.append(
            tuple(
                random_generator.randint(0, 1)
                for _ in range(node_count)
            )
        )

    best_value = -1.0
    best_assignment = tuple([0] * node_count)
    total_improvement_steps = 0

    for starting_assignment in starting_assignments:
        assignment, value, steps = improve_assignment(
            graph,
            starting_assignment,
        )
        total_improvement_steps += steps

        if value > best_value:
            best_value = value
            best_assignment = assignment

    return HeuristicMaxCutResult(
        best_value=best_value,
        best_assignment=best_assignment,
        restarts=restarts,
        improvement_steps=total_improvement_steps,
    )