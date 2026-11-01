import time
from dataclasses import dataclass

import networkx as nx
from qiskit import transpile
from qiskit.circuit.library import QAOAAnsatz
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

from quantumbench.classical import cut_value
from quantumbench.graphs import validate_graph
from quantumbench.qaoa import (
    bitstring_to_assignment,
    build_maxcut_hamiltonian,
)


@dataclass(frozen=True)
class NoisyQAOAResult:
    reps: int
    shots: int
    seed: int
    one_qubit_error: float
    two_qubit_error: float
    optimal_parameters: list[float]
    expected_cost: float
    expected_cut_value: float
    sampled_mean_cut_value: float
    best_sampled_value: float
    best_sampled_assignment: tuple[int, ...]
    counts: dict[str, int]
    circuit_depth: int
    runtime_seconds: float


def build_depolarizing_noise_model(
    one_qubit_error: float,
    two_qubit_error: float,
) -> NoiseModel:
    if not 0.0 <= one_qubit_error <= 1.0:
        raise ValueError("one_qubit_error must be between 0 and 1.")

    if not 0.0 <= two_qubit_error <= 1.0:
        raise ValueError("two_qubit_error must be between 0 and 1.")

    noise_model = NoiseModel()

    if one_qubit_error > 0:
        one_qubit_channel = depolarizing_error(
            one_qubit_error,
            num_qubits=1,
        )

        # RZ is treated as virtual; noise is applied to SX and X.
        noise_model.add_all_qubit_quantum_error(
            one_qubit_channel,
            ["sx", "x"],
        )

    if two_qubit_error > 0:
        two_qubit_channel = depolarizing_error(
            two_qubit_error,
            num_qubits=2,
        )
        noise_model.add_all_qubit_quantum_error(
            two_qubit_channel,
            ["cx"],
        )

    return noise_model


def evaluate_noisy_qaoa(
    graph: nx.Graph,
    optimal_parameters: list[float],
    reps: int,
    one_qubit_error: float,
    two_qubit_error: float,
    shots: int = 1024,
    seed: int = 42,
) -> NoisyQAOAResult:
    validate_graph(graph)

    if reps < 1:
        raise ValueError("reps must be at least one.")

    if shots < 1:
        raise ValueError("shots must be at least one.")

    started = time.perf_counter()
    cost_hamiltonian = build_maxcut_hamiltonian(graph)
    circuit = QAOAAnsatz(
        cost_operator=cost_hamiltonian,
        reps=reps,
    )
    bound_circuit = circuit.assign_parameters(optimal_parameters)

    noise_model = build_depolarizing_noise_model(
        one_qubit_error,
        two_qubit_error,
    )
    simulator = AerSimulator(
        noise_model=noise_model,
        basis_gates=["rz", "sx", "x", "cx"],
    )

    executable_circuit = transpile(
        bound_circuit,
        backend=simulator,
        optimization_level=1,
    )
    executable_circuit.measure_all()

    job = simulator.run(
        executable_circuit,
        shots=shots,
        seed_simulator=seed,
    )
    counts = dict(job.result().get_counts())

    sampled_total = 0.0
    best_sampled_value = -1.0
    best_sampled_assignment = tuple([0] * len(graph))

    for bitstring, count in counts.items():
        assignment = bitstring_to_assignment(bitstring)
        value = cut_value(graph, assignment)
        sampled_total += value * count

        if value > best_sampled_value:
            best_sampled_value = value
            best_sampled_assignment = assignment

    mean_cut_value = sampled_total / shots
    total_weight = sum(
        float(data.get("weight", 1))
        for _, _, data in graph.edges(data=True)
    )
    expected_cost = total_weight / 2.0 - mean_cut_value

    return NoisyQAOAResult(
        reps=reps,
        shots=shots,
        seed=seed,
        one_qubit_error=one_qubit_error,
        two_qubit_error=two_qubit_error,
        optimal_parameters=list(optimal_parameters),
        expected_cost=expected_cost,
        # In noisy experiments, these are finite-shot estimates.
        expected_cut_value=mean_cut_value,
        sampled_mean_cut_value=mean_cut_value,
        best_sampled_value=best_sampled_value,
        best_sampled_assignment=best_sampled_assignment,
        counts=counts,
        circuit_depth=executable_circuit.depth(),
        runtime_seconds=time.perf_counter() - started,
    )