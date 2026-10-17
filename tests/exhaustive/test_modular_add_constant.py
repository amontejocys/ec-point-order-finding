"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import unittest
import numpy as np
from qiskit.quantum_info import Statevector
from quantum_ec.circuits.arithmetic.modular_add_constant import modular_add_constant


class ModularAddConstantTests(unittest.TestCase):
    def test_all_small_inputs(self):
        checked = 0
        for width in range(1, 4):
            for modulus in range(2, (1 << width) + 1):
                for value in range(modulus):
                    circuit = modular_add_constant(width, modulus, value)
                    for x in range(1 << width):
                        initial = Statevector.from_int(x, 1 << circuit.num_qubits)
                        actual = initial.evolve(circuit)
                        y = (x + value) % modulus if x < modulus else x
                        expected = Statevector.from_int(y, len(actual.data))
                        np.testing.assert_allclose(actual.data, expected.data, atol=1e-10, rtol=0)
                        checked += 1
        print(f"Verified {checked} modular-addition basis transitions with clean auxiliaries.")

    def test_curve_example_in_superposition(self):
        width, modulus = 5, 29
        rng = np.random.default_rng(20261006)
        amplitudes = rng.normal(size=32) + 1j * rng.normal(size=32)
        amplitudes /= np.linalg.norm(amplitudes)
        for value in (0, 7, 28, -7):
            circuit = modular_add_constant(width, modulus, value)
            data = np.zeros(1 << circuit.num_qubits, dtype=complex)
            data[:32] = amplitudes
            initial = Statevector(data)
            actual = initial.evolve(circuit)
            expected = np.zeros_like(data)
            for x, amplitude in enumerate(amplitudes):
                y = (x + value) % modulus if x < modulus else x
                expected[y] = amplitude
            np.testing.assert_allclose(actual.data, expected, atol=1e-10, rtol=0)
            restored = actual.evolve(circuit.inverse())
            np.testing.assert_allclose(restored.data, data, atol=1e-10, rtol=0)

    def test_invalid_parameters(self):
        for args in ((0, 2, 0), (3, 1, 0), (3, 9, 0), (3, 5, 1.5), (True, 2, 0)):
            with self.assertRaises(ValueError):
                modular_add_constant(*args)
