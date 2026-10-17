"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import unittest
from quantum_ec.circuits.points.ordinary_point_slope import ordinary_point_slope
from tests.support.permutation import apply_basis, compile_x_permutation


class OrdinaryPointSlopeTests(unittest.TestCase):
    def test_small_coordinates_and_targets(self):
        width, modulus, u, v = 2, 3, 1, 1
        gates = compile_x_permutation(ordinary_point_slope(width, modulus, u, v))
        for x in range(4):
            for y in range(4):
                d = (x-u) % modulus if x < modulus else x
                n = (y-v) % modulus if y < modulus else y
                inverse = pow(d, -1, modulus) if 0 < d < modulus else 0
                slope = n*inverse % modulus
                for output in (0, 3):
                    initial = x | (y << width) | (output << (2 * width))
                    expected = x | (y << width) | ((output ^ slope) << (2 * width))
                    self.assertEqual(apply_basis(gates, initial), expected)
                    self.assertEqual(apply_basis(gates, expected), initial)

    def test_p29_examples_and_zero_denominator(self):
        width, modulus, u, v = 5, 29, 12, 13
        gates = compile_x_permutation(ordinary_point_slope(width, modulus, u, v))
        for x, y in ((6, 7), (6, 22), (13, 14), (0, 0), (28, 28), (12, 13), (12, 16), (31, 31)):
            d = (x-u) % modulus if x < modulus else x
            n = (y-v) % modulus if y < modulus else y
            inverse = pow(d, -1, modulus) if 0 < d < modulus else 0
            slope = n*inverse % modulus
            initial = x | (y << width)
            expected = initial | (slope << (2 * width))
            self.assertEqual(apply_basis(gates, initial), expected)
            self.assertEqual(apply_basis(gates, expected), initial)
        print("Verified 32 small slope transitions and 8 modulus-29 examples by logical gate propagation, including clean scratch.")
