"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

from quantum_ec.classical.curve import scalar_multiple
from quantum_ec.classical.curve import classical_add


def signing_attempt(z, private_key, nonce, order_candidate, point, p, a):
    """Return (r_sigma,s), or None when nonce must be retried.

    This function trusts its supplied domain order; it does NOT certify it.
    A nonminimal period may give incorrect signing parameters.
    """
    if (not isinstance(order_candidate, int) or isinstance(order_candidate, bool)
            or order_candidate < 2):
        raise ValueError('order_candidate must be an integer >= 2')
    if not 1 <= private_key < order_candidate or not 1 <= nonce < order_candidate:
        raise ValueError('Private key and nonce must lie in [1,order_candidate)')
    if not isinstance(z, int) or isinstance(z, bool) or z < 0:
        raise ValueError('z must be a nonnegative hash representative')
    result = scalar_multiple(nonce, point, p, a)
    if result is None:
        return None
    r_sigma = result[0] % order_candidate
    if not r_sigma:
        return None
    try:
        inverse = pow(nonce, -1, order_candidate)
    except ValueError:
        return None
    s = inverse*(z+r_sigma*private_key) % order_candidate
    return (r_sigma, s) if s else None


def verify_arithmetic(signature, z, public_key, order, point, p, a):
    """Toy verification equations with supplied domain and public key."""
    if signature is None:
        return False
    r_sigma, s = signature
    if not 1 <= r_sigma < order or not 1 <= s < order:
        return False
    try:
        inverse = pow(s, -1, order)
    except ValueError:
        return False
    u1, u2 = z*inverse % order, r_sigma*inverse % order
    result = classical_add(scalar_multiple(u1, point, p, a),
                           scalar_multiple(u2, public_key, p, a), p, a)
    return result is not None and result[0] % order == r_sigma
