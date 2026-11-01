import numpy as np


def aggregate_depth_study(depth_data: dict) -> dict:
    depths = sorted({
        int(depth)
        for instance in depth_data["instances"]
        for depth in instance["depths"]
    })
    aggregated = {}

    for depth in depths:
        summaries = [
            instance["depths"][str(depth)]["summary"]
            for instance in depth_data["instances"]
            if str(depth) in instance["depths"]
        ]

        aggregated[depth] = {
            "instance_count": len(summaries),
            "expected_ratio_mean": float(np.mean([
                summary["expected_ratio_mean"]
                for summary in summaries
            ])),
            "optimal_probability_mean": float(np.mean([
                summary["optimal_probability_mean"]
                for summary in summaries
            ])),
            "runtime_seconds_mean": float(np.mean([
                summary["runtime_seconds_mean"]
                for summary in summaries
            ])),
            "circuit_depth_mean": float(np.mean([
                summary["circuit_depth"]
                for summary in summaries
            ])),
        }

    return aggregated


def build_experiment_summary(depth_data: dict, noise_data: dict) -> dict:
    depth_summary = aggregate_depth_study(depth_data)
    best_depth = max(
        depth_summary,
        key=lambda depth: depth_summary[depth]["expected_ratio_mean"],
    )

    noise_summary = {
        name: {
            "one_qubit_error": level["one_qubit_error"],
            "two_qubit_error": level["two_qubit_error"],
            "sampled_ratio_mean": level["summary"]["sampled_ratio_mean"],
            "sampled_ratio_std": level["summary"]["sampled_ratio_std"],
            "optimal_probability_mean": (
                level["summary"]["optimal_probability_mean"]
            ),
        }
        for name, level in noise_data["noise_levels"].items()
    }

    return {
        "depth_study": depth_summary,
        "best_depth_by_mean_expected_ratio": best_depth,
        "noise_study": noise_summary,
        "exact_optimal_value": noise_data["exact"]["optimal_value"],
        "ideal_analysis": noise_data["ideal_optimization"]["analysis"],
    }


def summary_to_markdown(summary: dict) -> str:
    lines = [
        "# QuantumBench experimental summary",
        "",
        "This file is generated from the recorded depth and noise studies.",
        "",
        "## Depth study",
        "",
        "| Depth | Instances | Mean expected ratio | Mean optimal probability | Mean runtime (s) | Mean circuit depth |",
        "|---:|---:|---:|---:|---:|---:|",
    ]

    for depth, values in summary["depth_study"].items():
        lines.append(
            f"| {depth} "
            f"| {values['instance_count']} "
            f"| {values['expected_ratio_mean']:.4f} "
            f"| {values['optimal_probability_mean']:.4f} "
            f"| {values['runtime_seconds_mean']:.4f} "
            f"| {values['circuit_depth_mean']:.2f} |"
        )

    lines.extend([
        "",
        "The highest mean expected ratio occurred at "
        f"p={summary['best_depth_by_mean_expected_ratio']}. "
        "This is a descriptive result, not a significance test.",
        "",
        "## Noise study",
        "",
        "| Level | One-qubit error | Two-qubit error | Mean sampled ratio | Standard deviation | Mean optimal probability |",
        "|---|---:|---:|---:|---:|---:|",
    ])

    for name, values in summary["noise_study"].items():
        lines.append(
            f"| {name} "
            f"| {values['one_qubit_error']:.3f} "
            f"| {values['two_qubit_error']:.3f} "
            f"| {values['sampled_ratio_mean']:.4f} "
            f"| {values['sampled_ratio_std']:.4f} "
            f"| {values['optimal_probability_mean']:.4f} |"
        )

    ideal = summary["ideal_analysis"]
    lines.extend([
        "",
        "## Reference values",
        "",
        f"- Exact optimal cut value: {summary['exact_optimal_value']:.4f}",
        f"- Ideal expected approximation ratio: {ideal['expected_approximation_ratio']:.4f}",
        f"- Ideal optimal-sample probability: {ideal['optimal_sample_probability']:.4f}",
        "",
        "## Interpretation cautions",
        "",
        "- Results describe small simulated Max-Cut instances.",
        "- Repeated runs reduce sensitivity to individual outcomes but do not establish statistical significance.",
        "- The noise model is simplified and does not represent a specific quantum device.",
        "- No quantum advantage is claimed.",
        "",
    ])

    return "\n".join(lines)