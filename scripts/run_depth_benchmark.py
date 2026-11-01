import argparse
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from quantumbench.classical import solve_maxcut_exact
from quantumbench.evaluation import (
    evaluate_qaoa_result,
    summarize_qaoa_runs,
)
from quantumbench.heuristic import solve_maxcut_heuristic
from quantumbench.instances import create_default_suite, instance_to_dict
from quantumbench.qaoa import solve_qaoa_ideal


def main():
    parser = argparse.ArgumentParser(
        description="Compare QAOA depths across the benchmark suite."
    )
    parser.add_argument(
        "--reps",
        type=int,
        nargs="+",
        default=[1, 2, 3],
    )
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--shots", type=int, default=1024)
    parser.add_argument("--maxiter", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/depth_benchmark.json"),
    )
    args = parser.parse_args()

    if args.runs < 1:
        parser.error("runs must be at least one.")

    if any(reps < 1 for reps in args.reps):
        parser.error("Every QAOA depth must be at least one.")

    instance_results = []

    for instance_index, instance in enumerate(create_default_suite()):
        exact_result = solve_maxcut_exact(instance.graph)
        heuristic_result = solve_maxcut_heuristic(
            instance.graph,
            restarts=20,
            seed=args.seed,
        )

        depth_results = {}

        for reps in args.reps:
            runs = []

            for run_index in range(args.runs):
                run_seed = (
                    args.seed
                    + instance_index * 1000
                    + reps * 100
                    + run_index
                )

                qaoa_result = solve_qaoa_ideal(
                    instance.graph,
                    reps=reps,
                    shots=args.shots,
                    seed=run_seed,
                    maxiter=args.maxiter,
                )

                analysis = evaluate_qaoa_result(
                    instance.graph,
                    qaoa_result,
                    exact_result.optimal_value,
                )

                qaoa_dict = asdict(qaoa_result)
                qaoa_dict["optimal_sample_probability"] = (
                    analysis["optimal_sample_probability"]
                )

                runs.append({
                    "run_index": run_index,
                    "seed": run_seed,
                    "qaoa": qaoa_dict,
                    "analysis": analysis,
                })

            summary = summarize_qaoa_runs(runs)
            depth_results[str(reps)] = {
                "runs": runs,
                "summary": summary,
            }

            print(
                f"{instance.instance_id} p={reps}: "
                f"expected={summary['expected_ratio_mean']:.4f} "
                f"± {summary['expected_ratio_std']:.4f}, "
                f"optimal probability="
                f"{summary['optimal_probability_mean']:.4f}"
            )

        instance_results.append({
            "instance": instance_to_dict(instance),
            "exact": {
                "optimal_value": exact_result.optimal_value,
                "optimal_assignments": [
                    list(assignment)
                    for assignment in exact_result.optimal_assignments
                ],
            },
            "heuristic": {
                "best_value": heuristic_result.best_value,
                "best_assignment": list(
                    heuristic_result.best_assignment
                ),
            },
            "depths": depth_results,
        })

    experiment = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "simulation": "ideal_statevector",
        "configuration": {
            "reps": args.reps,
            "runs_per_setting": args.runs,
            "shots": args.shots,
            "maxiter": args.maxiter,
            "base_seed": args.seed,
        },
        "instances": instance_results,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(experiment, indent=2),
        encoding="utf-8",
    )

    print(f"\nSaved depth benchmark to {args.output}")


if __name__ == "__main__":
    main()