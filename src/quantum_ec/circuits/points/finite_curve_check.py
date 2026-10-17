"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit.library import MCXGate
from quantum_ec.circuits.points.curve_residual_accumulate import curve_residual_accumulate
from quantum_ec.circuits.arithmetic.equality_constant import equality_constant
from quantum_ec.circuits.arithmetic.less_than_constant import less_than_constant


def finite_curve_check(width: int, modulus: int, a: int, b: int) -> QuantumCircuit:
    """XOR [x<p and y<p and y*y-x**3-a*x-b == 0 mod p] into flag.

    Preserve x and y; all other registers except flag must start and end
    at zero. This tests finite coordinates only, not the identity encoding.
    It does not certify primality or curve nonsingularity.
    """
    residual_block = curve_residual_accumulate(width, modulus, a, b)
    x = QuantumRegister(width, "x")
    y = QuantumRegister(width, "y")
    flag = QuantumRegister(1, "flag")
    residual = QuantumRegister(width, "residual")
    square = QuantumRegister(width, "square")
    predicates = QuantumRegister(3, "predicates")
    carry = QuantumRegister(1, "carry")
    valid = QuantumRegister(1, "valid")
    reduce = QuantumRegister(1, "reduce")
    work = QuantumRegister(width + 2, "work")
    circuit = QuantumCircuit(x, y, flag, residual, square, predicates, carry, valid, reduce, work, name="finite_curve_check")
    aux = list(carry) + list(valid) + list(reduce) + list(work)
    residual_qubits = list(x) + list(y) + list(residual) + list(square) + aux
    range_check = less_than_constant(width, modulus)
    x_check_qubits = list(x) + [predicates[0]] + list(work[:width + 1])
    y_check_qubits = list(y) + [predicates[1]] + list(work[:width + 1])
    zero_check = equality_constant(width, 0)
    zero_check_qubits = list(residual) + [predicates[2]]

    circuit.compose(range_check, x_check_qubits, inplace=True)
    circuit.compose(range_check, y_check_qubits, inplace=True)
    circuit.compose(residual_block, residual_qubits, inplace=True)
    circuit.compose(zero_check, zero_check_qubits, inplace=True)
    circuit.append(MCXGate(3), list(predicates) + list(flag))
    circuit.compose(zero_check.inverse(), zero_check_qubits, inplace=True)
    circuit.compose(residual_block.inverse(), residual_qubits, inplace=True)
    circuit.compose(range_check.inverse(), y_check_qubits, inplace=True)
    circuit.compose(range_check.inverse(), x_check_qubits, inplace=True)
    return circuit
