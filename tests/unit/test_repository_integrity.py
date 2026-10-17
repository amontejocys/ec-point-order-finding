"""Fast guards for scripts that are not imported by numerical tests."""

import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

from experiments.scripts.audit_source_tree import source_manifest

ROOT = Path(__file__).resolve().parents[2]


class RepositoryIntegrityTests(unittest.TestCase):
    def test_all_active_python_files_compile_without_writing_bytecode(self):
        for prefix in ('src', 'tests', 'experiments'):
            for path in (ROOT / prefix).rglob('*.py'):
                with self.subTest(path=path.relative_to(ROOT).as_posix()):
                    compile(path.read_text(encoding='utf-8-sig'), str(path), 'exec')

    def test_non_argparse_recovery_entry_point(self):
        environment = dict(os.environ)
        environment['PYTHONPATH'] = str(ROOT / 'src')
        environment['PYTHONDONTWRITEBYTECODE'] = '1'
        result = subprocess.run([sys.executable, '-m', 'experiments.scripts.factor_free_recovery'],
                                cwd=ROOT, env=environment, text=True,
                                capture_output=True, check=True, timeout=30)
        data = json.loads(result.stdout)
        self.assertEqual(data['illustrative_outcomes_not_sampled']['verified_period'], 5)
        self.assertEqual(data['sufficient_unknown_order_register']['q'], 2048)

    def test_source_fingerprint_uses_sorted_portable_relative_paths(self):
        report = source_manifest(ROOT)
        names = [r['path'] for r in report['files']]
        self.assertEqual(names, sorted(names))
        self.assertTrue(all(name.startswith('src/') and '\\' not in name for name in names))
        self.assertEqual(len(report['source_tree_sha256']), 64)

    def test_new_metadata_paths_are_portable(self):
        paths = [ROOT / 'experiments/configs/expanded_curve_validation.json']
        paths += list((ROOT / 'results').glob('*/summary.json'))
        for path in paths:
            data = json.loads(path.read_text(encoding='utf-8'))
            def visit(value):
                if isinstance(value, dict):
                    for key, child in value.items():
                        if key in {'path', 'report', 'arrays', 'previous_full_validation'} and isinstance(child, str):
                            self.assertNotIn('\\', child, f'{path}: {key}')
                        visit(child)
                elif isinstance(value, list):
                    for child in value:
                        visit(child)
            visit(data)


if __name__ == '__main__':
    unittest.main()
