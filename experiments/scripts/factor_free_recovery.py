"""Migrated R6 example entry point; uses the shared package recovery policy."""

import json

from quantum_ec.recovery.factor_free_recovery import uniform_register_size
from quantum_ec.recovery.factor_free_recovery import accumulate_verified_periods

def main():
    print(json.dumps({'illustrative_outcomes_not_sampled': accumulate_verified_periods([3, 15], 32, (6, 7), 29, 0), 'sufficient_unknown_order_register': uniform_register_size(29)}, indent=2))


if __name__ == "__main__":
    main()
