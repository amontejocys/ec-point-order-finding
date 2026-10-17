"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

from qiskit import QuantumCircuit, QuantumRegister
from quantum_ec.circuits.arithmetic.modular_multiply_accumulate import modular_multiply_accumulate
from quantum_ec.circuits.arithmetic.modular_square_accumulate import modular_square_accumulate


def modular_cube_accumulate(width: int, modulus: int) -> QuantumCircuit:
    """Map (x, t) to (x, (t+x**3) % modulus) for t < modulus.

    Invalid t encodings are fixed. Register order: x, t, square,
    carry, valid, reduce, work. All auxiliary registers, including square,
    must start at zero and are returned to zero.
    """
    square_block = modular_square_accumulate(width, modulus)
    multiply_block = modular_multiply_accumulate(width, modulus)
    x = QuantumRegister(width, "x")
    t = QuantumRegister(width, "t")
    square = QuantumRegister(width, "square")
    carry = QuantumRegister(1, "carry")
    valid = QuantumRegister(1, "valid")
    reduce = QuantumRegister(1, "reduce")
    work = QuantumRegister(width + 2, "work")
    circuit = QuantumCircuit(x, t, square, carry, valid, reduce, work, name=f"cube_acc_mod_{modulus}")
    auxiliaries = list(carry) + list(valid) + list(reduce) + list(work)
    square_qubits = list(x) + list(square) + auxiliaries
    multiply_qubits = list(x) + list(square) + list(t) + auxiliaries

    circuit.compose(square_block, square_qubits, inplace=True)
    circuit.compose(multiply_block, multiply_qubits, inplace=True)
    circuit.compose(square_block.inverse(), square_qubits, inplace=True)
    return circuit
