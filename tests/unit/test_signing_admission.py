"""Exact toy order tests and explicit failure/status separation."""

import unittest
from unittest.mock import patch

from quantum_ec.recovery.factor_free_recovery import accumulate_verified_periods
from quantum_ec.signing.admission import admit_signing_order, OrderAdmissionError
from quantum_ec.signing.signature import signing_attempt


class SigningAdmissionTests(unittest.TestCase):
    def test_valid_prime_order_admission(self):
        result = admit_signing_order(5, (6, 7), 29, 0, b=7)
        self.assertEqual(result['status'], 'admitted')
        self.assertEqual(result['order_assurance'], 'exact')
        self.assertEqual(result['primality']['classification'], 'prime')
        larger = admit_signing_order(53, (28, 40), 41, 31, b=18)
        self.assertEqual(larger['status'], 'admitted')
        self.assertEqual(larger['primality']['method'], 'miller_rabin')
        self.assertEqual(larger['order_assurance'], 'conditional_on_probable_primality')

    def test_nonminimal_and_composite_true_orders_are_rejected(self):
        for candidate in (10, 15, 20):
            self.assertEqual(admit_signing_order(candidate, (6, 7), 29, 0)['reason'], 'candidate_not_prime')
        # (0,1) on y^2=x^3+x+1 over F5 has true order 9.
        self.assertEqual(admit_signing_order(9, (0, 1), 5, 1, b=1)['reason'], 'candidate_not_prime')

    def test_primality_alone_is_not_enough(self):
        self.assertEqual(admit_signing_order(7, (6, 7), 29, 0)['reason'],
                         'candidate_does_not_annihilate_point')
        self.assertEqual(admit_signing_order(5, None, 29, 0)['reason'], 'identity_point')
        self.assertEqual(admit_signing_order(41, (6, 7), 29, 0)['reason'], 'candidate_above_hasse_bound')

    def test_recovery_failure_and_invalid_order_are_distinct(self):
        for candidate in (None, 0):
            self.assertEqual(admit_signing_order(candidate, (6, 7), 29, 0)['status'], 'recovery_failure')
        for candidate in (1, -1, True, 5.0, '5'):
            self.assertEqual(admit_signing_order(candidate, (6, 7), 29, 0)['reason'], 'invalid_order_candidate')

    def test_point_and_curve_checks_when_b_is_supplied(self):
        self.assertEqual(admit_signing_order(5, (6, 8), 29, 0, b=7)['reason'], 'point_not_on_curve')
        self.assertEqual(admit_signing_order(2, (0, 0), 5, 0, b=0)['reason'], 'singular_curve')
        for point in ((29, 0), (1,), (True, 1), 'point'):
            self.assertEqual(admit_signing_order(5, point, 29, 0)['reason'], 'invalid_point_encoding')

    def test_order_two_remains_a_valid_arithmetic_test_not_secure_ecdsa(self):
        self.assertEqual(admit_signing_order(2, (0, 0), 5, 1, b=0)['status'], 'admitted')

    def test_probable_prime_assurance_is_not_reported_as_exact(self):
        with patch('quantum_ec.signing.admission.check_primality', return_value={
            'classification': 'probable_prime', 'fixed_composite_false_acceptance_bound': '2^-128'
        }):
            result = admit_signing_order(5, (6, 7), 29, 0)
        self.assertEqual(result['order_assurance'], 'conditional_on_probable_primality')

    def test_general_recovery_still_returns_composite_candidates(self):
        result = accumulate_verified_periods([3], 32, (6, 7), 29, 0)
        self.assertEqual(result['verified_period'], 10)
        self.assertFalse(result['minimality_certified'])
        with patch('quantum_ec.signing.signature.scalar_multiple', side_effect=AssertionError('nonce multiplication ran')):
            with self.assertRaises(OrderAdmissionError):
                signing_attempt(2, 2, 1, result['verified_period'], (6, 7), 29, 0)

    def test_bad_policy_or_field_parameters_are_errors(self):
        for rounds in (0, True, 1.5):
            with self.assertRaises(ValueError):
                admit_signing_order(5, (6, 7), 29, 0, primality_rounds=rounds)
        with self.assertRaises(ValueError):
            admit_signing_order(5, (6, 7), 4, 0)


if __name__ == '__main__':
    unittest.main()
