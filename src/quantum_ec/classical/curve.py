"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""




def classical_add(left, right, modulus, a):
    """Classical group operation for precomputing constants only; None is O."""
    if left is None:
        return right
    if right is None:
        return left
    x, y = left
    u, v = right
    if x == u:
        if (y + v) % modulus == 0:
            return None
        slope = (3*x*x + a)*pow(2*y % modulus, -1, modulus) % modulus
    else:
        slope = (y-v)*pow((x-u) % modulus, -1, modulus) % modulus
    result_x = (slope*slope-x-u) % modulus
    result_y = (slope*(x-result_x)-y) % modulus
    return result_x, result_y


def scalar_multiple(k, point, modulus, a):
    result = None
    while k:
        if k & 1:
            result = classical_add(result, point, modulus, a)
        point = classical_add(point, point, modulus, a)
        k >>= 1
    return result
