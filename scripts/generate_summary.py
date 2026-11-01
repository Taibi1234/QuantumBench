import argparse
import json
from pathlib import Path

from quantumbench.reporting import (
    build_experiment_summary,
    summary_to_markdown,
)


def main():
    parser = argparse.ArgumentParser(
        description="Generate an aggregated experimental summary."
    )
    parser.add_argument(
        "--depth-input",
        type=Path,
        default=Path("artifacts/depth_benchmark.json"),
    )
    parser.add_argument(
        "--noise-input",
        type=Path,
        default=Path("artifacts/noise_benchmark.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/experiment_summary.md"),
    )
    args = parser.parse_args()

    depth_data = json.loads(
        args.depth_input.read_text(encoding="utf-8")
    )
    noise_data = json.loads(
        args.noise_input.read_text(encoding="utf-8")
    )

    summary = build_experiment_summary(depth_data, noise_data)
    markdown = summary_to_markdown(summary)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markdown, encoding="utf-8")

    print(f"Saved experimental summary to {args.output}")


if __name__ == "__main__":
    main()