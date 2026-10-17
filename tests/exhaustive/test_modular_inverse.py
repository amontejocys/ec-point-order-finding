"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import math
import unittest
from quantum_ec.circuits.arithmetic.modular_inverse import modular_inverse
from tests.support.permutation import apply_basis, compile_x_permutation


class ModularInverseTests(unittest.TestCase):
    def test_all_small_inputs_and_arbitrary_targets(self):
        checked = 0
        for width, modulus in ((2, 3), (3, 5), (3, 7), (4, 9)):
            gates = compile_x_permutation(modular_inverse(width, modulus))
            count = 1 << width
            for d in range(count):
                inverse = pow(d, -1, modulus) if 0 < d < modulus and math.gcd(d, modulus) == 1 else 0
                for target in (0, count - 1):
                    initial = d | (target << width)
                    expected = d | ((target ^ inverse) << width)
                    self.assertEqual(apply_basis(gates, initial), expected)
                    self.assertEqual(apply_basis(gates, expected), initial)
                    checked += 1
        print(f"Verified {checked} modular-inverse transitions, including nonunits and clean history, by logical gate propagation.")

    def test_all_p29_inputs(self):
        width, modulus = 5, 29
        gates = compile_x_permutation(modular_inverse(width, modulus))
        for d in range(32):
            inverse = pow(d, -1, modulus) if 0 < d < modulus else 0
            expected = d | (inverse << width)
            self.assertEqual(apply_basis(gates, d), expected)
            self.assertEqual(apply_basis(gates, expected), d)
        print("Verified all 32 inputs for modulus 29 by logical gate propagation; not full statevector simulation.")

    def test_invalid_parameters(self):
        for width, modulus in ((0, 3), (2, 4), (2, 5), (True, 3)):
            with self.assertRaises(ValueError):
                modular_inverse(width, modulus)
