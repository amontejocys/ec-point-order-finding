"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import unittest
import numpy as np
from qiskit.quantum_info import Statevector
from quantum_ec.circuits.points.curve_residual_accumulate import curve_residual_accumulate
from tests.support.permutation import compile_x_permutation
from tests.support.permutation import apply_basis


class CurveResidualTests(unittest.TestCase):
    def test_small_exhaustive_logical_basis(self):
        checked = 0
        width, modulus = 2, 3
        for a in range(modulus):
            for b in range(modulus):
                circuit = curve_residual_accumulate(width, modulus, a, b)
                gates = compile_x_permutation(circuit)
                for x in range(4):
                    for y in range(4):
                        for t in range(4):
                            initial = x | (y << width) | (t << (2 * width))
                            result = (t + y*y - x**3 - a*x - b) % modulus if t < modulus else t
                            expected = x | (y << width) | (result << (2 * width))
                            self.assertEqual(apply_basis(gates, initial), expected)
                            self.assertEqual(apply_basis(list(reversed(gates)), expected), initial)
                            checked += 1
        print(f"Verified {checked} polynomial basis transitions using exact logical X-gate propagation.")

    def test_p29_logical_basis(self):
        width, modulus, a, b = 5, 29, 0, 7
        gates = compile_x_permutation(curve_residual_accumulate(width, modulus, a, b))
        for x in range(32):
            for y in range(32):
                initial = x | (y << width)
                result = (y*y - x**3 - a*x - b) % modulus
                self.assertEqual(apply_basis(gates, initial), initial | (result << (2 * width)))
        print("Verified 1024 coordinate pairs for p=29 by logical basis propagation, not full statevector simulation.")

    def test_complex_superposition_and_inverse(self):
        width, modulus, a, b = 2, 3, 1, 2
        circuit = curve_residual_accumulate(width, modulus, a, b)
        rng = np.random.default_rng(20261006)
        amplitudes = rng.normal(size=64) + 1j * rng.normal(size=64)
        amplitudes /= np.linalg.norm(amplitudes)
        data = np.zeros(1 << circuit.num_qubits, dtype=complex)
        data[:64] = amplitudes
        expected = np.zeros_like(data)
        for index, amplitude in enumerate(amplitudes):
            x, y, t = index & 3, (index >> 2) & 3, index >> 4
            result = (t + y*y - x**3 - a*x - b) % modulus if t < modulus else t
            expected[x | (y << 2) | (result << 4)] = amplitude
        actual = Statevector(data).evolve(circuit)
        np.testing.assert_allclose(actual.data, expected, atol=1e-10, rtol=0)
        np.testing.assert_allclose(actual.evolve(circuit.inverse()).data, data, atol=1e-10, rtol=0)

    def test_invalid_coefficients(self):
        for a, b in ((0.5, 7), (0, True)):
            with self.assertRaises(ValueError):
                curve_residual_accumulate(2, 3, a, b)
