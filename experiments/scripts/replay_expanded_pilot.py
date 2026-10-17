"""Replay saved ideal samples through the package; do not regenerate sampling."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from quantum_ec.recovery.factor_free_recovery import recover_prefixes


def replay(report_path, arrays_path):
    report = json.loads(report_path.read_text(encoding='utf-8'))
    totals = {row['shots']: dict(exact=0, nonminimal_multiple=0, no_candidate=0)
              for row in report['summary']}
    nonminimal_instances = 0
    with np.load(arrays_path, allow_pickle=False) as arrays:
        measurements = arrays['measurements']
        if len(measurements) != len(report['instances']):
            raise AssertionError('Sample/instance count mismatch')
        for instance, trials in zip(report['instances'], measurements):
            budgets = [row['shots'] for row in instance['results']]
            counts = {t: dict(exact=0, nonminimal_multiple=0, no_candidate=0) for t in budgets}
            cache = {}
            p, a, point = instance['p'], instance['a'], tuple(instance['point'])
            reference = instance['reference_order']
            for trial in trials:
                for t, candidate in recover_prefixes(trial, instance['q'], point, p, a,
                                                     budgets, cache).items():
                    if candidate is not None and candidate % reference:
                        raise AssertionError('Recovered candidate is not a multiple')
                    category = ('no_candidate' if candidate is None else
                                'exact' if candidate == reference else 'nonminimal_multiple')
                    counts[t][category] += 1
            for expected in instance['results']:
                t = expected['shots']
                for name, count in counts[t].items():
                    if count != expected[name]:
                        raise AssertionError(f'Changed result for p={p}, point={point}, T={t}')
                    totals[t][name] += count
            nonminimal_instances += any(c['nonminimal_multiple'] for c in counts.values())
    for row in report['summary']:
        if any(totals[row['shots']][name] != row[name] for name in totals[row['shots']]):
            raise AssertionError('Aggregate mismatch')
    return {
        'scope': 'Replay of saved ideal samples, not circuit execution or resampling',
        'instances': len(report['instances']),
        'instance_budget_rows_matched': sum(len(r['results']) for r in report['instances']),
        'instances_with_nonminimal_candidates': nonminimal_instances,
        'summary': totals,
        'input_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in (report_path, arrays_path)},
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--arrays', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = replay(args.report, args.arrays)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k != 'summary'}, indent=2))


if __name__ == '__main__':
    main()
