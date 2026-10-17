"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

from qiskit import QuantumCircuit, QuantumRegister
from quantum_ec.circuits.arithmetic.modular_add_constant import modular_add_constant
from quantum_ec.circuits.arithmetic.modular_add_register import modular_add_register
from quantum_ec.circuits.arithmetic.modular_square_accumulate import modular_square_accumulate
from quantum_ec.circuits.points.ordinary_point_slope import ordinary_point_slope


def ordinary_point_x(width: int, modulus: int, u: int, v: int) -> QuantumCircuit:
    """XOR (L*L-x-u)%p into X, preserving x,y and cleaning scratch.

    L is computed by ordinary_point_slope. A geometric interpretation
    requires valid finite points and invertible x-u. This arithmetic
    evaluator does not check those conditions or select special cases.
    Register order begins x,y,X. All scratch starts and ends at zero.
    """
    slope_block = ordinary_point_slope(width, modulus, u, v)
    square_block = modular_square_accumulate(width, modulus)
    add_register = modular_add_register(width, modulus)
    subtract_u = modular_add_constant(width, modulus, -u)
    x = QuantumRegister(width, "x")
    y = QuantumRegister(width, "y")
    output = QuantumRegister(width, "X")
    slope = QuantumRegister(width, "L")
    result = QuantumRegister(width, "X_work")
    slope_work = QuantumRegister(slope_block.num_qubits - 3 * width, "slope_work")
    arithmetic_work = QuantumRegister(square_block.num_qubits - 2 * width, "arithmetic_work")
    compute = QuantumCircuit(x, y, slope, result, slope_work, arithmetic_work, name="point_x_compute")
    aux = list(arithmetic_work)
    compute.compose(slope_block, list(x) + list(y) + list(slope) + list(slope_work), inplace=True)
    compute.compose(square_block, list(slope) + list(result) + aux, inplace=True)
    compute.compose(add_register.inverse(), list(result) + list(x) + aux, inplace=True)
    compute.compose(subtract_u, list(result) + aux, inplace=True)

    circuit = QuantumCircuit(x, y, output, slope, result, slope_work, arithmetic_work, name="ordinary_point_x")
    circuit.compose(compute, list(compute.qubits), inplace=True)
    for bit in range(width):
        circuit.cx(result[bit], output[bit])
    circuit.compose(compute.inverse(), list(compute.qubits), inplace=True)
    return circuit
