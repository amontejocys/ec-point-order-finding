"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""




def expected_sum_encoding(enc, width, p, a, b, u, v):
    identity = enc & 1
    x = (enc >> 1) & ((1 << width) - 1)
    y = enc >> (width + 1)
    if identity:
        return (u << 1) | (v << (width + 1)) if x == y == 0 else enc
    if x >= p or y >= p or (y*y-x**3-a*x-b) % p:
        return enc
    if x == u:
        if (y+v) % p == 0:
            return 1
        slope = (3*x*x+a)*pow(2*y, -1, p) % p
    else:
        slope = (y-v)*pow((x-u) % p, -1, p) % p
    result_x = (slope*slope-x-u) % p
    result_y = (slope*(x-result_x)-y) % p
    return (result_x << 1) | (result_y << (width + 1))
