"""Evaluate the offline law; never supply its reference order to signing."""

import argparse
import hashlib
import json
from pathlib import Path
import platform
import sys

import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    sys.path[:0] = [str(args.root), str(args.root / 'src')]
    from experiments.reference.curve import reference_order
    from experiments.reference.gcd_recovery_law import (
        admission_summary, divisor_inversion_law, gcd_law, one_shot_law)
    from quantum_ec.recovery.factor_free_recovery import uniform_register_size
    from quantum_ec.recovery.success_budget import sufficient_budget
    from experiments.scripts.audit_source_tree import source_manifest

    config = json.loads(args.config.read_text())
    report = {'scope': config['scope'], 'python': platform.python_version(),
              'numpy': np.__version__, 'numeric_kind': 'float64, no Monte Carlo',
              'rigorous_roundoff_enclosure': False, 'rows': [],
              'known_order_used_only_for_analysis': True,
              'project_source_sha256': source_manifest(args.root)['source_tree_sha256'],
              'reference_curve_sha256': hashlib.sha256((args.root / 'experiments/reference/curve.py').read_bytes()).hexdigest(),
              'config_sha256': hashlib.sha256(args.config.read_bytes()).hexdigest(),
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'model_sha256': hashlib.sha256((args.root / 'experiments/reference/gcd_recovery_law.py').read_bytes()).hexdigest()}
    for case in config['cases']:
        p, a, b = (case[key] for key in ('p', 'a', 'b'))
        point = tuple(case['point'])
        if (point[1]**2 - point[0]**3 - a*point[0] - b) % p:
            raise ValueError('Point not on configured curve')
        r = reference_order(point, p, a)
        register = uniform_register_size(p)
        q = register['q'] << case['extra_bits']
        weights = one_shot_law(q, point, p, a, r)
        row = {**case, 'reference_order': r, 'q': q,
               'bound': register['order_upper_bound'], 'one_shot': weights,
               'budget_rows': []}
        for t in config['budgets']:
            law = gcd_law(weights, t)
            inverted = divisor_inversion_law(weights, t)
            residual = max(abs(law.get(g, 0) - inverted.get(g, 0))
                           for g in set(law) | set(inverted))
            if residual > 1e-10 or abs(sum(law.values())-1) > 1e-10:
                raise AssertionError('Finite-law validation failed')
            row['budget_rows'].append({
                'shots': t, 'exact_order': law.get(r, 0),
                'no_candidate': law.get(0, 0),
                'nonminimal': sum(m for g, m in law.items() if g not in (0, r)),
                'dp_vs_inversion_max_abs_error': residual,
                'admission': admission_summary(law, r)})
        row['reference_conditioned_budget'] = next(
            (t for t in range(1, config['max_budget_search']+1)
             if gcd_law(weights, t).get(r, 0) >= 1-config['epsilon']), None)
        row['unknown_order_sufficient_budget'] = sufficient_budget(p, config['epsilon'])
        report['rows'].append(row)
        print(p, r, q, row['reference_conditioned_budget'], flush=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
