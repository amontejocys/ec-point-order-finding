"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit.library import MCXGate
from quantum_ec.circuits.arithmetic.modular_add_constant import modular_add_constant


def modular_add_register(width: int, modulus: int) -> QuantumCircuit:
    """Map (x, y) to ((x+y) % modulus, y) for x < modulus.

    Invalid x encodings are fixed; y can be any width-bit integer.
    Register order: x, y, carry, valid, reduce, work. All auxiliaries
    must start at zero and are returned to zero.
    """
    # Reuse the constant block's parameter validation.
    modular_add_constant(width, modulus, 0)
    x = QuantumRegister(width, "x")
    y = QuantumRegister(width, "y")
    carry = QuantumRegister(1, "carry")
    valid = QuantumRegister(1, "valid")
    reduce = QuantumRegister(1, "reduce")
    work = QuantumRegister(width + 2, "work")
    circuit = QuantumCircuit(x, y, carry, valid, reduce, work, name=f"add_register_mod_{modulus}")
    targets = list(x) + list(carry) + list(valid) + list(reduce) + list(work)

    for bit in range(width):
        value = (1 << bit) % modulus
        if value == 0:
            continue
        adder = modular_add_constant(width, modulus, value)
        # Control every X-family instruction, including the cleanup steps.
        for instruction in adder.data:
            if instruction.operation.name not in ("x", "cx", "ccx", "mcx"):
                raise ValueError("Unexpected gate in the reference modular adder")
            mapped = [targets[adder.find_bit(q).index] for q in instruction.qubits]
            if len(mapped) == 1:
                circuit.cx(y[bit], mapped[0])
            else:
                circuit.append(MCXGate(len(mapped)), [y[bit]] + mapped)
    return circuit
