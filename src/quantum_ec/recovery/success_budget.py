"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import math
from quantum_ec.recovery.factor_free_recovery import uniform_register_size


def sufficient_budget(modulus, failure_probability):
    if (isinstance(failure_probability, bool)
            or not isinstance(failure_probability, (int, float))
            or not 0 < failure_probability < 1):
        raise ValueError("failure_probability must lie strictly between 0 and 1")
    register = uniform_register_size(modulus)
    divisor = 16 * register["order_upper_bound"].bit_length()
    shots = math.ceil(divisor * -math.log(failure_probability))
    return {**register, "per_shot_success_lower_bound": 1/divisor,
            "target_failure_probability": failure_probability,
            "sufficient_independent_ideal_shots": shots,
            "scope": "Sufficient conservative bound, not a certificate or empirical rate"}
