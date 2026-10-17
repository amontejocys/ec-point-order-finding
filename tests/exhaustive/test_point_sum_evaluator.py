"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import unittest
from quantum_ec.circuits.points.point_sum_evaluator import point_sum_evaluator
from tests.support.permutation import apply_basis, compile_x_permutation
from tests.reference.encoding import expected_sum_encoding


class PointSumEvaluatorTests(unittest.TestCase):
    def test_order_two_constant(self):
        width, p, a, b, u, v = 3, 5, 1, 0, 0, 0
        gates = compile_x_permutation(point_sum_evaluator(width, p, a, b, u, v))
        size = 2 * width + 1
        for enc in range(1 << size):
            result = expected_sum_encoding(enc, width, p, a, b, u, v)
            expected = enc | (result << size)
            self.assertEqual(apply_basis(gates, enc), expected)
            self.assertEqual(apply_basis(gates, expected), enc)

    def test_all_small_encodings(self):
        width, p, a, b, u, v = 3, 5, 1, 1, 0, 1
        gates = compile_x_permutation(point_sum_evaluator(width, p, a, b, u, v))
        size = 2 * width + 1
        for enc in range(1 << size):
            result = expected_sum_encoding(enc, width, p, a, b, u, v)
            initial = enc
            expected = initial | (result << size)
            self.assertEqual(apply_basis(gates, initial), expected)
            self.assertEqual(apply_basis(gates, expected), initial)

    def test_p29_all_valid_points_and_invalid_examples(self):
        width, p, a, b, u, v = 5, 29, 0, 7, 12, 13
        gates = compile_x_permutation(point_sum_evaluator(width, p, a, b, u, v))
        size = 2 * width + 1
        valid = [1] + [(x << 1) | (y << (width + 1)) for x in range(p) for y in range(p) if (y*y-x**3-a*x-b) % p == 0]
        self.assertEqual(len(valid), 30)
        invalid = [0, 1 | (6 << 1) | (7 << (width + 1)), (31 << 1), (6 << 1) | (29 << (width + 1))]
        for enc in valid + invalid:
            result = expected_sum_encoding(enc, width, p, a, b, u, v)
            for output in (0, (1 << size) - 1):
                initial = enc | (output << size)
                expected = enc | ((output ^ result) << size)
                self.assertEqual(apply_basis(gates, initial), expected)
                self.assertEqual(apply_basis(gates, expected), initial)
        print("Verified all 128 small encodings and 30 curve points plus 4 invalid examples for p=29, with clean scratch by logical gate propagation.")
