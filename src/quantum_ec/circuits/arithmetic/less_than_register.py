"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit.library import MCXGate
from quantum_ec.circuits.arithmetic.binary_add_constant import binary_add_constant


def less_than_register(width: int) -> QuantumCircuit:
    """Map (A, B, flag, 0) to (A, B, flag XOR [A<B], 0).

    Register order: A, B, flag, work. A and B are unsigned width-bit
    integers; work has width+1 bits. No field modulus is involved.
    """
    if not isinstance(width, int) or isinstance(width, bool) or width < 1:
        raise ValueError("width must be a positive integer")
    a = QuantumRegister(width, "A")
    b = QuantumRegister(width, "B")
    flag = QuantumRegister(1, "flag")
    work = QuantumRegister(width + 1, "work")
    circuit = QuantumCircuit(a, b, flag, work, name="less_than_register")

    source = QuantumRegister(width, "source")
    target = QuantumRegister(width + 1, "target")
    subtract = QuantumCircuit(source, target, name="subtract_register")
    # Subtract B through its binary expansion; each source bit is a control.
    for bit in range(width):
        adder = binary_add_constant(width + 1, -(1 << bit))
        for instruction in adder.data:
            if instruction.operation.name not in ("x", "cx", "ccx", "mcx"):
                raise ValueError("Unexpected gate in the reference binary adder")
            mapped = [target[adder.find_bit(q).index] for q in instruction.qubits]
            if len(mapped) == 1:
                subtract.cx(source[bit], mapped[0])
            else:
                subtract.append(MCXGate(len(mapped)), [source[bit]] + mapped)

    for bit in range(width):
        circuit.cx(a[bit], work[bit])
    subtraction_qubits = list(b) + list(work)
    circuit.compose(subtract, subtraction_qubits, inplace=True)
    circuit.cx(work[width], flag[0])
    circuit.compose(subtract.inverse(), subtraction_qubits, inplace=True)
    for bit in reversed(range(width)):
        circuit.cx(a[bit], work[bit])
    return circuit
