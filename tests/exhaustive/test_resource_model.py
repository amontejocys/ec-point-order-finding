"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import unittest
from quantum_ec.circuits.arithmetic.binary_add_constant import binary_add_constant
from quantum_ec.circuits.arithmetic.less_than_constant import less_than_constant
from quantum_ec.circuits.arithmetic.modular_add_constant import modular_add_constant
from quantum_ec.circuits.arithmetic.modular_add_register import modular_add_register
from quantum_ec.circuits.arithmetic.modular_multiply_accumulate import modular_multiply_accumulate
from quantum_ec.circuits.arithmetic.modular_square_accumulate import modular_square_accumulate
from quantum_ec.circuits.arithmetic.modular_cube_accumulate import modular_cube_accumulate
from quantum_ec.circuits.arithmetic.equality_constant import equality_constant
from quantum_ec.circuits.arithmetic.less_than_register import less_than_register
from quantum_ec.circuits.arithmetic.division_reduce_step import division_reduce_step
from quantum_ec.circuits.arithmetic.binary_divide import binary_divide
from quantum_ec.circuits.arithmetic.binary_quotient import binary_quotient
from quantum_ec.circuits.arithmetic.modular_inverse_inplace import modular_inverse_inplace
from quantum_ec.circuits.points.curve_residual_accumulate import curve_residual_accumulate
from quantum_ec.circuits.points.finite_curve_check import finite_curve_check
from quantum_ec.circuits.points.point_encoding_check import point_encoding_check
from quantum_ec.circuits.points.point_addition_cases import point_addition_cases
from quantum_ec.circuits.points.ordinary_point_sum_shared import ordinary_point_sum_shared
from quantum_ec.circuits.points.point_sum_evaluator_compact import point_sum_evaluator_compact
from quantum_ec.circuits.order_finding.elliptic_order_finding import EllipticOrderFinding
from quantum_ec.resources.resource_model import binary_add_count, less_than_constant_count, modular_add_count, modular_register_add_count, modular_multiply_count, modular_square_count, modular_cube_count, equality_count, less_than_register_count, division_step_count, binary_divide_count, binary_quotient_count, binary_quotient_qubits, compact_inverse_breakdown, curve_residual_count, finite_curve_check_count, point_encoding_check_count, point_cases_count, compact_ordinary_count, compact_evaluator_resources, compact_controlled_point_resources, compact_scalar_resources


class ResourceModelTests(unittest.TestCase):
    def check_count(self, expected, circuit):
        self.assertTrue(all(i.operation.name in ("x", "cx", "ccx", "mcx") for i in circuit.data))
        self.assertEqual(expected, len(circuit.data))

    def test_binary_all_constants(self):
        for width in range(1, 7):
            for value in range(1 << width):
                self.check_count(binary_add_count(width, value), binary_add_constant(width, value))
            self.assertEqual(binary_add_count(width, -1), width * (width + 1) // 2)

    def test_comparison_all_limits(self):
        for width in range(1, 6):
            for limit in range((1 << width) + 1):
                self.check_count(less_than_constant_count(width, limit), less_than_constant(width, limit))

    def test_modular_constants_and_normalization(self):
        for width, modulus in ((2, 3), (3, 5), (4, 13), (5, 29), (3, 8)):
            for value in range(-1, modulus + 1):
                self.check_count(modular_add_count(width, modulus, value), modular_add_constant(width, modulus, value))

    def test_register_product_square_cube(self):
        pairs = (
            (modular_register_add_count, modular_add_register),
            (modular_multiply_count, modular_multiply_accumulate),
            (modular_square_count, modular_square_accumulate),
            (modular_cube_count, modular_cube_accumulate),
        )
        for width, modulus in ((2, 3), (3, 7), (4, 13), (5, 29), (6, 61), (3, 8)):
            for model, builder in pairs:
                self.check_count(model(width, modulus), builder(width, modulus))

    def test_invalid_inputs(self):
        for width, modulus, value in ((0, 3, 1), (True, 3, 1), (2, 5, 1), (2, 1, 1), (2, 3, True)):
            with self.assertRaises(ValueError):
                modular_add_count(width, modulus, value)

    def test_equality_counts(self):
        for width in range(1, 7):
            for value in range(1 << width):
                self.check_count(equality_count(width, value), equality_constant(width, value))

    def test_division_counts_and_quotient_memory(self):
        for width in range(1, 7):
            self.check_count(less_than_register_count(width), less_than_register(width))
            self.check_count(division_step_count(width), division_reduce_step(width))
            divider = binary_divide(width)
            quotient = binary_quotient(width)
            self.check_count(binary_divide_count(width), divider)
            self.check_count(binary_quotient_count(width), quotient)
            self.assertEqual(len(divider.data) - len(quotient.data), width)
            self.assertEqual(quotient.num_qubits, binary_quotient_qubits(width))

    def test_compact_inverse_counts_and_memory(self):
        for width, modulus in ((2, 3), (3, 5), (4, 9), (5, 29)):
            breakdown = compact_inverse_breakdown(width, modulus)
            circuit = modular_inverse_inplace(width, modulus)
            self.check_count(breakdown["total_instructions"], circuit)
            self.assertEqual(breakdown["total_qubits"], circuit.num_qubits)
        with self.assertRaises(ValueError):
            compact_inverse_breakdown(3, 8)

    def test_curve_validation_counts(self):
        for width, modulus, a, b in ((3, 5, 1, 1), (5, 29, 0, 7)):
            self.check_count(curve_residual_count(width, modulus, a, b), curve_residual_accumulate(width, modulus, a, b))
            self.check_count(finite_curve_check_count(width, modulus, a, b), finite_curve_check(width, modulus, a, b))
            self.check_count(point_encoding_check_count(width, modulus, a, b), point_encoding_check(width, modulus, a, b))

    def test_cases_ordinary_and_evaluator(self):
        for width, modulus, a, b, u, v in ((3, 5, 1, 1, 2, 1), (3, 5, 1, 0, 0, 0)):
            self.check_count(point_cases_count(width, modulus, a, b, u, v), point_addition_cases(width, modulus, a, b, u, v))
            ordinary = ordinary_point_sum_shared(width, modulus, u, v, inverse_variant="compact")
            self.check_count(compact_ordinary_count(width, modulus, u, v), ordinary)
            evaluator = point_sum_evaluator_compact(width, modulus, a, b, u, v)
            resources = compact_evaluator_resources(width, modulus, a, b, u, v)
            self.check_count(resources["total_instructions"], evaluator)
            self.assertEqual(resources["total_qubits"], evaluator.num_qubits)
            for key in ("case_scratch_width", "ordinary_scratch_width", "scratch_saved_by_pooling"):
                self.assertEqual(resources[key], evaluator.metadata[key])

    def test_actual_small_scalar_chain(self):
        builder = EllipticOrderFinding(3, 5, 1, 1, (2, 1), evaluator_variant="compact")
        circuit = builder.scalar_update()
        resources = compact_scalar_resources(builder.width, 5, 1, 1, builder.powers)
        self.assertEqual(resources["total_qubits"], circuit.num_qubits)
        self.assertEqual(resources["controlled_additions"], len(circuit.data))
        self.assertEqual(resources["total_instructions"], sum(len(i.operation.definition.data) for i in circuit.data))
        for instruction, point in zip(circuit.data, builder.powers):
            expected = compact_controlled_point_resources(builder.width, 5, 1, 1, *point)
            self.check_count(expected["total_instructions"], instruction.operation.definition)
            self.assertEqual(expected["total_qubits"], instruction.operation.num_qubits)

    def test_match_previously_recorded_p29_chain(self):
        # Regression against earlier real-circuit runs, not a new large build.
        builder = EllipticOrderFinding(5, 29, 0, 7, (6, 7), evaluator_variant="compact")
        resources = compact_scalar_resources(5, 29, 0, 7, builder.powers)
        self.assertEqual(resources["total_instructions"], 5334183)
        self.assertEqual(resources["total_qubits"], 221)
        self.assertEqual(resources["instructions_per_addition"], [1066799, 1066893, 1066799, 1066893, 1066799])
