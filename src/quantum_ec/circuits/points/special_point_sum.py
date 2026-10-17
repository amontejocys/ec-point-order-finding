"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

from qiskit import QuantumCircuit, QuantumRegister
from quantum_ec.circuits.points.point_addition_cases import point_addition_cases


def special_point_sum(width: int, modulus: int, a: int, b: int, u: int, v: int) -> QuantumCircuit:
    """XOR A, O, or 2A into output for identity, opposite, or doubling.

    Ordinary and invalid inputs leave output unchanged; this is NOT a
    complete point-sum evaluator. Input and output order: identity,x,y,
    out_identity,out_x,out_y, followed by zero-initialized scratch, which
    returns to zero. A is a fixed finite point and modulus is assumed prime.
    """
    cases = point_addition_cases(width, modulus, a, b, u, v)
    identity = QuantumRegister(1, "identity")
    x = QuantumRegister(width, "x")
    y = QuantumRegister(width, "y")
    out_identity = QuantumRegister(1, "out_identity")
    out_x = QuantumRegister(width, "out_x")
    out_y = QuantumRegister(width, "out_y")
    branches = QuantumRegister(4, "branches")
    work = QuantumRegister(cases.num_qubits - (2 * width + 1) - 4, "case_work")
    circuit = QuantumCircuit(identity, x, y, out_identity, out_x, out_y, branches, work, name="special_point_sum")
    case_qubits = list(identity) + list(x) + list(y) + list(branches) + list(work)
    circuit.compose(cases, case_qubits, inplace=True)

    a_encoding = (u << 1) | (v << (width + 1))
    if v == 0:
        double_encoding = 1
    else:
        slope = (3*u*u + a) * pow((2*v) % modulus, -1, modulus) % modulus
        double_x = (slope*slope - 2*u) % modulus
        double_y = (slope*(u-double_x) - v) % modulus
        double_encoding = (double_x << 1) | (double_y << (width + 1))
    output = list(out_identity) + list(out_x) + list(out_y)
    for branch, value in ((0, a_encoding), (1, 1), (2, double_encoding)):
        for bit, target in enumerate(output):
            if (value >> bit) & 1:
                circuit.cx(branches[branch], target)
    circuit.compose(cases.inverse(), case_qubits, inplace=True)
    return circuit
