"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import unittest
import numpy as np
from qiskit.quantum_info import Statevector
from quantum_ec.circuits.arithmetic.less_than_register import less_than_register
from tests.support.permutation import apply_basis, compile_x_permutation


class LessThanRegisterTests(unittest.TestCase):
    def test_logical_basis_and_cleanup(self):
        checked = 0
        for width in (1, 2, 3, 5):
            gates = compile_x_permutation(less_than_register(width))
            count = 1 << width
            for a in range(count):
                for b in range(count):
                    for flag in (0, 1):
                        initial = a | (b << width) | (flag << (2 * width))
                        expected = a | (b << width) | ((flag ^ int(a < b)) << (2 * width))
                        self.assertEqual(apply_basis(gates, initial), expected)
                        self.assertEqual(apply_basis(gates, expected), initial)
                        checked += 1
        print(f"Verified {checked} register comparisons by logical gate propagation, with clean work.")

    def test_complex_superposition_and_inverse(self):
        width = 3
        count = 1 << width
        circuit = less_than_register(width)
        rng = np.random.default_rng(20261007)
        amplitudes = rng.normal(size=2 * count**2) + 1j * rng.normal(size=2 * count**2)
        amplitudes /= np.linalg.norm(amplitudes)
        data = np.zeros(1 << circuit.num_qubits, dtype=complex)
        data[:len(amplitudes)] = amplitudes
        expected = np.zeros_like(data)
        for index, amplitude in enumerate(amplitudes):
            a, b = index % count, (index >> width) % count
            result = index ^ ((1 << (2 * width)) if a < b else 0)
            expected[result] = amplitude
        actual = Statevector(data).evolve(circuit)
        np.testing.assert_allclose(actual.data, expected, atol=1e-10, rtol=0)
        np.testing.assert_allclose(actual.evolve(circuit.inverse()).data, data, atol=1e-10, rtol=0)

    def test_invalid_width(self):
        for width in (0, -1, True, 2.5):
            with self.assertRaises(ValueError):
                less_than_register(width)
