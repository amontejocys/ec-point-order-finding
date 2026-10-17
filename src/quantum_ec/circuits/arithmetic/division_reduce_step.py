"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit.library import MCXGate
from quantum_ec.circuits.arithmetic.binary_add_constant import binary_add_constant
from quantum_ec.circuits.arithmetic.less_than_register import less_than_register


def division_reduce_step(width: int) -> QuantumCircuit:
    """Map (C,B,0,0) to (C-q*B,B,q,0), where q=[C>=B].

    Register order: candidate, divisor, quotient_bit, work. quotient_bit
    and work must start at zero. B must be positive for division semantics.
    The result is a remainder only if C < 2*B. B=0 mechanically produces
    q=1 and leaves C unchanged; a complete divider must guard that case.
    """
    comparator = less_than_register(width)
    candidate = QuantumRegister(width, "candidate")
    divisor = QuantumRegister(width, "divisor")
    quotient_bit = QuantumRegister(1, "quotient_bit")
    work = QuantumRegister(width + 1, "work")
    circuit = QuantumCircuit(candidate, divisor, quotient_bit, work, name="division_reduce_step")
    circuit.compose(comparator, list(candidate) + list(divisor) + list(quotient_bit) + list(work), inplace=True)
    circuit.x(quotient_bit[0])

    for bit in range(width):
        adder = binary_add_constant(width, -(1 << bit))
        for instruction in adder.data:
            if instruction.operation.name not in ("x", "cx", "ccx", "mcx"):
                raise ValueError("Unexpected gate in the reference binary adder")
            mapped = [candidate[adder.find_bit(q).index] for q in instruction.qubits]
            controls = [quotient_bit[0], divisor[bit]]
            circuit.append(MCXGate(len(mapped) + 1), controls + mapped)
    return circuit
