"""Standard Miller-Rabin (HAC Algorithm 4.24), not a primality certificate."""

import secrets

DEFAULT_PRIMALITY_ROUNDS = 64
SMALL_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)


def check_primality(value, *, rounds=DEFAULT_PRIMALITY_ROUNDS):
    """Classify an integer, with an explicit fixed-composite error bound.

    Beyond the small-prime checks, bases are independent uniform samples from
    [2,n-2]. A fixed odd composite passes all t rounds with probability at most
    4**(-t). This is not the posterior probability that an accepted value is
    composite. Small primes and detected composites have exact classifications.
    """
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError('value must be a Python integer')
    if not isinstance(rounds, int) or isinstance(rounds, bool) or rounds < 1:
        raise ValueError('rounds must be a positive integer')
    result = {'classification': 'composite', 'method': 'small_prime_checks',
              'rounds_requested': rounds, 'rounds_performed': 0,
              'fixed_composite_false_acceptance_bound': '0'}
    if value < 2:
        result['classification'] = 'not_prime'
        return result
    for prime in SMALL_PRIMES:
        if value == prime:
            result['classification'] = 'prime'
            return result
        if value % prime == 0:
            return result
    odd_part, powers_of_two = value - 1, 0
    while odd_part % 2 == 0:
        odd_part //= 2
        powers_of_two += 1
    result['method'] = 'miller_rabin'
    for index in range(rounds):
        base = secrets.randbelow(value - 3) + 2
        residue = pow(base, odd_part, value)
        result['rounds_performed'] = index + 1
        if residue in (1, value - 1):
            continue
        for _ in range(powers_of_two - 1):
            residue = residue * residue % value
            if residue == value - 1:
                break
        else:
            return result
    result['classification'] = 'probable_prime'
    result['fixed_composite_false_acceptance_bound'] = f'2^-{2 * rounds}'
    return result
