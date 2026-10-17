"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit.library import MCXGate
from quantum_ec.circuits.arithmetic.equality_constant import equality_constant
from quantum_ec.circuits.points.ordinary_point_sum import ordinary_point_sum
from quantum_ec.circuits.points.point_addition_cases import point_addition_cases
from quantum_ec.circuits.points.special_point_sum import special_point_sum


def point_sum_evaluator(width: int, modulus: int, a: int, b: int, u: int, v: int) -> QuantumCircuit:
    """Preserve z and XOR H_A(z) into output, cleaning zeroed scratch.

    H_A encodes R+A for valid z=enc(R), and is z for invalid encodings.
    A must be a finite curve point; modulus is assumed prime >3. Register
    order starts identity,x,y,out_identity,out_x,out_y. Output may be arbitrary.
    This is an evaluator, not an in-place point update or external control.
    """
    cases = point_addition_cases(width, modulus, a, b, u, v)
    special = special_point_sum(width, modulus, a, b, u, v)
    ordinary = ordinary_point_sum(width, modulus, u, v)
    identity = QuantumRegister(1, "identity")
    x = QuantumRegister(width, "x")
    y = QuantumRegister(width, "y")
    out_identity = QuantumRegister(1, "out_identity")
    out_x = QuantumRegister(width, "out_x")
    out_y = QuantumRegister(width, "out_y")
    branches = QuantumRegister(4, "branches")
    case_work = QuantumRegister(cases.num_qubits - (2 * width + 1) - 4, "case_work")
    ordinary_work = QuantumRegister(ordinary.num_qubits - 4 * width, "ordinary_work")
    invalid = QuantumRegister(1, "invalid")
    circuit = QuantumCircuit(identity, x, y, out_identity, out_x, out_y, branches, case_work, ordinary_work, invalid, name="point_sum_evaluator")
    encoding = list(identity) + list(x) + list(y)
    output = list(out_identity) + list(out_x) + list(out_y)
    case_qubits = encoding + list(branches) + list(case_work)

    circuit.compose(special, encoding + output + list(branches) + list(case_work), inplace=True)
    circuit.compose(cases, case_qubits, inplace=True)
    ordinary_qubits = list(x) + list(y) + list(out_x) + list(out_y) + list(ordinary_work)
    for instruction in ordinary.data:
        if instruction.operation.name not in ("x", "cx", "ccx", "mcx"):
            raise ValueError("Unexpected gate in the reference ordinary evaluator")
        mapped = [ordinary_qubits[ordinary.find_bit(q).index] for q in instruction.qubits]
        if len(mapped) == 1:
            circuit.cx(branches[3], mapped[0])
        else:
            circuit.append(MCXGate(len(mapped)), [branches[3]] + mapped)

    zero_branches = equality_constant(4, 0)
    circuit.compose(zero_branches, list(branches) + list(invalid), inplace=True)
    for source, destination in zip(encoding, output):
        circuit.ccx(invalid[0], source, destination)
    circuit.compose(zero_branches.inverse(), list(branches) + list(invalid), inplace=True)
    circuit.compose(cases.inverse(), case_qubits, inplace=True)
    return circuit
