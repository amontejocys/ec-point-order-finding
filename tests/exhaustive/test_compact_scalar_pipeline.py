"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import unittest
from quantum_ec.circuits.points.controlled_point_add import controlled_point_add
from quantum_ec.circuits.order_finding.elliptic_order_finding import EllipticOrderFinding
from quantum_ec.classical.curve import classical_add
from quantum_ec.circuits.points.point_add_inplace import point_add_inplace
from tests.support.permutation import apply_basis, compile_x_permutation
from tests.reference.encoding import expected_sum_encoding


class ReportingBuilder(EllipticOrderFinding):
    def _adder(self, point):
        fresh = point not in self._gates
        if fresh:
            print(f"Building real {self.evaluator_variant} arithmetic adder for p={self.modulus}, A={point}...", flush=True)
        gate = super()._adder(point)
        if fresh:
            print(f"Built A={point}: {gate.num_qubits} logical qubits, {len(gate.definition.data)} logical instructions.", flush=True)
        return gate


def verify_scalar_chain(test, builder, circuit):
    active_powers = [(bit, point) for bit, point in enumerate(builder.powers) if point is not None]
    test.assertEqual(len(circuit.data), len(active_powers))
    compiled = {}
    for instruction, (bit, point) in zip(circuit.data, active_powers):
        actual_wires = [circuit.find_bit(q).index for q in instruction.qubits]
        test.assertEqual(actual_wires, [bit] + list(range(builder.m, circuit.num_qubits)))
        if point not in compiled:
            compiled[point] = compile_x_permutation(instruction.operation.definition)
    point_size = 2 * builder.width + 1
    expected_point = None
    for k in range(1 << builder.m):
        point_and_work = 1  # Canonical identity encoding, with clean work.
        for bit, point in active_powers:
            control = (k >> bit) & 1
            local_input = control | (point_and_work << 1)
            local_output = apply_basis(compiled[point], local_input)
            test.assertEqual(local_output & 1, control)
            point_and_work = local_output >> 1
            test.assertEqual(point_and_work >> point_size, 0)
        if expected_point is None:
            expected_encoding = 1
        else:
            x, y = expected_point
            expected_encoding = (x << 1) | (y << (builder.width + 1))
        test.assertEqual(point_and_work, expected_encoding)
        expected_point = classical_add(expected_point, builder.point, builder.modulus, builder.a)
    return compiled


class CompactScalarPipelineTests(unittest.TestCase):
    def test_variants_are_explicit_and_validated(self):
        self.assertEqual(EllipticOrderFinding(3, 5, 1, 1, (2, 1)).evaluator_variant, "reference")
        with self.assertRaises(ValueError):
            EllipticOrderFinding(3, 5, 1, 1, (2, 1), evaluator_variant="unknown")
        with self.assertRaises(ValueError):
            point_add_inplace(3, 5, 1, 1, 2, 1, evaluator_variant="unknown")
        with self.assertRaises(ValueError):
            controlled_point_add(3, 5, 1, 1, 2, 1, evaluator_variant="unknown")

    def test_small_chain_and_all_controlled_encodings(self):
        builder = ReportingBuilder(3, 5, 1, 1, (2, 1), evaluator_variant="compact")
        circuit = builder.scalar_update()
        compiled = verify_scalar_chain(self, builder, circuit)
        for point, gates in compiled.items():
            inverse_gates = list(reversed(gates))
            for enc in range(1 << (2 * builder.width + 1)):
                for control in (0, 1):
                    initial = control | (enc << 1)
                    result = expected_sum_encoding(enc, builder.width, builder.modulus, builder.a, builder.b, *point) if control else enc
                    expected = control | (result << 1)
                    self.assertEqual(apply_basis(gates, initial), expected)
                    self.assertEqual(apply_basis(inverse_gates, expected), initial)
        self.assertEqual(circuit.metadata["evaluator_variant"], "compact")
        print(f"Small real compact scalar chain: {circuit.num_qubits} logical qubits; all 8 scalar inputs verified, plus both controls on all point encodings.", flush=True)

    def test_real_p29_q32_scalar_chain(self):
        builder = ReportingBuilder(5, 29, 0, 7, (6, 7), evaluator_variant="compact")
        circuit = builder.scalar_update()
        verify_scalar_chain(self, builder, circuit)
        self.assertEqual(len(builder._gates), 4)
        self.assertEqual(circuit.metadata["Q"], 32)
        self.assertEqual(circuit.num_qubits, 221)
        instructions = sum(len(instruction.operation.definition.data) for instruction in circuit.data)
        print(f"Real p=29,Q=32 scalar chain: {circuit.num_qubits} logical qubits, {len(circuit.data)} controlled additions, {instructions} expanded logical instructions. All 32 k values and clean work verified by logical gate propagation; no QFT histogram yet.", flush=True)
