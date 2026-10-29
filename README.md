\# QuantumBench



QuantumBench is a reproducible quantum-versus-classical optimization

benchmarking project.



The research question is:



\&gt; How do QAOA depth, sampling, and simulated noise affect solution quality

\&gt; on small weighted Max-Cut instances compared with classical algorithms?



\## Current status



The project currently provides:



\- Seeded weighted random graph generation

\- Cut-value calculation

\- An exact brute-force Max-Cut solver

\- A command-line classical baseline experiment

\- Automated correctness and reproducibility tests



QAOA simulation and noisy experiments will be added in later milestones.



\## Setup



```powershell

py -3.12 -m venv .venv

.\\.venv\\Scripts\\Activate.ps1

python -m pip install -r requirements.txt

```



\## Run the classical baseline



```powershell

python -m scripts.solve\_classical --nodes 6 --probability 0.5 --seed 42

```



Results are saved to `artifacts/classical\_baseline.json`.



\## Tests



```powershell

python -m pytest -q

```



\## Important limitation



The exact solver has exponential runtime and is intended only for small

validation instances. This project does not assume or claim quantum advantage.

