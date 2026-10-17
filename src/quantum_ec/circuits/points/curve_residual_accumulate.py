"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit.library import MCXGate
from quantum_ec.circuits.arithmetic.modular_add_constant import modular_add_constant
from quantum_ec.circuits.arithmetic.modular_cube_accumulate import modular_cube_accumulate
from quantum_ec.circuits.arithmetic.modular_square_accumulate import modular_square_accumulate


def curve_residual_accumulate(width: int, modulus: int, a: int, b: int) -> QuantumCircuit:
    """Accumulate y*y - x**3 - a*x - b modulo modulus into valid t.

    Preserve x and y, fix invalid t, and return zero-initialized auxiliaries
    to zero. Register order: x, y, t, square, carry, valid, reduce, work.
    This is polynomial arithmetic, not a complete curve-membership test.
    """
    cube_block = modular_cube_accumulate(width, modulus)
    for coefficient in (a, b):
        if not isinstance(coefficient, int) or isinstance(coefficient, bool):
            raise ValueError("coefficients must be integers")
    a, b = a % modulus, b % modulus
    x = QuantumRegister(width, "x")
    y = QuantumRegister(width, "y")
    t = QuantumRegister(width, "t")
    square = QuantumRegister(width, "square")
    carry = QuantumRegister(1, "carry")
    valid = QuantumRegister(1, "valid")
    reduce = QuantumRegister(1, "reduce")
    work = QuantumRegister(width + 2, "work")
    circuit = QuantumCircuit(x, y, t, square, carry, valid, reduce, work, name="curve_residual")
    aux = list(carry) + list(valid) + list(reduce) + list(work)
    accumulator_qubits = list(t) + aux

    circuit.compose(modular_square_accumulate(width, modulus), list(y) + list(t) + aux, inplace=True)
    circuit.compose(cube_block.inverse(), list(x) + list(t) + list(square) + aux, inplace=True)
    for bit in range(width):
        value = (-a * (1 << bit)) % modulus
        if value == 0:
            continue
        adder = modular_add_constant(width, modulus, value)
        for instruction in adder.data:
            if instruction.operation.name not in ("x", "cx", "ccx", "mcx"):
                raise ValueError("Unexpected gate in the reference modular adder")
            mapped = [accumulator_qubits[adder.find_bit(q).index] for q in instruction.qubits]
            if len(mapped) == 1:
                circuit.cx(x[bit], mapped[0])
            else:
                circuit.append(MCXGate(len(mapped)), [x[bit]] + mapped)
    circuit.compose(modular_add_constant(width, modulus, -b), accumulator_qubits, inplace=True)
    return circuit
