"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import unittest
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator, Statevector
from quantum_ec.circuits.order_finding.elliptic_order_finding import inverse_qft_gate
from quantum_ec.simulation.sparse_order_finding import fourier_probabilities
from quantum_ec.baselines.trial_recovery import prime_factors_trial, recovered_orders, reduce_order_multiple
from quantum_ec.classical.curve import scalar_multiple
from quantum_ec.recovery.continued_fractions import verified_candidates


class SparseFourierTests(unittest.TestCase):
    def test_matrix_convention(self):
        for m in range(1, 7):
            q = 1 << m
            np.testing.assert_allclose(
                np.fft.fft(np.eye(q), axis=0, norm="ortho"),
                Operator(inverse_qft_gate(m)).data, atol=1e-12,
            )

    def test_joint_statevector_and_partial_trace_probabilities(self):
        for outputs in ([0] * 8, list(range(8)), [0, 1, 2, 0, 1, 2, 0, 1]):
            state = np.zeros(64, dtype=complex)
            for k, label in enumerate(outputs):
                state[k | (label << 3)] = 1 / np.sqrt(8)
            circuit = QuantumCircuit(6)
            circuit.append(inverse_qft_gate(3), range(3))
            expected = Statevector(state).evolve(circuit).probabilities([0, 1, 2])
            np.testing.assert_allclose(fourier_probabilities(outputs), expected, atol=1e-12)

    def test_candidate_verification_not_just_fraction_denominator(self):
        for y in (6, 13, 19, 26):
            self.assertIn(5, verified_candidates(y, 32, (6, 7), 29, 0))
        self.assertEqual(verified_candidates(0, 32, (6, 7), 29, 0), [])

    def test_reduce_multiples_without_known_order_argument(self):
        for candidate in (5, 10, 15, 25, 30, 50, 75, 125):
            self.assertEqual(reduce_order_multiple(candidate, (6, 7), 29, 0), 5)
        for candidate in (3, 6, 9, 12, 27):
            self.assertEqual(reduce_order_multiple(candidate, (2, 1), 5, 1), 3)
        self.assertEqual(reduce_order_multiple(12, None, 5, 1), 1)

    def test_composite_order_and_minimality(self):
        # (0,1) has composite order 9 on y^2=x^3+x+1 over F5.
        for candidate in (9, 18, 27, 36, 81):
            result = reduce_order_multiple(candidate, (0, 1), 5, 1)
            self.assertEqual(result, 9)
            self.assertIsNone(scalar_multiple(result, (0, 1), 5, 1))
            for divisor in range(1, result):
                self.assertIsNotNone(scalar_multiple(divisor, (0, 1), 5, 1))

    def test_invalid_order_candidates(self):
        for candidate in (0, -5, True, 5.0, 1, 2, 6, 32):
            with self.assertRaises(ValueError):
                reduce_order_multiple(candidate, (6, 7), 29, 0)

    def test_recovery_from_all_measurements(self):
        accepted = []
        for y in range(32):
            orders = recovered_orders(y, 32, (6, 7), 29, 0)
            self.assertIn(orders, ([], [5]))
            if orders:
                accepted.append(y)
        self.assertEqual(accepted, [3, 6, 7, 13, 15, 17, 19, 25, 26, 29])

    def test_reference_factorization(self):
        for value, factors in ((1, []), (5, [5]), (12, [2, 3]), (75, [3, 5]), (125, [5])):
            self.assertEqual(prime_factors_trial(value), factors)
