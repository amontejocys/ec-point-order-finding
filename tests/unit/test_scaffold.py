"""Repository checks only; these do not validate scientific code."""

import importlib
import unittest


class ScaffoldTests(unittest.TestCase):
    def test_namespaces_import(self):
        for name in (
            "classical", "circuits.arithmetic", "circuits.points",
            "circuits.order_finding", "recovery", "signing",
            "simulation", "resources", "baselines",
        ):
            with self.subTest(name=name):
                importlib.import_module("quantum_ec." + name)

    def test_independent_reference_namespace_imports(self):
        importlib.import_module("tests.reference")


if __name__ == "__main__":
    unittest.main()
