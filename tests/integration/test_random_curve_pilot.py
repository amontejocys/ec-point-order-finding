"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import unittest
from unittest.mock import patch
import numpy as np
from experiments.scripts.random_curve_pilot import sample_instances, wilson_interval
from quantum_ec.simulation.ideal_distribution import ideal_probabilities
from quantum_ec.recovery.factor_free_recovery import recover_prefixes
from tests.reference.curve import reference_order
from quantum_ec.simulation.sparse_order_finding import fourier_probabilities


class RandomCurvePilotTests(unittest.TestCase):
    def test_distribution_against_independent_fft(self):
        for q in (8, 16, 32, 64):
            for order in range(1, q+1):
                np.testing.assert_allclose(ideal_probabilities(q, order),
                                           fourier_probabilities([k % order for k in range(q)]),
                                           atol=2e-13)

    def test_sampling_and_independent_orders(self):
        left = sample_instances(np.random.default_rng(1234), [11, 17, 29], 4)
        right = sample_instances(np.random.default_rng(1234), [11, 17, 29], 4)
        self.assertEqual(left, right)
        self.assertEqual(len({(r['p'], r['a'], r['b']) for r in left}), 12)
        for row in left:
            p, a, b = row['p'], row['a'], row['b']
            x, y = row['point']
            self.assertNotEqual((4*a**3+27*b*b) % p, 0)
            self.assertEqual((y*y-x**3-a*x-b) % p, 0)
            self.assertEqual(row['reference_group_size'] % row['reference_order'], 0)
        self.assertEqual(reference_order((6, 7), 29, 0), 5)

    def test_recovery_without_reference_or_factoring(self):
        with patch('quantum_ec.baselines.trial_recovery.prime_factors_trial', side_effect=AssertionError):
            self.assertEqual(recover_prefixes([3, 15, 0], 32, (6, 7), 29, 0,
                                             [1, 2, 3], {}), {1: 10, 2: 5, 3: 5})

    def test_intervals_do_not_claim_certainty(self):
        self.assertGreater(wilson_interval(0, 100)[1], 0)
        self.assertLess(wilson_interval(100, 100)[0], 1)

    def test_sampling_rejects_impossible_requests(self):
        for primes, count in (([11, 11], 1), ([15], 1), ([5], 21), ([], 1), ([11], 0)):
            with self.assertRaises(ValueError):
                sample_instances(np.random.default_rng(123), primes, count)
