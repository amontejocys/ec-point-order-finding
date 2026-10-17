"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

from qiskit import QuantumCircuit, QuantumRegister
from quantum_ec.circuits.arithmetic.modular_inverse import modular_inverse
from quantum_ec.circuits.arithmetic.modular_multiply_accumulate import modular_multiply_accumulate
from quantum_ec.circuits.points.point_differences import point_differences


def ordinary_point_slope(width: int, modulus: int, u: int, v: int) -> QuantumCircuit:
    """XOR N*inverse(D) modulo p into L, preserving x and y.

    For canonical inputs D=(x-u)%p and N=(y-v)%p. A geometric slope
    requires valid finite points and a nonzero invertible D. If D has no
    inverse, the reference inverse yields zero and so does this evaluator;
    that extension is not a valid slope. All scratch starts and ends at zero.
    Register order begins x,y,L. No geometric branch selection is performed.
    """
    differences = point_differences(width, modulus, u, v)
    inverse = modular_inverse(width, modulus)
    multiply = modular_multiply_accumulate(width, modulus)
    x = QuantumRegister(width, "x")
    y = QuantumRegister(width, "y")
    output = QuantumRegister(width, "L")
    d = QuantumRegister(width, "D")
    n = QuantumRegister(width, "N")
    i = QuantumRegister(width, "I")
    slope = QuantumRegister(width, "slope_work")
    differences_work = QuantumRegister(differences.num_qubits - 4 * width, "differences_work")
    inverse_work = QuantumRegister(inverse.num_qubits - 2 * width, "inverse_work")
    multiply_work = QuantumRegister(multiply.num_qubits - 3 * width, "multiply_work")
    compute = QuantumCircuit(x, y, d, n, i, slope, differences_work, inverse_work, multiply_work, name="slope_compute")
    compute.compose(differences, list(x) + list(y) + list(d) + list(n) + list(differences_work), inplace=True)
    compute.compose(inverse, list(d) + list(i) + list(inverse_work), inplace=True)
    compute.compose(multiply, list(n) + list(i) + list(slope) + list(multiply_work), inplace=True)

    circuit = QuantumCircuit(x, y, output, d, n, i, slope, differences_work, inverse_work, multiply_work, name="ordinary_point_slope")
    circuit.compose(compute, list(compute.qubits), inplace=True)
    for bit in range(width):
        circuit.cx(slope[bit], output[bit])
    circuit.compose(compute.inverse(), list(compute.qubits), inplace=True)
    return circuit
