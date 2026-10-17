"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import unittest
from quantum_ec.circuits.points.controlled_point_add import controlled_point_add
from tests.support.permutation import apply_basis, compile_x_permutation
from tests.reference.encoding import expected_sum_encoding


class ControlledPointAddTests(unittest.TestCase):
    def test_all_small_encodings_and_controls(self):
        width, p, a, b, u, v = 3, 5, 1, 1, 0, 1
        gates = compile_x_permutation(controlled_point_add(width, p, a, b, u, v))
        inverse_gates = list(reversed(gates))
        for enc in range(1 << (2 * width + 1)):
            for control in (0, 1):
                initial = control | (enc << 1)
                result = expected_sum_encoding(enc, width, p, a, b, u, v) if control else enc
                expected = control | (result << 1)
                self.assertEqual(apply_basis(gates, initial), expected)
                self.assertEqual(apply_basis(inverse_gates, expected), initial)

    def test_p29_points_invalid_inputs_and_both_controls(self):
        width, p, a, b, u, v = 5, 29, 0, 7, 12, 13
        gates = compile_x_permutation(controlled_point_add(width, p, a, b, u, v))
        inverse_gates = list(reversed(gates))
        valid = [1] + [(x << 1) | (y << (width + 1)) for x in range(p) for y in range(p) if (y*y-x**3-a*x-b) % p == 0]
        invalid = [0, 1 | (6 << 1) | (7 << (width + 1)), 31 << 1, (6 << 1) | (29 << (width + 1))]
        for enc in valid + invalid:
            for control in (0, 1):
                initial = control | (enc << 1)
                result = expected_sum_encoding(enc, width, p, a, b, u, v) if control else enc
                expected = control | (result << 1)
                self.assertEqual(apply_basis(gates, initial), expected)
                self.assertEqual(apply_basis(inverse_gates, expected), initial)
        print("Verified both control branches on 128 small encodings and 30 p=29 points plus invalid examples, with clean work by logical gate propagation.")
