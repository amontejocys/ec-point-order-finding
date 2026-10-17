"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import math
import unittest
from quantum_ec.simulation.ideal_distribution import ideal_probabilities
from quantum_ec.recovery.continued_fractions import convergent_denominators
from quantum_ec.recovery.success_budget import sufficient_budget


class SuccessBudgetTests(unittest.TestCase):
    def test_good_events_and_finite_bound(self):
        for order in range(2, 65):
            q = 1 << (order*order).bit_length()
            good_y = []
            for s in range(1, order):
                if math.gcd(s, order) == 1:
                    # Exact nearest-integer rounding with upward tie breaking.
                    y = (2*q*s+order)//(2*order)
                    self.assertIn(order, list(convergent_denominators(y, q)))
                    good_y.append(y)
            self.assertEqual(len(set(good_y)), len(good_y))
            lower = len(good_y)/(16*order)
            self.assertGreaterEqual(float(ideal_probabilities(q, order)[good_y].sum())+1e-12, lower)
            self.assertGreaterEqual(lower+1e-12, 1/(16*order.bit_length()))

    def test_budget_and_unknown_order(self):
        result = sufficient_budget(29, 0.01)
        self.assertEqual(result["q"], 2048)
        self.assertEqual(result["sufficient_independent_ideal_shots"], 443)
        alpha = result["per_shot_success_lower_bound"]
        shots = result["sufficient_independent_ideal_shots"]
        self.assertLessEqual(math.exp(-alpha*shots), 0.01)

    def test_invalid_failure_probabilities(self):
        for value in (0, 1, -0.1, float('nan'), True, '0.01'):
            with self.assertRaises(ValueError):
                sufficient_budget(29, value)
