"""Plot frozen P3 tables only; does not rerun the scientific model."""

import argparse
import csv
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
import platform


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_plot_rows(budgets_path, summary_path, config_path):
    config = json.loads(config_path.read_text())
    summary = json.loads(summary_path.read_text())
    if digest(config_path) != summary['config_sha256']:
        raise ValueError('Plot configuration differs from evaluated configuration')
    with budgets_path.open(encoding='utf-8', newline='') as stream:
        csv_rows = list(csv.DictReader(stream))
    rows = []
    for row in csv_rows:
        item = {key: int(row[key]) for key in ('p', 'q', 'extra_bits', 'shots')}
        item['epsilon'] = float(row['epsilon'])
        if row['status'] != 'numerically_estimated_first_crossing' or row['precision_status'] != 'numerical_only':
            raise ValueError('Plot cannot imply a resolved/certified budget for other statuses')
        bound = item['p'] + 1 + math.isqrt(4*item['p'])
        if item['q'] != 1 << ((bound*bound).bit_length()+item['extra_bits']):
            raise ValueError('Plot register does not match frozen sizing')
        if not 1 <= item['shots'] <= config['budget_search']['maximum_shots']:
            raise ValueError('Plot budget outside frozen range')
        rows.append(item)
    expected = {(p, extra, eps) for p in config['grid']['primes']
                for extra in config['grid']['extra_bits']
                for eps in config['grid']['failure_targets']}
    keys = [(row['p'], row['extra_bits'], row['epsilon']) for row in rows]
    if set(keys) != expected or len(keys) != len(expected):
        raise ValueError('Plot requires the complete frozen grid, without duplicates')
    mapped = {(row['p'], row['extra_bits'], row['epsilon']): row['shots'] for row in rows}
    reference = {(row['p'], row['extra_bits'], row['epsilon']): row['shots'] for row in summary['budgets']}
    if mapped != reference:
        raise ValueError('CSV and audited summary disagree')
    return rows, config, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    if args.output_dir.exists():
        parser.error('Choose a new output directory; existing figures are not overwritten')
    root = args.root.resolve()
    budgets_path = root/'results/m2-f/budgets.csv'
    summary_path = root/'results/m2-f/summary.json'
    config_path = root/'experiments/configs/m2_f_main.json'
    rows, config, summary = load_plot_rows(budgets_path, summary_path, config_path)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    with plt.rc_context({'font.size': 8, 'axes.labelsize': 8, 'xtick.labelsize': 7,
                         'ytick.labelsize': 7, 'font.family': 'DejaVu Sans'}):
        figure, axis = plt.subplots(figsize=(3.5, 2.65), dpi=500)
        figure.subplots_adjust(left=.15, right=.985, bottom=.18, top=.76)
        colors = ['#0072b2', '#009e73', '#d55e00']
        for epsilon, color in zip(config['grid']['failure_targets'], colors):
            for extra in config['grid']['extra_bits']:
                series = sorted((r for r in rows if r['epsilon'] == epsilon
                                 and r['extra_bits'] == extra), key=lambda r: r['p'])
                axis.plot([r['p'] for r in series], [r['shots'] for r in series],
                          color=color, linewidth=1, linestyle='-' if extra == 0 else '--',
                          marker='o' if extra == 0 else 's', markersize=2.8 if extra == 0 else 4,
                          markerfacecolor=color if extra == 0 else 'none', markeredgewidth=.65)
        axis.set_xlabel('Field prime $p$')
        axis.set_ylabel('Estimated measurement budget $T$')
        axis.set_xticks(config['grid']['primes'])
        axis.set_ylim(4, 26)
        axis.set_yticks([4, 8, 12, 16, 20, 24])
        axis.grid(axis='y', color='#dddddd', linewidth=.5)
        axis.set_axisbelow(True)
        axis.spines[['top', 'right']].set_visible(False)
        figure.legend([Line2D([], [], color=c, linewidth=1.4) for c in colors],
                      [rf'$\varepsilon={eps:g}$' for eps in config['grid']['failure_targets']],
                      loc='upper center', bbox_to_anchor=(.56, 1.02), ncol=3, frameon=False,
                      handlelength=1.4, columnspacing=.8, fontsize=7.5)
        figure.legend([Line2D([], [], color='#333333', marker='o', markersize=3, linewidth=1),
                       Line2D([], [], color='#333333', marker='s', markerfacecolor='none',
                              markersize=4, linestyle='--', linewidth=1)],
                      ['$Q_0$', '$2Q_0$'], loc='upper center', bbox_to_anchor=(.56, .91),
                      ncol=2, frameon=False, fontsize=7.5, handlelength=2.4)
        args.output_dir.mkdir(parents=True)
        path = args.output_dir/'f_reliability_budgets.png'
        figure.savefig(path, dpi=500, facecolor='white')
        plt.close(figure)
    manifest = {'scope': 'P5 figure generated from existing numerical P3 tables; no scientific rerun',
        'figure_sha256': digest(path), 'script_sha256': digest(Path(__file__)),
        'budgets_csv_sha256': digest(budgets_path), 'summary_sha256': digest(summary_path),
        'config_sha256': digest(config_path), 'scientific_source_commit': summary['commit'],
        'production_source_sha256': summary['production_source_sha256'],
        'python_version': platform.python_version(),
        'plotting_packages': {name: importlib.metadata.version(name) for name in ('matplotlib', 'numpy', 'pillow')},
        'plotting_environment_is_separate_from_scientific_environment': True,
        'dpi': 500, 'size_inches': [3.5, 2.65], 'data_rows': len(rows),
        'precision_status': 'numerical_only',
        'caption': 'Numerically estimated budgets over every integer order 2 <= r <= B for ideal independent executions. Q0 is the frozen baseline register, with Q0 > B^2; dashed squares double Q0. Lines connect evaluated primes only. These are offline small-field calibrations, not certified guarantees.'}
    (args.output_dir/'f_reliability_budgets.json').write_text(json.dumps(manifest, indent=2)+'\n',
                                                           encoding='utf-8', newline='\n')
    print(path.name)


if __name__ == '__main__':
    main()
