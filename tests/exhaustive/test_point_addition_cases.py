"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import unittest
from quantum_ec.circuits.points.point_addition_cases import point_addition_cases
from tests.support.permutation import apply_basis, compile_x_permutation


class PointAdditionCasesTests(unittest.TestCase):
    def test_all_encodings(self):
        checked = 0
        for width, modulus, a, b, u, v in ((3, 5, 1, 1, 0, 1), (3, 5, 1, 0, 0, 0), (5, 29, 0, 7, 12, 13)):
            gates = compile_x_permutation(point_addition_cases(width, modulus, a, b, u, v))
            counts = [0, 0, 0, 0]
            for identity in (0, 1):
                for x in range(1 << width):
                    for y in range(1 << width):
                        finite = identity == 0 and x < modulus and y < modulus and (y*y-x**3-a*x-b) % modulus == 0
                        is_identity = identity == 1 and x == 0 and y == 0
                        branch = None
                        if is_identity:
                            branch = 0
                        elif finite:
                            if (x, y) == (u, (-v) % modulus):
                                branch = 1
                            elif (x, y) == (u, v):
                                branch = 2
                            else:
                                branch = 3
                        mask = 0 if branch is None else 1 << branch
                        if branch is not None:
                            counts[branch] += 1
                        initial = identity | (x << 1) | (y << (width + 1))
                        expected = initial | (mask << (2 * width + 1))
                        self.assertEqual(apply_basis(gates, initial), expected)
                        self.assertEqual(apply_basis(gates, expected), initial)
                        checked += 1
            if modulus == 29:
                self.assertEqual(counts, [1, 1, 1, 27])
            if v == 0:
                self.assertEqual(counts[2], 0)
        print(f"Verified {checked} encodings with exclusive branches and clean scratch by logical gate propagation.")

    def test_invalid_constant_point(self):
        with self.assertRaises(ValueError):
            point_addition_cases(5, 29, 0, 7, 6, 8)
