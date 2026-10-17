"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import unittest
from quantum_ec.circuits.points.ordinary_point_sum import ordinary_point_sum
from quantum_ec.circuits.points.ordinary_point_sum_shared import ordinary_point_sum_shared
from tests.support.permutation import apply_basis, compile_x_permutation


class SharedOrdinarySumTests(unittest.TestCase):
    def test_small_equivalence_including_invalid_coordinates(self):
        width, p, u, v = 2, 3, 1, 1
        baseline = compile_x_permutation(ordinary_point_sum(width, p, u, v))
        variants = [compile_x_permutation(ordinary_point_sum_shared(width, p, u, v, inverse_variant=variant)) for variant in ("history", "compact")]
        for x in range(4):
            for y in range(4):
                for out_x, out_y in ((0, 0), (3, 2)):
                    initial = x | (y << width) | (out_x << (2 * width)) | (out_y << (3 * width))
                    expected = apply_basis(baseline, initial)
                    self.assertLess(expected, 1 << (4 * width))
                    for shared in variants:
                        self.assertEqual(apply_basis(shared, initial), expected)
                        self.assertEqual(apply_basis(shared, expected), initial)

    def test_p29_curve_points_and_resource_comparison(self):
        width, p, u, v = 5, 29, 12, 13
        shared_circuit = ordinary_point_sum_shared(width, p, u, v)
        compact_circuit = ordinary_point_sum_shared(width, p, u, v, inverse_variant="compact")
        variants = [compile_x_permutation(circuit) for circuit in (shared_circuit, compact_circuit)]
        checked = 0
        for x in range(p):
            for y in range(p):
                if x == u or (y*y-x**3-7) % p:
                    continue
                slope = (y-v)*pow((x-u) % p, -1, p) % p
                result_x = (slope*slope-x-u) % p
                result_y = (slope*(x-result_x)-y) % p
                initial = x | (y << width)
                expected = initial | (result_x << (2 * width)) | (result_y << (3 * width))
                for gates in variants:
                    self.assertEqual(apply_basis(gates, initial), expected)
                    self.assertEqual(apply_basis(gates, expected), initial)
                checked += 1
        self.assertEqual(checked, 27)
        baseline = ordinary_point_sum(width, p, u, v)
        self.assertLess(shared_circuit.num_qubits, baseline.num_qubits)
        self.assertLess(len(shared_circuit.data), len(baseline.data))
        self.assertLess(compact_circuit.num_qubits, shared_circuit.num_qubits)
        self.assertLess(len(compact_circuit.data), len(baseline.data))
        self.assertEqual(compact_circuit.metadata["inverse_variant"], "compact")
        print(f"p=29 ordinary evaluator: baseline {baseline.num_qubits} qubits / {len(baseline.data)} logical instructions; shared {shared_circuit.num_qubits} qubits / {len(shared_circuit.data)} logical instructions.")
        print(f"p=29 combined shared/compact: {compact_circuit.num_qubits} qubits / {len(compact_circuit.data)} logical instructions.")
        print("Verified 27 ordinary curve points and cleanup by logical gate propagation; no hardware-level cost claim.")

    def test_unknown_variant(self):
        with self.assertRaises(ValueError):
            ordinary_point_sum_shared(2, 3, 1, 1, inverse_variant="unknown")
