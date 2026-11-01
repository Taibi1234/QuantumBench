\# QuantumBench: Reproducible QAOA and Classical Max-Cut Benchmarking



\## Abstract



QuantumBench is a reproducible benchmarking platform for comparing quantum

and classical optimization methods on small weighted Max-Cut instances. The

project combines exact classical enumeration, multi-start local search,

ideal state-vector QAOA simulation, repeated parameter-optimization runs,

finite-shot sampling, and controlled depolarizing-noise experiments.



Across the five-instance depth study, increasing QAOA depth from p=1 to p=3

improved the mean expected approximation ratio from 0.6837 to 0.7502. Mean

runtime increased from 35.0874 to 97.3830 seconds, while mean transpiled

logical circuit depth increased from 29.00 to 69.60. In a separate

single-instance noise study, increasing simulated noise reduced both the

mean sampled approximation ratio and optimal-sample probability.



These results demonstrate a reproducible experimental workflow and illustrate

trade-offs between solution quality, computational cost, circuit depth, and

noise. They do not demonstrate quantum advantage or statistical significance.



\## Research questions



1\. How does increasing QAOA depth affect expected solution quality,

&#x20;  optimal-sample probability, runtime, and transpiled circuit depth?

2\. How does simplified depolarizing noise affect QAOA sampling outcomes when

&#x20;  ideal-trained parameters are held fixed?

3\. How do the recorded QAOA results compare with exact and heuristic

&#x20;  classical baselines on the same small instances?



\## Methods



\### Benchmark suite



The depth study uses five seeded weighted graphs with integer edge weights

from 1 through 10:



| Instance | Nodes | Edges | Edge probability | Graph seed | Exact optimum |

|---|---:|---:|---:|---:|---:|

| n04\_p0500\_s0011 | 4 | 2 | 0.5 | 11 | 17 |

| n06\_p0400\_s0022 | 6 | 7 | 0.4 | 22 | 28 |

| n06\_p0700\_s0033 | 6 | 10 | 0.7 | 33 | 57 |

| n08\_p0500\_s0044 | 8 | 17 | 0.5 | 44 | 74 |

| n08\_p0800\_s0055 | 8 | 24 | 0.8 | 55 | 90 |



The graphs, weights, exact answers, heuristic results, and individual QAOA

runs are stored in the JSON artifacts.



\### Classical baselines



The exact solver enumerates assignments with the first bit fixed to zero.

Complementary assignments have the same cut value, so this reduces the search

from 2^n to 2^(n-1) candidates without removing any distinct optimum.



The heuristic performs multi-start one-flip local search with 20 restarts.

It repeatedly applies the best positive-gain node flip until reaching a local

optimum.



The heuristic found the exact optimum on all five recorded suite instances.

This describes the selected small suite only; the heuristic does not

guarantee optimality in general.



\### Ideal QAOA depth study



The depth study evaluates p=1, p=2, and p=3 using:



\- Ideal state-vector simulation

\- COBYLA parameter optimization

\- At most 100 optimizer iterations per run

\- Three independently seeded optimization runs per instance and depth

\- 1,024 samples per run

\- Deterministic seeds derived from the instance, depth, and run index



Expected cut values are calculated from the optimized state vector. Sampled

metrics are calculated from seeded finite-shot draws from its probability

distribution.



Circuit depth is measured after transpilation into the RZ, SX, X, and CX

basis gates with optimization level 1. This is a logical circuit-depth

metric, not a hardware-routed depth for a specific device.



\### Noise study



The noise study uses a separate six-node instance generated with edge

probability 0.5 and seed 42. It uses p=1, 1,024 shots, and five sampled runs

per noise level.



QAOA parameters are optimized once under ideal conditions and then held

fixed across all noise levels. This isolates the effect of noise and sampling

from variation caused by retraining parameters.



| Level | One-qubit depolarizing error | Two-qubit depolarizing error |

|---|---:|---:|

| None | 0.000 | 0.000 |

| Low | 0.001 | 0.010 |

| Medium | 0.005 | 0.030 |

| High | 0.010 | 0.050 |



Noise is applied to SX, X, and CX gates. RZ is treated as virtual. The model

does not include measurement error, thermal relaxation, crosstalk, device

topology, or device-specific calibration data.



\### Metrics



\- \*\*Approximation ratio:\*\* cut value divided by the exact optimum.

\- \*\*Expected approximation ratio:\*\* ratio derived from the ideal optimized

&#x20; state-vector expectation.

\- \*\*Sampled approximation ratio:\*\* ratio derived from finite-shot samples.

\- \*\*Optimal-sample probability:\*\* fraction of samples whose assignment

&#x20; reaches the exact optimum.

\- \*\*Runtime:\*\* local wall-clock time, including experiment-specific

&#x20; simulation work.

\- \*\*Circuit depth:\*\* depth after basis-gate transpilation.



\## Results



\### Classical benchmark



| Instance | Exact optimum | Heuristic best | Heuristic ratio | Optimum found |

|---|---:|---:|---:|---|

| n04\_p0500\_s0011 | 17 | 17 | 1.0000 | Yes |

| n06\_p0400\_s0022 | 28 | 28 | 1.0000 | Yes |

| n06\_p0700\_s0033 | 57 | 57 | 1.0000 | Yes |

| n08\_p0500\_s0044 | 74 | 74 | 1.0000 | Yes |

| n08\_p0800\_s0055 | 90 | 90 | 1.0000 | Yes |



The exact solver provides ground truth for evaluating both the heuristic

and QAOA. On this suite, the heuristic is a stronger practical comparator

than enumeration alone because it reached every recorded optimum without

exhaustively enumerating every assignment.



\### QAOA depth study



| Depth | Instances | Mean expected ratio | Mean optimal probability | Mean runtime (s) | Mean transpiled depth |

|---:|---:|---:|---:|---:|---:|

| 1 | 5 | 0.6837 | 0.1522 | 35.0874 | 29.00 |

| 2 | 5 | 0.7190 | 0.1539 | 71.7226 | 49.00 |

| 3 | 5 | 0.7502 | 0.2100 | 97.3830 | 69.60 |



Increasing p from 1 to 2 improved the mean expected ratio by 0.0353, while

mean optimal-sample probability changed only from 0.1522 to 0.1539.

Increasing p from 2 to 3 improved the mean expected ratio by another 0.0312

and increased mean optimal-sample probability to 0.2100.



The highest aggregate expected ratio and optimal-sample probability occurred

at p=3. However, this improvement came with approximately 2.78 times the

recorded mean runtime of p=1 and a substantially deeper transpiled circuit.



These are aggregate descriptive results. They do not establish that p=3 is

better for every graph, optimizer seed, or experimental configuration.



!\[Expected approximation ratio by QAOA depth](artifacts/figures/approximation\_ratio\_by\_depth.png)



!\[Optimal-sample probability by QAOA depth](artifacts/figures/optimal\_probability\_by\_depth.png)



!\[Runtime and transpiled circuit depth](artifacts/figures/runtime\_and\_circuit\_depth.png)



\### Noise study



The exact optimum for the noise-study instance was 29. Before the repeated

noisy sampling experiments, the ideal p=1 optimization produced:



\- Expected approximation ratio: 0.6317

\- Optimal-sample probability: 0.0498



| Noise level | Mean sampled ratio | Standard deviation | Mean optimal probability |

|---|---:|---:|---:|

| None | 0.6372 | 0.0043 | 0.0695 |

| Low | 0.6217 | 0.0080 | 0.0602 |

| Medium | 0.6088 | 0.0044 | 0.0553 |

| High | 0.5966 | 0.0044 | 0.0447 |



From none to high noise, the mean sampled ratio decreased by 0.0406 and the

mean optimal-sample probability decreased by 0.0248. Both aggregate metrics

declined monotonically across the recorded noise levels.



The no-noise sampled values need not exactly equal the ideal state-vector

reference values: the former are finite-shot estimates from repeated sampled

runs, while the expected ratio is calculated directly from the state vector.



The standard deviations summarize only five repeated sampling runs. They are

not confidence intervals and do not establish statistical significance.



!\[Sampled approximation ratio under noise](artifacts/figures/noise\_approximation\_ratio.png)



!\[Optimal-sample probability under noise](artifacts/figures/noise\_optimal\_probability.png)



\## Discussion



The experiments show three practical trade-offs.



First, additional QAOA layers improved aggregate expected solution quality in

the recorded depth study, but also increased optimization runtime and logical

circuit depth. A higher p therefore should not be treated as automatically

preferable without considering its computational cost.



Second, the noise experiment illustrates why ideal solution quality alone is

insufficient for evaluating a quantum optimization pipeline. Even with fixed

parameters, increasing simplified gate noise reduced the recorded sampling

metrics.



Third, the classical heuristic reached the optimum on every suite instance,

whereas the aggregate QAOA expected ratios remained below 1. The experiment

therefore provides no basis for claiming that QAOA outperformed the classical

baselines.



The primary value of QuantumBench is its reproducible comparison methodology:

exact ground truth, a non-exact classical comparator, seeded repeated runs,

explicit sampling metrics, controlled noise evaluation, and preserved raw

artifacts.



\## Limitations



\- The suite contains only five small graphs with at most eight nodes.

\- The noise study examines only one graph and one ideal parameter set.

\- Exact enumeration and state-vector simulation scale exponentially.

\- Three optimization runs per depth do not support strong statistical claims.

\- Five sampling runs per noise level provide only limited variability

&#x20; estimates.

\- COBYLA can converge to different local parameter choices, and the 100-

&#x20; iteration limit may prevent convergence.

\- The depolarizing-noise model is simplified and does not represent a

&#x20; specific quantum device.

\- Transpilation uses a basis gate set without device-specific routing,

&#x20; connectivity, or calibration constraints.

\- Runtime measurements depend on the local computer and software versions.

\- The heuristic's perfect results on this suite do not generalize to all

&#x20; Max-Cut instances.

\- No quantum advantage, scaling advantage, or statistical significance is

&#x20; claimed.



\## Conclusion



Within these small simulated experiments, increasing QAOA depth improved

aggregate expected approximation ratio and optimal-sample probability, with

the best recorded means at p=3. These gains were accompanied by higher

runtime and deeper transpiled circuits. Increasing depolarizing noise reduced

both sampled solution quality and optimal-sample probability in the separate

fixed-parameter experiment.



QuantumBench meets its goal as a reproducible research-oriented benchmarking

project. Its results should be interpreted as a demonstration of experimental

methodology and observed trade-offs, not as evidence of quantum advantage.



\## Reproducing the experiments



```powershell

py -3.12 -m venv .venv

.\\.venv\\Scripts\\Activate.ps1

python -m pip install -r requirements.txt



python -m scripts.run\_classical\_benchmark --restarts 20 --seed 42



python -m scripts.run\_depth\_benchmark --reps 1 2 3 --runs 3 --shots 1024 --maxiter 100 --seed 42

python -m scripts.plot\_depth\_results --reps 1



python -m scripts.run\_noise\_benchmark --nodes 6 --probability 0.5 --seed 42 --reps 1 --shots 1024 --runs 5

python -m scripts.plot\_noise\_results

python -m scripts.generate\_summary



python -m pytest -q

