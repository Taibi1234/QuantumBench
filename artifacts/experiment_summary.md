# QuantumBench experimental summary

This file is generated from the recorded depth and noise studies.

## Depth study

| Depth | Instances | Mean expected ratio | Mean optimal probability | Mean runtime (s) | Mean circuit depth |
|---:|---:|---:|---:|---:|---:|
| 1 | 5 | 0.6837 | 0.1522 | 34.3360 | 1.00 |
| 2 | 5 | 0.7190 | 0.1539 | 69.7786 | 1.00 |
| 3 | 5 | 0.7502 | 0.2100 | 97.2187 | 1.00 |

The highest mean expected ratio occurred at p=3. This is a descriptive result, not a significance test.

## Noise study

| Level | One-qubit error | Two-qubit error | Mean sampled ratio | Standard deviation | Mean optimal probability |
|---|---:|---:|---:|---:|---:|
| none | 0.000 | 0.000 | 0.6372 | 0.0043 | 0.0695 |
| low | 0.001 | 0.010 | 0.6217 | 0.0080 | 0.0602 |
| medium | 0.005 | 0.030 | 0.6088 | 0.0044 | 0.0553 |
| high | 0.010 | 0.050 | 0.5966 | 0.0044 | 0.0447 |

## Reference values

- Exact optimal cut value: 29.0000
- Ideal expected approximation ratio: 0.6317
- Ideal optimal-sample probability: 0.0498

## Interpretation cautions

- Results describe small simulated Max-Cut instances.
- Repeated runs reduce sensitivity to individual outcomes but do not establish statistical significance.
- The noise model is simplified and does not represent a specific quantum device.
- No quantum advantage is claimed.
