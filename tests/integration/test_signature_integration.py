"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import unittest
from quantum_ec.signing.signature import signing_attempt, verify_arithmetic
from tests.reference.signature import reference_attempt
from quantum_ec.classical.curve import scalar_multiple
from quantum_ec.signing.admission import OrderAdmissionError


class SignatureIntegrationTests(unittest.TestCase):
    def test_all_small_domain_signing_inputs(self):
        accepted = rejected = 0
        for private_key in range(1, 5):
            public = scalar_multiple(private_key, (6, 7), 29, 0)
            for nonce in range(1, 5):
                for z in range(5):
                    actual = signing_attempt(z, private_key, nonce, 5, (6, 7), 29, 0)
                    expected = reference_attempt(z, private_key, nonce, 5, (6, 7), 29, 0)
                    self.assertEqual(actual, expected)
                    if actual is None:
                        rejected += 1
                    else:
                        accepted += 1
                        self.assertTrue(verify_arithmetic(actual, z, public, 5, (6, 7), 29, 0))
        self.assertEqual((accepted, rejected), (64, 16))

    def test_example_and_nonminimal_period_is_rejected(self):
        actual = signing_attempt(2, 2, 1, 5, (6, 7), 29, 0)
        self.assertEqual(actual, (1, 4))
        with self.assertRaises(OrderAdmissionError) as error:
            signing_attempt(2, 2, 1, 10, (6, 7), 29, 0)
        self.assertEqual(error.exception.status, 'order_not_admissible_for_signing')
        self.assertEqual(error.exception.reason, 'candidate_not_prime')

    def test_rejections(self):
        self.assertIsNone(signing_attempt(3, 2, 1, 5, (6, 7), 29, 0))
        for order in (0, 1, True):
            with self.assertRaises(ValueError):
                signing_attempt(2, 2, 1, order, (6, 7), 29, 0)
