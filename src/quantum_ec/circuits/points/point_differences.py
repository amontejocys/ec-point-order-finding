"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

from qiskit import QuantumCircuit, QuantumRegister
from quantum_ec.circuits.arithmetic.modular_add_constant import modular_add_constant


def point_differences(width: int, modulus: int, u: int, v: int) -> QuantumCircuit:
    """XOR T_-u(x) and T_-v(y) into D and N; preserve coordinates.

    For canonical coordinates these are (x-u)%p and (y-v)%p. As a total
    extension, each out-of-range coordinate is copied unchanged to its
    difference output. Outputs may be arbitrary; all scratch starts and
    ends at zero. Register order: x,y,D,N,dx,ny,arithmetic_work.
    This block does not certify curve membership or a nonzero denominator.
    """
    validation = modular_add_constant(width, modulus, 0)
    for coordinate in (u, v):
        if not isinstance(coordinate, int) or isinstance(coordinate, bool) or not 0 <= coordinate < modulus:
            raise ValueError("constant coordinates must be canonical residues")
    subtract_u = modular_add_constant(width, modulus, -u)
    subtract_v = modular_add_constant(width, modulus, -v)
    x = QuantumRegister(width, "x")
    y = QuantumRegister(width, "y")
    d = QuantumRegister(width, "D")
    n = QuantumRegister(width, "N")
    dx = QuantumRegister(width, "dx")
    ny = QuantumRegister(width, "ny")
    arithmetic_work = QuantumRegister(validation.num_qubits - width, "arithmetic_work")
    compute = QuantumCircuit(x, y, dx, ny, arithmetic_work, name="difference_work")
    for bit in range(width):
        compute.cx(x[bit], dx[bit])
        compute.cx(y[bit], ny[bit])
    compute.compose(subtract_u, list(dx) + list(arithmetic_work), inplace=True)
    compute.compose(subtract_v, list(ny) + list(arithmetic_work), inplace=True)

    circuit = QuantumCircuit(x, y, d, n, dx, ny, arithmetic_work, name="point_differences")
    circuit.compose(compute, list(compute.qubits), inplace=True)
    for bit in range(width):
        circuit.cx(dx[bit], d[bit])
        circuit.cx(ny[bit], n[bit])
    circuit.compose(compute.inverse(), list(compute.qubits), inplace=True)
    return circuit
