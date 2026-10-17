"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

from quantum_ec.classical.curve import scalar_multiple
from quantum_ec.recovery.continued_fractions import verified_candidates


def prime_factors_trial(value):
    """Distinct prime factors by trial division: small-instance reference only."""
    factors = []
    divisor = 2
    while divisor * divisor <= value:
        if value % divisor == 0:
            factors.append(divisor)
            while value % divisor == 0:
                value //= divisor
        divisor = 3 if divisor == 2 else divisor + 2
    if value > 1:
        factors.append(value)
    return factors


def reduce_order_multiple(candidate, point, modulus, a):
    """Certify and reduce a positive multiple; no known order is supplied.

    Factoring uses trial division for this small experiment, not a scalable
    factorization implementation or a polynomial-time complexity claim.
    """
    if not isinstance(candidate, int) or isinstance(candidate, bool) or candidate < 1:
        raise ValueError("candidate must be a positive integer")
    if scalar_multiple(candidate, point, modulus, a) is not None:
        raise ValueError("candidate is not a multiple of the point order")
    reduced = candidate
    for prime in prime_factors_trial(candidate):
        while reduced % prime == 0:
            smaller = reduced // prime
            if scalar_multiple(smaller, point, modulus, a) is not None:
                break
            reduced = smaller
    return reduced


def recovered_orders(y, q, point, modulus, a):
    return sorted({reduce_order_multiple(d, point, modulus, a)
                   for d in verified_candidates(y, q, point, modulus, a)})
