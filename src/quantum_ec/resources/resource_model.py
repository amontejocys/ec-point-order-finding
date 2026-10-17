"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""




def _width(width):
    if not isinstance(width, int) or isinstance(width, bool) or width < 1:
        raise ValueError("width must be a positive integer")


def binary_add_count(width, value):
    _width(width)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError("value must be an integer")
    value %= 1 << width
    return sum(width - shift for shift in range(width) if (value >> shift) & 1)


def less_than_constant_count(width, limit):
    _width(width)
    if not isinstance(limit, int) or isinstance(limit, bool) or not 0 <= limit <= 1 << width:
        raise ValueError("limit must fit the comparison domain")
    return 2 * width + 2 * binary_add_count(width + 1, -limit) + 1


def modular_add_count(width, modulus, value):
    _width(width)
    if not isinstance(modulus, int) or isinstance(modulus, bool) or not 2 <= modulus <= 1 << width:
        raise ValueError("modulus must be between 2 and 2**width")
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError("value must be an integer")
    value %= modulus
    return (
        2 * less_than_constant_count(width, modulus)
        + binary_add_count(width + 1, value)
        + less_than_constant_count(width + 1, modulus)
        + 1  # valid XOR reduce
        + binary_add_count(width + 1, -modulus)
        + less_than_constant_count(width + 1, value)
    )


def _sum_constants(width, modulus, values):
    modular_add_count(width, modulus, 0)  # Validate even if all terms are zero.
    return sum(modular_add_count(width, modulus, value)
               for value in values if value % modulus)


def modular_register_add_count(width, modulus):
    _width(width)
    return _sum_constants(width, modulus, (1 << j for j in range(width)))


def modular_multiply_count(width, modulus):
    _width(width)
    return _sum_constants(width, modulus,
                          (1 << (i + j) for i in range(width) for j in range(width)))


def modular_square_count(width, modulus):
    _width(width)
    values = [1 << (2 * i) for i in range(width)]
    values += [1 << (i + j + 1) for i in range(width) for j in range(i + 1, width)]
    return _sum_constants(width, modulus, values)


def modular_cube_count(width, modulus):
    return 2 * modular_square_count(width, modulus) + modular_multiply_count(width, modulus)


def equality_count(width, value):
    _width(width)
    if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value < 1 << width:
        raise ValueError("equality constant must fit in width")
    return 2 * (width - value.bit_count()) + 1


def binary_register_subtract_count(width, destination_width):
    _width(width)
    _width(destination_width)
    return sum(binary_add_count(destination_width, -(1 << bit)) for bit in range(width))


def less_than_register_count(width):
    _width(width)
    return 2 * width + 2 * binary_register_subtract_count(width, width + 1) + 1


def division_step_count(width):
    _width(width)
    return less_than_register_count(width) + 1 + binary_register_subtract_count(width, width)


def division_compute_count(width):
    _width(width)
    # Guard B=0, copy dividend/previous remainders, then width reduction steps.
    return equality_count(width, 0) + 1 + width * width + width * division_step_count(width + 1)


def binary_divide_count(width):
    return 2 * division_compute_count(width) + 2 * width


def binary_quotient_count(width):
    return 2 * division_compute_count(width) + width


def binary_quotient_qubits(width):
    _width(width)
    # Three width-bit input/output registers and the retained divider history.
    return width * width + 6 * width + 4


def binary_product_subtract_count(width):
    _width(width)
    return sum(binary_add_count(width, -(1 << (i + j)))
               for i in range(width) for j in range(width - i))


def compact_inverse_breakdown(width, modulus):
    modular_add_count(width, modulus, 0)
    if modulus == 1 << width:
        raise ValueError("modulus itself must fit in the remainder register")
    initialization = modulus.bit_count() + width + 1
    activation = equality_count(width, 0) + 1
    quotient = binary_quotient_count(width)
    binary_subtraction = binary_product_subtract_count(width)
    coefficient_subtraction = modular_multiply_count(width, modulus)
    controlled_swaps = 6 * width
    round_count = activation + quotient + binary_subtraction + coefficient_subtraction + controlled_swaps
    final_predicates = (
        less_than_constant_count(width, modulus)
        + equality_count(width, 0) + 1
        + equality_count(width, 1)
        + equality_count(width, 0)
    )
    rounds = 2 * width + 1
    compute = initialization + rounds * round_count + final_predicates
    return {
        "rounds": rounds,
        "initialization": initialization,
        "activation_per_round": activation,
        "quotient_per_round": quotient,
        "binary_subtraction_per_round": binary_subtraction,
        "coefficient_subtraction_per_round": coefficient_subtraction,
        "controlled_swaps_per_round": controlled_swaps,
        "instructions_per_round": round_count,
        "final_predicates": final_predicates,
        "compute_instructions": compute,
        "output_transfer": width,
        "total_instructions": 2 * compute + width,
        "total_qubits": 3 * width * width + 13 * width + 14,
    }


def compact_inverse_count(width, modulus):
    return compact_inverse_breakdown(width, modulus)["total_instructions"]


def curve_residual_count(width, modulus, a, b):
    modular_add_count(width, modulus, 0)
    a, b = a % modulus, b % modulus
    linear = _sum_constants(width, modulus, (-a * (1 << j) for j in range(width)))
    return (modular_square_count(width, modulus) + modular_cube_count(width, modulus)
            + linear + modular_add_count(width, modulus, -b))


def finite_curve_check_count(width, modulus, a, b):
    return (4 * less_than_constant_count(width, modulus)
            + 2 * curve_residual_count(width, modulus, a, b)
            + 2 * equality_count(width, 0) + 1)


def point_encoding_check_count(width, modulus, a, b):
    return 2 * finite_curve_check_count(width, modulus, a, b) + 4 * width + 4


def _point_constants(width, modulus, a, b, u, v):
    modular_add_count(width, modulus, 0)
    if modulus <= 3 or modulus % 2 == 0:
        raise ValueError("modulus is assumed prime greater than 3")
    if not all(isinstance(c, int) and not isinstance(c, bool) for c in (a, b, u, v)):
        raise ValueError("coefficients and coordinates must be integers")
    if not 0 <= u < modulus or not 0 <= v < modulus:
        raise ValueError("constant point coordinates must be canonical")
    if (v*v - u**3 - a*u - b) % modulus or (4*a**3 + 27*b*b) % modulus == 0:
        raise ValueError("constant point must lie on a nonsingular curve")
    encoding = (u << 1) | (v << (width + 1))
    negative = (u << 1) | (((-v) % modulus) << (width + 1))
    if v == 0:
        double_encoding = 1
    else:
        slope = (3*u*u + a) * pow((2*v) % modulus, -1, modulus) % modulus
        double_x = (slope*slope - 2*u) % modulus
        double_y = (slope*(u - double_x) - v) % modulus
        double_encoding = (double_x << 1) | (double_y << (width + 1))
    return encoding, negative, double_encoding


def point_cases_count(width, modulus, a, b, u, v):
    encoding, negative, _ = _point_constants(width, modulus, a, b, u, v)
    size = 2 * width + 1
    compute = (point_encoding_check_count(width, modulus, a, b)
               + equality_count(size, 1)
               + equality_count(size, encoding)
               + equality_count(size, negative))
    return 2 * compute + 12


def compact_ordinary_count(width, modulus, u, v):
    compute = (
        3 * width
        + 2 * modular_add_count(width, modulus, -u)
        + modular_add_count(width, modulus, -v)
        + compact_inverse_count(width, modulus)
        + 2 * modular_multiply_count(width, modulus)
        + modular_square_count(width, modulus)
        + 3 * modular_register_add_count(width, modulus)
    )
    return 2 * compute + 2 * width


def compact_evaluator_resources(width, modulus, a, b, u, v):
    encoding, _, double_encoding = _point_constants(width, modulus, a, b, u, v)
    size = 2 * width + 1
    cases = point_cases_count(width, modulus, a, b, u, v)
    ordinary = compact_ordinary_count(width, modulus, u, v)
    special = encoding.bit_count() + 1 + double_encoding.bit_count()
    invalid = 2 * equality_count(4, 0) + size
    case_work = 3 * width + 13
    ordinary_work = compact_inverse_breakdown(width, modulus)["total_qubits"] + 6 * width + 5
    pool = max(case_work, ordinary_work)
    return {
        "case_instructions": cases,
        "ordinary_instructions": ordinary,
        "special_instructions": special,
        "invalid_instructions": invalid,
        "total_instructions": 2 * cases + ordinary + special + invalid,
        "total_qubits": 2 * size + 5 + pool,
        "case_scratch_width": case_work,
        "ordinary_scratch_width": ordinary_work,
        "scratch_saved_by_pooling": min(case_work, ordinary_work),
    }


def compact_controlled_point_resources(width, modulus, a, b, u, v):
    forward = compact_evaluator_resources(width, modulus, a, b, u, v)
    backward = compact_evaluator_resources(width, modulus, a, b, u, (-v) % modulus)
    size = 2 * width + 1
    evaluator_work = max(forward["total_qubits"], backward["total_qubits"]) - 2 * size
    return {
        "forward_instructions": forward["total_instructions"],
        "backward_instructions": backward["total_instructions"],
        "controlled_swap_instructions": 3 * size,
        "total_instructions": forward["total_instructions"] + backward["total_instructions"] + 3 * size,
        "total_qubits": 1 + 2 * size + evaluator_work,
        "point_width": size,
        "clean_work_width": size + evaluator_work,
    }


def compact_scalar_resources(width, modulus, a, b, powers):
    """Count a scalar_update chain given its precomputed constants; exclude QFT.

    powers must start with a finite point, matching EllipticOrderFinding.
    Repeated constants still contribute once per circuit call, not per cache.
    """
    if not powers or powers[0] is None:
        raise ValueError("powers must start with the finite base point")
    adders = [compact_controlled_point_resources(width, modulus, a, b, *point)
              for point in powers if point is not None]
    if any(row["total_qubits"] != adders[0]["total_qubits"] for row in adders):
        raise ValueError("adder scratch dimensions differ")
    return {
        "m": len(powers),
        "controlled_additions": len(adders),
        "instructions_per_addition": [row["total_instructions"] for row in adders],
        "total_instructions": sum(row["total_instructions"] for row in adders),
        "total_qubits": len(powers) + adders[0]["total_qubits"] - 1,
        "point_width": adders[0]["point_width"],
        "clean_work_width": adders[0]["clean_work_width"],
    }
