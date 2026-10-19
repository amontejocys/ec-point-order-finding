"""Audit a saved P3 report and regenerate small versionable result tables."""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys


def mobius(value):
    sign, divisor = 1, 2
    while divisor * divisor <= value:
        if value % divisor == 0:
            value //= divisor
            sign = -sign
            if value % divisor == 0:
                return 0
        divisor += 1
    return -sign if value > 1 else sign


def audit_report(report, config):
    """Independent scalar Mobius formula; imports no model or production code."""
    tolerance = config['precision']['probability_mass_absolute_tolerance']
    tie_tolerance = config['precision']['worst_order_tie_absolute_tolerance']
    threshold_tolerance = config['precision']['threshold_absolute_tolerance']
    expected = {(p, extra) for p in config['grid']['primes']
                for extra in config['grid']['extra_bits']}
    keys = [(g['p'], g['extra_bits']) for g in report['groups']]
    if set(keys) != expected or len(keys) != len(expected):
        raise ValueError('Missing or duplicated field/register group')
    if report['phase'] != 'P3_main_numerical' or report['precision_status'] != 'numerical_only':
        raise ValueError('Not a numerical P3 report')
    rows, order_rows = [], []
    diagnostics = {'law_count': 0, 'budget_count': 0, 'outcome_count': 0,
                   'mobius_max_abs_difference': 0.0, 'partition_max_abs_residual': 0.0,
                   'dp_vs_inversion_max_abs_difference': 0.0,
                   'high_precision_max_abs_difference': 0.0,
                   'high_precision_one_shot_max_abs_difference': 0.0,
                   'unresolved_or_unreached_budgets': 0,
                   'operation_totals': {}, 'all_admission_partitions_exact_for_policy': True}

    def require(condition, message):
        if not condition:
            raise ValueError(message)

    for group in report['groups']:
        p, q, bound = group['p'], group['q'], group['bound']
        require(bound == p + 1 + math.isqrt(4*p), 'Wrong Hasse bound')
        require(q == 1 << ((bound*bound).bit_length() + group['extra_bits']), 'Wrong register')
        orders = {row['r']: row for row in group['orders']}
        require(set(orders) == set(range(2, bound+1)) and len(orders) == len(group['orders']),
                'Missing or duplicated order')
        diagnostics['law_count'] += len(orders)
        last = len(group['worst_history']) - 1
        require(last <= config['budget_search']['maximum_shots'], 'Budget cap exceeded')
        for r, row in orders.items():
            weights = {int(d): weight for d, weight in row['one_shot'].items()}
            require(all(0 <= d <= bound and (d == 0 or d % r == 0)
                        and math.isfinite(w) and w >= 0 for d, w in weights.items()),
                    'Invalid one-shot weights')
            require(abs(sum(weights.values())-1) <= tolerance, 'One-shot mass mismatch')
            require(row['raw_mass_residual'] <= tolerance, 'Raw spectrum mass failed')
            require([v['shots'] for v in row['outcomes']] == list(range(last+1)),
                    'Missing budget outcomes')
            previous = 0.0
            for t, outcome in enumerate(row['outcomes']):
                exact, none, nonminimal = (outcome[k] for k in ('exact_order', 'no_candidate', 'nonminimal'))
                require(all(math.isfinite(v) and -tolerance <= v <= 1+tolerance
                            for v in (exact, none, nonminimal)), 'Invalid outcome mass')
                mass_error = abs(exact+none+nonminimal-1)
                require(mass_error <= tolerance, 'Outcome partition failed')
                require(exact+tolerance >= previous, 'Monotonicity failed')
                previous = exact
                terms = []
                for j in range(1, bound//r+1):
                    coefficient = mobius(j)
                    if coefficient:
                        divisible_mass = math.fsum(w for d, w in weights.items() if d % (r*j) == 0)
                        terms.append(coefficient*(divisible_mass**t - weights.get(0, 0)**t))
                residual = abs(exact-math.fsum(terms))
                require(residual <= tolerance, 'Independent Mobius audit failed')
                require(abs(none-weights.get(0, 0)**t) <= tolerance, 'No-candidate law failed')
                require(outcome['dp_vs_inversion_residual'] <= tolerance, 'Inversion diagnostic failed')
                require(exact+tolerance >= 1-(1-weights.get(r, 0))**t, 'Single-exact-event bound failed')
                admission = outcome['admission']
                partition = sum(admission[k] for k in ('recovery_failure', 'admitted_correct',
                    'rejected_exact_composite_order_ideal', 'rejected_nonminimal_ideal'))
                require(abs(partition-1) <= tolerance, 'Admission partition failed')
                diagnostics['all_admission_partitions_exact_for_policy'] &= admission['admission_partition_exact_for_policy']
                diagnostics['outcome_count'] += 1
                diagnostics['mobius_max_abs_difference'] = max(diagnostics['mobius_max_abs_difference'], residual)
                diagnostics['partition_max_abs_residual'] = max(diagnostics['partition_max_abs_residual'], mass_error)
                diagnostics['dp_vs_inversion_max_abs_difference'] = max(
                    diagnostics['dp_vs_inversion_max_abs_difference'], outcome['dp_vs_inversion_residual'])
            for name, value in row['operation_counts'].items():
                require(type(value) is int and value >= 0, 'Invalid operation count')
                diagnostics['operation_totals'][name] = diagnostics['operation_totals'].get(name, 0) + value
            order_rows.append({'p': p, 'q': q, 'r': r, 'bound': bound,
                'one_shot_exact_order': weights.get(r, 0), 'one_shot_no_candidate': weights.get(0, 0),
                'last_shots_evaluated': last, 'last_exact_order_probability': row['outcomes'][-1]['exact_order'],
                **row['operation_counts']})
        for t, worst in enumerate(group['worst_history']):
            values = {r: row['outcomes'][t]['exact_order'] for r, row in orders.items()}
            minimum = min(values.values())
            tied = sorted(r for r, v in values.items() if v-minimum <= tie_tolerance)
            require(worst == {'shots': t, 'worst_probability': minimum, 'orders': tied}, 'Worst-order mismatch')
        require(sorted(b['epsilon'] for b in group['budgets']) == sorted(config['grid']['failure_targets']),
                'Missing error targets')
        for budget in group['budgets']:
            diagnostics['budget_count'] += 1
            epsilon = budget['epsilon']
            crossing = next((h for h in group['worst_history'][1:]
                             if h['worst_probability'] >= 1-epsilon), None)
            if crossing is None:
                require(budget['shots'] is None and budget['status'] == 'not_reached', 'Wrong missing crossing')
                diagnostics['unresolved_or_unreached_budgets'] += 1
                rows.append({'p': p, 'q': q, 'epsilon': epsilon, 'shots': None, 'status': 'not_reached'})
                continue
            t = crossing['shots']
            require(budget['shots'] == t and budget['at_budget'] == crossing
                    and budget['previous_budget'] == group['worst_history'][t-1], 'Wrong first crossing')
            expected_status = ('unresolved' if any(abs(h['worst_probability']-(1-epsilon)) <= threshold_tolerance
                               for h in (crossing, group['worst_history'][t-1]))
                               else 'numerically_estimated_first_crossing')
            require(budget['status'] == expected_status, 'Wrong numerical threshold status')
            diagnostics['unresolved_or_unreached_budgets'] += expected_status == 'unresolved'
            selected = set(crossing['orders']) | set(group['worst_history'][t-1]['orders'])
            require(set(map(int, budget['high_precision_checks'])) == selected, 'Missing high-precision cases')
            for r_string, check in budget['high_precision_checks'].items():
                r = int(r_string)
                require(check['digits'] == 80 and [v['shots'] for v in check['budgets']] == [t-1, t],
                        'Wrong high-precision selection')
                require(check['one_shot_max_abs_difference'] <= tolerance, 'High-precision one-shot mismatch')
                diagnostics['high_precision_one_shot_max_abs_difference'] = max(
                    diagnostics['high_precision_one_shot_max_abs_difference'], check['one_shot_max_abs_difference'])
                for v in check['budgets']:
                    require(v['max_abs_difference'] <= tolerance, 'High-precision T-shot mismatch')
                    require(abs(float(v['reference_exact_order'])-orders[r]['outcomes'][v['shots']]['exact_order']) <= tolerance,
                            'High-precision probability mismatch')
                    diagnostics['high_precision_max_abs_difference'] = max(
                        diagnostics['high_precision_max_abs_difference'], v['max_abs_difference'])
            baseline = math.ceil(16*bound.bit_length()*-math.log(epsilon))
            require(baseline == budget['existing_sufficient_shots'], 'Baseline budget mismatch')
            require(abs(budget['baseline_ratio']-baseline/t) <= tolerance, 'Baseline ratio mismatch')
            rows.append({'p': p, 'q': q, 'extra_bits': group['extra_bits'], 'bound': bound,
                'epsilon': epsilon, 'shots': t, 'status': expected_status,
                'worst_orders': ';'.join(map(str, crossing['orders'])),
                'worst_probability_at_T': crossing['worst_probability'],
                'worst_probability_at_previous_T': group['worst_history'][t-1]['worst_probability'],
                'existing_sufficient_shots': baseline, 'ratio_to_own_sufficient_bound': baseline/t,
                'offline_group_wall_seconds': group['offline_wall_seconds'], 'precision_status': 'numerical_only'})
    return rows, order_rows, diagnostics


def write_csv(path, rows):
    fieldnames = list(dict.fromkeys(key for row in rows for key in row))
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--input', type=Path)
    source.add_argument('--run', action='store_true', help='Run the committed P3 driver, then audit and summarize')
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    input_path = args.input
    if args.run:
        input_path = args.output_dir / 'raw/evaluation.json'
        if input_path.exists():
            parser.error('Raw output already exists; choose a new output directory for reproduction')
        driver = Path(__file__).resolve().with_name('evaluate_bounded_reliability.py')
        subprocess.run([sys.executable, str(driver), '--root', str(args.root.resolve()),
                        '--config', str(args.config.resolve()), '--mode', 'main',
                        '--output', str(input_path.resolve())], check=True)
    raw = input_path.read_bytes()
    report = json.loads(raw)
    config_bytes = args.config.read_bytes()
    if hashlib.sha256(config_bytes).hexdigest() != report['config_sha256']:
        parser.error('Report/config hash mismatch')
    rows, orders, diagnostics = audit_report(report, json.loads(config_bytes))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary = {key: report[key] for key in ('commit', 'dirty_status', 'config_sha256',
        'driver_sha256', 'model_sha256', 'support_model_sha256', 'python_version', 'numpy_version',
        'high_precision_backend_and_version', 'precision_status', 'elapsed_wall_seconds', 'operation_count_definition')}
    summary.update({'production_source_sha256': report['production_source_manifest']['source_tree_sha256'],
        'raw_report_path': 'raw/evaluation.json', 'raw_report_sha256': hashlib.sha256(raw).hexdigest(),
        'raw_report_size_bytes': len(raw),
        'summarizer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'scope': 'P3 numerical finite-law characterization; not certified or literature superiority',
        'diagnostics': diagnostics, 'budgets': rows})
    (args.output_dir / 'summary.json').write_text(json.dumps(summary, indent=2, allow_nan=False)+'\n',
                                                encoding='utf-8', newline='\n')
    write_csv(args.output_dir / 'budgets.csv', rows)
    write_csv(args.output_dir / 'orders.csv', orders)
    print(json.dumps(diagnostics, indent=2))


if __name__ == '__main__':
    main()
