"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import unittest
import numpy as np
from qiskit.quantum_info import Statevector
from quantum_ec.circuits.arithmetic.binary_divide import binary_divide
from tests.support.permutation import apply_basis, compile_x_permutation


class BinaryDivideTests(unittest.TestCase):
    def test_all_inputs_with_clean_outputs(self):
        checked = 0
        for width in (1, 2, 3, 5):
            count = 1 << width
            gates = compile_x_permutation(binary_divide(width))
            for a in range(count):
                for b in range(count):
                    q, r = divmod(a, b) if b else (0, a)
                    initial = a | (b << width)
                    expected = initial | (q << (2 * width)) | (r << (3 * width))
                    self.assertEqual(apply_basis(gates, initial), expected)
                    self.assertEqual(apply_basis(gates, expected), initial)
                    checked += 1
        print(f"Verified {checked} divisions including zero-divisor convention and clean history by logical gate propagation.")

    def test_arbitrary_outputs(self):
        width = 2
        gates = compile_x_permutation(binary_divide(width))
        for a in range(4):
            for b in range(4):
                q, r = divmod(a, b) if b else (0, a)
                for q_out in range(4):
                    for r_out in range(4):
                        initial = a | (b << 2) | (q_out << 4) | (r_out << 6)
                        expected = a | (b << 2) | ((q_out ^ q) << 4) | ((r_out ^ r) << 6)
                        self.assertEqual(apply_basis(gates, initial), expected)

    def test_complex_superposition_and_inverse(self):
        circuit = binary_divide(1)
        rng = np.random.default_rng(20261007)
        amplitudes = rng.normal(size=16) + 1j * rng.normal(size=16)
        amplitudes /= np.linalg.norm(amplitudes)
        data = np.zeros(1 << circuit.num_qubits, dtype=complex)
        data[:16] = amplitudes
        expected = np.zeros_like(data)
        for index, amplitude in enumerate(amplitudes):
            a, b = index & 1, (index >> 1) & 1
            q, r = divmod(a, b) if b else (0, a)
            expected[index ^ (q << 2) ^ (r << 3)] = amplitude
        actual = Statevector(data).evolve(circuit)
        np.testing.assert_allclose(actual.data, expected, atol=1e-10, rtol=0)
        np.testing.assert_allclose(actual.evolve(circuit.inverse()).data, data, atol=1e-10, rtol=0)
