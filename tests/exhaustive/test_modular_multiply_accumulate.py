"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import unittest
import numpy as np
from qiskit.quantum_info import Statevector
from quantum_ec.circuits.arithmetic.modular_multiply_accumulate import modular_multiply_accumulate


class ModularMultiplyAccumulateTests(unittest.TestCase):
    def test_small_basis_inputs(self):
        checked = 0
        for width, modulus in ((1, 2), (2, 3), (2, 4)):
            count = 1 << width
            circuit = modular_multiply_accumulate(width, modulus)
            for x in range(count):
                for y in range(count):
                    for t in range(count):
                        initial_index = x | (y << width) | (t << (2 * width))
                        actual = Statevector.from_int(initial_index, 1 << circuit.num_qubits).evolve(circuit)
                        result = (t + x * y) % modulus if t < modulus else t
                        expected_index = x | (y << width) | (result << (2 * width))
                        expected = Statevector.from_int(expected_index, len(actual.data))
                        np.testing.assert_allclose(actual.data, expected.data, atol=1e-10, rtol=0)
                        checked += 1
        print(f"Verified {checked} multiplication transitions with preserved operands and clean auxiliaries.")

    def test_complex_superposition_and_inverse(self):
        width, modulus = 2, 3
        count = 1 << width
        circuit = modular_multiply_accumulate(width, modulus)
        rng = np.random.default_rng(20261006)
        amplitudes = rng.normal(size=count**3) + 1j * rng.normal(size=count**3)
        amplitudes /= np.linalg.norm(amplitudes)
        data = np.zeros(1 << circuit.num_qubits, dtype=complex)
        data[:count**3] = amplitudes
        expected = np.zeros_like(data)
        for index, amplitude in enumerate(amplitudes):
            x = index % count
            y = (index >> width) % count
            t = index >> (2 * width)
            result = (t + x * y) % modulus if t < modulus else t
            expected[x | (y << width) | (result << (2 * width))] = amplitude
        actual = Statevector(data).evolve(circuit)
        np.testing.assert_allclose(actual.data, expected, atol=1e-10, rtol=0)
        np.testing.assert_allclose(actual.evolve(circuit.inverse()).data, data, atol=1e-10, rtol=0)

    def test_invalid_parameters(self):
        for args in ((0, 2), (3, 1), (3, 9), (True, 2)):
            with self.assertRaises(ValueError):
                modular_multiply_accumulate(*args)
