"""Finite-domain M1 validation; reference orders are used only to score decisions."""

import argparse
import json
import math
from pathlib import Path

from experiments.reference.curve import reference_order
from quantum_ec.recovery.factor_free_recovery import uniform_register_size
from quantum_ec.signing.admission import admit_signing_order


def validate():
    cases = [(5, 1, 1, (0, 1)), (5, 1, 1, (2, 1)), (7, 0, 1, (3, 0)),
             (29, 0, 7, (6, 7)), (41, 31, 18, (28, 40))]
    records = []
    for p, a, b, point in cases:
        order = reference_order(point, p, a)
        prime_reference = order >= 2 and all(order % d for d in range(2, math.isqrt(order) + 1))
        bound = uniform_register_size(p)['order_upper_bound']
        decisions = []
        for candidate in [None, *range(bound + 2)]:
            decision = admit_signing_order(candidate, point, p, a, b=b)
            expected = candidate == order and prime_reference
            if (decision['status'] == 'admitted') != expected:
                raise AssertionError(f'Wrong gate decision: {p}, {point}, {candidate}')
            decisions.append(decision)
        records.append({'p': p, 'a': a, 'b': b, 'point': point,
                        'reference_order_for_validation_only': order,
                        'decisions': decisions})
    return {'scope': 'Classical finite admission tests, no circuit execution or production ECDSA security claim',
            'cases': records, 'decisions_checked': sum(len(r['decisions']) for r in records),
            'all_decisions_match_independent_reference': True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = validate()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(f"Validated {report['decisions_checked']} admission decisions across {len(report['cases'])} curves/points.")


if __name__ == '__main__':
    main()
