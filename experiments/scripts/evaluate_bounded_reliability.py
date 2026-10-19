"""Validate P2 or explicitly evaluate the committed all-orders P3 grid."""

import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
import sys
import time


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(root, *arguments):
    return subprocess.check_output(['git', '-C', str(root), *arguments])


def validate_config(config):
    """Reject unsupported policy changes instead of silently ignoring them."""
    import math
    grid = config['grid']
    if (config['schema_version'] != 1 or config['experiment_id'] != 'm2-f-main'
            or grid['order_bound'] != 'p + 1 + isqrt(4*p)'
            or grid['register_bits'] != '(order_bound**2).bit_length() + extra_bits'
            or grid['register_size'] != '1 << register_bits'
            or grid['orders'] != {'minimum': 2, 'maximum': 'order_bound', 'step': 1}
            or grid['extra_bits'] != [0, 1]):
        raise ValueError('Unsupported grid definition')
    if (grid['primes'] != [5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41]
            or grid['failure_targets'] != [0.1, 0.01, 0.001]
            or config['budget_search']['minimum_shots'] != 1
            or config['budget_search']['maximum_shots'] != 2048):
        raise ValueError('Configuration does not match the P1 freeze')
    if (config['precision']['status'] != 'numerical_only'
            or config['precision']['interval_certificate']
            or config['precision']['primary_arithmetic'] != 'float64'
            or config['admission']['miller_rabin_rounds'] != 64
            or config['model']['executions'] != 'ideal_independent'
            or config['model']['monte_carlo'] or config['model']['new_circuit_runs']):
        raise ValueError('Unsupported model or precision policy')
    for name, value in config['precision'].items():
        if name.endswith('_tolerance') and (type(value) not in (int, float)
                or not math.isfinite(value) or value <= 0):
            raise ValueError('Tolerances must be positive and finite')
    reference = config['precision']['high_precision_check']
    if (reference['decimal_digits'] != 80 or type(reference['absolute_tolerance']) not in (int, float)
            or not math.isfinite(reference['absolute_tolerance']) or reference['absolute_tolerance'] <= 0):
        raise ValueError('High-precision reference must match the 80-digit freeze')
    if (config['model']['recovery_policy'] != 'all_verified_convergent_denominators_accumulated_by_gcd'
            or config['model']['empty_candidate_statistic'] != 0
            or not config['model']['true_order_is_offline_analysis_only']
            or not grid['orders_are_conservative_superset']
            or not config['provenance']['main_run_requires_configuration_commit']):
        raise ValueError('Unsupported recovery semantics or provenance gate')


def provenance(root, config_path):
    from experiments.scripts.audit_source_tree import source_manifest
    return {
        'config_sha256': sha256(config_path),
        'commit': git(root, 'rev-parse', 'HEAD').decode().strip(),
        'dirty_status': git(root, 'status', '--porcelain').decode().splitlines(),
        'driver_sha256': sha256(Path(__file__)),
        'model_sha256': sha256(root / 'experiments/reference/bounded_recovery_law.py'),
        'support_model_sha256': sha256(root / 'experiments/reference/gcd_recovery_law.py'),
        'reference_curve_sha256': sha256(root / 'experiments/reference/curve.py'),
        'pilot_config_sha256': sha256(root / 'experiments/configs/m2_f_pilot.json'),
        'production_source_manifest': source_manifest(root),
        'python_version': platform.python_version(),
        'numpy_version': importlib.metadata.version('numpy'),
        'high_precision_backend_and_version': 'mpmath ' + importlib.metadata.version('mpmath'),
        'precision_status': 'numerical_only',
        'random_seed': None,
    }


def precision_check(q, r, bound, weights, states, digits, tolerance, intervals=False):
    from experiments.reference.bounded_recovery_law import (
        interval_endpoints, precision_law, precision_weights)
    reference, context = precision_weights(q, r, bound, digits)
    difference = max(abs(float(reference.get(d, 0)) - weights.get(d, 0))
                     for d in set(weights) | set(reference))
    if difference > tolerance or abs(float(sum(reference.values())) - 1) > tolerance:
        raise ArithmeticError('High-precision one-shot check failed')
    report = {'digits': digits, 'one_shot_max_abs_difference': difference,
              'reference_mass': context.nstr(sum(reference.values()), digits), 'budgets': []}
    interval_weights = None
    if intervals:
        interval_weights, interval_context = precision_weights(q, r, bound, digits, True)
        total = sum(interval_weights.values())
        if not total.a <= 1 <= total.b:
            raise ArithmeticError('Interval one-shot mass does not enclose one')
        report['diagnostic_mass_interval'] = interval_endpoints(total, digits)
    for t, state in sorted(states.items()):
        expected = precision_law(reference, t)
        delta = max(abs(float(expected.get(g, 0)) - state.get(g, 0))
                    for g in set(expected) | set(state))
        if delta > tolerance:
            raise ArithmeticError('High-precision T-shot check failed')
        row = {'shots': t, 'max_abs_difference': delta,
               'reference_exact_order': context.nstr(expected.get(r, context.mpf(0)), digits)}
        if intervals:
            enclosed = precision_law(interval_weights, t).get(r, 0)
            if not hasattr(enclosed, '_mpi_'):
                from mpmath.ctx_iv import MPIntervalContext
                iv = MPIntervalContext()
                iv.dps = digits
                enclosed = iv.mpf(enclosed)
            reference_point = interval_context.mpf(expected.get(r, 0))
            if not enclosed.a <= reference_point <= enclosed.b:
                raise ArithmeticError('Interval does not contain high-precision diagnostic point')
            row['diagnostic_exact_order_interval'] = interval_endpoints(enclosed, digits)
            row['contains_high_precision_diagnostic_point'] = True
            row['interval_is_not_a_field_budget_certificate'] = True
        report['budgets'].append(row)
    return report


def validate_pilot(root, config):
    from experiments.reference.bounded_recovery_law import (
        accepted_by_order, advance_law, checked_outcomes, one_shot_by_order)
    from experiments.reference.curve import reference_order
    from quantum_ec.recovery.continued_fractions import verified_candidates
    from quantum_ec.recovery.factor_free_recovery import uniform_register_size
    from quantum_ec.simulation.ideal_distribution import ideal_probabilities
    pilot = json.loads((root / 'experiments/configs/m2_f_pilot.json').read_text())
    rows = []
    for case in pilot['cases']:
        p, a = case['p'], case['a']
        point = tuple(case['point'])
        r = reference_order(point, p, a)
        register = uniform_register_size(p)
        bound, q = register['order_upper_bound'], register['q'] << case['extra_bits']
        matched = 0
        for y in range(q):
            if accepted_by_order(y, q, r, bound) != verified_candidates(y, q, point, p, a):
                raise AssertionError('Order predicate differs from production group verification')
            matched += 1
        weights, counts, mass_error = one_shot_by_order(q, r, bound)
        state, states, outcomes = {0: 1}, {}, []
        for t in range(max(pilot['budgets']) + 1):
            if t in pilot['budgets']:
                states[t] = dict(state)
                outcomes.append(checked_outcomes(state, weights, r, t, 1e-10))
            state = advance_law(state, weights)
        from experiments.reference.bounded_recovery_law import raw_probabilities
        import numpy as np
        comparison = float(np.max(np.abs(raw_probabilities(q, r) - ideal_probabilities(q, r))))
        precision = config['precision']['high_precision_check']
        rows.append({**case, 'reference_order': r, 'q': q, 'bound': bound,
                     'production_predicate_outcomes_checked': matched,
                     'raw_mass_residual': mass_error,
                     'raw_vs_normalized_production_max_abs_difference': comparison,
                     'operation_counts': counts, 'outcomes': outcomes,
                     'precision_check': precision_check(q, r, bound, weights, states,
                         precision['decimal_digits'], precision['absolute_tolerance'], True)})
    return {'phase': 'P2_validation_only', 'main_grid_evaluated': False, 'rows': rows}


def evaluate_main(root, config):
    from experiments.reference.bounded_recovery_law import (
        advance_law, checked_outcomes, classify_threshold, one_shot_by_order, worst_orders)
    from experiments.reference.gcd_recovery_law import admission_summary
    from quantum_ec.recovery.factor_free_recovery import uniform_register_size
    from quantum_ec.recovery.success_budget import sufficient_budget
    groups = []
    tolerances = config['precision']
    tolerance = tolerances['probability_mass_absolute_tolerance']
    cap = config['budget_search']['maximum_shots']
    for p in config['grid']['primes']:
        register = uniform_register_size(p)
        bound = register['order_upper_bound']
        for extra_bits in config['grid']['extra_bits']:
            start = time.perf_counter()
            q = register['q'] << extra_bits
            models = {}
            for r in range(2, bound + 1):
                before = time.perf_counter()
                weights, counts, error = one_shot_by_order(q, r, bound, tolerance)
                models[r] = {'weights': weights, 'state': {0: 1}, 'counts': counts,
                             'raw_mass_residual': error, 'outcomes': [],
                             'one_shot_wall_seconds': time.perf_counter() - before}
            targets, prior_exact, prior_states, worst_history = {}, {}, {}, []
            for t in range(cap + 1):
                exact = {}
                for r, model in models.items():
                    outcome = checked_outcomes(model['state'], model['weights'], r, t, tolerance)
                    outcome['admission'] = admission_summary(model['state'], r,
                                                           config['admission']['miller_rabin_rounds'])
                    if t and outcome['exact_order'] + tolerances['monotonicity_absolute_tolerance'] < prior_exact[r]:
                        raise ArithmeticError('Exact-order probability is not monotone')
                    model['outcomes'].append(outcome)
                    exact[r] = outcome['exact_order']
                minimum, tied = worst_orders(exact, tolerances['worst_order_tie_absolute_tolerance'])
                worst_history.append({'shots': t, 'worst_probability': minimum, 'orders': tied})
                for epsilon in config['grid']['failure_targets']:
                    if t == 0 or epsilon in targets or minimum < 1 - epsilon:
                        continue
                    selected = set(tied)
                    selected.update(worst_history[-2]['orders'])
                    hp = tolerances['high_precision_check']
                    checks = {r: precision_check(q, r, bound, models[r]['weights'],
                              {t - 1: prior_states[r], t: models[r]['state']},
                              hp['decimal_digits'], hp['absolute_tolerance']) for r in sorted(selected)}
                    baseline = sufficient_budget(p, epsilon)['sufficient_independent_ideal_shots']
                    threshold_status = classify_threshold(minimum, epsilon, tolerances['threshold_absolute_tolerance'])
                    previous_status = classify_threshold(worst_history[-2]['worst_probability'],
                                                         epsilon, tolerances['threshold_absolute_tolerance'])
                    targets[epsilon] = {'epsilon': epsilon, 'shots': t,
                        'status': ('unresolved' if 'unresolved' in (threshold_status, previous_status)
                                   else 'numerically_estimated_first_crossing'),
                        'precision_status': 'numerical_only',
                        'at_budget': worst_history[-1], 'previous_budget': worst_history[-2],
                        'existing_sufficient_shots': baseline, 'baseline_ratio': baseline / t,
                        'high_precision_checks': checks}
                if len(targets) == len(config['grid']['failure_targets']) or t == cap:
                    break
                prior_exact = exact
                prior_states = {r: dict(model['state']) for r, model in models.items()}
                for model in models.values():
                    model['state'] = advance_law(model['state'], model['weights'], model['counts'])
            for epsilon in config['grid']['failure_targets']:
                if epsilon not in targets:
                    targets[epsilon] = {'epsilon': epsilon, 'shots': None, 'status': 'not_reached'}
            groups.append({'p': p, 'bound': bound, 'extra_bits': extra_bits, 'q': q,
                'budgets': list(targets.values()), 'worst_history': worst_history,
                'orders': [{'r': r, 'one_shot': m['weights'], 'operation_counts': m['counts'],
                            'raw_mass_residual': m['raw_mass_residual'],
                            'one_shot_wall_seconds': m['one_shot_wall_seconds'],
                            'outcomes': m['outcomes']} for r, m in models.items()],
                'offline_wall_seconds': time.perf_counter() - start})
            print(f'p={p} Q={q}: numerical evaluation completed', flush=True)
    return {'phase': 'P3_main_numerical', 'groups': groups, 'main_grid_evaluated': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--mode', choices=['validate-pilot', 'main'], default='validate-pilot')
    args = parser.parse_args()
    root = args.root.resolve()
    config_path = args.config.resolve()
    sys.path[:0] = [str(root), str(root / 'src')]
    config = json.loads(config_path.read_text())
    validate_config(config)
    if args.mode == 'main':
        relative = config_path.relative_to(root).as_posix()
        committed = git(root, 'show', f'HEAD:{relative}')
        if hashlib.sha256(committed).hexdigest() != sha256(config_path):
            parser.error('Main configuration differs from its committed version')
    from experiments.reference.bounded_recovery_law import OPERATION_COUNT_DEFINITION
    start = time.perf_counter()
    report = provenance(root, config_path)
    report['operation_count_definition'] = OPERATION_COUNT_DEFINITION
    report.update(validate_pilot(root, config) if args.mode == 'validate-pilot'
                  else evaluate_main(root, config))
    report['elapsed_wall_seconds'] = time.perf_counter() - start
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + '\n',
                           encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
