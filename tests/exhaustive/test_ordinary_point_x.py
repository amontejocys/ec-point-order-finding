"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import unittest
from quantum_ec.circuits.points.ordinary_point_x import ordinary_point_x
from tests.support.permutation import apply_basis, compile_x_permutation


class OrdinaryPointXTests(unittest.TestCase):
    def test_small_arithmetic_and_arbitrary_outputs(self):
        width, modulus, u, v = 2, 3, 1, 1
        gates = compile_x_permutation(ordinary_point_x(width, modulus, u, v))
        for x in range(4):
            for y in range(4):
                d = (x-u) % modulus if x < modulus else x
                n = (y-v) % modulus if y < modulus else y
                inverse = pow(d, -1, modulus) if 0 < d < modulus else 0
                slope = n*inverse % modulus
                result = (slope*slope-x-u) % modulus
                for output in (0, 3):
                    initial = x | (y << width) | (output << (2 * width))
                    expected = x | (y << width) | ((output ^ result) << (2 * width))
                    self.assertEqual(apply_basis(gates, initial), expected)
                    self.assertEqual(apply_basis(gates, expected), initial)

    def test_p29_ordinary_points(self):
        width, modulus, u, v = 5, 29, 12, 13
        gates = compile_x_permutation(ordinary_point_x(width, modulus, u, v))
        for x, y in ((6, 7), (6, 22), (13, 0), (0, 6)):
            self.assertEqual((y*y-x**3-7) % modulus, 0)
            slope = (y-v)*pow((x-u) % modulus, -1, modulus) % modulus
            result = (slope*slope-x-u) % modulus
            initial = x | (y << width)
            expected = initial | (result << (2 * width))
            self.assertEqual(apply_basis(gates, initial), expected)
            self.assertEqual(apply_basis(gates, expected), initial)
        print("Verified 32 small arithmetic transitions and 4 ordinary curve points for p=29 by logical gate propagation.")
