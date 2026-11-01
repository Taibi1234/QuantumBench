import time
from dataclasses import dataclass

import networkx as nx
import numpy as np
from qiskit import transpile
from qiskit.circuit.library import QAOAAnsatz
from qiskit.quantum_info import SparsePauliOp, Statevector
from scipy.optimize import minimize

from quantumbench.classical import cut_value
from quantumbench.graphs import validate_graph


@dataclass(frozen=True)
class IdealQAOAResult:
    reps: int
    shots: int
    seed: int
    initial_parameters: list[float]
    optimal_parameters: list[float]
    expected_cost: float
    expected_cut_value: float
    sampled_mean_cut_value: float
    best_sampled_value: float
    best_sampled_assignment: tuple[int, ...]
    optimal_sample_probability: float | None
    counts: dict[str, int]
    objective_history: list[float]
    optimizer_success: bool
    optimizer_message: str
    circuit_depth: int
    runtime_seconds: float


def build_maxcut_hamiltonian(graph: nx.Graph) -> SparsePauliOp:
    validate_graph(graph)

    if graph.number_of_edges() == 0:
        raise ValueError("QAOA requires a graph with at least one edge.")

    terms = []

    for source, target, data in graph.edges(data=True):
        weight = float(data.get("weight", 1))
        terms.append(
            ("ZZ", [source, target], weight / 2.0)
        )

    return SparsePauliOp.from_sparse_list(
        terms,
        num_qubits=len(graph),
    )


def transpiled_circuit_depth(circuit) -> int:
    """Return depth after decomposition into the experiment's basis gates."""
    transpiled_circuit = transpile(
        circuit,
        basis_gates=["rz", "sx", "x", "cx"],
        optimization_level=1,
    )
    return transpiled_circuit.depth()


def bitstring_to_assignment(bitstring: str) -> tuple[int, ...]:
    # Qiskit displays the highest-index qubit on the left.
    return tuple(int(bit) for bit in reversed(bitstring))


def sample_state_counts(
    state: Statevector,
    qubit_count: int,
    shots: int,
    seed: int,
) -> dict[str, int]:
    probabilities = state.probabilities()
    random_generator = np.random.default_rng(seed)

    sampled_indices = random_generator.choice(
        len(probabilities),
        size=shots,
        p=probabilities,
    )

    unique_indices, sampled_counts = np.unique(
        sampled_indices,
        return_counts=True,
    )

    return {
        format(int(index), f"0{qubit_count}b"): int(count)
        for index, count in zip(unique_indices, sampled_counts)
    }


def solve_qaoa_ideal(
    graph: nx.Graph,
    reps: int = 1,
    shots: int = 1024,
    seed: int = 42,
    maxiter: int = 100,
) -> IdealQAOAResult:
    validate_graph(graph)

    if reps < 1:
        raise ValueError("reps must be at least one.")

    if shots < 1:
        raise ValueError("shots must be at least one.")

    if maxiter < 1:
        raise ValueError("maxiter must be at least one.")

    if seed < 0:
        raise ValueError("seed cannot be negative.")

    if len(graph) == 0:
        raise ValueError("QAOA requires at least one graph node.")

    started = time.perf_counter()
    cost_hamiltonian = build_maxcut_hamiltonian(graph)
    circuit = QAOAAnsatz(
        cost_operator=cost_hamiltonian,
        reps=reps,
    )

    random_generator = np.random.default_rng(seed)
    initial_betas = random_generator.uniform(0, np.pi, reps)
    initial_gammas = random_generator.uniform(0, 2 * np.pi, reps)
    initial_parameters = np.concatenate([
        initial_betas,
        initial_gammas,
    ])

    objective_history = []

    def objective(parameters):
        bound_circuit = circuit.assign_parameters(parameters)
        state = Statevector.from_instruction(bound_circuit)
        expected_cost = state.expectation_value(cost_hamiltonian)
        real_cost = float(np.real(expected_cost))
        objective_history.append(real_cost)
        return real_cost

    optimization_result = minimize(
        objective,
        initial_parameters,
        method="COBYLA",
        options={
            "maxiter": maxiter,
            "rhobeg": 0.5,
        },
    )

    optimized_circuit = circuit.assign_parameters(
        optimization_result.x
    )
    optimized_state = Statevector.from_instruction(optimized_circuit)

    expected_cost = float(
        np.real(
            optimized_state.expectation_value(cost_hamiltonian)
        )
    )

    total_weight = sum(
        float(data.get("weight", 1))
        for _, _, data in graph.edges(data=True)
    )

    # C = sum(w/2) - H, so <C> = sum(w/2) - <H>.
    expected_cut_value = total_weight / 2.0 - expected_cost

    counts = sample_state_counts(
        optimized_state,
        qubit_count=len(graph),
        shots=shots,
        seed=seed + 1,
    )

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

    sampled_mean_cut_value = sampled_total / shots

    return IdealQAOAResult(
        reps=reps,
        shots=shots,
        seed=seed,
        initial_parameters=initial_parameters.tolist(),
        optimal_parameters=optimization_result.x.tolist(),
        expected_cost=expected_cost,
        expected_cut_value=expected_cut_value,
        sampled_mean_cut_value=sampled_mean_cut_value,
        best_sampled_value=best_sampled_value,
        best_sampled_assignment=best_sampled_assignment,
        optimal_sample_probability=None,
        counts=counts,
        objective_history=objective_history,
        optimizer_success=bool(optimization_result.success),
        optimizer_message=str(optimization_result.message),
        circuit_depth=transpiled_circuit_depth(optimized_circuit),
        runtime_seconds=time.perf_counter() - started,
    )