"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

from qiskit import QuantumCircuit, QuantumRegister
from quantum_ec.circuits.points.point_sum_evaluator import point_sum_evaluator
from quantum_ec.circuits.points.point_sum_evaluator_compact import point_sum_evaluator_compact


def point_add_inplace(width: int, modulus: int, a: int, b: int, u: int, v: int, *, evaluator_variant: str = "reference") -> QuantumCircuit:
    """Map z to H_A(z), returning all zero-initialized work to zero.

    H_A adds A to valid point encodings and fixes invalid encodings.
    Register order: identity,x,y,point_work,evaluator_work. A is finite;
    modulus is assumed prime >3, as in the underlying evaluator. The
    reference remains the default; compact selects the optimized evaluator.
    """
    if evaluator_variant not in ("reference", "compact"):
        raise ValueError("evaluator_variant must be reference or compact")
    evaluator = point_sum_evaluator_compact if evaluator_variant == "compact" else point_sum_evaluator
    forward = evaluator(width, modulus, a, b, u, v)
    backward = evaluator(width, modulus, a, b, u, (-v) % modulus)
    size = 2 * width + 1
    forward_scratch = forward.num_qubits - 2 * size
    backward_scratch = backward.num_qubits - 2 * size
    identity = QuantumRegister(1, "identity")
    x = QuantumRegister(width, "x")
    y = QuantumRegister(width, "y")
    point_work = QuantumRegister(size, "point_work")
    evaluator_work = QuantumRegister(max(forward_scratch, backward_scratch), "evaluator_work")
    circuit = QuantumCircuit(identity, x, y, point_work, evaluator_work, name="point_add_inplace")
    point = list(identity) + list(x) + list(y)
    circuit.compose(forward, point + list(point_work) + list(evaluator_work[:forward_scratch]), inplace=True)
    for source, destination in zip(point, point_work):
        circuit.swap(source, destination)
    # Evaluate subtraction on the new point to erase the old-point work.
    circuit.compose(backward, point + list(point_work) + list(evaluator_work[:backward_scratch]), inplace=True)
    circuit.metadata = {"evaluator_variant": evaluator_variant}
    return circuit
