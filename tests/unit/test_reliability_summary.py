"""Tests for the P3 report auditor; no main-grid or circuit execution."""

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

import pytest

from experiments.scripts.summarize_bounded_reliability import audit_report, mobius


@pytest.mark.parametrize('value,expected', [(1, 1), (2, -1), (3, -1), (4, 0),
                                         (6, 1), (12, 0), (30, -1)])
def test_small_mobius_values(value, expected):
    assert mobius(value) == expected


@pytest.fixture(scope='module')
def small_report():
    pytest.importorskip('mpmath')
    from experiments.scripts.evaluate_bounded_reliability import evaluate_main
    root = Path(__file__).resolve().parents[2]
    config = json.loads((root / 'experiments/configs/m2_f_main.json').read_text())
    config['grid']['primes'] = [5]
    config['grid']['extra_bits'] = [0]
    config['grid']['failure_targets'] = [.1, .01]
    config['budget_search']['maximum_shots'] = 32
    report = evaluate_main(root, config)
    report['precision_status'] = 'numerical_only'
    return config, report


def test_small_report_complete_audit(small_report):
    config, report = small_report
    rows, orders, diagnostics = audit_report(report, config)
    assert len(rows) == 2 and len(orders) == 9
    assert [row['shots'] for row in rows] == [7, 13]
    assert diagnostics['law_count'] == 9
    assert diagnostics['budget_count'] == 2
    assert diagnostics['mobius_max_abs_difference'] < 1e-10
    assert diagnostics['unresolved_or_unreached_budgets'] == 0


@pytest.mark.parametrize('corruption', ['duplicate_group', 'missing_order', 'mass',
                                      'threshold', 'high_precision', 'count'])
def test_reject_corrupt_report(small_report, corruption):
    config, original = small_report
    report = deepcopy(original)
    group = report['groups'][0]
    if corruption == 'duplicate_group':
        report['groups'].append(deepcopy(group))
    elif corruption == 'missing_order':
        group['orders'].pop()
    elif corruption == 'mass':
        group['orders'][0]['outcomes'][1]['exact_order'] += .02
    elif corruption == 'threshold':
        group['budgets'][0]['shots'] += 1
    elif corruption == 'high_precision':
        next(iter(group['budgets'][0]['high_precision_checks'].values()))['budgets'][0]['reference_exact_order'] = '0'
    else:
        group['orders'][0]['operation_counts']['divisibility_checks'] = -1
    with pytest.raises(ValueError):
        audit_report(report, config)


def test_one_command_replay_refuses_to_overwrite_raw_data(tmp_path):
    root = Path(__file__).resolve().parents[2]
    raw = tmp_path / 'raw/evaluation.json'
    raw.parent.mkdir()
    raw.write_text('existing raw data', encoding='utf-8')
    result = subprocess.run([sys.executable,
        str(root / 'experiments/scripts/summarize_bounded_reliability.py'),
        '--run', '--config', str(root / 'experiments/configs/m2_f_main.json'),
        '--output-dir', str(tmp_path)], capture_output=True, text=True)
    assert result.returncode == 2
    assert 'Raw output already exists' in result.stderr
    assert raw.read_text(encoding='utf-8') == 'existing raw data'
