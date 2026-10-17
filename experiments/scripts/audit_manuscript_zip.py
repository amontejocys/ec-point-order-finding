"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import argparse
import csv
from decimal import Decimal
import hashlib
import json
import math
from pathlib import Path
import re
import zipfile


def scientific_cell(cell):
    # Parse only the explicit scientific-number format used in this table.
    match = re.fullmatch(r'\s*\$([0-9.]+)\\!\\times\\!10\^\{([0-9]+)\}\$\s*', cell)
    if not match:
        raise ValueError(f'Unsupported historical numeric cell: {cell}')
    return Decimal(match[1]) * Decimal(10) ** int(match[2])


def audit_zip(path):
    before = hashlib.sha256(path.read_bytes()).hexdigest()
    with zipfile.ZipFile(path) as archive:
        texts = {name: archive.read(name).decode('utf-8') for name in archive.namelist()
                 if name.endswith(('.tex', '.bib'))}
    after = hashlib.sha256(path.read_bytes()).hexdigest()
    if before != after:
        raise AssertionError('ZIP changed during read-only audit')
    keys = set(re.findall(r'@\w+\s*\{\s*([^,\s]+)\s*,', texts['main.bib']))
    citations = set()
    for name, source in texts.items():
        if name.endswith('.tex'):
            for group in re.findall(r'\\cite(?:\[[^]]*\])*\{([^}]+)\}', source):
                citations.update(key.strip() for key in group.split(','))
    rows = []
    source = texts['sec/04-results_discussions.tex']
    table = re.search(r'\\begin\{tabular\}\{rrrr\}(.*?)\\end\{tabular\}', source, re.S).group(1)
    for line in table.splitlines():
        if not re.match(r'^\s*\d+\s*&', line):
            continue
        cells = line.removesuffix('\\\\').split('&')
        n = int(cells[0])
        given = [scientific_cell(cell) for cell in cells[1:]]
        enum = 2**n
        coherent_shape = n**3 * int(math.log2(n))
        table_shape = 2**(2*n)*n*n
        rows.append({'n': n, 'reported_classical': str(given[0]),
                     'reported_coherent': str(given[1]), 'reported_lookup': str(given[2]),
                     'diagnostic_2_power_n': str(enum),
                     'diagnostic_n_cubed_log2_n': str(coherent_shape),
                     'diagnostic_2_power_2n_times_n_squared': str(table_shape),
                     'reported_lookup_over_expression': str(given[2]/Decimal(table_shape))})
    locations = []
    patterns = ['C(n)', 'C_{\\mathrm{tbl}}', 'parity', 'lookup', 'constant probability',
                'constant success', '4/\\pi', 'bit-identical', 'classical order', 'statevector']
    for name, source in texts.items():
        if not name.endswith('.tex'):
            continue
        for number, line in enumerate(source.splitlines(), 1):
            matches = [pattern for pattern in patterns if pattern in line]
            if matches:
                locations.append({'file': name, 'line': number, 'markers': matches})
    return {'zip_path': str(path.resolve()), 'sha256_unchanged': before,
            'main_file': 'main.tex', 'cited_keys_missing_from_bib': sorted(citations-keys),
            'relevant_existing_keys': sorted(keys & {'ProosZalka2003', 'Roetteler2017', 'Haner2020', 'Litinski2023', 'Shor1997'}),
            'historical_table_scope': 'Numerical consistency diagnostic only; not comparable runtimes or a replacement table',
            'historical_table': rows, 'locations_to_reconcile': locations}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('zip_path', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
    report = audit_zip(args.zip_path)
    args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    with args.output.with_suffix('.csv').open('w', newline='', encoding='ascii') as file:
        writer = csv.DictWriter(file, fieldnames=list(report['historical_table'][0]))
        writer.writeheader()
        writer.writerows(report['historical_table'])
    print(json.dumps({'sha256_unchanged': report['sha256_unchanged'],
                      'missing_citation_keys': report['cited_keys_missing_from_bib'],
                      'lookup_column_ratios': [{ 'n': row['n'], 'ratio': row['reported_lookup_over_expression'] }
                                               for row in report['historical_table']]}, indent=2))


if __name__ == "__main__":
    main()
