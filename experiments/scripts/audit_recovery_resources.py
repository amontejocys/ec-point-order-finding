"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import argparse
import csv
import json
from pathlib import Path
from quantum_ec.resources.complete_resources import complete_quantum_resources
from experiments.reference.curve import reference_add
from quantum_ec.resources.resource_model import compact_scalar_resources
from quantum_ec.recovery.success_budget import sufficient_budget


def audit_cases(report):
    rows = []
    for case in report['cases']:
        p, a, b, point = case['p'], case['a'], case['b'], tuple(case['point'])
        width = p.bit_length()
        powers = [point]
        for _ in range(1, case['m']):
            powers.append(reference_add(powers[-1], powers[-1], p, a))
        model = compact_scalar_resources(width, p, a, b, powers)
        actual = case['logical_resources_arithmetic']
        if model['total_instructions'] != actual['input_instructions']:
            raise AssertionError('Actual scalar instructions disagree with analytic count')
        if model['total_qubits'] != actual['original_qubits']:
            raise AssertionError('Actual scalar memory disagrees with analytic count')
        complete = complete_quantum_resources({
            'basis': 'X,CX,CCX with exact full-Toffoli clean AND chains',
            'parameters': {'m': case['m']}, 'resources': actual})
        budget = sufficient_budget(p, 0.01)
        rows.append({'p': p, 'a': a, 'b': b, 'Px': point[0], 'Py': point[1],
                     'ell': width, 'm': case['m'], 'Q': case['q'],
                     'controlled_additions': case['controlled_additions'],
                     'arithmetic_high_level_instructions': actual['input_instructions'],
                     'arithmetic_ccx': actual['ccx_count'],
                     'logical_qubits_with_clean_mcx_pool': complete['logical_qubits'],
                     'full_x': complete['gate_counts']['x'],
                     'full_cx': complete['gate_counts']['cx'],
                     'full_h': complete['gate_counts']['h'],
                     'full_cp_ideal': complete['gate_counts']['cp'],
                     'full_mixed_basis_instructions': complete['unitary_instructions_in_this_mixed_basis'],
                     'sufficient_T_for_epsilon_0_01': budget['sufficient_independent_ideal_shots']})
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
    report = json.loads(args.input.read_text(encoding='ascii'))
    rows = audit_cases(report)
    with args.output.open('w', newline='', encoding='ascii') as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
