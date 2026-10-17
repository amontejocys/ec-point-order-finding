"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import unittest
import numpy as np
from qiskit.quantum_info import Statevector
from quantum_ec.circuits.points.point_differences import point_differences
from tests.support.permutation import apply_basis, compile_x_permutation


class PointDifferencesTests(unittest.TestCase):
    def test_logical_coordinates(self):
        checked = 0
        for width, modulus, u, v in ((3, 5, 2, 3), (5, 29, 12, 13)):
            gates = compile_x_permutation(point_differences(width, modulus, u, v))
            count = 1 << width
            for x in range(count):
                for y in range(count):
                    d = (x-u) % modulus if x < modulus else x
                    n = (y-v) % modulus if y < modulus else y
                    initial = x | (y << width)
                    expected = initial | (d << (2 * width)) | (n << (3 * width))
                    self.assertEqual(apply_basis(gates, initial), expected)
                    self.assertEqual(apply_basis(gates, expected), initial)
                    checked += 1
        print(f"Verified {checked} difference pairs with preserved coordinates and clean scratch by logical gate propagation.")

    def test_complex_superposition_and_arbitrary_outputs(self):
        width, modulus, u, v = 1, 2, 1, 0
        circuit = point_differences(width, modulus, u, v)
        rng = np.random.default_rng(20261007)
        amplitudes = rng.normal(size=16) + 1j * rng.normal(size=16)
        amplitudes /= np.linalg.norm(amplitudes)
        data = np.zeros(1 << circuit.num_qubits, dtype=complex)
        data[:16] = amplitudes
        expected = np.zeros_like(data)
        for index, amplitude in enumerate(amplitudes):
            x, y = index & 1, (index >> 1) & 1
            d, n = (x-u) % modulus, (y-v) % modulus
            expected[index ^ (d << 2) ^ (n << 3)] = amplitude
        actual = Statevector(data).evolve(circuit)
        np.testing.assert_allclose(actual.data, expected, atol=1e-10, rtol=0)
        np.testing.assert_allclose(actual.evolve(circuit.inverse()).data, data, atol=1e-10, rtol=0)

    def test_invalid_constants(self):
        for u, v in ((-1, 0), (0, 5), (True, 0), (0.5, 0)):
            with self.assertRaises(ValueError):
                point_differences(3, 5, u, v)
