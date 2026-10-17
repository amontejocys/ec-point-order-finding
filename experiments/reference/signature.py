"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

from experiments.reference.curve import reference_add


def reference_attempt(z, private_key, nonce, order, point, p, a):
    """Independent benchmark: repeated reference additions and direct equation."""
    result = None
    for _ in range(nonce):
        result = reference_add(result, point, p, a)
    if result is None:
        return None
    r_sigma = result[0] % order
    if not r_sigma:
        return None
    try:
        s = (z+r_sigma*private_key)*pow(nonce, -1, order) % order
    except ValueError:
        return None
    return (r_sigma, s) if s else None
