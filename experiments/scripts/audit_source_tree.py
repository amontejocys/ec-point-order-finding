"""Reproduce the historical src/**/*.py raw-byte fingerprint with a manifest."""

import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import sys


def source_manifest(root):
    files = [(p.relative_to(root).as_posix(), p) for p in (root / 'src').rglob('*.py')]
    records = [{'path': name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
               for name, path in sorted(files)]
    payload = '\n'.join(f"{row['path']} {row['sha256']}" for row in records)
    return {
        'algorithm': 'sha256 of UTF-8 path + space + raw-file SHA256 records, POSIX lexical order, LF separators, no final LF',
        'scope': 'All src/**/*.py only; not tests, experiments, manuscript, or a Git commit',
        'line_endings': 'File bytes are not normalized; checkout line-ending conversion changes the hash',
        'source_tree_sha256': hashlib.sha256(payload.encode('utf-8')).hexdigest(),
        'files': records,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--expect', help='Expected tree fingerprint; mismatch is an error')
    args = parser.parse_args()
    report = source_manifest(args.root)
    if args.expect and report['source_tree_sha256'] != args.expect:
        parser.error('Source tree fingerprint differs from --expect')
    report['environment_observed_now'] = {
        'python': platform.python_version(), 'sys_version': sys.version,
        'implementation': platform.python_implementation(),
        'executable': 'not recorded: local interpreter paths contain user names',
        'dependencies': {name: importlib.metadata.version(name) for name in ['qiskit', 'numpy', 'pytest']},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(report['source_tree_sha256'])


if __name__ == '__main__':
    main()
