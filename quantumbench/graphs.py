import random

import networkx as nx


def generate_weighted_graph(
    node_count: int,
    edge_probability: float,
    seed: int,
    weight_range: tuple[int, int] = (1, 10),
) -> nx.Graph:
    if node_count < 0:
        raise ValueError("node_count cannot be negative.")

    if not 0.0 <= edge_probability <= 1.0:
        raise ValueError("edge_probability must be between 0 and 1.")

    minimum_weight, maximum_weight = weight_range

    if minimum_weight < 1 or maximum_weight < minimum_weight:
        raise ValueError("Weights must be positive and correctly ordered.")

    graph = nx.gnp_random_graph(
        node_count,
        edge_probability,
        seed=seed,
    )

    random_generator = random.Random(seed)

    for source, target in graph.edges():
        graph[source][target]["weight"] = random_generator.randint(
            minimum_weight,
            maximum_weight,
        )

    return graph


def validate_graph(graph: nx.Graph) -> None:
    node_count = len(graph)
    expected_nodes = set(range(node_count))

    if set(graph.nodes()) != expected_nodes:
        raise ValueError(
            "Graph nodes must be consecutive integers starting at zero."
        )

    if any(source == target for source, target in graph.edges()):
        raise ValueError("Self-loops are not supported.")

    for _, _, data in graph.edges(data=True):
        weight = data.get("weight", 1)

        if weight <= 0:
            raise ValueError("All edge weights must be positive.")