"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import unittest
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator, Statevector
from quantum_ec.circuits.arithmetic.equality_constant import equality_constant


class EqualityConstantTests(unittest.TestCase):
    def test_all_basis_inputs_and_constants(self):
        checked = 0
        for width in range(1, 7):
            count = 1 << width
            dimension = 2 * count
            for value in range(count):
                with self.subTest(width=width, value=value):
                    actual = Operator(equality_constant(width, value)).data
                    expected = np.zeros((dimension, dimension), dtype=complex)
                    for flag in (0, 1):
                        for z in range(count):
                            source = z | (flag << width)
                            target_flag = flag ^ int(z == value)
                            target = z | (target_flag << width)
                            expected[target, source] = 1.0
                            checked += 1
                    np.testing.assert_allclose(
                        actual, expected, atol=1e-12, rtol=0
                    )
        print(f"Verified {checked} basis transitions, including their phases.")

    def test_complex_superposition(self):
        width, value = 4, 9
        dimension = 1 << (width + 1)
        rng = np.random.default_rng(20261006)
        amplitudes = rng.normal(size=dimension) + 1j * rng.normal(size=dimension)
        amplitudes /= np.linalg.norm(amplitudes)
        initial = Statevector(amplitudes)
        actual = initial.evolve(equality_constant(width, value))
        expected = np.zeros(dimension, dtype=complex)
        for index, amplitude in enumerate(amplitudes):
            z = index & ((1 << width) - 1)
            target = index ^ ((1 << width) if z == value else 0)
            expected[target] = amplitude
        np.testing.assert_allclose(actual.data, expected, atol=1e-12, rtol=0)

    def test_indicator_cleanup(self):
        width, value = 3, 5
        preparation = QuantumCircuit(width + 1)
        preparation.h(range(width))
        initial = Statevector.from_instruction(preparation)
        comparator = equality_constant(width, value)
        marked = initial.evolve(comparator)
        # The flag is the highest-index qubit in this register layout.
        self.assertAlmostEqual(
            marked.probabilities([width])[1], 1 / (1 << width), places=12
        )
        restored = marked.evolve(comparator)
        np.testing.assert_allclose(restored.data, initial.data, atol=1e-12, rtol=0)
        self.assertAlmostEqual(restored.probabilities([width])[1], 0.0, places=12)

    def test_phase_kickback(self):
        width, value = 3, 5
        preparation = QuantumCircuit(width + 1)
        preparation.h(range(width))
        preparation.x(width)
        preparation.h(width)
        initial = Statevector.from_instruction(preparation)
        actual = initial.evolve(equality_constant(width, value))
        expected = initial.data.copy()
        for index in range(len(expected)):
            if (index & ((1 << width) - 1)) == value:
                expected[index] *= -1
        np.testing.assert_allclose(actual.data, expected, atol=1e-12, rtol=0)

    def test_invalid_parameters(self):
        for width, value in [(0, 0), (-1, 0), (2, -1), (2, 4), (2.5, 0)]:
            with self.subTest(width=width, value=value):
                with self.assertRaises(ValueError):
                    equality_constant(width, value)
