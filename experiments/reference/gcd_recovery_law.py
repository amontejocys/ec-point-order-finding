"""Offline finite-law model of the existing recovery policy, not a new solver."""

from collections import defaultdict
import math

from quantum_ec.recovery.continued_fractions import verified_candidates
from quantum_ec.simulation.ideal_distribution import ideal_probabilities


def validate_weights(weights):
    if not weights or any(type(d) is not int or d < 0 for d in weights):
        raise ValueError('States must be nonnegative Python integers')
    if any(not math.isfinite(float(w)) or w < 0 for w in weights.values()):
        raise ValueError('Weights must be finite and nonnegative')
    if not math.isclose(float(sum(weights.values())), 1, abs_tol=1e-12, rel_tol=0):
        raise ValueError('Weights must sum to one')


def one_shot_law(q, point, p, a, order):
    """Numerically sum all outcomes; supplied order is an evaluation reference."""
    weights = defaultdict(float)
    for y, probability in enumerate(ideal_probabilities(q, order)):
        candidates = verified_candidates(y, q, point, p, a)
        if any(d % order for d in candidates):
            raise AssertionError('Reference order disagrees with verified candidates')
        d = math.gcd(*candidates) if candidates else 0
        weights[d] += float(probability)
    validate_weights(weights)
    return dict(sorted(weights.items()))


def gcd_law(weights, shots):
    """DP recurrence, retaining rational arithmetic if weights are Fraction."""
    validate_weights(weights)
    if type(shots) is not int or shots < 0:
        raise ValueError('Shots must be a nonnegative Python integer')
    state = {0: 1}
    for _ in range(shots):
        following = defaultdict(int)
        for g, mass in state.items():
            for d, weight in weights.items():
                following[math.gcd(g, d)] += mass * weight
        state = dict(following)
    return state


def divisor_inversion_law(weights, shots):
    """Independent divisibility-poset inversion; no Markov transitions."""
    validate_weights(weights)
    if type(shots) is not int or shots < 0:
        raise ValueError('Shots must be a nonnegative Python integer')
    zero = weights.get(0, 0) ** shots
    law = {0: zero}
    maximum = max(weights)
    for g in range(maximum, 0, -1):
        divisible = sum(w for d, w in weights.items() if d % g == 0)
        law[g] = divisible**shots - zero - sum(
            law[multiple] for multiple in range(2*g, maximum+1, g))
    return law


def is_prime_small(value):
    """Exact trial reference for bounded offline experiments, not M1 policy."""
    return value >= 2 and all(value % d for d in range(2, math.isqrt(value)+1))


def admission_summary(law, order, rounds=64):
    """Exact ideal classification plus the actual policy's false-pass bound."""
    from quantum_ec.classical.primality import SMALL_PRIMES

    if type(rounds) is not int or rounds < 1:
        raise ValueError('Rounds must be positive')
    if order < 2 or any(g and g % order for g in law):
        raise ValueError('Only multiples of a nonidentity point order are allowed')
    prime = is_prime_small(order)
    uncertain = sum(mass for g, mass in law.items() if g and not is_prime_small(g)
                    and not any(g % s == 0 for s in SMALL_PRIMES))
    return {
        'recovery_failure': law.get(0, 0),
        'admitted_correct': law.get(order, 0) if prime else 0,
        'rejected_exact_composite_order_ideal': law.get(order, 0) if not prime else 0,
        'rejected_nonminimal_ideal': sum(m for g, m in law.items() if g not in (0, order)),
        'incorrect_admission_lower_bound': 0,
        'incorrect_admission_upper_bound': uncertain * 4**(-rounds),
        'admission_partition_exact_for_policy': uncertain == 0,
    }
