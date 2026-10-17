"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

from qiskit import QuantumCircuit, QuantumRegister
from quantum_ec.circuits.arithmetic.modular_add_constant import modular_add_constant
from quantum_ec.circuits.arithmetic.modular_add_register import modular_add_register
from quantum_ec.circuits.arithmetic.modular_multiply_accumulate import modular_multiply_accumulate
from quantum_ec.circuits.arithmetic.modular_square_accumulate import modular_square_accumulate
from quantum_ec.circuits.points.ordinary_point_slope import ordinary_point_slope


def ordinary_point_sum(width: int, modulus: int, u: int, v: int) -> QuantumCircuit:
    """XOR ordinary sum coordinates into X_out,Y_out; preserve x,y.

    Requires valid finite points with invertible x-u for a geometric sum.
    No branch selection or identity encoding is performed. Other inputs
    follow the reference primitives' arithmetic extensions, not the group
    law. Register order starts x,y,X_out,Y_out. Scratch starts and ends zero.
    """
    slope_block = ordinary_point_slope(width, modulus, u, v)
    square_block = modular_square_accumulate(width, modulus)
    add_register = modular_add_register(width, modulus)
    multiply = modular_multiply_accumulate(width, modulus)
    subtract_u = modular_add_constant(width, modulus, -u)
    x = QuantumRegister(width, "x")
    y = QuantumRegister(width, "y")
    x_out = QuantumRegister(width, "X_out")
    y_out = QuantumRegister(width, "Y_out")
    slope = QuantumRegister(width, "L")
    result_x = QuantumRegister(width, "X_work")
    difference = QuantumRegister(width, "T_work")
    result_y = QuantumRegister(width, "Y_work")
    slope_work = QuantumRegister(slope_block.num_qubits - 3 * width, "slope_work")
    arithmetic_work = QuantumRegister(square_block.num_qubits - 2 * width, "arithmetic_work")
    registers = [x, y, slope, result_x, difference, result_y, slope_work, arithmetic_work]
    compute = QuantumCircuit(*registers, name="ordinary_sum_compute")
    aux = list(arithmetic_work)
    compute.compose(slope_block, list(x) + list(y) + list(slope) + list(slope_work), inplace=True)
    compute.compose(square_block, list(slope) + list(result_x) + aux, inplace=True)
    compute.compose(add_register.inverse(), list(result_x) + list(x) + aux, inplace=True)
    compute.compose(subtract_u, list(result_x) + aux, inplace=True)

    for bit in range(width):
        compute.cx(x[bit], difference[bit])
    compute.compose(add_register.inverse(), list(difference) + list(result_x) + aux, inplace=True)
    compute.compose(multiply, list(slope) + list(difference) + list(result_y) + aux, inplace=True)
    compute.compose(add_register.inverse(), list(result_y) + list(y) + aux, inplace=True)

    circuit = QuantumCircuit(x, y, x_out, y_out, *registers[2:], name="ordinary_point_sum")
    circuit.compose(compute, list(compute.qubits), inplace=True)
    for bit in range(width):
        circuit.cx(result_x[bit], x_out[bit])
        circuit.cx(result_y[bit], y_out[bit])
    circuit.compose(compute.inverse(), list(compute.qubits), inplace=True)
    return circuit
