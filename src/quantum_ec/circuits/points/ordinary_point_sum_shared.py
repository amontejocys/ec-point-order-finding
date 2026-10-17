"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

from qiskit import QuantumCircuit, QuantumRegister
from quantum_ec.circuits.arithmetic.modular_add_constant import modular_add_constant
from quantum_ec.circuits.arithmetic.modular_add_register import modular_add_register
from quantum_ec.circuits.arithmetic.modular_inverse import modular_inverse
from quantum_ec.circuits.arithmetic.modular_inverse_inplace import modular_inverse_inplace
from quantum_ec.circuits.arithmetic.modular_multiply_accumulate import modular_multiply_accumulate
from quantum_ec.circuits.arithmetic.modular_square_accumulate import modular_square_accumulate


def ordinary_point_sum_shared(width: int, modulus: int, u: int, v: int, *, inverse_variant: str = "history") -> QuantumCircuit:
    """Preserve x,y and XOR ordinary sum coordinates into X_out,Y_out.

    Retain D,N,I,L until both coordinates are transferred, then uncompute
    once. The geometric preconditions and invalid-input extensions match
    ordinary_point_sum. All scratch starts and ends at zero. Register order
    begins x,y,X_out,Y_out. inverse_variant selects the retained "history"
    inverse or the "compact" inverse with in-place Euclidean state updates.
    """
    modular_add_constant(width, modulus, 0)
    if inverse_variant not in ("history", "compact"):
        raise ValueError("inverse_variant must be history or compact")
    for coordinate in (u, v):
        if not isinstance(coordinate, int) or isinstance(coordinate, bool) or not 0 <= coordinate < modulus:
            raise ValueError("constant coordinates must be canonical residues")
    subtract_u = modular_add_constant(width, modulus, -u)
    subtract_v = modular_add_constant(width, modulus, -v)
    inverse_builder = modular_inverse_inplace if inverse_variant == "compact" else modular_inverse
    inverse = inverse_builder(width, modulus)
    multiply = modular_multiply_accumulate(width, modulus)
    square = modular_square_accumulate(width, modulus)
    add_register = modular_add_register(width, modulus)
    x = QuantumRegister(width, "x")
    y = QuantumRegister(width, "y")
    x_out = QuantumRegister(width, "X_out")
    y_out = QuantumRegister(width, "Y_out")
    d = QuantumRegister(width, "D")
    n = QuantumRegister(width, "N")
    i = QuantumRegister(width, "I")
    slope = QuantumRegister(width, "L")
    result_x = QuantumRegister(width, "X_work")
    difference = QuantumRegister(width, "T_work")
    result_y = QuantumRegister(width, "Y_work")
    inverse_work = QuantumRegister(inverse.num_qubits - 2 * width, "inverse_work")
    arithmetic_work = QuantumRegister(multiply.num_qubits - 3 * width, "arithmetic_work")
    scratch = [d, n, i, slope, result_x, difference, result_y, inverse_work, arithmetic_work]
    compute = QuantumCircuit(x, y, *scratch, name="shared_ordinary_compute")
    aux = list(arithmetic_work)
    for bit in range(width):
        compute.cx(x[bit], d[bit])
        compute.cx(y[bit], n[bit])
    compute.compose(subtract_u, list(d) + aux, inplace=True)
    compute.compose(subtract_v, list(n) + aux, inplace=True)
    compute.compose(inverse, list(d) + list(i) + list(inverse_work), inplace=True)
    compute.compose(multiply, list(n) + list(i) + list(slope) + aux, inplace=True)
    compute.compose(square, list(slope) + list(result_x) + aux, inplace=True)
    compute.compose(add_register.inverse(), list(result_x) + list(x) + aux, inplace=True)
    compute.compose(subtract_u, list(result_x) + aux, inplace=True)
    for bit in range(width):
        compute.cx(x[bit], difference[bit])
    compute.compose(add_register.inverse(), list(difference) + list(result_x) + aux, inplace=True)
    compute.compose(multiply, list(slope) + list(difference) + list(result_y) + aux, inplace=True)
    compute.compose(add_register.inverse(), list(result_y) + list(y) + aux, inplace=True)

    circuit = QuantumCircuit(x, y, x_out, y_out, *scratch, name="ordinary_point_sum_shared")
    circuit.compose(compute, list(compute.qubits), inplace=True)
    for bit in range(width):
        circuit.cx(result_x[bit], x_out[bit])
        circuit.cx(result_y[bit], y_out[bit])
    circuit.compose(compute.inverse(), list(compute.qubits), inplace=True)
    circuit.metadata = {"variant": "shared_intermediates", "inverse_variant": inverse_variant, "inverse_block_uses": 2}
    return circuit
