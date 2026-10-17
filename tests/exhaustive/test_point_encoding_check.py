"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import unittest
from quantum_ec.circuits.points.point_encoding_check import point_encoding_check
from tests.support.permutation import apply_basis, compile_x_permutation


class PointEncodingCheckTests(unittest.TestCase):
    def test_all_small_encodings_and_both_flags(self):
        width, modulus, a, b = 3, 5, 1, 1
        gates = compile_x_permutation(point_encoding_check(width, modulus, a, b))
        checked = 0
        for identity in (0, 1):
            for x in range(8):
                for y in range(8):
                    finite = x < modulus and y < modulus and (y*y-x**3-a*x-b) % modulus == 0
                    valid = (identity == 0 and finite) or (identity == 1 and x == 0 and y == 0)
                    for flag in (0, 1):
                        encoding = identity | (x << 1) | (y << (width + 1))
                        initial = encoding | (flag << (2 * width + 1))
                        expected = encoding | ((flag ^ int(valid)) << (2 * width + 1))
                        self.assertEqual(apply_basis(gates, initial), expected)
                        self.assertEqual(apply_basis(gates, expected), initial)
                        checked += 1
        print(f"Verified {checked} point-encoding transitions with clean scratch by logical gate propagation.")

    def test_p29_examples(self):
        width = 5
        gates = compile_x_permutation(point_encoding_check(width, 29, 0, 7))
        cases = ((1, 0, 0, 1), (0, 6, 7, 1), (1, 6, 7, 0), (1, 0, 1, 0), (0, 0, 0, 0), (0, 6, 29, 0))
        for identity, x, y, valid in cases:
            initial = identity | (x << 1) | (y << (width + 1))
            self.assertEqual(apply_basis(gates, initial), initial | (valid << (2 * width + 1)))
