"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import unittest
import random
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import MCXGate
from qiskit.quantum_info import Statevector
from quantum_ec.resources.mcx_basis import basis_resources, control_profile, lower_x_family


class McxBasisTests(unittest.TestCase):
    def compare_complex_state(self, original):
        lowered = lower_x_family(original)
        rng = np.random.default_rng(20261008)
        amplitudes = rng.normal(size=1 << original.num_qubits) + 1j * rng.normal(size=1 << original.num_qubits)
        amplitudes /= np.linalg.norm(amplitudes)
        input_data = np.zeros(1 << lowered.num_qubits, dtype=complex)
        input_data[:len(amplitudes)] = amplitudes
        expected = np.zeros_like(input_data)
        expected[:len(amplitudes)] = Statevector(amplitudes).evolve(original).data
        actual = Statevector(input_data).evolve(lowered).data
        np.testing.assert_allclose(actual, expected, atol=1e-12, rtol=0)
        np.testing.assert_allclose(Statevector(actual).evolve(lowered.inverse()).data,
                                   input_data, atol=1e-12, rtol=0)
        resources = basis_resources(control_profile(original), original.num_qubits)
        self.assertEqual(len(lowered.data), resources["lowered_instructions"])
        self.assertEqual(lowered.num_qubits, resources["lowered_qubits"])
        self.assertEqual(lowered.count_ops().get("ccx", 0), resources["ccx_count"])
        self.assertTrue(all(i.operation.name in ("x", "cx", "ccx") for i in lowered.data))
        return resources

    def test_zero_to_seven_controls(self):
        for count in range(8):
            circuit = QuantumCircuit(count + 1)
            if count == 0:
                circuit.x(0)
            elif count == 1:
                circuit.cx(0, 1)
            else:
                circuit.append(MCXGate(count), circuit.qubits)
            resources = self.compare_complex_state(circuit)
            self.assertEqual(resources["extra_clean_ancillas"], max(0, count - 2))
            self.assertEqual(resources["ccx_count"], 2 * count - 3 if count >= 2 else 0)

    def test_shared_pool_between_different_arities(self):
        circuit = QuantumCircuit(6)
        circuit.x(0)
        circuit.cx(0, 5)
        circuit.ccx(0, 1, 5)
        circuit.append(MCXGate(3), [0, 1, 2, 5])
        circuit.append(MCXGate(5), circuit.qubits)
        resources = self.compare_complex_state(circuit)
        self.assertEqual(resources["ccx_count"], 11)
        self.assertEqual(resources["extra_clean_ancillas"], 3)

    def test_reject_nonpermutation_gates(self):
        circuit = QuantumCircuit(1)
        circuit.h(0)
        with self.assertRaises(ValueError):
            lower_x_family(circuit)

    def test_large_arities_by_exact_basis_propagation(self):
        rng = random.Random(20261008)
        for count in (8, 13, 32):
            original = QuantumCircuit(count + 1)
            original.append(MCXGate(count), original.qubits)
            lowered = lower_x_family(original)
            gates = []
            for instruction in lowered.data:
                positions = [lowered.find_bit(q).index for q in instruction.qubits]
                gates.append((sum(1 << bit for bit in positions[:-1]), 1 << positions[-1]))
            inputs = [0, (1 << count) - 1, 1 << count, (1 << (count + 1)) - 1]
            inputs += [rng.getrandbits(count + 1) for _ in range(100)]
            mask = (1 << count) - 1
            for initial in inputs:
                actual = initial
                for controls, target in gates:
                    if actual & controls == controls:
                        actual ^= target
                expected = initial ^ (1 << count) if initial & mask == mask else initial
                self.assertEqual(actual, expected)
