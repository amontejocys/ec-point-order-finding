"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit.library import MCXGate
from quantum_ec.circuits.points.finite_curve_check import finite_curve_check


def point_encoding_check(width: int, modulus: int, a: int, b: int) -> QuantumCircuit:
    """XOR validity of (identity, x, y) into flag and clean scratch.

    Valid encodings are (0,x,y) with finite coordinates on the curve,
    and the single identity encoding (1,0,0). Register order is identity,
    x, y, flag, finite, scratch. finite and scratch start and end at zero.
    This checks encodings, not primality or curve nonsingularity.
    """
    finite_block = finite_curve_check(width, modulus, a, b)
    identity = QuantumRegister(1, "identity")
    x = QuantumRegister(width, "x")
    y = QuantumRegister(width, "y")
    flag = QuantumRegister(1, "flag")
    finite = QuantumRegister(1, "finite")
    scratch = QuantumRegister(finite_block.num_qubits - 2 * width - 1, "scratch")
    circuit = QuantumCircuit(identity, x, y, flag, finite, scratch, name="point_encoding_check")
    finite_qubits = list(x) + list(y) + list(finite) + list(scratch)

    circuit.compose(finite_block, finite_qubits, inplace=True)
    circuit.x(identity[0])
    circuit.ccx(identity[0], finite[0], flag[0])
    circuit.x(identity[0])
    circuit.compose(finite_block.inverse(), finite_qubits, inplace=True)

    # Identity requires its bit to be one and every coordinate bit zero.
    coordinates = list(x) + list(y)
    for bit in coordinates:
        circuit.x(bit)
    circuit.append(MCXGate(2 * width + 1), list(identity) + coordinates + list(flag))
    for bit in reversed(coordinates):
        circuit.x(bit)
    return circuit
