# QuantumBench

QuantumBench is a reproducible quantum-versus-classical optimization
benchmarking project.

The research question is:

&gt; How do QAOA depth, sampling, and simulated noise affect solution quality
&gt; on small weighted Max-Cut instances compared with classical algorithms?

## Current status

Implemented:

- Seeded weighted random graph generation
- A reusable five-instance benchmark suite
- Exact brute-force Max-Cut solutions
- Multi-start local-search heuristic solutions
- Weighted Max-Cut Hamiltonian construction
- Ideal state-vector QAOA simulation
- Classical optimization of QAOA parameters
- Final bitstring sampling
- Expected, sampled, and optimal-solution metrics
- Automated correctness and reproducibility tests

No IBM Quantum account or physical quantum computer is required.

## Setup

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Classical experiments

Run one exact experiment:

```powershell
python -m scripts.solve_classical --nodes 6 --probability 0.5 --seed 42
```

Run the exact-versus-heuristic suite:

```powershell
python -m scripts.run_classical_benchmark --restarts 20 --seed 42
```

## Ideal QAOA experiment

```powershell
python -m scripts.run_qaoa_ideal --nodes 6 --probability 0.5 --seed 42 --reps 1 --shots 1024 --maxiter 100
```

Results are saved to `artifacts/qaoa_ideal.json`.

The experiment records:

- Exact optimal value
- Optimized QAOA parameters
- Expected cost and expected cut value
- Sampled mean and best sampled cut values
- Optimal sample probability
- Measurement counts
- Objective history
- Circuit depth and runtime

`reps` controls the QAOA depth. Increasing it adds more parameters and
circuit operations but does not guarantee a better result after optimization.

## Evaluation metrics

- **Expected approximation ratio:** expected cut value divided by optimum
- **Sampled approximation ratio:** sampled mean or best value divided by optimum
- **Optimal sample probability:** fraction of shots producing an optimal assignment

These metrics measure different properties and should not be treated as
interchangeable.

## Tests

```powershell
python -m pytest -q
```

## Limitations

- Exact classical solving has exponential runtime.
- State-vector simulation has exponential memory requirements.
- Small simulated experiments do not demonstrate quantum advantage.
- QAOA optimization can converge to poor local parameter choices.
- Ideal simulation does not include hardware noise.