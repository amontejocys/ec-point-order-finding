"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import unittest
from quantum_ec.circuits.points.special_point_sum import special_point_sum
from tests.support.permutation import apply_basis, compile_x_permutation


class SpecialPointSumTests(unittest.TestCase):
    def test_all_small_encodings_and_arbitrary_outputs(self):
        checked = 0
        for width, p, a, b, u, v in ((3, 5, 1, 1, 0, 1), (3, 5, 1, 0, 0, 0)):
            gates = compile_x_permutation(special_point_sum(width, p, a, b, u, v))
            count = 1 << (2 * width + 1)
            a_enc = (u << 1) | (v << (width + 1))
            neg_enc = (u << 1) | (((-v) % p) << (width + 1))
            if v:
                slope = (3*u*u+a)*pow(2*v, -1, p) % p
                dx = (slope*slope-2*u) % p
                dy = (slope*(u-dx)-v) % p
                double_enc = (dx << 1) | (dy << (width + 1))
            else:
                double_enc = 1
            for enc in range(count):
                contribution = a_enc if enc == 1 else 1 if enc == neg_enc else double_enc if enc == a_enc else 0
                for output in (0, count-1):
                    initial = enc | (output << (2 * width + 1))
                    expected = enc | ((output ^ contribution) << (2 * width + 1))
                    self.assertEqual(apply_basis(gates, initial), expected)
                    self.assertEqual(apply_basis(gates, expected), initial)
                    checked += 1
        print(f"Verified {checked} special-branch transitions by logical gate propagation with clean scratch.")

    def test_p29_examples(self):
        width = 5
        gates = compile_x_permutation(special_point_sum(width, 29, 0, 7, 12, 13))
        def encode(identity, x, y):
            return identity | (x << 1) | (y << (width + 1))
        cases = (
            (encode(1, 0, 0), encode(0, 12, 13)),
            (encode(0, 12, 16), encode(1, 0, 0)),
            (encode(0, 12, 13), encode(0, 6, 22)),
            (encode(0, 6, 7), 0),
            (encode(1, 6, 7), 0),
        )
        for enc, contribution in cases:
            expected = enc | (contribution << (2 * width + 1))
            self.assertEqual(apply_basis(gates, enc), expected)
            self.assertEqual(apply_basis(gates, expected), enc)
