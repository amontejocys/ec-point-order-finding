"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import math
from quantum_ec.classical.curve import scalar_multiple


def convergent_denominators(numerator, denominator):
    p_old, p_current = 0, 1
    q_old, q_current = 1, 0
    while denominator:
        quotient, remainder = divmod(numerator, denominator)
        p_old, p_current = p_current, quotient * p_current + p_old
        q_old, q_current = q_current, quotient * q_current + q_old
        yield q_current
        numerator, denominator = denominator, remainder


def verified_candidates(y, q, point, modulus, a):
    """A candidate is a verified multiple of the order, not necessarily the order."""
    bound = modulus + 1 + math.isqrt(4 * modulus)
    return sorted({d for d in convergent_denominators(y, q)
                   if 1 <= d <= bound and scalar_multiple(d, point, modulus, a) is None})
