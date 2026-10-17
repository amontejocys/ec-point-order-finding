"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import math
import unittest
import numpy as np
from qiskit.quantum_info import Statevector
from quantum_ec.circuits.arithmetic.binary_quotient import binary_quotient
from quantum_ec.circuits.arithmetic.modular_inverse import modular_inverse
from quantum_ec.circuits.arithmetic.modular_inverse_inplace import modular_inverse_inplace
from tests.support.permutation import apply_basis, compile_x_permutation


class CompactInverseTests(unittest.TestCase):
    def test_quotient_with_arbitrary_output(self):
        for width in (1, 2, 3):
            count = 1 << width
            gates = compile_x_permutation(binary_quotient(width))
            for a in range(count):
                for b in range(count):
                    for output in range(count):
                        initial = a | (b << width) | (output << (2 * width))
                        q = a // b if b else 0
                        expected = a | (b << width) | ((output ^ q) << (2 * width))
                        self.assertEqual(apply_basis(gates, initial), expected)

    def test_quotient_superposition(self):
        circuit = binary_quotient(1)
        rng = np.random.default_rng(20261007)
        amplitudes = rng.normal(size=8) + 1j*rng.normal(size=8)
        amplitudes /= np.linalg.norm(amplitudes)
        data = np.zeros(1 << circuit.num_qubits, dtype=complex)
        data[:8] = amplitudes
        expected = np.zeros_like(data)
        for index, amplitude in enumerate(amplitudes):
            a, b = index & 1, (index >> 1) & 1
            q = a // b if b else 0
            expected[index ^ (q << 2)] = amplitude
        actual = Statevector(data).evolve(circuit)
        np.testing.assert_allclose(actual.data, expected, atol=1e-10, rtol=0)

    def test_compact_inverse_and_resource_comparison(self):
        checked = 0
        for width, modulus in ((2, 3), (3, 5), (3, 7), (4, 9), (5, 29)):
            circuit = modular_inverse_inplace(width, modulus)
            gates = compile_x_permutation(circuit)
            for d in range(1 << width):
                inverse = pow(d, -1, modulus) if 0 < d < modulus and math.gcd(d, modulus) == 1 else 0
                for output in (0, (1 << width)-1):
                    initial = d | (output << width)
                    expected = d | ((output ^ inverse) << width)
                    self.assertEqual(apply_basis(gates, initial), expected)
                    self.assertEqual(apply_basis(gates, expected), initial)
                    checked += 1
            if modulus == 29:
                baseline = modular_inverse(width, modulus)
                self.assertLess(circuit.num_qubits, baseline.num_qubits)
                print(f"p=29 inverse: baseline {baseline.num_qubits} qubits / {len(baseline.data)} logical instructions; in-place {circuit.num_qubits} qubits / {len(circuit.data)} logical instructions.")
        print(f"Verified {checked} inverse transitions including invalid inputs and nonunits, with clean scratch by logical gate propagation.")
