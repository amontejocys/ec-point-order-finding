"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit.library import MCXGate


def equality_constant(width: int, value: int) -> QuantumCircuit:
    """Map |z>|t> to |z>|t XOR [z == value]>; z[0] is the LSB."""
    if not isinstance(width, int) or isinstance(width, bool) or width < 1:
        raise ValueError("width must be a positive integer")
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or not 0 <= value < (1 << width)
    ):
        raise ValueError("value must be an integer that fits in width bits")

    z = QuantumRegister(width, "z")
    flag = QuantumRegister(1, "flag")
    circuit = QuantumCircuit(z, flag, name=f"eq_{value}")
    zero_bits = [bit for bit in range(width) if ((value >> bit) & 1) == 0]

    # Turn equality with value into an all-ones control pattern.
    for bit in zero_bits:
        circuit.x(z[bit])

    if width == 1:
        circuit.cx(z[0], flag[0])
    else:
        circuit.append(MCXGate(width), list(z) + [flag[0]])

    for bit in reversed(zero_bits):
        circuit.x(z[bit])

    return circuit
