"""P4: reuse hash-frozen outputs/distributions; never build or execute a circuit."""

import argparse
from collections import defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import time

import numpy as np


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked_path(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('Anchor path must remain inside the repository')
    return path


def load_frozen_inputs(root, anchors):
    report_path = checked_path(root, anchors['source_report'])
    array_path = checked_path(root, anchors['source_arrays'])
    for path, expected in ((report_path, anchors['source_report_sha256']),
                           (array_path, anchors['source_arrays_sha256'])):
        if not path.is_file():
            raise FileNotFoundError(f'Missing frozen artifact: {path.name}; restore the archived dataset, not new circuit output')
        if sha256(path) != expected:
            raise ValueError(f'Frozen artifact hash mismatch: {path.name}')
    report = json.loads(report_path.read_text())
    cases = anchors['cases']
    if sorted(case['index'] for case in cases) != list(range(len(report['cases']))):
        raise ValueError('Frozen case indices are missing or duplicated')
    if not report['not_dense_statevector'] or not report['cache_is_simulation_only_not_circuit_lookup']:
        raise ValueError('Unexpected historical simulation scope')
    loaded = []
    with np.load(array_path, allow_pickle=False) as arrays:
        for case in cases:
            index = case['index']
            historical = report['cases'][index]
            if any(historical[key] != case[key] for key in ('p', 'a', 'b', 'point', 'q')):
                raise ValueError('Frozen anchor does not match historical metadata')
            if case['probabilities_array'] != f'probabilities_{index}':
                raise ValueError('Unexpected frozen probability-array mapping')
            loaded.append((case, historical, arrays[f'outputs_{index}'].copy(),
                           arrays[case['probabilities_array']].copy()))
    return report['scope'], loaded


def validate_arrays(outputs, probabilities, q, tolerance):
    if (outputs.shape != (q,) or not np.issubdtype(outputs.dtype, np.integer)
            or probabilities.shape != (q,) or not np.issubdtype(probabilities.dtype, np.floating)):
        raise ValueError('Saved array shape or dtype mismatch')
    if (not np.isfinite(probabilities).all() or probabilities.min() < 0
            or abs(float(probabilities.sum())-1) > tolerance):
        raise ValueError('Saved probabilities are invalid; no clipping or renormalization allowed')


def weights_from_saved(probabilities, q, point, p, a, order, bound):
    from experiments.reference.bounded_recovery_law import accepted_by_order
    from quantum_ec.recovery.continued_fractions import verified_candidates
    weights = defaultdict(float)
    for y, probability in enumerate(probabilities):
        candidates = verified_candidates(y, q, point, p, a)
        if candidates != accepted_by_order(y, q, order, bound):
            raise AssertionError('Saved-anchor acceptance differs from analytical predicate')
        weights[math.gcd(*candidates) if candidates else 0] += float(probability)
    return dict(sorted(weights.items()))


def actual_admission(state, order, point, p, a, b, rounds, decisions):
    from quantum_ec.signing.admission import admit_signing_order
    partition = {'recovery_failure': 0.0, 'admitted_correct': 0.0,
                 'rejected_exact_composite_order': 0.0, 'rejected_nonminimal': 0.0}
    for g, mass in state.items():
        if g not in decisions:
            decisions[g] = admit_signing_order(g or None, point, p, a, b=b, primality_rounds=rounds)
        decision = decisions[g]
        primality = decision['primality']
        if primality is not None and primality['method'] != 'small_prime_checks':
            raise ValueError('Frozen P4 admission replay must stay within deterministic small-prime checks')
        if decision['status'] == 'recovery_failure' and g == 0:
            key = 'recovery_failure'
        elif decision['status'] == 'admitted' and g == order:
            key = 'admitted_correct'
        elif decision['status'] == 'order_not_admissible_for_signing' and decision['reason'] == 'candidate_not_prime':
            key = 'rejected_exact_composite_order' if g == order else 'rejected_nonminimal'
        else:
            raise AssertionError('Unexpected production admission decision')
        partition[key] += float(mass)
    return partition


def evaluate_anchor(case, historical, outputs, probabilities, config):
    from experiments.reference.bounded_recovery_law import (
        advance_law, checked_outcomes, one_shot_by_order, raw_probabilities)
    from experiments.reference.curve import reference_add, reference_order
    from experiments.reference.gcd_recovery_law import admission_summary
    from quantum_ec.recovery.factor_free_recovery import uniform_register_size
    from quantum_ec.simulation.sparse_order_finding import fourier_probabilities
    p, a, b, q = (case[key] for key in ('p', 'a', 'b', 'q'))
    point = tuple(case['point'])
    tolerance = config['anchors']['agreement_absolute_tolerance']
    validate_arrays(outputs, probabilities, q, tolerance)
    if ((4*a**3+27*b*b) % p == 0 or (point[1]**2-point[0]**3-a*point[0]-b) % p):
        raise ValueError('Invalid frozen curve or point')
    register = uniform_register_size(p)
    if register['q'] != q or historical['basis_inputs_checked'] != q:
        raise ValueError('Historical register or scalar coverage mismatch')
    order = reference_order(point, p, a)
    if order != historical['reference_order_for_evaluation_only']:
        raise ValueError('Independent point order disagrees with historical report')
    width = p.bit_length()
    current = None
    for value in outputs:
        expected = 1 if current is None else (current[0] << 1) | (current[1] << (width+1))
        if int(value) != expected:
            raise ValueError('Saved full point/work label disagrees with canonical group output')
        current = reference_add(current, point, p, a)
    # No label masks: any saved nonzero high work bits are retained and rejected above.
    fft = fourier_probabilities([int(value) for value in outputs])
    ideal_probabilities = raw_probabilities(q, order)
    spectrum_differences = {
        'saved_vs_reconstructed_fft': float(np.max(np.abs(probabilities-fft))),
        'saved_vs_raw_ideal': float(np.max(np.abs(probabilities-ideal_probabilities))),
        'reconstructed_fft_vs_raw_ideal': float(np.max(np.abs(fft-ideal_probabilities))),
    }
    if max(spectrum_differences.values()) > tolerance:
        raise ArithmeticError('Saved spectrum does not match the reconstructed/ideal law')
    bound = register['order_upper_bound']
    weights = weights_from_saved(probabilities, q, point, p, a, order, bound)
    ideal_weights, _, _ = one_shot_by_order(q, order, bound, tolerance)
    weight_error = max(abs(weights.get(d, 0)-ideal_weights.get(d, 0))
                       for d in set(weights) | set(ideal_weights))
    if weight_error > tolerance:
        raise ArithmeticError('Saved one-shot statistic law mismatch')
    budgets = {0, *(row['shots'] for row in historical['recovery_results'])}
    if any(type(t) is not int or t < 0 for t in budgets):
        raise ValueError('Invalid historical measurement budget')
    state, ideal_state, decisions, rows = {0: 1}, {0: 1}, {}, []
    rounds = config['admission']['miller_rabin_rounds']
    for t in range(max(budgets)+1):
        if t in budgets:
            observed = checked_outcomes(state, weights, order, t, tolerance)
            ideal = checked_outcomes(ideal_state, ideal_weights, order, t, tolerance)
            state_error = max(abs(float(state.get(g, 0)-ideal_state.get(g, 0)))
                              for g in set(state) | set(ideal_state))
            actual = actual_admission(state, order, point, p, a, b, rounds, decisions)
            model = admission_summary(state, order, rounds)
            mapping = {'recovery_failure': 'recovery_failure', 'admitted_correct': 'admitted_correct',
                'rejected_exact_composite_order': 'rejected_exact_composite_order_ideal',
                'rejected_nonminimal': 'rejected_nonminimal_ideal'}
            admission_error = max(abs(actual[key]-model[value]) for key, value in mapping.items())
            partition_error = abs(sum(actual.values())-1)
            if (max(state_error, admission_error, partition_error) > tolerance
                    or model['incorrect_admission_upper_bound'] != 0
                    or not model['admission_partition_exact_for_policy']):
                raise ArithmeticError('P4 recovery/admission comparison failed')
            rows.append({'shots': t, 'saved_distribution_recovery': observed,
                         'ideal_recovery': ideal, 'full_law_max_abs_difference': state_error,
                         'actual_production_admission': actual, 'model_admission': model,
                         'admission_max_abs_difference': admission_error,
                         'admission_partition_residual': partition_error})
        if t < max(budgets):
            state = advance_law(state, weights)
            ideal_state = advance_law(ideal_state, ideal_weights)
    return {'index': case['index'], 'p': p, 'a': a, 'b': b, 'point': list(point),
        'q': q, 'order': order, 'bound': bound, 'scalar_outputs_rechecked': q,
        'saved_probability_mass_residual': abs(float(probabilities.sum())-1),
        'spectrum_max_abs_differences': spectrum_differences,
        'saved_one_shot_statistic_law': weights, 'ideal_one_shot_statistic_law': ideal_weights,
        'one_shot_max_abs_difference': weight_error, 'budgets': rows,
        'production_admission_decisions': decisions,
        'historical_coverage': {key: historical[key] for key in ('basis_inputs_checked',
            'actual_gate_propagations', 'controlled_additions', 'distinct_adder_definitions',
            'logical_resources_arithmetic')},
        'coverage_limit': 'Saved initialized scalar path only; no new gate execution or universal adder-domain proof'}


def write_budget_csv(path, cases):
    rows = []
    for case in cases:
        for budget in case['budgets']:
            recovery = budget['saved_distribution_recovery']
            rows.append({'index': case['index'], 'p': case['p'], 'q': case['q'], 'order': case['order'],
                'shots': budget['shots'], 'exact_order': recovery['exact_order'],
                'no_candidate': recovery['no_candidate'], 'nonminimal': recovery['nonminimal'],
                **budget['actual_production_admission'],
                'full_law_max_abs_difference': budget['full_law_max_abs_difference'],
                'admission_max_abs_difference': budget['admission_max_abs_difference']})
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    root, config_path = args.root.resolve(), args.config.resolve()
    if args.output_dir.exists():
        parser.error('Output directory exists; choose a new directory')
    sys.path[:0] = [str(root), str(root / 'src')]
    config = json.loads(config_path.read_text())
    from experiments.scripts.evaluate_bounded_reliability import validate_config
    from experiments.scripts.audit_source_tree import source_manifest
    validate_config(config)
    committed = subprocess.check_output(['git', '-C', str(root), 'show',
                                         'HEAD:'+config_path.relative_to(root).as_posix()])
    if hashlib.sha256(committed).hexdigest() != sha256(config_path):
        parser.error('Frozen configuration differs from HEAD')
    start = time.perf_counter()
    historical_scope, cases = load_frozen_inputs(root, config['anchors'])
    report = {'phase': 'P4_saved_circuit_anchors', 'precision_status': 'numerical_only',
        'no_new_circuit_execution': True, 'no_new_sampling': True,
        'historical_scope': historical_scope, 'config_sha256': sha256(config_path),
        'source_report_sha256': config['anchors']['source_report_sha256'],
        'source_arrays_sha256': config['anchors']['source_arrays_sha256'],
        'script_sha256': sha256(Path(__file__)),
        'model_sha256': sha256(root/'experiments/reference/bounded_recovery_law.py'),
        'support_model_sha256': sha256(root/'experiments/reference/gcd_recovery_law.py'),
        'reference_curve_sha256': sha256(root/'experiments/reference/curve.py'),
        'production_source_manifest': source_manifest(root), 'python_version': platform.python_version(),
        'numpy_version': np.__version__,
        'commit': subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD']).decode().strip(),
        'dirty_status': subprocess.check_output(['git', '-C', str(root), 'status', '--porcelain']).decode().splitlines(),
        'cases': [evaluate_anchor(case, old, outputs, probabilities, config)
                  for case, old, outputs, probabilities in cases]}
    report['elapsed_wall_seconds'] = time.perf_counter()-start
    report['max_full_law_abs_difference'] = max(b['full_law_max_abs_difference']
        for c in report['cases'] for b in c['budgets'])
    report['max_admission_abs_difference'] = max(b['admission_max_abs_difference']
        for c in report['cases'] for b in c['budgets'])
    args.output_dir.mkdir(parents=True)
    (args.output_dir/'summary.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n',
                                             encoding='utf-8', newline='\n')
    write_budget_csv(args.output_dir/'budgets.csv', report['cases'])
    print(json.dumps({'cases': len(report['cases']), 'scalar_outputs_rechecked': sum(
        c['scalar_outputs_rechecked'] for c in report['cases']),
        'max_full_law_abs_difference': report['max_full_law_abs_difference'],
        'max_admission_abs_difference': report['max_admission_abs_difference']}, indent=2))


if __name__ == '__main__':
    main()
