"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import argparse
import json
from pathlib import Path
import numpy as np
from quantum_ec.recovery.factor_free_recovery import uniform_register_size
from quantum_ec.circuits.order_finding.elliptic_order_finding import EllipticOrderFinding
from quantum_ec.simulation.sparse_order_finding import fourier_probabilities
from quantum_ec.resources.complete_resources import quantum_overhead
from experiments.reference.curve import reference_add, reference_order
from quantum_ec.simulation.ideal_distribution import ideal_probabilities
from quantum_ec.recovery.factor_free_recovery import recover_prefixes
from quantum_ec.simulation.real_arithmetic import cached_arithmetic_outputs


def validate_reference_outputs(outputs, builder):
    # Reference is consulted only after actual gate propagation completes.
    current = None
    for output in outputs:
        expected = (1 if current is None else
                    (current[0] << 1) | (current[1] << (builder.width+1)))
        if output != expected:
            raise AssertionError("Arithmetic disagrees with independent reference")
        current = reference_add(current, builder.point, builder.modulus, builder.a)


def run_case(p, a, b, point, trials, seed):
    register = uniform_register_size(p)
    builder = EllipticOrderFinding(register['m'], p, a, b, point, evaluator_variant='compact')
    print(f"Building real arithmetic: p={p}, P={point}, Q={register['q']}", flush=True)
    outputs, audit = cached_arithmetic_outputs(builder)
    validate_reference_outputs(outputs, builder)
    probabilities = fourier_probabilities(outputs)
    order = reference_order(point, p, a)
    np.testing.assert_allclose(probabilities, ideal_probabilities(register['q'], order), atol=2e-12)
    budgets = [1, 2, 4, 8, 16, 32, 64]
    sampled = np.random.default_rng(seed).choice(register['q'], size=(trials, 64), p=probabilities)
    cache = {}
    counts = {t: {'exact': 0, 'nonminimal_multiple': 0, 'no_candidate': 0} for t in budgets}
    for measurements in sampled:
        for t, period in recover_prefixes(measurements, register['q'], point, p, a, budgets, cache).items():
            category = ('no_candidate' if period is None else
                        'exact' if period == order else 'nonminimal_multiple')
            if period is not None and period % order:
                raise AssertionError("Invalid recovered period")
            counts[t][category] += 1
    results = [{'shots': t, **counts[t], 'exact_rate': counts[t]['exact']/trials} for t in budgets]
    overhead = quantum_overhead(register['m'])
    report = {'p': p, 'a': a, 'b': b, 'point': point, **register,
              'reference_order_for_evaluation_only': order, 'seed': seed,
              'trials': trials, 'minimality_certified_by_recovery': False,
              **audit, 'quantum_overhead': overhead, 'recovery_results': results}
    print(f"Validated all {len(outputs)} arithmetic inputs; reference order={order}", flush=True)
    return report, outputs, probabilities, sampled


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--trials', type=int, default=100)
    args = parser.parse_args()
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.trials < 1:
        parser.error('--trials must be positive')
    cases = [(5, 1, 1, (0, 1)), (7, 0, 1, (3, 0)),
             (7, 0, 1, (0, 1)), (11, 4, 3, (10, 3)), (29, 0, 7, (6, 7))]
    rows, arrays = [], {}
    for index, case in enumerate(cases):
        row, outputs, probabilities, sampled = run_case(*case, args.trials, 20261008+index)
        rows.append(row)
        arrays[f'outputs_{index}'] = np.asarray(outputs)
        arrays[f'probabilities_{index}'] = probabilities
        arrays[f'measurements_{index}'] = sampled
    report = {'scope': 'Actual phase-free arithmetic gate propagation for every scalar input; ideal IQFT via FFT; no noise',
              'not_dense_statevector': True,
              'no_factorization_in_recovery': True,
              'cache_is_simulation_only_not_circuit_lookup': True,
              'cases': rows}
    args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='ascii')
    np.savez_compressed(args.output.with_suffix('.npz'), **arrays)


if __name__ == "__main__":
    main()
