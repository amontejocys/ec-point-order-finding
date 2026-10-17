"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit.library import MCXGate
from quantum_ec.circuits.arithmetic.equality_constant import equality_constant
from quantum_ec.circuits.points.point_encoding_check import point_encoding_check


def point_addition_cases(width: int, modulus: int, a: int, b: int, u: int, v: int) -> QuantumCircuit:
    """XOR four case predicates into branches; preserve the point encoding.

    Branch order: identity, opposite, doubling, ordinary. Zero-initialized
    branches are one-hot for valid points and all zero for invalid encodings.
    A=(u,v) must be a canonical finite curve point; modulus is assumed prime
    >3. Other scratch starts and ends at zero. Input order: identity,x,y,
    branches, predicates, validation_work. Coincident opposite/doubling
    predicates for order-two A are assigned to opposite, yielding identity.
    """
    validation = point_encoding_check(width, modulus, a, b)
    if modulus <= 3:
        raise ValueError("short-Weierstrass branch selection requires a prime greater than 3")
    for coordinate in (u, v):
        if not isinstance(coordinate, int) or isinstance(coordinate, bool) or not 0 <= coordinate < modulus:
            raise ValueError("constant coordinates must be canonical residues")
    if (v*v-u**3-a*u-b) % modulus:
        raise ValueError("constant point must satisfy the curve equation")
    if (4*a**3 + 27*b*b) % modulus == 0:
        raise ValueError("curve must be nonsingular")
    identity = QuantumRegister(1, "identity")
    x = QuantumRegister(width, "x")
    y = QuantumRegister(width, "y")
    branches = QuantumRegister(4, "branches")
    predicates = QuantumRegister(4, "predicates")
    validation_work = QuantumRegister(validation.num_qubits - (2 * width + 2), "validation_work")
    encoding = list(identity) + list(x) + list(y)
    compute = QuantumCircuit(identity, x, y, predicates, validation_work, name="case_predicates")
    compute.compose(validation, encoding + [predicates[0]] + list(validation_work), inplace=True)
    values = (1, (u << 1) | (v << (width + 1)), (u << 1) | (((-v) % modulus) << (width + 1)))
    for index, value in enumerate(values, start=1):
        compute.compose(equality_constant(2 * width + 1, value), encoding + [predicates[index]], inplace=True)

    circuit = QuantumCircuit(identity, x, y, branches, predicates, validation_work, name="point_addition_cases")
    circuit.compose(compute, list(compute.qubits), inplace=True)
    valid, is_identity, is_a, is_negative_a = predicates
    circuit.ccx(valid, is_identity, branches[0])
    circuit.ccx(valid, is_negative_a, branches[1])
    circuit.x(is_negative_a)
    circuit.append(MCXGate(3), [valid, is_a, is_negative_a, branches[2]])
    circuit.x(is_negative_a)
    negatives = [is_identity, is_a, is_negative_a]
    for bit in negatives:
        circuit.x(bit)
    circuit.append(MCXGate(4), [valid] + negatives + [branches[3]])
    for bit in reversed(negatives):
        circuit.x(bit)
    circuit.compose(compute.inverse(), list(compute.qubits), inplace=True)
    return circuit
