"""Order admission for toy signing, distinct from general order recovery."""

from quantum_ec.classical.curve import scalar_multiple
from quantum_ec.classical.primality import check_primality, DEFAULT_PRIMALITY_ROUNDS
from quantum_ec.recovery.factor_free_recovery import uniform_register_size


class OrderAdmissionError(ValueError):
    """Explicit recovery/admission status; not a request to retry the nonce."""

    def __init__(self, admission):
        self.admission = admission
        self.status = admission['status']
        self.reason = admission['reason']
        super().__init__(f'{self.status}: {self.reason}')


def admit_signing_order(candidate, point, p, a, *, b=None,
                       primality_rounds=DEFAULT_PRIMALITY_ROUNDS):
    """Admit only a nonidentity point annihilated by an accepted prime candidate.

    Caller must supply a prime field p>3 and a valid nonsingular curve. If b is
    provided, its nonsingularity and the point equation are also checked; if b
    is omitted, on-curve validity remains a caller precondition. Field primality
    and cryptographic domain security are not established by this order gate.
    """
    bound = uniform_register_size(p)['order_upper_bound']
    if not isinstance(a, int) or isinstance(a, bool):
        raise ValueError('a must be an integer')
    if b is not None and (not isinstance(b, int) or isinstance(b, bool)):
        raise ValueError('b must be an integer when supplied')
    if (not isinstance(primality_rounds, int) or isinstance(primality_rounds, bool)
            or primality_rounds < 1):
        raise ValueError('primality_rounds must be a positive integer')
    result = {'status': 'order_not_admissible_for_signing', 'reason': None,
              'order_candidate': candidate, 'primality': None,
              'order_assurance': None,
              'curve_check': 'caller_precondition' if b is None else 'equation_and_nonsingularity'}
    if candidate is None or (type(candidate) is int and candidate == 0):
        result.update(status='recovery_failure', reason='no_order_candidate')
        return result
    if not isinstance(candidate, int) or isinstance(candidate, bool) or candidate < 2:
        result['reason'] = 'invalid_order_candidate'
        return result
    if point is None:
        result['reason'] = 'identity_point'
        return result
    if (not isinstance(point, (tuple, list)) or len(point) != 2
            or any(not isinstance(c, int) or isinstance(c, bool) or not 0 <= c < p for c in point)):
        result['reason'] = 'invalid_point_encoding'
        return result
    x, y = point
    if b is not None:
        if (4 * a**3 + 27 * b*b) % p == 0:
            result['reason'] = 'singular_curve'
            return result
        if (y*y - x**3 - a*x - b) % p:
            result['reason'] = 'point_not_on_curve'
            return result
    if candidate > bound:
        result['reason'] = 'candidate_above_hasse_bound'
        return result
    primality = check_primality(candidate, rounds=primality_rounds)
    result['primality'] = primality
    if primality['classification'] not in {'prime', 'probable_prime'}:
        result['reason'] = 'candidate_not_prime'
        return result
    if scalar_multiple(candidate, tuple(point), p, a) is not None:
        result['reason'] = 'candidate_does_not_annihilate_point'
        return result
    result.update(status='admitted', reason='accepted_candidate_annihilates_nonidentity_point',
                  order_assurance='exact' if primality['classification'] == 'prime'
                  else 'conditional_on_probable_primality')
    return result
