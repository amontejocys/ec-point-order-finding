"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

from qiskit import QuantumCircuit, QuantumRegister
from quantum_ec.circuits.arithmetic.binary_add_constant import binary_add_constant


def less_than_constant(width: int, limit: int) -> QuantumCircuit:
    """Map |x>|t>|0> to |x>|t XOR [x < limit]>|0>.

    Register order is x (LSB first), flag, work (width + 1 clean qubits).
    No primality assumption is needed for this binary comparison.
    """
    if not isinstance(width, int) or isinstance(width, bool) or width < 1:
        raise ValueError("width must be a positive integer")
    if (
        not isinstance(limit, int)
        or isinstance(limit, bool)
        or not 0 <= limit <= (1 << width)
    ):
        raise ValueError("limit must be between 0 and 2**width inclusive")

    x = QuantumRegister(width, "x")
    flag = QuantumRegister(1, "flag")
    work = QuantumRegister(width + 1, "work")
    circuit = QuantumCircuit(x, flag, work, name=f"lt_{limit}")

    for bit in range(width):
        circuit.cx(x[bit], work[bit])

    # This is binary subtraction modulo 2**(width + 1), not modulo limit.
    subtract = binary_add_constant(width + 1, -limit)
    circuit.compose(subtract, qubits=list(work), inplace=True)
    circuit.cx(work[width], flag[0])
    circuit.compose(subtract.inverse(), qubits=list(work), inplace=True)

    for bit in reversed(range(width)):
        circuit.cx(x[bit], work[bit])

    return circuit
