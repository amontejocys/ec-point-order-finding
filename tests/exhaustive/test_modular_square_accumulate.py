"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import unittest
import numpy as np
from qiskit.quantum_info import Statevector
from quantum_ec.circuits.arithmetic.modular_square_accumulate import modular_square_accumulate


class ModularSquareAccumulateTests(unittest.TestCase):
    def test_small_basis_inputs(self):
        checked = 0
        for width, modulus in ((1, 2), (2, 3), (2, 4)):
            count = 1 << width
            circuit = modular_square_accumulate(width, modulus)
            for x in range(count):
                for t in range(count):
                    initial_index = x | (t << width)
                    actual = Statevector.from_int(initial_index, 1 << circuit.num_qubits).evolve(circuit)
                    result = (t + x*x) % modulus if t < modulus else t
                    expected = Statevector.from_int(x | (result << width), len(actual.data))
                    np.testing.assert_allclose(actual.data, expected.data, atol=1e-10, rtol=0)
                    checked += 1
        print(f"Verified {checked} square transitions with preserved x and clean auxiliaries.")

    def test_complex_superposition_and_inverse(self):
        width, modulus = 3, 5
        count = 1 << width
        circuit = modular_square_accumulate(width, modulus)
        rng = np.random.default_rng(20261006)
        amplitudes = rng.normal(size=count**2) + 1j * rng.normal(size=count**2)
        amplitudes /= np.linalg.norm(amplitudes)
        data = np.zeros(1 << circuit.num_qubits, dtype=complex)
        data[:count**2] = amplitudes
        expected = np.zeros_like(data)
        for index, amplitude in enumerate(amplitudes):
            x, t = index % count, index // count
            result = (t + x*x) % modulus if t < modulus else t
            expected[x | (result << width)] = amplitude
        actual = Statevector(data).evolve(circuit)
        np.testing.assert_allclose(actual.data, expected, atol=1e-10, rtol=0)
        np.testing.assert_allclose(actual.evolve(circuit.inverse()).data, data, atol=1e-10, rtol=0)

    def test_invalid_parameters(self):
        for args in ((0, 2), (3, 1), (3, 9), (True, 2)):
            with self.assertRaises(ValueError):
                modular_square_accumulate(*args)
