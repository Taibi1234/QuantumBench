from dataclasses import dataclass

import networkx as nx

from quantumbench.graphs import generate_weighted_graph


@dataclass(frozen=True)
class BenchmarkInstance:
    instance_id: str
    graph: nx.Graph
    edge_probability: float
    seed: int


def create_instance(
    node_count: int,
    edge_probability: float,
    seed: int,
) -> BenchmarkInstance:
    graph = generate_weighted_graph(
        node_count=node_count,
        edge_probability=edge_probability,
        seed=seed,
    )

    probability_label = f"{edge_probability:.3f}".replace(".", "")
    instance_id = (
        f"n{node_count:02d}_p{probability_label}_s{seed:04d}"
    )

    return BenchmarkInstance(
        instance_id=instance_id,
        graph=graph,
        edge_probability=edge_probability,
        seed=seed,
    )


def create_default_suite() -> list[BenchmarkInstance]:
    configurations = [
        (4, 0.5, 11),
        (6, 0.4, 22),
        (6, 0.7, 33),
        (8, 0.5, 44),
        (8, 0.8, 55),
    ]

    return [
        create_instance(node_count, probability, seed)
        for node_count, probability, seed in configurations
    ]


def instance_to_dict(instance: BenchmarkInstance) -> dict:
    return {
        "instance_id": instance.instance_id,
        "node_count": len(instance.graph),
        "edge_count": instance.graph.number_of_edges(),
        "edge_probability": instance.edge_probability,
        "seed": instance.seed,
        "edges": [
            {
                "source": source,
                "target": target,
                "weight": data["weight"],
            }
            for source, target, data in instance.graph.edges(data=True)
        ],
    }