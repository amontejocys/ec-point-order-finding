"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import unittest
from qiskit import QuantumCircuit
from quantum_ec.simulation.real_arithmetic import cached_arithmetic_outputs
from quantum_ec.simulation.sparse_order_finding import compile_permutation, propagate


class FixtureBuilder:
    m = 4
    width = 1

    def __init__(self):
        # Toy clean, phase-free point update. Not elliptic-curve arithmetic.
        block = QuantumCircuit(4)
        block.cx(0, 2)
        gate = block.to_gate()
        self.circuit = QuantumCircuit(7)
        for bit in range(4):
            self.circuit.append(gate, [bit, 4, 5, 6])

    def scalar_update(self):
        return self.circuit


class RealCircuitRecoveryTests(unittest.TestCase):
    def test_cache_matches_uncached_actual_gates(self):
        builder = FixtureBuilder()
        outputs, audit = cached_arithmetic_outputs(builder)
        gates = compile_permutation(builder.circuit.data[0].operation.definition)
        expected = []
        for k in range(16):
            point = 1
            for bit in range(4):
                point = propagate(gates, ((k >> bit) & 1) | (point << 1)) >> 1
            expected.append(point)
        self.assertEqual(outputs, expected)
        self.assertGreater(audit['simulation_cache_hits'], 0)
        self.assertEqual(audit['logical_resources_arithmetic']['cx_count'], 4)
