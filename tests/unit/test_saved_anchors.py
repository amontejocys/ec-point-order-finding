"""Synthetic fixtures for P4; no dependence on ignored data or gate execution."""

from copy import deepcopy
import json
from pathlib import Path

import numpy as np
import pytest

from experiments.reference.curve import reference_add
from experiments.scripts.evaluate_saved_anchors import (
    actual_admission, checked_path, evaluate_anchor, load_frozen_inputs, sha256)
from quantum_ec.simulation.sparse_order_finding import fourier_probabilities


def fixture_case(p=7, a=0, b=1, point=(3, 0), order=2, q=256):
    root = Path(__file__).resolve().parents[2]
    config = json.loads((root/'experiments/configs/m2_f_main.json').read_text())
    case = {'index': 0, 'p': p, 'a': a, 'b': b, 'point': list(point), 'q': q,
            'probabilities_array': 'probabilities_0'}
    historical = {**case, 'reference_order_for_evaluation_only': order,
        'basis_inputs_checked': q, 'actual_gate_propagations': 0,
        'controlled_additions': 0, 'distinct_adder_definitions': 0,
        'logical_resources_arithmetic': {},
        'recovery_results': [{'shots': t} for t in (1, 2, 4, 8)]}
    current, outputs = None, []
    for _ in range(q):
        outputs.append(1 if current is None else (current[0] << 1) | (current[1] << (p.bit_length()+1)))
        current = reference_add(current, point, p, a)
    outputs = np.asarray(outputs, dtype=np.int64)
    probabilities = fourier_probabilities(outputs)
    return config, case, historical, outputs, probabilities


def test_synthetic_prime_order_recovery_and_actual_admission(monkeypatch):
    import quantum_ec.classical.primality as primality
    monkeypatch.setattr(primality.secrets, 'randbelow', lambda _: pytest.fail('Unexpected randomized test'))
    config, case, historical, outputs, probabilities = fixture_case()
    row = evaluate_anchor(case, historical, outputs, probabilities, config)
    assert row['scalar_outputs_rechecked'] == 256
    for budget in row['budgets']:
        expected = 1 - 2.0**(-budget['shots'])
        assert budget['saved_distribution_recovery']['exact_order'] == pytest.approx(expected, abs=1e-12)
        assert budget['actual_production_admission']['admitted_correct'] == pytest.approx(expected, abs=1e-12)
        assert budget['model_admission']['incorrect_admission_upper_bound'] == 0
        assert budget['full_law_max_abs_difference'] < 1e-10


def test_synthetic_composite_order_recovered_but_rejected():
    config, case, historical, outputs, probabilities = fixture_case(5, 1, 1, (0, 1), 9, 128)
    row = evaluate_anchor(case, historical, outputs, probabilities, config)
    for budget in row['budgets']:
        recovered = budget['saved_distribution_recovery']['exact_order']
        assert budget['actual_production_admission']['admitted_correct'] == 0
        assert budget['actual_production_admission']['rejected_exact_composite_order'] == recovered


def test_nonminimal_order_rejection_is_not_recovery_failure():
    actual = actual_admission({0: .1, 5: .8, 10: .1}, 5, (6, 7), 29, 0, 7, 64, {})
    assert actual == {'recovery_failure': .1, 'admitted_correct': .8,
                      'rejected_exact_composite_order': 0, 'rejected_nonminimal': .1}


@pytest.mark.parametrize('corruption', ['shape', 'dtype', 'negative', 'mass', 'nan',
                                      'label', 'high_work_bit', 'spectrum', 'order', 'coverage'])
def test_reject_corrupted_anchor(corruption):
    config, case, historical, outputs, probabilities = fixture_case()
    if corruption == 'shape':
        probabilities = probabilities[:-1]
    elif corruption == 'dtype':
        outputs = outputs.astype(float)
    elif corruption == 'negative':
        probabilities[1] = -1e-15
    elif corruption == 'mass':
        probabilities *= .9
    elif corruption == 'nan':
        probabilities[0] = float('nan')
    elif corruption == 'label':
        outputs[0] = 0
    elif corruption == 'high_work_bit':
        outputs[1] |= 1 << (2*case['p'].bit_length()+1)
    elif corruption == 'spectrum':
        probabilities = np.roll(probabilities, 1)
    elif corruption == 'order':
        historical['reference_order_for_evaluation_only'] = 3
    else:
        historical['basis_inputs_checked'] -= 1
    with pytest.raises((ValueError, ArithmeticError)):
        evaluate_anchor(case, historical, outputs, probabilities, config)


def test_frozen_loader_and_hash_guard(tmp_path):
    _, case, historical, outputs, probabilities = fixture_case()
    report = {'scope': 'Synthetic test fixture, not gate propagation', 'not_dense_statevector': True,
              'cache_is_simulation_only_not_circuit_lookup': True, 'cases': [historical]}
    report_path, array_path = tmp_path/'report.json', tmp_path/'arrays.npz'
    report_path.write_text(json.dumps(report), encoding='utf-8')
    np.savez(array_path, outputs_0=outputs, probabilities_0=probabilities)
    anchors = {'source_report': 'report.json', 'source_report_sha256': sha256(report_path),
               'source_arrays': 'arrays.npz', 'source_arrays_sha256': sha256(array_path), 'cases': [case]}
    _, loaded = load_frozen_inputs(tmp_path, anchors)
    assert len(loaded) == 1
    assert np.array_equal(loaded[0][2], outputs)
    corrupted = deepcopy(anchors)
    corrupted['source_arrays_sha256'] = '0'*64
    with pytest.raises(ValueError, match='hash mismatch'):
        load_frozen_inputs(tmp_path, corrupted)
    corrupted = deepcopy(anchors)
    corrupted['cases'][0]['point'] = [0, 1]
    with pytest.raises(ValueError, match='metadata'):
        load_frozen_inputs(tmp_path, corrupted)
    corrupted = deepcopy(anchors)
    corrupted['cases'].append(deepcopy(case))
    with pytest.raises(ValueError, match='indices'):
        load_frozen_inputs(tmp_path, corrupted)


def test_missing_archive_and_path_escape_fail_without_regeneration(tmp_path):
    anchors = {'source_report': 'missing.json', 'source_arrays': 'missing.npz',
               'source_report_sha256': '0'*64, 'source_arrays_sha256': '0'*64}
    with pytest.raises(FileNotFoundError, match='restore the archived dataset'):
        load_frozen_inputs(tmp_path, anchors)
    with pytest.raises(ValueError, match='inside the repository'):
        checked_path(tmp_path, '../escape.json')
