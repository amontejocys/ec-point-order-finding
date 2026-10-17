"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import unittest
import numpy as np
from qiskit.quantum_info import Operator
from quantum_ec.resources.complete_resources import classical_trace, complete_quantum_resources, qft_with_cx_swaps, quantum_overhead


class CompleteResourceTests(unittest.TestCase):
    def test_exact_qft_and_swap_lowering(self):
        for m in range(1, 7):
            original, lowered = qft_with_cx_swaps(m)
            expected = np.fft.fft(np.eye(1 << m), axis=0, norm="ortho")
            np.testing.assert_allclose(Operator(original).data, expected, atol=1e-12)
            np.testing.assert_allclose(Operator(lowered).data, expected, atol=1e-12)
            overhead = quantum_overhead(m)
            self.assertEqual(lowered.count_ops().get("cx", 0), overhead["iqft_cx_after_swaps"])
            self.assertEqual(sum(row["count"] for row in overhead["cp_angles_radians"]), m*(m-1)//2)

    def test_complete_count_composition(self):
        # This fixture isolates overhead composition; actual data are loaded by CLI.
        report = {"basis": "X,CX,CCX with exact full-Toffoli clean AND chains",
                  "parameters": {"m": 5},
                  "resources": {"x_count": 0, "cx_count": 11024, "ccx_count": 42160043, "lowered_qubits": 231}}
        result = complete_quantum_resources(report)
        self.assertEqual(result["gate_counts"], {"x": 1, "cx": 11030, "ccx": 42160043, "h": 10, "cp": 10})
        self.assertEqual(result["unitary_instructions_in_this_mixed_basis"], 42171094)
        self.assertEqual(result["measurements"], 5)
        self.assertEqual(result["logical_qubits"], 231)

    def test_actual_classical_trace_all_outcomes(self):
        accepted = []
        for y in range(32):
            row = classical_trace(y, 32, (6, 7), 29, 0)
            self.assertIn(row["orders"], ([], [5]))
            self.assertEqual(sum(row["classical_add_classification"].values()), row["classical_add_function_calls"])
            self.assertEqual(row["classical_add_function_calls"], sum(k.bit_length()+k.bit_count() for k in row["scalars_checked"]))
            if row["orders"]:
                accepted.append(y)
        self.assertEqual(accepted, [3, 6, 7, 13, 15, 17, 19, 25, 26, 29])

    def test_small_independent_curve_trace(self):
        found = False
        for y in range(8):
            row = classical_trace(y, 8, (2, 1), 5, 1)
            self.assertIn(row["orders"], ([], [3]))
            found |= bool(row["orders"])
        self.assertTrue(found)
