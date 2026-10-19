from fractions import Fraction
from itertools import product
import math

import pytest

from experiments.reference.gcd_recovery_law import (
    admission_summary, divisor_inversion_law, gcd_law, one_shot_law)
from quantum_ec.recovery.factor_free_recovery import accumulate_verified_periods


def test_exact_fraction_law_against_brute_force_and_inversion():
    weights = {0: Fraction(1, 4), 10: Fraction(1, 4), 15: Fraction(1, 2)}
    for t in range(5):
        expected = {}
        for values in product(weights, repeat=t):
            mass = math.prod(weights[d] for d in values)
            g = math.gcd(*values) if values else 0
            expected[g] = expected.get(g, 0) + mass
        actual = gcd_law(weights, t)
        inverted = divisor_inversion_law(weights, t)
        assert actual == expected
        assert all(actual.get(g, 0) == inverted.get(g, 0)
                   for g in set(actual) | set(inverted))


def test_combination_recovers_order_without_single_shot_order():
    assert gcd_law({10: Fraction(1, 2), 15: Fraction(1, 2)}, 2)[5] == Fraction(1, 2)


def test_zero_is_no_candidate_and_order_is_absorbing():
    assert gcd_law({0: 1}, 4) == {0: 1}
    weights = {0: Fraction(1, 2), 5: Fraction(1, 2)}
    assert gcd_law(weights, 3) == {0: Fraction(1, 8), 5: Fraction(7, 8)}


def test_policy_replay_for_all_two_shot_sequences():
    q, point, p, a = 8, (0, 1), 5, 0
    from quantum_ec.simulation.ideal_distribution import ideal_probabilities
    probs = ideal_probabilities(q, 3)
    expected = {}
    for values in product(range(q), repeat=2):
        g = accumulate_verified_periods(values, q, point, p, a)['verified_period'] or 0
        expected[g] = expected.get(g, 0) + probs[values[0]] * probs[values[1]]
    actual = gcd_law(one_shot_law(q, point, p, a, 3), 2)
    assert actual == pytest.approx(expected, abs=1e-12)


def test_admission_small_exact_and_general_bound():
    result = admission_summary({0: .1, 5: .8, 10: .1}, 5)
    assert result['admitted_correct'] == .8
    assert result['incorrect_admission_upper_bound'] == 0
    assert result['admission_partition_exact_for_policy']
    result = admission_summary({9: 1}, 9)
    assert result['rejected_exact_composite_order_ideal'] == 1
    result = admission_summary({41: .75, 41*43: .25}, 41)
    assert result['incorrect_admission_upper_bound'] == .25 * 2**(-128)
    assert not result['admission_partition_exact_for_policy']


@pytest.mark.parametrize('weights,shots', [({0: .5}, 1), ({-1: 1}, 1),
                                         ({0: 1}, -1), ({0: float('nan')}, 1)])
def test_invalid_laws(weights, shots):
    with pytest.raises(ValueError):
        gcd_law(weights, shots)
