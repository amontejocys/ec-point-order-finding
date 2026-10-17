"""Capture a clean resolved environment; validate tests before publishing its lock."""

import argparse
import hashlib
from pathlib import Path
import platform
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path.cwd())
    args = parser.parse_args()
    spec = args.root / 'pyproject.toml'
    digest = hashlib.sha256(spec.read_bytes()).hexdigest()
    lines = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'], text=True).splitlines()
    pins = sorted(line for line in lines if line and not line.startswith(('#', '-e'))
                  and not line.lower().startswith(('ec-point-order-finding', 'ec_point_order_finding')))
    header = [
        '# Generated migration validation environment, not a historical-run lock.',
        '# Python: ' + platform.python_version() + '; platform: ' + platform.system(),
        '# pyproject.toml SHA256: ' + digest,
        '# Regenerate from a clean environment with python -m experiments.scripts.lock_environment',
    ]
    (args.root / 'requirements-lock.txt').write_text('\n'.join(header + pins) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
