"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import unittest
from unittest.mock import patch
from quantum_ec.recovery.factor_free_recovery import accumulate_verified_periods, uniform_register_size
from quantum_ec.classical.curve import scalar_multiple


class FactorFreeRecoveryTests(unittest.TestCase):
    def test_actual_denominators_without_factoring(self):
        with patch("quantum_ec.baselines.trial_recovery.prime_factors_trial", side_effect=AssertionError("factoring called")):
            single = accumulate_verified_periods([3], 32, (6, 7), 29, 0)
            combined = accumulate_verified_periods([3, 15], 32, (6, 7), 29, 0)
        self.assertEqual(single["verified_period"], 10)
        self.assertFalse(single["minimality_certified"])
        self.assertEqual(combined["history"][1]["verified_multiples"], [15])
        self.assertEqual(combined["verified_period"], 5)
        self.assertFalse(combined["minimality_certified"])

    def test_empty_and_uninformative_outcomes(self):
        for outcomes in ([], [0], [0, 0]):
            result = accumulate_verified_periods(outcomes, 32, (6, 7), 29, 0)
            self.assertIsNone(result["verified_period"])

    def test_all_outcomes_and_multiple_curves(self):
        # Known orders are test references only, never recovery inputs.
        for p, a, point, order, q in (
            (29, 0, (6, 7), 5, 32),
            (5, 1, (2, 1), 3, 64),
            (7, 0, (3, 0), 2, 64),
        ):
            result = accumulate_verified_periods(range(q), q, point, p, a)
            previous = None
            for row in result["history"]:
                current = row["accumulated_period"]
                if current is not None:
                    self.assertEqual(current % order, 0)
                    self.assertIsNone(scalar_multiple(current, point, p, a))
                    if previous is not None:
                        self.assertEqual(previous % current, 0)
                    previous = current
            self.assertEqual(result["verified_period"], order)

    def test_exact_order_anchor_cannot_be_spoiled(self):
        result = accumulate_verified_periods([13, 3, 15, 0], 32, (6, 7), 29, 0)
        self.assertEqual([row["accumulated_period"] for row in result["history"]], [5, 5, 5, 5])

    def test_resolution_bound_without_known_order(self):
        self.assertEqual(uniform_register_size(29), {"order_upper_bound": 40, "m": 11, "q": 2048})
        for p in (5, 7, 17, 29, 101):
            result = uniform_register_size(p)
            self.assertGreater(result["q"], result["order_upper_bound"] ** 2)
            self.assertLessEqual(result["q"] // 2, result["order_upper_bound"] ** 2)

    def test_invalid_measurements_and_registers(self):
        for q in (0, 1, 3, True):
            with self.assertRaises(ValueError):
                accumulate_verified_periods([], q, (6, 7), 29, 0)
        for y in (-1, 32, True, 1.5):
            with self.assertRaises(ValueError):
                accumulate_verified_periods([y], 32, (6, 7), 29, 0)
