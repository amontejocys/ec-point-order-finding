"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import unittest
import numpy as np
from qiskit.quantum_info import Operator
from quantum_ec.circuits.order_finding.elliptic_order_finding import EllipticOrderFinding, inverse_qft_gate
from quantum_ec.classical.curve import classical_add
from tests.support.permutation import apply_basis


def compile_nested_permutation(circuit):
    gates = []
    def visit(block, mapping):
        for instruction in block.data:
            bits = [mapping[block.find_bit(q).index] for q in instruction.qubits]
            if instruction.operation.name in ("x", "cx", "ccx", "mcx"):
                gates.append((sum(1 << bit for bit in bits[:-1]), 1 << bits[-1]))
            elif instruction.operation.definition is not None:
                visit(instruction.operation.definition, bits)
            else:
                raise AssertionError("Unexpected non-permutation operation")
    visit(circuit, list(range(circuit.num_qubits)))
    return gates


class EllipticOrderFindingTests(unittest.TestCase):
    def test_inverse_qft_convention(self):
        for width in range(1, 6):
            count = 1 << width
            indices = np.arange(count)
            expected = np.exp(-2j*np.pi*np.outer(indices, indices)/count)/np.sqrt(count)
            np.testing.assert_allclose(Operator(inverse_qft_gate(width)).data, expected, atol=1e-12, rtol=0)

    def test_p29_constants_without_building_large_circuit(self):
        builder = EllipticOrderFinding(5, 29, 0, 7, (6, 7))
        self.assertEqual(builder.powers, [(6, 7), (12, 13), (6, 22), (12, 16), (6, 7)])
        self.assertEqual(builder._gates, {})

    def test_identity_powers_and_validation(self):
        builder = EllipticOrderFinding(3, 5, 1, 0, (0, 0))
        self.assertEqual(builder.powers, [(0, 0), None, None])
        for args in ((0, 29, 0, 7, (6, 7)), (5, 29, 0, 7, (6, 8)), (3, 5, 0, 0, (0, 0))):
            with self.assertRaises(ValueError):
                EllipticOrderFinding(*args)

    def test_real_arithmetic_linkage_and_order_finding_structure(self):
        # Odd order three: this example requires no parity correction.
        builder = EllipticOrderFinding(3, 5, 1, 1, (2, 1))
        evaluation = builder.periodic_evaluation()
        gates = compile_nested_permutation(evaluation)
        inverse_gates = list(reversed(gates))
        point = None
        for k in range(8):
            if point is None:
                encoded = 1
            else:
                x, y = point
                encoded = (x << 1) | (y << (builder.width + 1))
            expected = k | (encoded << builder.m)
            self.assertEqual(apply_basis(gates, k), expected)
            self.assertEqual(apply_basis(inverse_gates, expected), k)
            point = classical_add(point, builder.point, builder.modulus, builder.a)
        self.assertEqual(len(builder._gates), 2)
        circuit = builder.order_finding()
        names = [instruction.operation.name for instruction in circuit.data]
        self.assertEqual(names[:3], ["h"] * 3)
        self.assertEqual(names[3:5], ["evaluate_kP", "iqft"])
        self.assertEqual(names[5:], ["measure"] * 3)
        self.assertEqual(circuit.num_clbits, 3)
        self.assertEqual(circuit.metadata["Q"], 8)
        for bit, instruction in enumerate(circuit.data[-3:]):
            self.assertEqual(circuit.find_bit(instruction.qubits[0]).index, bit)
            self.assertEqual(circuit.find_bit(instruction.clbits[0]).index, bit)
        print(f"Verified real arithmetic kP linkage for all 8 scalar inputs on an odd-order point; {circuit.num_qubits} logical qubits. Order-finding structure checked, not its histogram.")
