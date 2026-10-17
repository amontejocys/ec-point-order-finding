"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import argparse
import json
from pathlib import Path
import numpy as np
from quantum_ec.recovery.factor_free_recovery import accumulate_verified_periods
from quantum_ec.classical.curve import scalar_multiple
from quantum_ec.signing.signature import signing_attempt
from quantum_ec.signing.signature import verify_arithmetic
from experiments.reference.signature import reference_attempt


def validate_saved_recoveries(report_path, arrays_path, shots=4):
    report = json.loads(Path(report_path).read_text(encoding='ascii'))
    index = next(i for i, case in enumerate(report['cases'])
                 if case['p'] == 29 and case['point'] == [6, 7])
    case = report['cases'][index]
    point, p, a, reference_order = tuple(case['point']), case['p'], case['a'], case['reference_order_for_evaluation_only']
    public_key = scalar_multiple(2, point, p, a)
    counts = {'exact_order': 0, 'no_candidate': 0, 'nonminimal_period': 0,
              'matching_verified_signatures': 0}
    with np.load(arrays_path) as arrays:
        for measurements in arrays[f'measurements_{index}']:
            recovered = accumulate_verified_periods([int(y) for y in measurements[:shots]],
                                                     case['q'], point, p, a)['verified_period']
            if recovered is None:
                counts['no_candidate'] += 1
                continue
            if recovered != reference_order:
                counts['nonminimal_period'] += 1
                continue
            counts['exact_order'] += 1
            signature = signing_attempt(2, 2, 1, recovered, point, p, a)
            expected = reference_attempt(2, 2, 1, reference_order, point, p, a)
            if signature != expected or not verify_arithmetic(signature, 2, public_key, reference_order, point, p, a):
                raise AssertionError('Recovered order failed signature arithmetic integration')
            counts['matching_verified_signatures'] += 1
    return {'scope': 'Toy ECDSA-like arithmetic only; correctness conditional on exact recovered order',
            'shots': shots, 'z_test': 2, 'd_test': 2, 'k_test': 1,
            'reference_signature': reference_attempt(2, 2, 1, reference_order, point, p, a),
            'recovery_minimality_certification': False, **counts}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--arrays', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--shots', type=int, default=4)
    args = parser.parse_args()
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
    result = validate_saved_recoveries(args.report, args.arrays, args.shots)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='ascii')
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
