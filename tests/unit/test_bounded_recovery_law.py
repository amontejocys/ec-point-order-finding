"""P2 checks: no main-grid or new reversible-circuit execution."""

from copy import deepcopy
from fractions import Fraction
import json
import math
from pathlib import Path

import numpy as np
import pytest

from experiments.reference.bounded_recovery_law import (
    accepted_by_order, advance_law, checked_outcomes, classify_threshold,
    independent_denominators, interval_endpoints, one_shot_by_order,
    precision_law, precision_weights, raw_probabilities, worst_orders)
from experiments.reference.curve import reference_order
from experiments.reference.gcd_recovery_law import gcd_law
from experiments.scripts.evaluate_bounded_reliability import evaluate_main, validate_config
from quantum_ec.recovery.continued_fractions import (
    convergent_denominators, verified_candidates)


def test_independent_fraction_reference():
    for q in (8, 16, 32):
        for y in range(q):
            assert independent_denominators(y, q) == list(convergent_denominators(y, q))


@pytest.mark.parametrize('p,a,point,q', [
    (5, 1, (0, 1), 128), (7, 0, (3, 0), 256), (7, 0, (0, 1), 256),
    (11, 4, (10, 3), 512), (29, 0, (6, 7), 2048)])
def test_divisibility_matches_every_production_outcome(p, a, point, q):
    r = reference_order(point, p, a)
    bound = p + 1 + math.isqrt(4*p)
    for y in range(q):
        assert accepted_by_order(y, q, r, bound) == verified_candidates(y, q, point, p, a)


@pytest.mark.parametrize('q,r', [(8, 2), (8, 3), (16, 5), (16, 4), (8, 8)])
def test_raw_spectrum_matches_explicit_fiber_dft(q, r):
    expected = np.array([sum(abs(sum(np.exp(2j*np.pi*k*y/q)
                        for k in range(offset, q, r)))**2
                        for offset in range(r)) / q**2 for y in range(q)])
    actual = raw_probabilities(q, r)
    assert actual == pytest.approx(expected, abs=1e-13)
    assert sum(actual) == pytest.approx(1, abs=1e-13)


def test_operation_counts_match_declared_units():
    q, r, bound = 16, 3, 10
    weights, counts, residual = one_shot_by_order(q, r, bound)
    denominators = [list(convergent_denominators(y, q)) for y in range(q)]
    assert counts['cf_denominators_generated'] == sum(map(len, denominators))
    assert counts['bounded_denominators_tested'] == sum(
        1 for row in denominators for d in row if 1 <= d <= bound)
    assert counts['divisibility_checks'] == counts['bounded_denominators_tested']
    assert counts['statistic_gcd_updates'] == sum(
        len({d for d in row if 1 <= d <= bound and d % r == 0}) for row in denominators)
    assert counts['dp_gcd_updates'] == 0
    state = advance_law({0: 1}, weights, counts)
    assert counts['dp_gcd_updates'] == len(weights)
    assert checked_outcomes(state, weights, r, 1, 1e-10)['partition_residual'] < 1e-10
    assert residual < 1e-10


def test_fraction_recurrence_and_combination():
    weights = {0: Fraction(1, 4), 10: Fraction(1, 4), 15: Fraction(1, 2)}
    state = {0: 1}
    for t in range(5):
        assert state == gcd_law(weights, t)
        state = advance_law(state, weights)
    assert precision_law({10: Fraction(1, 2), 15: Fraction(1, 2)}, 2)[5] == Fraction(1, 2)


def test_high_precision_and_interval_dyadic_case():
    pytest.importorskip('mpmath')
    weights, _ = precision_weights(8, 2, 4)
    interval, context = precision_weights(8, 2, 4, intervals=True)
    assert {d: p for d, p in weights.items() if p} == {0: Fraction(1, 2), 2: Fraction(1, 2)}
    for t in (0, 1, 2, 8):
        expected = 1 - Fraction(1, 2)**t
        enclosed = precision_law(interval, t).get(2, context.mpf(0))
        value = context.mpf(expected.numerator) / expected.denominator
        assert enclosed.a <= value <= enclosed.b
        assert len(interval_endpoints(enclosed)) == 2


def test_precision_reference_non_dyadic_and_no_global_context_mutation():
    mp = pytest.importorskip('mpmath')
    before = (mp.mp.dps, mp.iv.dps)
    reference, _ = precision_weights(16, 5, 10)
    weights, _, _ = one_shot_by_order(16, 5, 10)
    assert {d: float(p) for d, p in reference.items()} == pytest.approx(weights, abs=1e-13)
    precision_weights(16, 5, 10, intervals=True)
    assert (mp.mp.dps, mp.iv.dps) == before


def test_threshold_and_ties_do_not_certify_roundoff():
    assert classify_threshold(.99, .01, 1e-10) == 'unresolved'
    assert classify_threshold(.995, .01, 1e-10) == 'above'
    assert classify_threshold(.98, .01, 1e-10) == 'below'
    minimum, ties = worst_orders({5: .9, 6: .9+1e-12, 7: .95}, 1e-10)
    assert minimum == .9 and ties == [5, 6]


def test_driver_small_grid_not_main_configuration():
    root = Path(__file__).resolve().parents[2]
    config = json.loads((root / 'experiments/configs/m2_f_main.json').read_text())
    validate_config(config)
    small = deepcopy(config)
    small['grid']['primes'] = [5]
    small['grid']['extra_bits'] = [0]
    small['grid']['failure_targets'] = [.01]
    small['budget_search']['maximum_shots'] = 1
    report = evaluate_main(root, small)
    group = report['groups'][0]
    assert group['budgets'] == [{'epsilon': .01, 'shots': None, 'status': 'not_reached'}]
    assert len(group['orders']) == 9
    assert all(len(row['outcomes']) == 2 for row in group['orders'])


def test_driver_threshold_pair_and_high_precision_selection():
    pytest.importorskip('mpmath')
    root = Path(__file__).resolve().parents[2]
    config = json.loads((root / 'experiments/configs/m2_f_main.json').read_text())
    config['grid']['primes'] = [5]
    config['grid']['extra_bits'] = [0]
    config['grid']['failure_targets'] = [.1]
    config['budget_search']['maximum_shots'] = 32
    group = evaluate_main(root, config)['groups'][0]
    budget = group['budgets'][0]
    assert budget['status'] == 'numerically_estimated_first_crossing'
    assert budget['previous_budget']['worst_probability'] < .9
    assert budget['at_budget']['worst_probability'] > .9
    assert budget['previous_budget']['shots'] == budget['shots'] - 1
    selected = set(budget['at_budget']['orders']) | set(budget['previous_budget']['orders'])
    assert set(budget['high_precision_checks']) == selected
    assert all(len(check['budgets']) == 2 for check in budget['high_precision_checks'].values())


@pytest.mark.parametrize('q,r,bound', [(7, 3, 4), (8, 1, 4), (8, 5, 4),
                                     (8, 3, 10), (True, 2, 4)])
def test_reject_invalid_domain(q, r, bound):
    with pytest.raises(ValueError):
        one_shot_by_order(q, r, bound)


def test_reject_unsupported_config_and_corrupted_law():
    root = Path(__file__).resolve().parents[2]
    config = json.loads((root / 'experiments/configs/m2_f_main.json').read_text())
    config['grid']['orders']['minimum'] = 3
    with pytest.raises(ValueError):
        validate_config(config)
    with pytest.raises(ArithmeticError):
        checked_outcomes({0: 1.2}, {0: 1}, 2, 1, 1e-10)
