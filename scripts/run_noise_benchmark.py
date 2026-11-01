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
from quantumbench.instances import create_instance, instance_to_dict
from quantumbench.noisy import evaluate_noisy_qaoa
from quantumbench.qaoa import solve_qaoa_ideal


NOISE_LEVELS = [
    ("none", 0.0, 0.0),
    ("low", 0.001, 0.01),
    ("medium", 0.005, 0.03),
    ("high", 0.01, 0.05),
]


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate ideal-trained QAOA parameters under noise."
    )
    parser.add_argument("--nodes", type=int, default=6)
    parser.add_argument("--probability", type=float, default=0.5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--reps", type=int, default=1)
    parser.add_argument("--shots", type=int, default=1024)
    parser.add_argument("--maxiter", type=int, default=100)
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/noise_benchmark.json"),
    )
    args = parser.parse_args()

    if args.runs < 1:
        parser.error("runs must be at least one.")

    instance = create_instance(
        node_count=args.nodes,
        edge_probability=args.probability,
        seed=args.seed,
    )
    exact_result = solve_maxcut_exact(instance.graph)

    ideal_result = solve_qaoa_ideal(
        instance.graph,
        reps=args.reps,
        shots=args.shots,
        seed=args.seed,
        maxiter=args.maxiter,
    )
    ideal_analysis = evaluate_qaoa_result(
        instance.graph,
        ideal_result,
        exact_result.optimal_value,
    )

    noise_results = {}

    for level_index, (name, one_error, two_error) in enumerate(
        NOISE_LEVELS
    ):
        runs = []

        for run_index in range(args.runs):
            run_seed = (
                args.seed
                + level_index * 1000
                + run_index
            )

            noisy_result = evaluate_noisy_qaoa(
                instance.graph,
                optimal_parameters=ideal_result.optimal_parameters,
                reps=args.reps,
                one_qubit_error=one_error,
                two_qubit_error=two_error,
                shots=args.shots,
                seed=run_seed,
            )
            analysis = evaluate_qaoa_result(
                instance.graph,
                noisy_result,
                exact_result.optimal_value,
            )

            runs.append({
                "run_index": run_index,
                "seed": run_seed,
                "qaoa": asdict(noisy_result),
                "analysis": analysis,
            })

        summary = summarize_qaoa_runs(runs)
        noise_results[name] = {
            "one_qubit_error": one_error,
            "two_qubit_error": two_error,
            "runs": runs,
            "summary": summary,
        }

        print(
            f"{name}: "
            f"mean ratio={summary['sampled_ratio_mean']:.4f}, "
            f"optimal probability="
            f"{summary['optimal_probability_mean']:.4f}"
        )

    experiment = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "method": (
            "Ideal-trained parameters evaluated with simplified "
            "depolarizing gate noise"
        ),
        "instance": instance_to_dict(instance),
        "configuration": {
            "reps": args.reps,
            "shots": args.shots,
            "maxiter": args.maxiter,
            "runs_per_noise_level": args.runs,
            "seed": args.seed,
        },
        "exact": {
            "optimal_value": exact_result.optimal_value,
        },
        "ideal_optimization": {
            "qaoa": asdict(ideal_result),
            "analysis": ideal_analysis,
        },
        "noise_levels": noise_results,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(experiment, indent=2),
        encoding="utf-8",
    )

    print(f"\nSaved noise benchmark to {args.output}")


if __name__ == "__main__":
    main()