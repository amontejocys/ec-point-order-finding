"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import unittest
from quantum_ec.circuits.points.point_add_inplace import point_add_inplace
from tests.support.permutation import apply_basis
from tests.reference.encoding import expected_sum_encoding


def compile_permutation(circuit):
    gates = []
    for instruction in circuit.data:
        bits = [circuit.find_bit(q).index for q in instruction.qubits]
        name = instruction.operation.name
        if name == "swap":
            left, right = bits
            gates.extend(((1 << left, 1 << right), (1 << right, 1 << left), (1 << left, 1 << right)))
        elif name in ("x", "cx", "ccx", "mcx"):
            gates.append((sum(1 << bit for bit in bits[:-1]), 1 << bits[-1]))
        else:
            raise AssertionError("Unexpected gate in logical permutation checker")
    return gates


class PointAddInplaceTests(unittest.TestCase):
    def test_all_small_encodings(self):
        width, p, a, b, u, v = 3, 5, 1, 1, 0, 1
        gates = compile_permutation(point_add_inplace(width, p, a, b, u, v))
        inverse_gates = list(reversed(gates))
        for enc in range(1 << (2 * width + 1)):
            expected = expected_sum_encoding(enc, width, p, a, b, u, v)
            self.assertEqual(apply_basis(gates, enc), expected)
            self.assertEqual(apply_basis(inverse_gates, expected), enc)

    def test_order_two_constant(self):
        width, p, a, b, u, v = 3, 5, 1, 0, 0, 0
        gates = compile_permutation(point_add_inplace(width, p, a, b, u, v))
        for enc in (0, 1, 4, 6, 3):
            expected = expected_sum_encoding(enc, width, p, a, b, u, v)
            self.assertEqual(apply_basis(gates, enc), expected)
            self.assertEqual(apply_basis(gates, expected), enc)

    def test_p29_points_and_invalid_examples(self):
        width, p, a, b, u, v = 5, 29, 0, 7, 12, 13
        gates = compile_permutation(point_add_inplace(width, p, a, b, u, v))
        inverse_gates = list(reversed(gates))
        valid = [1] + [(x << 1) | (y << (width + 1)) for x in range(p) for y in range(p) if (y*y-x**3-a*x-b) % p == 0]
        invalid = [0, 1 | (6 << 1) | (7 << (width + 1)), 31 << 1, (6 << 1) | (29 << (width + 1))]
        for enc in valid + invalid:
            expected = expected_sum_encoding(enc, width, p, a, b, u, v)
            self.assertEqual(apply_basis(gates, enc), expected)
            self.assertEqual(apply_basis(inverse_gates, expected), enc)
        print("Verified in-place addition on all 128 small encodings, order-two examples, and 30 p=29 points plus invalid examples, with clean work by logical gate propagation.")
