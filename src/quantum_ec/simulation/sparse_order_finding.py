"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import math
import numpy as np


def compile_permutation(circuit):
    gates = []
    for instruction in circuit.data:
        if instruction.operation.name not in ("x", "cx", "ccx", "mcx"):
            raise ValueError("Arithmetic must contain only positive-control X gates")
        bits = [circuit.find_bit(q).index for q in instruction.qubits]
        gates.append((sum(1 << bit for bit in bits[:-1]), 1 << bits[-1]))
    return gates


def propagate(gates, index):
    for controls, target in gates:
        if index & controls == controls:
            index ^= target
    return index


def arithmetic_outputs(builder):
    """Apply the actual scalar-update gates to every initially occupied basis state."""
    circuit = builder.scalar_update()
    compiled = {}
    blocks = []
    for instruction in circuit.data:
        wires = [circuit.find_bit(q).index for q in instruction.qubits]
        if wires[1:] != list(range(builder.m, circuit.num_qubits)):
            raise ValueError("Unexpected point/work wire layout")
        key = id(instruction.operation)
        if key not in compiled:
            compiled[key] = compile_permutation(instruction.operation.definition)
        blocks.append((wires[0], compiled[key]))
    outputs = []
    point_width = 2 * builder.width + 1
    for k in range(1 << builder.m):
        point_work = 1  # Prepare O, not the all-zero finite-coordinate encoding.
        for bit, gates in blocks:
            control = (k >> bit) & 1
            result = propagate(gates, control | (point_work << 1))
            if result & 1 != control:
                raise AssertionError("Arithmetic changed the scalar control")
            point_work = result >> 1
            if point_work >> point_width:
                raise AssertionError("Arithmetic left nonzero auxiliary bits")
        outputs.append(point_work)
    return outputs, circuit.num_qubits


def fourier_probabilities(outputs):
    """Keep orthogonal point labels separate, then trace them out after IQFT."""
    q = len(outputs)
    amplitudes = {}
    for k, label in enumerate(outputs):
        if label not in amplitudes:
            amplitudes[label] = np.zeros(q, dtype=complex)
        amplitudes[label][k] = 1 / math.sqrt(q)
    probabilities = np.zeros(q)
    for vector in amplitudes.values():
        transformed = np.fft.fft(vector, norm="ortho")
        probabilities += np.abs(transformed) ** 2
    if not np.isclose(probabilities.sum(), 1, atol=1e-12):
        raise AssertionError("Probability normalization failed")
    return probabilities
