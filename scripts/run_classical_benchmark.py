import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path

from quantumbench.classical import solve_maxcut_exact
from quantumbench.heuristic import solve_maxcut_heuristic
from quantumbench.instances import create_default_suite, instance_to_dict


def main():
    parser = argparse.ArgumentParser(
        description="Compare exact and heuristic Max-Cut solvers."
    )
    parser.add_argument("--restarts", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/classical_benchmark.json"),
    )
    args = parser.parse_args()

    results = []

    for instance in create_default_suite():
        exact_result = solve_maxcut_exact(instance.graph)
        heuristic_result = solve_maxcut_heuristic(
            instance.graph,
            restarts=args.restarts,
            seed=args.seed,
        )

        if exact_result.optimal_value == 0:
            approximation_ratio = (
                1.0 if heuristic_result.best_value == 0 else 0.0
            )
        else:
            approximation_ratio = (
                heuristic_result.best_value / exact_result.optimal_value
            )

        record = {
            "instance": instance_to_dict(instance),
            "exact": {
                "optimal_value": exact_result.optimal_value,
                "optimal_assignments": [
                    list(assignment)
                    for assignment in exact_result.optimal_assignments
                ],
                "evaluated_assignments": (
                    exact_result.evaluated_assignments
                ),
            },
            "heuristic": {
                "best_value": heuristic_result.best_value,
                "best_assignment": list(
                    heuristic_result.best_assignment
                ),
                "restarts": heuristic_result.restarts,
                "improvement_steps": (
                    heuristic_result.improvement_steps
                ),
            },
            "approximation_ratio": approximation_ratio,
            "optimal_found": math.isclose(
                heuristic_result.best_value,
                exact_result.optimal_value,
            ),
        }
        results.append(record)

        print(
            f"{instance.instance_id}: "
            f"exact={exact_result.optimal_value:.1f}, "
            f"heuristic={heuristic_result.best_value:.1f}, "
            f"ratio={approximation_ratio:.4f}"
        )

    experiment = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "suite": "default_v1",
        "heuristic_seed": args.seed,
        "results": results,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(experiment, indent=2),
        encoding="utf-8",
    )

    print(f"\nSaved benchmark results to {args.output}")


if __name__ == "__main__":
    main()