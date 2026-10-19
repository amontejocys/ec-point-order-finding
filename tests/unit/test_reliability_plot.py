"""Validate figure inputs/provenance without requiring Matplotlib in CI."""

import csv
import hashlib
import json
from pathlib import Path
import shutil

import pytest

from experiments.scripts.plot_reliability_budgets import load_plot_rows


@pytest.fixture
def plot_inputs(tmp_path):
    root = Path(__file__).resolve().parents[2]
    sources = [root/'results/m2-f/budgets.csv', root/'results/m2-f/summary.json',
               root/'experiments/configs/m2_f_main.json']
    copied = []
    for source in sources:
        target = tmp_path/source.name
        shutil.copyfile(source, target)
        copied.append(target)
    return copied


def test_full_plot_grid(plot_inputs):
    rows, config, summary = load_plot_rows(*plot_inputs)
    assert len(rows) == 66
    assert len(config['grid']['primes']) == 11
    assert summary['precision_status'] == 'numerical_only'


@pytest.mark.parametrize('corruption', ['status', 'shots', 'missing', 'duplicate', 'register'])
def test_reject_changed_plot_values(plot_inputs, corruption):
    csv_path, summary_path, config_path = plot_inputs
    with csv_path.open(newline='', encoding='utf-8') as stream:
        reader = csv.DictReader(stream)
        fields, rows = reader.fieldnames, list(reader)
    if corruption == 'status':
        rows[0]['status'] = 'unresolved'
    elif corruption == 'shots':
        rows[0]['shots'] = str(int(rows[0]['shots'])+1)
    elif corruption == 'missing':
        rows.pop()
    elif corruption == 'duplicate':
        rows.append(dict(rows[0]))
    else:
        rows[0]['q'] = str(int(rows[0]['q'])//2)
    with csv_path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    with pytest.raises(ValueError):
        load_plot_rows(csv_path, summary_path, config_path)


def test_reject_changed_plot_config(plot_inputs):
    csv_path, summary_path, config_path = plot_inputs
    config_path.write_text('{}', encoding='utf-8')
    with pytest.raises(ValueError, match='configuration'):
        load_plot_rows(csv_path, summary_path, config_path)


def test_figure_asset_and_manifest_match_inputs():
    root = Path(__file__).resolve().parents[2]
    prefix = root/'paper/figures/f_reliability_budgets'
    manifest = json.loads(prefix.with_suffix('.json').read_text())
    data = prefix.with_suffix('.png').read_bytes()
    assert data[:8] == b'\x89PNG\r\n\x1a\n'
    assert hashlib.sha256(data).hexdigest() == manifest['figure_sha256']
    dimensions = [int.from_bytes(data[16:20], 'big'), int.from_bytes(data[20:24], 'big')]
    assert dimensions == [round(v*manifest['dpi']) for v in manifest['size_inches']]
    for path, key in [('results/m2-f/budgets.csv', 'budgets_csv_sha256'),
                      ('results/m2-f/summary.json', 'summary_sha256'),
                      ('experiments/configs/m2_f_main.json', 'config_sha256'),
                      ('experiments/scripts/plot_reliability_budgets.py', 'script_sha256')]:
        assert hashlib.sha256((root/path).read_bytes()).hexdigest() == manifest[key]
    assert manifest['data_rows'] == 66
    assert manifest['precision_status'] == 'numerical_only'
