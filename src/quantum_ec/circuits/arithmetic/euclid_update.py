"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

from qiskit import QuantumCircuit, QuantumRegister
from quantum_ec.circuits.arithmetic.binary_divide import binary_divide
from quantum_ec.circuits.arithmetic.modular_multiply_accumulate import modular_multiply_accumulate


def euclid_update(width: int, modulus: int) -> QuantumCircuit:
    """Compute q, remainder, and (c0-q*c1) % modulus in clean outputs.

    Input order: r0, r1, c0, c1. Output order: q, remainder, coefficient.
    Outputs and scratch must start at zero. Inputs are preserved; scratch
    returns to zero. c0,c1 must be canonical residues. For r1=0 the divider
    convention gives q=0, remainder=r0, coefficient=c0. The full Euclidean
    loop must freeze its state rather than advance that terminal branch.
    No primality assertion is made by this arithmetic block.
    """
    multiply = modular_multiply_accumulate(width, modulus)
    if modulus == (1 << width):
        raise ValueError("modulus itself must fit in the remainder input register")
    divide = binary_divide(width)
    r0 = QuantumRegister(width, "r0")
    r1 = QuantumRegister(width, "r1")
    c0 = QuantumRegister(width, "c0")
    c1 = QuantumRegister(width, "c1")
    quotient = QuantumRegister(width, "quotient")
    remainder = QuantumRegister(width, "remainder")
    coefficient = QuantumRegister(width, "coefficient")
    division_work = QuantumRegister(divide.num_qubits - 4 * width, "division_work")
    multiplication_work = QuantumRegister(multiply.num_qubits - 3 * width, "multiplication_work")
    circuit = QuantumCircuit(r0, r1, c0, c1, quotient, remainder, coefficient, division_work, multiplication_work, name="euclid_update")

    divide_qubits = list(r0) + list(r1) + list(quotient) + list(remainder) + list(division_work)
    circuit.compose(divide, divide_qubits, inplace=True)
    for bit in range(width):
        circuit.cx(c0[bit], coefficient[bit])
    multiply_qubits = list(quotient) + list(c1) + list(coefficient) + list(multiplication_work)
    circuit.compose(multiply.inverse(), multiply_qubits, inplace=True)
    return circuit
