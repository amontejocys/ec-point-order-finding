"""Guard runtime code against accidental dependence on experiments or tests."""

import ast
from pathlib import Path
import unittest


class PackageBoundaryTests(unittest.TestCase):
    def test_runtime_imports_do_not_use_validation_or_legacy_modules(self):
        root = Path(__file__).resolve().parents[2] / 'src' / 'quantum_ec'
        for path in root.rglob('*.py'):
            tree = ast.parse(path.read_text(encoding='utf-8'))
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    imports.append(node.module or '')
                elif isinstance(node, ast.Import):
                    imports.extend(alias.name for alias in node.names)
                elif isinstance(node, ast.Call) and ast.unparse(node.func) == 'sys.path.insert':
                    self.fail(f'Legacy path injection in {path}')
            for name in imports:
                with self.subTest(path=path, module=name):
                    self.assertNotIn(name.split('.')[0], {'tests', 'experiments', 'r5', 'r6'})


if __name__ == '__main__':
    unittest.main()
