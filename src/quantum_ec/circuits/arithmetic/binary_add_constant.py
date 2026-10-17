"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit.library import MCXGate


def binary_add_constant(width: int, value: int) -> QuantumCircuit:
    """Map |z> to |z + value mod 2**width>; z[0] is the LSB."""
    if not isinstance(width, int) or isinstance(width, bool) or width < 1:
        raise ValueError("width must be a positive integer")
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError("value must be an integer")
    value %= 1 << width
    z = QuantumRegister(width, "z")
    circuit = QuantumCircuit(z, name=f"add_{value}")

    for shift in range(width):
        if ((value >> shift) & 1) == 0:
            continue
        # Increment the suffix starting at shift; inspect carries before flipping it.
        for target in range(width - 1, shift, -1):
            controls = list(z[shift:target])
            if len(controls) == 1:
                circuit.cx(controls[0], z[target])
            else:
                circuit.append(MCXGate(len(controls)), controls + [z[target]])
        circuit.x(z[shift])

    return circuit
