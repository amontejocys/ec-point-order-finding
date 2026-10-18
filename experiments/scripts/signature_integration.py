"""Evaluate M1-gated signing on saved recovery samples; references score outputs."""

import argparse
import json
from pathlib import Path
import numpy as np
from quantum_ec.recovery.factor_free_recovery import accumulate_verified_periods
from quantum_ec.classical.curve import scalar_multiple
from quantum_ec.signing.signature import signing_attempt
from quantum_ec.signing.signature import verify_arithmetic
from experiments.reference.signature import reference_attempt
from quantum_ec.signing.admission import OrderAdmissionError
from quantum_ec.classical.primality import DEFAULT_PRIMALITY_ROUNDS


def validate_saved_recoveries(report_path, arrays_path, shots=4):
    if not isinstance(shots, int) or isinstance(shots, bool) or shots < 1:
        raise ValueError('shots must be a positive integer')
    report = json.loads(Path(report_path).read_text(encoding='ascii'))
    index = next(i for i, case in enumerate(report['cases'])
                 if case['p'] == 29 and case['point'] == [6, 7])
    case = report['cases'][index]
    point, p, a, reference_order = tuple(case['point']), case['p'], case['a'], case['reference_order_for_evaluation_only']
    public_key = scalar_multiple(2, point, p, a)
    counts = {'exact_order': 0, 'no_candidate': 0, 'nonminimal_period': 0,
              'matching_verified_signatures': 0}
    admission_counts = {'admitted': 0, 'recovery_failure': 0,
                        'order_not_admissible_for_signing': 0}
    rejection_reasons = {}
    with np.load(arrays_path, allow_pickle=False) as arrays:
        for measurements in arrays[f'measurements_{index}']:
            if len(measurements) < shots:
                raise ValueError('shots exceeds the saved measurement budget')
            recovered = accumulate_verified_periods([int(y) for y in measurements[:shots]],
                                                     case['q'], point, p, a)['verified_period']
            if recovered is None:
                counts['no_candidate'] += 1
            elif recovered != reference_order:
                counts['nonminimal_period'] += 1
            else:
                counts['exact_order'] += 1
            try:
                signature = signing_attempt(2, 2, 1, recovered, point, p, a, b=case['b'])
            except OrderAdmissionError as error:
                admission_counts[error.status] += 1
                rejection_reasons[error.reason] = rejection_reasons.get(error.reason, 0) + 1
                continue
            admission_counts['admitted'] += 1
            expected = reference_attempt(2, 2, 1, reference_order, point, p, a)
            if signature != expected or not verify_arithmetic(signature, 2, public_key, reference_order, point, p, a):
                raise AssertionError('Recovered order failed signature arithmetic integration')
            counts['matching_verified_signatures'] += 1
    return {'scope': 'Toy signing with order admission; reference order used for evaluation only',
            'shots': shots, 'z_test': 2, 'd_test': 2, 'k_test': 1,
            'reference_signature': reference_attempt(2, 2, 1, reference_order, point, p, a),
            'recovery_minimality_certification': False,
            'signing_admission': {'default_primality_rounds': DEFAULT_PRIMALITY_ROUNDS,
                                 'counts': admission_counts, 'rejection_reasons': rejection_reasons},
            **counts}


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
    args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='ascii', newline='\n')
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
