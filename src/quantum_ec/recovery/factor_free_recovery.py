"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import math
from quantum_ec.recovery.continued_fractions import verified_candidates


def uniform_register_size(modulus):
    """Choose power-of-two Q strictly above B**2 using an unknown-order bound.

    B = floor(p + 1 + 2*sqrt(p)) bounds every point order by Hasse.
    This is a sufficient resolution choice, not a per-shot success guarantee.
    Primality is a caller precondition, not checked here.
    """
    if (not isinstance(modulus, int) or isinstance(modulus, bool)
            or modulus <= 3 or modulus % 2 == 0):
        raise ValueError("modulus must be an odd prime > 3 (primality assumed)")
    bound = modulus + 1 + math.isqrt(4 * modulus)
    m = (bound * bound).bit_length()
    return {"order_upper_bound": bound, "m": m, "q": 1 << m}


def iter_verified_periods(measurements, q, point, modulus, a, *, verification_cache=None):
    """Yield recovery history using the single authoritative gcd policy.

    Optional caller-owned caching accelerates simulations only. Keys include
    the complete verification domain; cached checks are not online cost savings.
    Inputs and optional cache are trusted experiment data, not cryptographic input.
    """
    if (not isinstance(q, int) or isinstance(q, bool)
            or q < 2 or q & (q - 1)):
        raise ValueError("q must be a power of two >= 2")
    accumulated = 0
    domain = (q, tuple(point) if point is not None else None, modulus, a)
    for y in measurements:
        if not isinstance(y, int) or isinstance(y, bool) or not 0 <= y < q:
            raise ValueError("measurement must be an integer in [0, q)")
        if verification_cache is None:
            candidates = verified_candidates(y, q, point, modulus, a)
        else:
            key = (*domain, y)
            if key not in verification_cache:
                verification_cache[key] = verified_candidates(y, q, point, modulus, a)
            candidates = verification_cache[key]
        for candidate in candidates:
            accumulated = math.gcd(accumulated, candidate)
        yield {"measurement": y, "verified_multiples": candidates,
               "accumulated_period": accumulated or None}


def accumulate_verified_periods(measurements, q, point, modulus, a):
    """Return verified-period gcd and history, without certifying minimality."""
    rows = list(iter_verified_periods(measurements, q, point, modulus, a))
    return {"verified_period": rows[-1]["accumulated_period"] if rows else None,
            "minimality_certified": False, "history": rows}


def recover_prefixes(measurements, q, point, p, a, budgets, cache=None):
    """Observe the same policy at chosen shot budgets, optionally with caching.

    int conversion retains the legacy experiment adapter for NumPy samples;
    accumulate_verified_periods retains strict Python-int measurement validation.
    """
    rows = iter_verified_periods((int(y) for y in measurements), q, point, p, a,
                                 verification_cache=cache)
    return {shot: row["accumulated_period"] for shot, row in enumerate(rows, 1)
            if shot in budgets}
