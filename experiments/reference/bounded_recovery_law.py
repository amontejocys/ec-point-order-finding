"""Offline all-orders model; never an input to production recovery or signing."""

from collections import defaultdict
import math

import numpy as np

from experiments.reference.gcd_recovery_law import divisor_inversion_law
from quantum_ec.recovery.continued_fractions import convergent_denominators


OPERATION_COUNT_DEFINITION = {
    'cf_denominators_generated': 'Every yielded convergent denominator, including repeats, over all Q outcomes',
    'bounded_denominators_tested': 'Yielded denominators in [1,B], including repeats; matches production verification attempts',
    'divisibility_checks': 'One offline r-divides-v check per bounded denominator; not a scalar multiplication',
    'statistic_gcd_updates': 'One gcd update per distinct accepted denominator per outcome, starting at zero',
    'dp_gcd_updates': 'One gcd update per (current state, one-shot statistic) pair per DP step',
    'scope': 'Offline model operations only, not gates or scalable online costs',
}


def validate_domain(q, order, bound):
    if any(type(v) is not int for v in (q, order, bound)):
        raise ValueError('Q, order and bound must be Python integers')
    if q < 2 or q & (q - 1) or not 2 <= order <= bound <= q:
        raise ValueError('Expected power-of-two Q and 2 <= r <= B <= Q')


def accepted_by_order(y, q, order, bound, counts=None):
    """r | v iff vP=O for true order r; only the offline model knows r."""
    validate_domain(q, order, bound)
    if type(y) is not int or not 0 <= y < q:
        raise ValueError('Outcome outside [0,Q)')
    accepted = set()
    for v in convergent_denominators(y, q):
        if counts is not None:
            counts['cf_denominators_generated'] += 1
        if 1 <= v <= bound:
            if counts is not None:
                counts['bounded_denominators_tested'] += 1
                counts['divisibility_checks'] += 1
            if v % order == 0:
                accepted.add(v)
    return sorted(accepted)


def raw_probabilities(q, order):
    """Finite fiber law, without the production simulator's normalization step."""
    validate_domain(q, order, order)
    length, remainder = divmod(q, order)
    residues = (order * np.arange(q, dtype=np.int64)) % q
    phase = residues.astype(float) / q
    phase = np.where(phase > .5, phase - 1, phase)

    def squared(n):
        return (n * np.sinc(n * phase) / np.sinc(phase)) ** 2

    return (remainder * squared(length + 1)
            + (order - remainder) * squared(length)) / q**2


def one_shot_by_order(q, order, bound, tolerance=1e-10):
    validate_domain(q, order, bound)
    probabilities = raw_probabilities(q, order)
    mass_error = abs(float(probabilities.sum()) - 1)
    if not np.isfinite(probabilities).all() or probabilities.min() < 0 or mass_error > tolerance:
        raise ArithmeticError('Invalid raw finite probability distribution')
    counts = {key: 0 for key in OPERATION_COUNT_DEFINITION if key != 'scope'}
    weights = defaultdict(float)
    for y, probability in enumerate(probabilities):
        d = 0
        for v in accepted_by_order(y, q, order, bound, counts):
            d = math.gcd(d, v)
            counts['statistic_gcd_updates'] += 1
        weights[d] += float(probability)
    return dict(sorted(weights.items())), counts, mass_error


def advance_law(state, weights, counts=None):
    """Works with float, Fraction, mpmath mpf and interval values."""
    following = defaultdict(int)
    for g, mass in state.items():
        for d, weight in weights.items():
            following[math.gcd(g, d)] += mass * weight
            if counts is not None:
                counts['dp_gcd_updates'] += 1
    return dict(following)


def checked_outcomes(state, weights, order, shots, tolerance):
    inverted = divisor_inversion_law(weights, shots)
    residual = max(abs(float(state.get(g, 0) - inverted.get(g, 0)))
                   for g in set(state) | set(inverted))
    exact = float(state.get(order, 0))
    none = float(state.get(0, 0))
    nonminimal = float(sum(m for g, m in state.items() if g not in (0, order)))
    mass_error = abs(exact + none + nonminimal - 1)
    lower = 1 - (1 - float(weights.get(order, 0))) ** shots
    if (any(not math.isfinite(float(v)) or float(v) < -tolerance for v in state.values())
            or residual > tolerance or mass_error > tolerance or exact + tolerance < lower):
        raise ArithmeticError('Finite recovery law validation failed')
    return {'shots': shots, 'exact_order': exact, 'no_candidate': none,
            'nonminimal': nonminimal, 'partition_residual': mass_error,
            'dp_vs_inversion_residual': residual, 'single_exact_event_lower_bound': lower}


def classify_threshold(probability, epsilon, tolerance):
    """Proximity is an unresolved numerical observation, never a certificate."""
    gap = probability - (1 - epsilon)
    if abs(gap) <= tolerance:
        return 'unresolved'
    return 'above' if gap > 0 else 'below'


def worst_orders(probabilities, tie_tolerance):
    minimum = min(probabilities.values())
    return minimum, sorted(r for r, p in probabilities.items() if p - minimum <= tie_tolerance)


def independent_denominators(y, q):
    """Reference CF calculation using the quotient list and backward evaluation."""
    quotients = []
    while q:
        term, remainder = divmod(y, q)
        quotients.append(term)
        y, q = q, remainder
    result = []
    for end in range(1, len(quotients) + 1):
        numerator, denominator = quotients[end - 1], 1
        for term in reversed(quotients[:end - 1]):
            numerator, denominator = term * numerator + denominator, numerator
        result.append(denominator)
    return result


def precision_weights(q, order, bound, digits=80, intervals=False):
    """Independent modular-phase sine formula; no FFT, normalization or float inputs."""
    validate_domain(q, order, bound)
    if type(digits) is not int or digits < 30:
        raise ValueError('At least 30 decimal digits required')
    try:
        import mpmath
    except ImportError as exc:
        raise RuntimeError('P2 reference requires mpmath; production dependencies are unchanged') from exc
    if intervals:
        from mpmath.ctx_iv import MPIntervalContext
        context = MPIntervalContext()
    else:
        context = mpmath.mp.clone()
    context.dps = digits
    weights = defaultdict(int)
    length, remainder = divmod(q, order)
    for y in range(q):
        phase = order * y % q
        if phase == 0:
            probability = context.mpf(remainder * (length + 1)**2
                                      + (order - remainder) * length**2) / q**2
        else:
            denominator = context.sin(context.pi * phase / q)**2

            def squared(n):
                numerator_phase = n * phase % q
                if numerator_phase == 0:
                    return context.mpf(0)
                return context.sin(context.pi * numerator_phase / q)**2 / denominator

            probability = (remainder * squared(length + 1)
                           + (order - remainder) * squared(length)) / q**2
        candidates = {v for v in independent_denominators(y, q)
                      if 1 <= v <= bound and v % order == 0}
        statistic = math.gcd(*candidates) if candidates else 0
        weights[statistic] += probability
    return dict(sorted(weights.items())), context


def precision_law(weights, shots):
    if type(shots) is not int or shots < 0:
        raise ValueError('Shots must be a nonnegative integer')
    state = {0: 1}
    for _ in range(shots):
        state = advance_law(state, weights)
    return state


def interval_endpoints(value, digits=80):
    """Decimal output only; never use rounded endpoint strings for decisions."""
    import mpmath
    context = mpmath.mp.clone()
    context.dps = digits
    lower, upper = value._mpi_
    return [context.nstr(context.make_mpf(lower), digits),
            context.nstr(context.make_mpf(upper), digits)]
