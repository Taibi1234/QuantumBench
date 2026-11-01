import argparse
from pathlib import Path

from quantumbench.noise_plotting import (
    generate_noise_plots,
    load_noise_results,
)


def main():
    parser = argparse.ArgumentParser(
        description="Generate figures from the QAOA noise study."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("artifacts/noise_benchmark.json"),
    )
    parser.add_argument(
        "--output-directory",
        type=Path,
        default=Path("artifacts/figures"),
    )
    args = parser.parse_args()

    data = load_noise_results(args.input)
    paths = generate_noise_plots(data, args.output_directory)

    for path in paths:
        print(f"Created {path}")


if __name__ == "__main__":
    main()