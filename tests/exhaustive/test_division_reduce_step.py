"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import unittest
import numpy as np
from qiskit.quantum_info import Statevector
from quantum_ec.circuits.arithmetic.division_reduce_step import division_reduce_step
from tests.support.permutation import apply_basis, compile_x_permutation


class DivisionReduceStepTests(unittest.TestCase):
    def test_positive_divisors(self):
        checked = 0
        for width in (1, 2, 3, 5):
            count = 1 << width
            gates = compile_x_permutation(division_reduce_step(width))
            for candidate in range(count):
                for divisor in range(1, count):
                    q = int(candidate >= divisor)
                    result = candidate - q * divisor
                    initial = candidate | (divisor << width)
                    expected = result | (divisor << width) | (q << (2 * width))
                    self.assertEqual(apply_basis(gates, initial), expected)
                    self.assertEqual(apply_basis(list(reversed(gates)), expected), initial)
                    if candidate < 2 * divisor:
                        self.assertLess(result, divisor)
                    checked += 1
        print(f"Verified {checked} compare/subtract transitions with retained quotient bit and clean work.")

    def test_complex_superposition_and_inverse(self):
        width = 2
        count = 1 << width
        circuit = division_reduce_step(width)
        rng = np.random.default_rng(20261007)
        amplitudes = rng.normal(size=12) + 1j * rng.normal(size=12)
        amplitudes /= np.linalg.norm(amplitudes)
        data = np.zeros(1 << circuit.num_qubits, dtype=complex)
        expected = np.zeros_like(data)
        position = 0
        for divisor in range(1, count):
            for candidate in range(count):
                initial = candidate | (divisor << width)
                q = int(candidate >= divisor)
                result = candidate - q * divisor
                target = result | (divisor << width) | (q << (2 * width))
                data[initial] = amplitudes[position]
                expected[target] = amplitudes[position]
                position += 1
        actual = Statevector(data).evolve(circuit)
        np.testing.assert_allclose(actual.data, expected, atol=1e-10, rtol=0)
        np.testing.assert_allclose(actual.evolve(circuit.inverse()).data, data, atol=1e-10, rtol=0)

    def test_zero_divisor_is_not_division(self):
        width = 3
        gates = compile_x_permutation(division_reduce_step(width))
        for candidate in range(8):
            self.assertEqual(apply_basis(gates, candidate), candidate | (1 << (2 * width)))

    def test_invalid_width(self):
        for width in (0, -1, True, 2.5):
            with self.assertRaises(ValueError):
                division_reduce_step(width)
