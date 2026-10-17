"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import unittest
from quantum_ec.circuits.arithmetic.euclid_update import euclid_update
from tests.support.permutation import apply_basis, compile_x_permutation


class EuclidUpdateTests(unittest.TestCase):
    def test_small_inputs_and_clean_scratch(self):
        width, modulus = 2, 3
        gates = compile_x_permutation(euclid_update(width, modulus))
        checked = 0
        for r0 in range(4):
            for r1 in range(4):
                for c0 in range(modulus):
                    for c1 in range(modulus):
                        q, remainder = divmod(r0, r1) if r1 else (0, r0)
                        coefficient = (c0-q*c1) % modulus
                        initial = r0 | (r1 << width) | (c0 << (2 * width)) | (c1 << (3 * width))
                        expected = initial | (q << (4 * width)) | (remainder << (5 * width)) | (coefficient << (6 * width))
                        self.assertEqual(apply_basis(gates, initial), expected)
                        self.assertEqual(apply_basis(list(reversed(gates)), expected), initial)
                        checked += 1
        print(f"Verified {checked} Euclidean updates and inverses by logical gate propagation, with clean scratch.")

    def test_p29_trace(self):
        width, modulus = 5, 29
        gates = compile_x_permutation(euclid_update(width, modulus))
        cases = (
            (29, 23, 0, 1, 1, 6, 28),
            (23, 6, 1, 28, 3, 5, 4),
            (6, 5, 28, 4, 1, 1, 24),
            (5, 1, 4, 24, 5, 0, 0),
            (1, 0, 24, 0, 0, 1, 24),
        )
        for r0, r1, c0, c1, q, remainder, coefficient in cases:
            initial = r0 | (r1 << width) | (c0 << (2 * width)) | (c1 << (3 * width))
            expected = initial | (q << (4 * width)) | (remainder << (5 * width)) | (coefficient << (6 * width))
            self.assertEqual(apply_basis(gates, initial), expected)
            self.assertEqual(apply_basis(list(reversed(gates)), expected), initial)

    def test_invalid_parameters(self):
        for width, modulus in ((0, 3), (2, 4), (2, 5), (True, 3)):
            with self.assertRaises(ValueError):
                euclid_update(width, modulus)
