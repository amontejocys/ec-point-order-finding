"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import unittest
from quantum_ec.circuits.points.finite_curve_check import finite_curve_check
from tests.support.permutation import apply_basis, compile_x_permutation


class FiniteCurveCheckTests(unittest.TestCase):
    def test_all_small_coordinates_and_both_flags(self):
        width, modulus, a, b = 3, 5, 1, 1
        gates = compile_x_permutation(finite_curve_check(width, modulus, a, b))
        checked = 0
        for x in range(8):
            for y in range(8):
                predicate = x < modulus and y < modulus and (y*y-x**3-a*x-b) % modulus == 0
                for flag in (0, 1):
                    initial = x | (y << width) | (flag << (2 * width))
                    expected = x | (y << width) | ((flag ^ int(predicate)) << (2 * width))
                    self.assertEqual(apply_basis(gates, initial), expected)
                    self.assertEqual(apply_basis(gates, expected), initial)
                    checked += 1
        print(f"Verified {checked} finite-curve predicate transitions with clean scratch by logical gate propagation.")

    def test_p29_examples_and_invalid_coordinate(self):
        width = 5
        gates = compile_x_permutation(finite_curve_check(width, 29, 0, 7))
        # (6, 22) is valid, while (6, 29) is outside the coordinate range.
        for x, y, expected_flag in ((6, 7, 1), (6, 22, 1), (6, 8, 0), (6, 29, 0), (29, 6, 0)):
            initial = x | (y << width)
            expected = initial | (expected_flag << (2 * width))
            self.assertEqual(apply_basis(gates, initial), expected)
