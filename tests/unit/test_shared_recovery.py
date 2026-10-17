"""Shared policy, simulation-cache isolation and experiment wiring."""

import unittest
from unittest.mock import patch

import numpy as np
import quantum_ec.recovery.factor_free_recovery as recovery
from experiments.scripts import random_curve_pilot, real_circuit_recovery


class SharedRecoveryTests(unittest.TestCase):
    def test_prefixes_match_public_history_with_and_without_cache(self):
        for p, a, point, q in [(29, 0, (6, 7), 32), (5, 1, (2, 1), 64),
                               (7, 0, (3, 0), 64)]:
            measurements = list(range(q)) + [0, 3, 3]
            history = recovery.accumulate_verified_periods(measurements, q, point, p, a)['history']
            budgets = list(range(1, len(measurements) + 1))
            expected = {i: row['accumulated_period'] for i, row in enumerate(history, 1)}
            for cache in (None, {}):
                self.assertEqual(recovery.recover_prefixes(np.asarray(measurements), q,
                                                         point, p, a, budgets, cache), expected)

    def test_cache_is_scoped_to_the_complete_verification_domain(self):
        cache = {}
        with patch.object(recovery, 'verified_candidates', wraps=recovery.verified_candidates) as verify:
            recovery.recover_prefixes([3, 3], 32, (6, 7), 29, 0, [1, 2], cache)
            self.assertEqual(verify.call_count, 1)
            recovery.recover_prefixes([3], 64, (6, 7), 29, 0, [1], cache)
            recovery.recover_prefixes([3], 32, (12, 13), 29, 0, [1], cache)
            self.assertEqual(verify.call_count, 3)

    def test_both_adapters_use_the_authoritative_iterator(self):
        with patch.object(recovery, 'iter_verified_periods', wraps=recovery.iter_verified_periods) as core:
            recovery.accumulate_verified_periods([3, 15], 32, (6, 7), 29, 0)
            result = recovery.recover_prefixes([3, 15], 32, (6, 7), 29, 0, [1, 2], {})
            self.assertEqual(core.call_count, 2)
            self.assertEqual(result, {1: 10, 2: 5})

    def test_experiments_reuse_package_objects(self):
        self.assertIs(random_curve_pilot.recover_prefixes, recovery.recover_prefixes)
        self.assertIs(real_circuit_recovery.recover_prefixes, recovery.recover_prefixes)


if __name__ == '__main__':
    unittest.main()
