"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit.library import MCXGate
from quantum_ec.circuits.arithmetic.modular_add_constant import modular_add_constant


def modular_square_accumulate(width: int, modulus: int) -> QuantumCircuit:
    """Map (x, t) to (x, (t+x*x) % modulus) for t < modulus.

    Invalid t encodings are fixed. x may be any width-bit integer.
    Register order: x, t, carry, valid, reduce, work. Auxiliaries
    must start at zero and are returned to zero.
    """
    modular_add_constant(width, modulus, 0)
    x = QuantumRegister(width, "x")
    t = QuantumRegister(width, "t")
    carry = QuantumRegister(1, "carry")
    valid = QuantumRegister(1, "valid")
    reduce = QuantumRegister(1, "reduce")
    work = QuantumRegister(width + 2, "work")
    circuit = QuantumCircuit(x, t, carry, valid, reduce, work, name=f"square_acc_mod_{modulus}")
    targets = list(t) + list(carry) + list(valid) + list(reduce) + list(work)

    terms = [([x[i]], (1 << (2 * i)) % modulus) for i in range(width)]
    terms += [
        ([x[i], x[j]], (1 << (i + j + 1)) % modulus)
        for i in range(width)
        for j in range(i + 1, width)
    ]
    for controls, value in terms:
        if value == 0:
            continue
        adder = modular_add_constant(width, modulus, value)
        for instruction in adder.data:
            if instruction.operation.name not in ("x", "cx", "ccx", "mcx"):
                raise ValueError("Unexpected gate in the reference modular adder")
            mapped = [targets[adder.find_bit(q).index] for q in instruction.qubits]
            if len(controls) == 1 and len(mapped) == 1:
                circuit.cx(controls[0], mapped[0])
            else:
                circuit.append(MCXGate(len(controls) + len(mapped) - 1), controls + mapped)
    return circuit
