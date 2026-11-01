# QuantumBench

QuantumBench is a reproducible quantum-versus-classical optimization
benchmarking project.

The research question is:

&gt; How do QAOA depth, sampling, and simulated noise affect solution quality
&gt; on small weighted Max-Cut instances compared with classical algorithms?

## Implemented

- Seeded weighted graph generation and a reusable benchmark suite
- Exact brute-force and multi-start heuristic classical solvers
- Weighted Max-Cut Hamiltonian construction
- Ideal state-vector QAOA simulation and parameter optimization
- Multi-run QAOA depth comparisons
- Approximation, success-probability, runtime, and circuit-depth metrics
- Automated depth-study visualization
- Controlled one- and two-qubit depolarizing-noise simulations
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

## Ideal QAOA experiments

Single experiment:

```powershell
python -m scripts.run_qaoa_ideal --nodes 6 --probability 0.5 --seed 42 --reps 1 --shots 1024 --maxiter 100
```

Depth study:

```powershell
python -m scripts.run_depth_benchmark --reps 1 2 3 --runs 3 --shots 1024 --maxiter 100 --seed 42
```

Generate depth-study figures:

```powershell
python -m scripts.plot_depth_results --reps 1
```

## Noise study

```powershell
python -m scripts.run_noise_benchmark --nodes 6 --probability 0.5 --seed 42 --reps 1 --shots 1024 --runs 5
```

Results are saved to `artifacts/noise_benchmark.json`.

The experiment first optimizes parameters under ideal conditions. It then
holds those parameters fixed while evaluating four noise configurations:

| Level | One-qubit error | Two-qubit error |
|---|---:|---:|
| None | 0.000 | 0.000 |
| Low | 0.001 | 0.010 |
| Medium | 0.005 | 0.030 |
| High | 0.010 | 0.050 |

Holding parameters fixed helps isolate noise effects from optimizer variation.
Each configuration is sampled repeatedly to capture finite-shot variation.

The simplified model applies depolarizing channels to SX, X, and CX gates.
RZ is treated as virtual. Measurement error, thermal relaxation, crosstalk,
and device-specific calibration are not modeled.

## Evaluation metrics

- Expected and sampled approximation ratios
- Optimal-sample probability
- Circuit depth
- Local runtime
- Mean and standard deviation across repeated runs

Higher depth or higher noise does not guarantee a particular result in every
individual run. Conclusions should be based on aggregated experiments.

## Tests

```powershell
python -m pytest -q
```

## Limitations

- Exact classical solving and state-vector simulation scale exponentially.
- Small simulated experiments do not demonstrate quantum advantage.
- QAOA optimization can converge to poor local parameter choices.
- The noise model is simplified and is not a specific hardware model.
- Runtime measurements depend on the local computer.