import argparse
import json
from pathlib import Path

from quantumbench.classical import solve_maxcut_exact
from quantumbench.graphs import generate_weighted_graph


def main():
    parser = argparse.ArgumentParser(
        description="Solve a small weighted Max-Cut instance exactly."
    )
    parser.add_argument("--nodes", type=int, default=6)
    parser.add_argument("--probability", type=float, default=0.5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/classical_baseline.json"),
    )
    args = parser.parse_args()

    graph = generate_weighted_graph(
        node_count=args.nodes,
        edge_probability=args.probability,
        seed=args.seed,
    )
    result = solve_maxcut_exact(graph)

    experiment = {
        "graph": {
        "node_count": len(graph),
            "edge_probability": args.probability,
            "seed": args.seed,
            "edges": [
                {
                    "source": source,
                    "target": target,
                    "weight": data["weight"],
                }
                for source, target, data in graph.edges(data=True)
            ],
        },
        "solver": "exact_brute_force",
        "optimal_value": result.optimal_value,
        "optimal_assignments": [
            list(assignment)
            for assignment in result.optimal_assignments
        ],
        "evaluated_assignments": result.evaluated_assignments,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(experiment, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(experiment, indent=2))
    print(f"\nSaved results to {args.output}")


if __name__ == "__main__":
    main()