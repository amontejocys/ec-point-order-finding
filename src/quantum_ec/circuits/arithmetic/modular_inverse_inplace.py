"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit.library import MCXGate
from quantum_ec.circuits.arithmetic.binary_add_constant import binary_add_constant
from quantum_ec.circuits.arithmetic.binary_quotient import binary_quotient
from quantum_ec.circuits.arithmetic.equality_constant import equality_constant
from quantum_ec.circuits.arithmetic.less_than_constant import less_than_constant
from quantum_ec.circuits.arithmetic.modular_multiply_accumulate import modular_multiply_accumulate


def modular_inverse_inplace(width: int, modulus: int) -> QuantumCircuit:
    """Same clean XOR inverse contract as modular_inverse, with less state history.

    Retains one quartet r0,r1,c0,c1 rather than one per round. Quotients and
    activation bits are retained for reversal. Register order starts d,target;
    all other registers start and end zero. Nonunits and invalid d yield zero.
    This still uses the reference divider and multiplier, not optimized paper
    implementations. Modulus must fit in width.
    """
    multiply = modular_multiply_accumulate(width, modulus)
    if modulus == (1 << width):
        raise ValueError("modulus itself must fit in the remainder register")
    quotient_block = binary_quotient(width)
    d = QuantumRegister(width, "d")
    target = QuantumRegister(width, "target")
    r0 = QuantumRegister(width, "r0")
    r1 = QuantumRegister(width, "r1")
    c0 = QuantumRegister(width, "c0")
    c1 = QuantumRegister(width, "c1")
    rounds = 2 * width + 1
    quotients = [QuantumRegister(width, f"q_{stage}") for stage in range(rounds)]
    active = QuantumRegister(rounds, "active_history")
    division_work = QuantumRegister(quotient_block.num_qubits - 3 * width, "division_work")
    multiply_work = QuantumRegister(multiply.num_qubits - 3 * width, "multiply_work")
    predicates = QuantumRegister(4, "predicates")
    registers = [r0, r1, c0, c1, *quotients, active, division_work, multiply_work, predicates]
    compute = QuantumCircuit(d, *registers, name="compact_inverse_compute")

    q_bits = QuantumRegister(width, "q")
    source = QuantumRegister(width, "source")
    destination = QuantumRegister(width, "destination")
    subtract_product = QuantumCircuit(q_bits, source, destination, name="binary_product_subtract")
    for i in range(width):
        for j in range(width - i):
            adder = binary_add_constant(width, -(1 << (i + j)))
            for instruction in adder.data:
                if instruction.operation.name not in ("x", "cx", "ccx", "mcx"):
                    raise ValueError("Unexpected gate in binary product subtractor")
                mapped = [destination[adder.find_bit(q).index] for q in instruction.qubits]
                subtract_product.append(MCXGate(len(mapped) + 1), [q_bits[i], source[j]] + mapped)

    for bit in range(width):
        if (modulus >> bit) & 1:
            compute.x(r0[bit])
        compute.cx(d[bit], r1[bit])
    compute.x(c1[0])
    zero_check = equality_constant(width, 0)
    for stage in range(rounds):
        enabled = active[stage]
        quotient = quotients[stage]
        compute.compose(zero_check, list(r1) + [enabled], inplace=True)
        compute.x(enabled)
        quotient_qubits = list(r0) + list(r1) + list(quotient) + list(division_work)
        for instruction in quotient_block.data:
            if instruction.operation.name not in ("x", "cx", "ccx", "mcx"):
                raise ValueError("Unexpected gate in quotient evaluator")
            mapped = [quotient_qubits[quotient_block.find_bit(q).index] for q in instruction.qubits]
            if len(mapped) == 1:
                compute.cx(enabled, mapped[0])
            else:
                compute.append(MCXGate(len(mapped)), [enabled] + mapped)
        # Inactive rounds have q=0, so both product subtractions are identity.
        compute.compose(subtract_product, list(quotient) + list(r1) + list(r0), inplace=True)
        compute.compose(multiply.inverse(), list(quotient) + list(c1) + list(c0) + list(multiply_work), inplace=True)
        for left, right in ((r0, r1), (c0, c1)):
            for bit in range(width):
                compute.ccx(enabled, left[bit], right[bit])
                compute.ccx(enabled, right[bit], left[bit])
                compute.ccx(enabled, left[bit], right[bit])

    compute.compose(less_than_constant(width, modulus), list(d) + [predicates[0]] + list(division_work[:width + 1]), inplace=True)
    compute.compose(zero_check, list(d) + [predicates[1]], inplace=True)
    compute.x(predicates[1])
    compute.compose(equality_constant(width, 1), list(r0) + [predicates[2]], inplace=True)
    compute.compose(zero_check, list(r1) + [predicates[3]], inplace=True)
    circuit = QuantumCircuit(d, target, *registers, name="modular_inverse_inplace")
    circuit.compose(compute, list(compute.qubits), inplace=True)
    for bit in range(width):
        circuit.append(MCXGate(5), list(predicates) + [c0[bit], target[bit]])
    circuit.compose(compute.inverse(), list(compute.qubits), inplace=True)
    return circuit
