import argparse
import json
import math
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from quantumbench.classical import cut_value, solve_maxcut_exact
from quantumbench.instances import create_instance, instance_to_dict
from quantumbench.qaoa import (
    bitstring_to_assignment,
    solve_qaoa_ideal,
)


def approximation_ratio(value, optimal_value):
    if optimal_value == 0:
        return 1.0 if value == 0 else 0.0

    return value / optimal_value


def main():
    parser = argparse.ArgumentParser(
        description="Run ideal state-vector QAOA on one Max-Cut instance."
    )
    parser.add_argument("--nodes", type=int, default=6)
    parser.add_argument("--probability", type=float, default=0.5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--reps", type=int, default=1)
    parser.add_argument("--shots", type=int, default=1024)
    parser.add_argument("--maxiter", type=int, default=100)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/qaoa_ideal.json"),
    )
    args = parser.parse_args()

    instance = create_instance(
        node_count=args.nodes,
        edge_probability=args.probability,
        seed=args.seed,
    )
    exact_result = solve_maxcut_exact(instance.graph)
    qaoa_result = solve_qaoa_ideal(
        instance.graph,
        reps=args.reps,
        shots=args.shots,
        seed=args.seed,
        maxiter=args.maxiter,
    )

    optimal_sample_count = 0

    for bitstring, count in qaoa_result.counts.items():
        assignment = bitstring_to_assignment(bitstring)
        value = cut_value(instance.graph, assignment)

        if math.isclose(value, exact_result.optimal_value):
            optimal_sample_count += count

    optimal_sample_probability = (
        optimal_sample_count / qaoa_result.shots
    )

    result_dict = asdict(qaoa_result)
    result_dict["optimal_sample_probability"] = (
        optimal_sample_probability
    )

    experiment = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "simulation": "ideal_statevector",
        "instance": instance_to_dict(instance),
        "exact": {
            "optimal_value": exact_result.optimal_value,
            "optimal_assignments": [
                list(assignment)
                for assignment in exact_result.optimal_assignments
            ],
        },
        "qaoa": result_dict,
        "analysis": {
            "expected_approximation_ratio": approximation_ratio(
                qaoa_result.expected_cut_value,
                exact_result.optimal_value,
            ),
            "sampled_mean_approximation_ratio": approximation_ratio(
                qaoa_result.sampled_mean_cut_value,
                exact_result.optimal_value,
            ),
            "best_sampled_approximation_ratio": approximation_ratio(
                qaoa_result.best_sampled_value,
                exact_result.optimal_value,
            ),
            "optimal_sample_probability": optimal_sample_probability,
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(experiment, indent=2),
        encoding="utf-8",
    )

    print(f"Instance: {instance.instance_id}")
    print(f"Exact optimum: {exact_result.optimal_value:.4f}")
    print(
        "QAOA expected cut: "
        f"{qaoa_result.expected_cut_value:.4f}"
    )
    print(
        "Best sampled cut: "
        f"{qaoa_result.best_sampled_value:.4f}"
    )
    print(
        "Optimal sample probability: "
        f"{optimal_sample_probability:.4f}"
    )
    print(f"Circuit depth: {qaoa_result.circuit_depth}")
    print(f"Saved results to {args.output}")


if __name__ == "__main__":
    main()