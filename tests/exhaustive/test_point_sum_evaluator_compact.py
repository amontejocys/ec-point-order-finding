"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import unittest
from quantum_ec.circuits.points.point_sum_evaluator import point_sum_evaluator
from quantum_ec.circuits.points.point_sum_evaluator_compact import point_sum_evaluator_compact
from tests.support.permutation import apply_basis, compile_x_permutation
from tests.reference.encoding import expected_sum_encoding


class CompactPointSumTests(unittest.TestCase):
    def test_all_small_encodings_and_order_two(self):
        for width, p, a, b, u, v in ((3, 5, 1, 1, 0, 1), (3, 5, 1, 0, 0, 0)):
            gates = compile_x_permutation(point_sum_evaluator_compact(width, p, a, b, u, v))
            size = 2 * width + 1
            for enc in range(1 << size):
                result = expected_sum_encoding(enc, width, p, a, b, u, v)
                for output in (0, (1 << size)-1):
                    initial = enc | (output << size)
                    expected = enc | ((output ^ result) << size)
                    self.assertEqual(apply_basis(gates, initial), expected)
                    self.assertEqual(apply_basis(gates, expected), initial)

    def test_p29_points_and_resource_comparison(self):
        width, p, a, b, u, v = 5, 29, 0, 7, 12, 13
        compact = point_sum_evaluator_compact(width, p, a, b, u, v)
        gates = compile_x_permutation(compact)
        size = 2 * width + 1
        valid = [1] + [(x << 1) | (y << (width + 1)) for x in range(p) for y in range(p) if (y*y-x**3-a*x-b) % p == 0]
        self.assertEqual(len(valid), 30)
        invalid = [0, 1 | (6 << 1) | (7 << (width + 1)), 31 << 1, (6 << 1) | (29 << (width + 1))]
        for enc in valid + invalid:
            result = expected_sum_encoding(enc, width, p, a, b, u, v)
            for output in (0, (1 << size)-1):
                initial = enc | (output << size)
                expected = enc | ((output ^ result) << size)
                self.assertEqual(apply_basis(gates, initial), expected)
                self.assertEqual(apply_basis(gates, expected), initial)
        baseline = point_sum_evaluator(width, p, a, b, u, v)
        self.assertLess(compact.num_qubits, baseline.num_qubits)
        self.assertLess(len(compact.data), len(baseline.data))
        self.assertEqual(compact.metadata["scratch_saved_by_pooling"], 28)
        print(f"p=29 total sum evaluator: baseline {baseline.num_qubits} qubits / {len(baseline.data)} logical instructions; compact {compact.num_qubits} qubits / {len(compact.data)} logical instructions.")
        print("Verified all small encodings, order-two branches, 30 p=29 points, invalid examples, arbitrary outputs, and clean pooled scratch by logical gate propagation.")
