"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import math


def reference_add(left, right, p, a):
    """Independent benchmark arithmetic, not the production helper."""
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    numerator, denominator = ((3*x1*x1+a, 2*y1) if left == right
                              else (y2-y1, x2-x1))
    slope = numerator * pow(denominator % p, -1, p) % p
    x3 = (slope*slope-x1-x2) % p
    return x3, (slope*(x1-x3)-y1) % p


def reference_order(point, p, a):
    current = None
    for k in range(1, p + 2 + math.isqrt(4*p)):
        current = reference_add(current, point, p, a)
        if current is None:
            return k
    raise AssertionError("Reference order exceeds Hasse bound")
