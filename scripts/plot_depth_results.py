import argparse
from pathlib import Path

from quantumbench.plotting import generate_all_plots, load_depth_results


def main():
    parser = argparse.ArgumentParser(
        description="Generate figures from a QAOA depth benchmark."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("artifacts/depth_benchmark.json"),
    )
    parser.add_argument(
        "--output-directory",
        type=Path,
        default=Path("artifacts/figures"),
    )
    parser.add_argument("--instance", default=None)
    parser.add_argument("--reps", type=int, default=1)
    args = parser.parse_args()

    data = load_depth_results(args.input)

    if not data["instances"]:
        parser.error("The benchmark contains no instances.")

    convergence_instance = (
        args.instance
        or data["instances"][0]["instance"]["instance_id"]
    )

    paths = generate_all_plots(
        data,
        output_directory=args.output_directory,
        convergence_instance=convergence_instance,
        convergence_reps=args.reps,
    )

    for path in paths:
        print(f"Created {path}")


if __name__ == "__main__":
    main()