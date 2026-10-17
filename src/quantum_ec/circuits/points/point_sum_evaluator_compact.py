"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit.library import MCXGate
from quantum_ec.circuits.arithmetic.equality_constant import equality_constant
from quantum_ec.circuits.points.ordinary_point_sum_shared import ordinary_point_sum_shared
from quantum_ec.circuits.points.point_addition_cases import point_addition_cases


def point_sum_evaluator_compact(width: int, modulus: int, a: int, b: int, u: int, v: int) -> QuantumCircuit:
    """Same clean total XOR contract as point_sum_evaluator.

    Input and output point encodings precede scratch. All scratch starts and
    ends at zero; arbitrary outputs are supported. Valid R maps to R+A and
    invalid encodings are copied unchanged. Modulus is assumed prime >3.
    Case and ordinary scratch share a pool because their lifetimes do not
    overlap; branch flags stay separate and live until final uncomputation.
    """
    cases = point_addition_cases(width, modulus, a, b, u, v)
    ordinary = ordinary_point_sum_shared(width, modulus, u, v, inverse_variant="compact")
    identity = QuantumRegister(1, "identity")
    x = QuantumRegister(width, "x")
    y = QuantumRegister(width, "y")
    out_identity = QuantumRegister(1, "out_identity")
    out_x = QuantumRegister(width, "out_x")
    out_y = QuantumRegister(width, "out_y")
    branches = QuantumRegister(4, "branches")
    case_width = cases.num_qubits - (2 * width + 1) - 4
    ordinary_width = ordinary.num_qubits - 4 * width
    work = QuantumRegister(max(case_width, ordinary_width), "shared_work")
    invalid = QuantumRegister(1, "invalid")
    circuit = QuantumCircuit(identity, x, y, out_identity, out_x, out_y, branches, work, invalid, name="point_sum_evaluator_compact")
    encoding = list(identity) + list(x) + list(y)
    output = list(out_identity) + list(out_x) + list(out_y)
    case_qubits = encoding + list(branches) + list(work[:case_width])
    circuit.compose(cases, case_qubits, inplace=True)

    a_encoding = (u << 1) | (v << (width + 1))
    if v == 0:
        double_encoding = 1
    else:
        slope = (3*u*u+a)*pow((2*v) % modulus, -1, modulus) % modulus
        double_x = (slope*slope-2*u) % modulus
        double_y = (slope*(u-double_x)-v) % modulus
        double_encoding = (double_x << 1) | (double_y << (width + 1))
    for branch, value in ((0, a_encoding), (1, 1), (2, double_encoding)):
        for bit, destination in enumerate(output):
            if (value >> bit) & 1:
                circuit.cx(branches[branch], destination)

    ordinary_qubits = list(x) + list(y) + list(out_x) + list(out_y) + list(work[:ordinary_width])
    for instruction in ordinary.data:
        if instruction.operation.name not in ("x", "cx", "ccx", "mcx"):
            raise ValueError("Unexpected gate in the shared ordinary evaluator")
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
    circuit.metadata = {
        "variant": "shared_selectors_and_compact_inverse",
        "case_scratch_width": case_width,
        "ordinary_scratch_width": ordinary_width,
        "scratch_saved_by_pooling": min(case_width, ordinary_width),
    }
    return circuit
