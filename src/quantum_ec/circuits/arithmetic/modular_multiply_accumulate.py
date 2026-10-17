"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit.library import MCXGate
from quantum_ec.circuits.arithmetic.modular_add_constant import modular_add_constant


def modular_multiply_accumulate(width: int, modulus: int) -> QuantumCircuit:
    """Map (x, y, t) to (x, y, (t+x*y) % modulus) for t < modulus.

    Invalid t encodings are fixed. x and y may be any width-bit integers.
    Register order: x, y, t, carry, valid, reduce, work. All auxiliaries
    must start at zero and are returned to zero.
    """
    modular_add_constant(width, modulus, 0)
    x = QuantumRegister(width, "x")
    y = QuantumRegister(width, "y")
    t = QuantumRegister(width, "t")
    carry = QuantumRegister(1, "carry")
    valid = QuantumRegister(1, "valid")
    reduce = QuantumRegister(1, "reduce")
    work = QuantumRegister(width + 2, "work")
    circuit = QuantumCircuit(x, y, t, carry, valid, reduce, work, name=f"mul_acc_mod_{modulus}")
    targets = list(t) + list(carry) + list(valid) + list(reduce) + list(work)

    for i in range(width):
        for j in range(width):
            value = (1 << (i + j)) % modulus
            if value == 0:
                continue
            adder = modular_add_constant(width, modulus, value)
            # Both operand bits control every operation, including cleanup.
            for instruction in adder.data:
                if instruction.operation.name not in ("x", "cx", "ccx", "mcx"):
                    raise ValueError("Unexpected gate in the reference modular adder")
                mapped = [targets[adder.find_bit(q).index] for q in instruction.qubits]
                circuit.append(MCXGate(len(mapped) + 1), [x[i], y[j]] + mapped)
    return circuit
