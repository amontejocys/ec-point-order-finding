"""Independent small-integer reference and controlled Miller-Rabin branches."""

import math
import unittest
from unittest.mock import patch

from quantum_ec.classical.primality import check_primality


class PrimalityTests(unittest.TestCase):
    def test_small_integers_against_trial_division(self):
        # Every composite below 1600 has a factor <=37, so this test is exact.
        for n in range(-2, 1600):
            expected = n >= 2 and all(n % d for d in range(2, math.isqrt(n) + 1))
            observed = check_primality(n, rounds=2)['classification'] in {'prime', 'probable_prime'}
            self.assertEqual(observed, expected, n)

    def test_small_primes_and_composites_do_not_draw_randomness(self):
        with patch('quantum_ec.classical.primality.secrets.randbelow', side_effect=AssertionError):
            self.assertEqual(check_primality(5)['classification'], 'prime')
            self.assertEqual(check_primality(10)['classification'], 'composite')

    def test_requested_rounds_uniform_range_and_bound(self):
        with patch('quantum_ec.classical.primality.secrets.randbelow', return_value=0) as draw:
            result = check_primality(41)
        self.assertEqual(result['classification'], 'probable_prime')
        self.assertEqual(result['rounds_performed'], 64)
        self.assertEqual(result['fixed_composite_false_acceptance_bound'], '2^-128')
        self.assertEqual(draw.call_count, 64)
        draw.assert_called_with(38)

    def test_strong_pseudoprime_is_not_a_certificate(self):
        # 1373653 = 829*1657 is a strong pseudoprime to base 2, but not base 5.
        with patch('quantum_ec.classical.primality.secrets.randbelow', return_value=0):
            self.assertEqual(check_primality(1373653, rounds=1)['classification'], 'probable_prime')
        with patch('quantum_ec.classical.primality.secrets.randbelow', return_value=3):
            self.assertEqual(check_primality(1373653, rounds=1)['classification'], 'composite')

    def test_invalid_parameters(self):
        for n in (True, 5.0, '5', None):
            with self.assertRaises(ValueError):
                check_primality(n)
        for rounds in (0, -1, True, 1.5):
            with self.assertRaises(ValueError):
                check_primality(5, rounds=rounds)


if __name__ == '__main__':
    unittest.main()
