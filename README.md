# QuantumBench

QuantumBench is a reproducible quantum-versus-classical optimization
benchmarking project.

The research question is:

&gt; How do QAOA depth, sampling, and simulated noise affect solution quality
&gt; on small weighted Max-Cut instances compared with classical algorithms?

## Implemented

- Seeded weighted random graph generation
- A reusable five-instance benchmark suite
- Exact brute-force and multi-start heuristic classical solvers
- Weighted Max-Cut Hamiltonian construction
- Ideal state-vector QAOA simulation
- Classical optimization of QAOA parameters
- Multi-run comparisons of QAOA depths 1, 2, and 3
- Approximation-ratio, success-probability, runtime, and circuit-depth metrics
- Automated result visualization
- Automated correctness and reproducibility tests

No IBM Quantum account or physical quantum computer is required.

## Setup

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Classical experiments

```powershell
python -m scripts.solve_classical --nodes 6 --probability 0.5 --seed 42
python -m scripts.run_classical_benchmark --restarts 20 --seed 42
```

## Single ideal QAOA experiment

```powershell
python -m scripts.run_qaoa_ideal --nodes 6 --probability 0.5 --seed 42 --reps 1 --shots 1024 --maxiter 100
```

Results are saved to `artifacts/qaoa_ideal.json`.

## QAOA depth benchmark

```powershell
python -m scripts.run_depth_benchmark --reps 1 2 3 --runs 3 --shots 1024 --maxiter 100 --seed 42
```

The default configuration evaluates five instances, three depths, and three
seeded runs per depth, for 45 total QAOA optimization runs.

Results are saved to `artifacts/depth_benchmark.json`.

## Generate figures

```powershell
python -m scripts.plot_depth_results --reps 1
```

Generated figures:

- `artifacts/figures/approximation_ratio_by_depth.png`
- `artifacts/figures/optimal_probability_by_depth.png`
- `artifacts/figures/runtime_and_circuit_depth.png`
- `artifacts/figures/qaoa_convergence.png`

To plot convergence for a different instance:

```powershell
python -m scripts.plot_depth_results --instance INSTANCE_ID --reps 2
```

Instance identifiers are recorded in the benchmark JSON.

## Evaluation metrics

- **Expected approximation ratio:** expected cut value divided by optimum
- **Sampled approximation ratio:** sampled value divided by optimum
- **Optimal-sample probability:** fraction of shots producing an optimal assignment
- **Runtime:** local wall-clock duration of one QAOA experiment
- **Circuit depth:** depth of the optimized QAOA circuit

These measurements describe small simulations and should not be interpreted
as evidence of quantum advantage.

## Tests

```powershell
python -m pytest -q
```

## Limitations

- Exact classical solving has exponential runtime.
- State-vector simulation has exponential memory requirements.
- QAOA optimization can converge to poor local parameter choices.
- Ideal simulation does not include hardware noise.
- Runtime measurements depend on the computer and background workload.