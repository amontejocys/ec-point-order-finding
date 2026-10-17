"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import unittest
import numpy as np
from qiskit.quantum_info import Operator, Statevector
from quantum_ec.circuits.arithmetic.binary_add_constant import binary_add_constant
from quantum_ec.circuits.arithmetic.less_than_constant import less_than_constant


class BinaryAddConstantTests(unittest.TestCase):
    def test_all_small_additions(self):
        checked = 0
        for width in range(1, 6):
            count = 1 << width
            for value in range(count):
                expected = np.zeros((count, count), dtype=complex)
                for z in range(count):
                    expected[(z + value) % count, z] = 1
                    checked += 1
                actual = Operator(binary_add_constant(width, value)).data
                np.testing.assert_allclose(actual, expected, atol=1e-12, rtol=0)
        print(f"Verified {checked} binary-addition basis transitions.")

    def test_negative_constant(self):
        actual = Operator(binary_add_constant(4, -5)).data
        expected = np.zeros((16, 16), dtype=complex)
        for z in range(16):
            expected[(z - 5) % 16, z] = 1
        np.testing.assert_allclose(actual, expected, atol=1e-12, rtol=0)


class LessThanConstantTests(unittest.TestCase):
    def test_basis_inputs_and_clean_work(self):
        configurations = [
            (width, limit)
            for width in range(1, 4)
            for limit in range((1 << width) + 1)
        ] + [(5, 29)]
        checked = 0
        for width, limit in configurations:
            comparator = less_than_constant(width, limit)
            count = 1 << width
            for flag in (0, 1):
                for x in range(count):
                    with self.subTest(width=width, limit=limit, x=x, flag=flag):
                        initial_index = x | (flag << width)
                        initial = Statevector.from_int(initial_index, 1 << comparator.num_qubits)
                        actual = initial.evolve(comparator)
                        expected_index = x | ((flag ^ int(x < limit)) << width)
                        expected = Statevector.from_int(expected_index, len(actual.data))
                        np.testing.assert_allclose(
                            actual.data, expected.data, atol=1e-11, rtol=0
                        )
                        checked += 1
        print(f"Verified {checked} range-check basis transitions with clean work.")

    def test_complex_superposition_and_cleanup(self):
        width, limit = 5, 29
        comparator = less_than_constant(width, limit)
        rng = np.random.default_rng(20261006)
        count = 1 << (width + 1)
        amplitudes = rng.normal(size=count) + 1j * rng.normal(size=count)
        amplitudes /= np.linalg.norm(amplitudes)
        initial_data = np.zeros(1 << comparator.num_qubits, dtype=complex)
        initial_data[:count] = amplitudes
        initial = Statevector(initial_data)
        actual = initial.evolve(comparator)
        expected = np.zeros_like(initial_data)
        for index, amplitude in enumerate(amplitudes):
            x = index & ((1 << width) - 1)
            target = index ^ ((1 << width) if x < limit else 0)
            expected[target] = amplitude
        np.testing.assert_allclose(actual.data, expected, atol=1e-11, rtol=0)
        restored = actual.evolve(comparator)
        np.testing.assert_allclose(restored.data, initial.data, atol=1e-11, rtol=0)

    def test_invalid_parameters(self):
        for width, limit in [(0, 0), (3, -1), (3, 9), (3, 2.5)]:
            with self.subTest(width=width, limit=limit):
                with self.assertRaises(ValueError):
                    less_than_constant(width, limit)
