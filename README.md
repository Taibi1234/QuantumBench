# QuantumBench

QuantumBench is a reproducible quantum-versus-classical optimization
benchmarking project.

The research question is:

&gt; How do QAOA depth, sampling, and simulated noise affect solution quality
&gt; on small weighted Max-Cut instances compared with classical algorithms?

## Current status

The project currently provides:

- Seeded weighted random graph generation
- A reusable five-instance benchmark suite
- Cut-value calculation
- An exact brute-force Max-Cut solver
- A multi-start local-search heuristic
- Approximation-ratio and optimal-solution comparisons
- Automated correctness and reproducibility tests

QAOA simulation and noisy experiments will be added in later milestones.

## Setup

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run a single exact experiment

```powershell
python -m scripts.solve_classical --nodes 6 --probability 0.5 --seed 42
```

Results are saved to `artifacts/classical_baseline.json`.

## Run the classical benchmark

```powershell
python -m scripts.run_classical_benchmark --restarts 20 --seed 42
```

Results are saved to `artifacts/classical_benchmark.json`.

For each instance, the benchmark records:

- Exact optimal cut value and assignments
- Heuristic best value and assignment
- Heuristic restart and improvement counts
- Approximation ratio
- Whether the heuristic found an optimal value

An approximation ratio of `1.0` means the heuristic reached the optimum.
Heuristic results do not prove optimality; the exact solver provides the
reference value for these small instances.

## Tests

```powershell
python -m pytest -q
```

## Limitations

- The exact solver has exponential runtime and is only for small instances.
- Local search can stop at a non-optimal local maximum.
- The current benchmark uses small synthetic weighted graphs.
- The project does not assume or claim quantum advantage.