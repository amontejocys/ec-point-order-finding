"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit.library import MCXGate
from quantum_ec.circuits.arithmetic.equality_constant import equality_constant
from quantum_ec.circuits.arithmetic.euclid_update import euclid_update
from quantum_ec.circuits.arithmetic.less_than_constant import less_than_constant


def modular_inverse(width: int, modulus: int) -> QuantumCircuit:
    """XOR inverse(d) into target; preserve d and clean zero-initialized scratch.

    The inverse is zero for d=0, d>=modulus, or gcd(d,modulus)!=1.
    Register order begins d, target, then scratch. Modulus must fit in width.
    The circuit has 2*width+1 rounds, retains history, and is not optimized.
    """
    update = euclid_update(width, modulus)
    d = QuantumRegister(width, "d")
    target = QuantumRegister(width, "target")
    rounds = 2 * width + 1
    states = [
        [QuantumRegister(width, f"{name}_{stage}") for name in ("r0", "r1", "c0", "c1")]
        for stage in range(rounds + 1)
    ]
    quotients = [QuantumRegister(width, f"q_{stage}") for stage in range(rounds)]
    active = QuantumRegister(rounds, "active_history")
    update_work = QuantumRegister(update.num_qubits - 7 * width, "update_work")
    predicates = QuantumRegister(4, "output_predicates")
    state_registers = [register for state in states for register in state]
    compute = QuantumCircuit(d, *state_registers, *quotients, active, update_work, predicates, name="inverse_history")
    r0, r1, c0, c1 = states[0]
    for bit in range(width):
        if (modulus >> bit) & 1:
            compute.x(r0[bit])
        compute.cx(d[bit], r1[bit])
    compute.x(c1[0])

    zero_check = equality_constant(width, 0)
    for stage in range(rounds):
        r0, r1, c0, c1 = states[stage]
        next_r0, next_r1, next_c0, next_c1 = states[stage + 1]
        enabled = active[stage]
        compute.compose(zero_check, list(r1) + [enabled], inplace=True)
        compute.x(enabled)
        mapped_update = list(r0) + list(r1) + list(c0) + list(c1) + list(quotients[stage]) + list(next_r1) + list(next_c1) + list(update_work)
        for instruction in update.data:
            if instruction.operation.name not in ("x", "cx", "ccx", "mcx"):
                raise ValueError("Unexpected gate in the reference Euclidean update")
            mapped = [mapped_update[update.find_bit(q).index] for q in instruction.qubits]
            if len(mapped) == 1:
                compute.cx(enabled, mapped[0])
            else:
                compute.append(MCXGate(len(mapped)), [enabled] + mapped)
        for bit in range(width):
            compute.ccx(enabled, r1[bit], next_r0[bit])
            compute.ccx(enabled, c1[bit], next_c0[bit])
        # Inactive branches copy the terminal state unchanged.
        compute.x(enabled)
        for source, destination in zip(states[stage], states[stage + 1]):
            for bit in range(width):
                compute.ccx(enabled, source[bit], destination[bit])
        compute.x(enabled)

    final_r0, final_r1, final_c0, _ = states[-1]
    range_check = less_than_constant(width, modulus)
    compute.compose(range_check, list(d) + [predicates[0]] + list(update_work[:width + 1]), inplace=True)
    compute.compose(zero_check, list(d) + [predicates[1]], inplace=True)
    compute.x(predicates[1])
    compute.compose(equality_constant(width, 1), list(final_r0) + [predicates[2]], inplace=True)
    compute.compose(zero_check, list(final_r1) + [predicates[3]], inplace=True)

    circuit = QuantumCircuit(d, target, *state_registers, *quotients, active, update_work, predicates, name="modular_inverse")
    circuit.compose(compute, list(compute.qubits), inplace=True)
    for bit in range(width):
        circuit.append(MCXGate(5), list(predicates) + [final_c0[bit], target[bit]])
    circuit.compose(compute.inverse(), list(compute.qubits), inplace=True)
    return circuit
