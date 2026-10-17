"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

from qiskit import QuantumCircuit, QuantumRegister
from quantum_ec.circuits.arithmetic.binary_divide import binary_divide


def binary_quotient(width: int) -> QuantumCircuit:
    """XOR A//B into quotient, or zero for B=0; preserve inputs and clean work."""
    divider = binary_divide(width)
    discarded = set(divider.qregs[3])
    a = QuantumRegister(width, "A")
    b = QuantumRegister(width, "B")
    quotient = QuantumRegister(width, "quotient")
    work = QuantumRegister(divider.num_qubits - 4 * width, "work")
    circuit = QuantumCircuit(a, b, quotient, work, name="binary_quotient")
    kept = [q for q in divider.qubits if q not in discarded]
    mapping = dict(zip(kept, circuit.qubits))
    for instruction in divider.data:
        if any(q in discarded for q in instruction.qubits):
            # The remainder output participates only in its final CNOT transfer.
            if instruction.operation.name != "cx" or instruction.qubits[-1] not in discarded or instruction.qubits[0] in discarded:
                raise ValueError("Remainder output is not independent of divider work")
            continue
        circuit.append(instruction.operation, [mapping[q] for q in instruction.qubits])
    return circuit
