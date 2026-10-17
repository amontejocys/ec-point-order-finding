"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import unittest
from quantum_ec.circuits.points.ordinary_point_sum import ordinary_point_sum
from tests.support.permutation import apply_basis, compile_x_permutation


class OrdinaryPointSumTests(unittest.TestCase):
    def test_small_canonical_arithmetic_and_outputs(self):
        width, modulus, u, v = 2, 3, 1, 1
        gates = compile_x_permutation(ordinary_point_sum(width, modulus, u, v))
        for x in range(modulus):
            for y in range(modulus):
                d = (x-u) % modulus
                slope = (y-v)*pow(d, -1, modulus) % modulus if d else 0
                result_x = (slope*slope-x-u) % modulus
                result_y = (slope*(x-result_x)-y) % modulus
                for out_x, out_y in ((0, 0), (3, 2)):
                    initial = x | (y << width) | (out_x << (2 * width)) | (out_y << (3 * width))
                    expected = x | (y << width) | ((out_x ^ result_x) << (2 * width)) | ((out_y ^ result_y) << (3 * width))
                    self.assertEqual(apply_basis(gates, initial), expected)
                    self.assertEqual(apply_basis(gates, expected), initial)

    def test_all_ordinary_p29_points(self):
        width, modulus, u, v = 5, 29, 12, 13
        gates = compile_x_permutation(ordinary_point_sum(width, modulus, u, v))
        checked = 0
        # Enumeration is only an independent test oracle, not circuit synthesis.
        for x in range(modulus):
            for y in range(modulus):
                if x == u or (y*y-x**3-7) % modulus:
                    continue
                slope = (y-v)*pow((x-u) % modulus, -1, modulus) % modulus
                result_x = (slope*slope-x-u) % modulus
                result_y = (slope*(x-result_x)-y) % modulus
                self.assertEqual((result_y*result_y-result_x**3-7) % modulus, 0)
                initial = x | (y << width)
                expected = initial | (result_x << (2 * width)) | (result_y << (3 * width))
                self.assertEqual(apply_basis(gates, initial), expected)
                self.assertEqual(apply_basis(gates, expected), initial)
                checked += 1
        self.assertEqual(checked, 27)
        print("Verified all 27 ordinary finite inputs for p=29, plus 18 small arithmetic transitions, by logical gate propagation with clean scratch.")
