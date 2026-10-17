"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit.library import MCXGate
from quantum_ec.circuits.arithmetic.binary_add_constant import binary_add_constant
from quantum_ec.circuits.arithmetic.less_than_constant import less_than_constant


def _append_controlled_binary_add(circuit, control, targets, value):
    adder = binary_add_constant(len(targets), value)
    # The reference adder contains only positive-control X-family gates.
    for instruction in adder.data:
        if instruction.operation.name not in ("x", "cx", "mcx", "ccx"):
            raise ValueError("Unexpected gate in the reference binary adder")
        mapped = [targets[adder.find_bit(bit).index] for bit in instruction.qubits]
        if len(mapped) == 1:
            circuit.cx(control, mapped[0])
        else:
            circuit.append(MCXGate(len(mapped)), [control] + mapped)


def modular_add_constant(width: int, modulus: int, value: int) -> QuantumCircuit:
    """Add value modulo modulus for x < modulus, otherwise preserve x.

    Requires all auxiliary registers initially zero and returns them to zero.
    Register order: x, carry, valid, reduce, work. No primality is required.
    """
    if not isinstance(width, int) or isinstance(width, bool) or width < 1:
        raise ValueError("width must be a positive integer")
    if (
        not isinstance(modulus, int)
        or isinstance(modulus, bool)
        or not 2 <= modulus <= (1 << width)
    ):
        raise ValueError("modulus must be between 2 and 2**width")
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError("value must be an integer")
    value %= modulus

    x = QuantumRegister(width, "x")
    carry = QuantumRegister(1, "carry")
    valid = QuantumRegister(1, "valid")
    reduce = QuantumRegister(1, "reduce")
    work = QuantumRegister(width + 2, "work")
    circuit = QuantumCircuit(x, carry, valid, reduce, work, name=f"add_{value}_mod_{modulus}")
    widened = list(x) + list(carry)

    range_check = less_than_constant(width, modulus)
    circuit.compose(range_check, list(x) + list(valid) + list(work[:width + 1]), inplace=True)
    _append_controlled_binary_add(circuit, valid[0], widened, value)

    sum_check = less_than_constant(width + 1, modulus)
    circuit.compose(sum_check, widened + list(reduce) + list(work), inplace=True)
    circuit.cx(valid[0], reduce[0])
    _append_controlled_binary_add(circuit, reduce[0], widened, -modulus)

    cleanup_check = less_than_constant(width + 1, value)
    circuit.compose(cleanup_check, widened + list(reduce) + list(work), inplace=True)
    circuit.compose(range_check, list(x) + list(valid) + list(work[:width + 1]), inplace=True)
    return circuit
