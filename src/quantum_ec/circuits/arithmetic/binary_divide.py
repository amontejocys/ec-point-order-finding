"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit.library import MCXGate
from quantum_ec.circuits.arithmetic.division_reduce_step import division_reduce_step
from quantum_ec.circuits.arithmetic.equality_constant import equality_constant


def binary_divide(width: int) -> QuantumCircuit:
    """XOR quotient and remainder into outputs, preserving A and B.

    B>0: quotient=A//B, remainder=A%B. B=0: quotient=0, remainder=A.
    Register order starts A, B, quotient_out, remainder_out, followed by
    zero-initialized scratch. Outputs may have arbitrary initial values.
    All scratch returns to zero. This history-heavy circuit is not optimized.
    """
    step = division_reduce_step(width + 1)
    zero_check = equality_constant(width, 0)
    a = QuantumRegister(width, "A")
    b = QuantumRegister(width, "B")
    quotient_out = QuantumRegister(width, "quotient_out")
    remainder_out = QuantumRegister(width, "remainder_out")
    quotient = QuantumRegister(width, "quotient_history")
    stages = [QuantumRegister(width + 1, f"remainder_{i}") for i in range(width)]
    enabled = QuantumRegister(1, "enabled")
    padding = QuantumRegister(1, "divisor_padding")
    work = QuantumRegister(width + 2, "work")
    compute = QuantumCircuit(a, b, quotient, *stages, enabled, padding, work, name="division_history")
    compute.compose(zero_check, list(b) + list(enabled), inplace=True)
    compute.x(enabled[0])

    for stage_index, bit in enumerate(reversed(range(width))):
        candidate = stages[stage_index]
        if stage_index:
            previous = stages[stage_index - 1]
            # Reachable remainders have a zero top bit; retain previous intact.
            for position in range(width):
                compute.cx(previous[position], candidate[position + 1])
        compute.cx(a[bit], candidate[0])
        targets = list(candidate) + list(b) + list(padding) + [quotient[bit]] + list(work)
        for instruction in step.data:
            if instruction.operation.name not in ("x", "cx", "ccx", "mcx"):
                raise ValueError("Unexpected gate in the reference division step")
            mapped = [targets[step.find_bit(q).index] for q in instruction.qubits]
            if len(mapped) == 1:
                compute.cx(enabled[0], mapped[0])
            else:
                compute.append(MCXGate(len(mapped)), list(enabled) + mapped)

    circuit = QuantumCircuit(a, b, quotient_out, remainder_out, quotient, *stages, enabled, padding, work, name="binary_divide")
    compute_qubits = list(compute.qubits)
    circuit.compose(compute, compute_qubits, inplace=True)
    for bit in range(width):
        circuit.cx(quotient[bit], quotient_out[bit])
        circuit.cx(stages[-1][bit], remainder_out[bit])
    circuit.compose(compute.inverse(), compute_qubits, inplace=True)
    return circuit
