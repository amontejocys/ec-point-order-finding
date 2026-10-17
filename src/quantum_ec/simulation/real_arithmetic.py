"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

from collections import Counter
from quantum_ec.simulation.sparse_order_finding import compile_permutation, propagate
from quantum_ec.resources.mcx_basis import control_profile, basis_resources


def cached_arithmetic_outputs(builder):
    circuit = builder.scalar_update()
    compiled, profiles, blocks = {}, {}, []
    for instruction in circuit.data:
        wires = [circuit.find_bit(q).index for q in instruction.qubits]
        if wires[1:] != list(range(builder.m, circuit.num_qubits)):
            raise ValueError("Unexpected arithmetic wire layout")
        key = id(instruction.operation)
        if key not in compiled:
            definition = instruction.operation.definition
            compiled[key] = compile_permutation(definition)
            profiles[key] = control_profile(definition)
        blocks.append((wires[0], key))
    profile = Counter()
    for _, key in blocks:
        profile.update(profiles[key])
    transitions = {}
    outputs = []
    hits = 0
    point_width = 2*builder.width+1
    for k in range(1 << builder.m):
        point_work = 1
        for bit, key in blocks:
            control = (k >> bit) & 1
            local_input = control | (point_work << 1)
            cache_key = (key, local_input)
            if cache_key not in transitions:
                result = propagate(compiled[key], local_input)
                if result & 1 != control or result >> (point_width+1):
                    raise AssertionError("Control changed or auxiliary work not clean")
                transitions[cache_key] = result
            else:
                hits += 1
            point_work = transitions[cache_key] >> 1
        outputs.append(point_work)
    resources = basis_resources(profile, circuit.num_qubits)
    return outputs, {
        "logical_resources_arithmetic": resources,
        "controlled_additions": len(blocks),
        "distinct_adder_definitions": len(compiled),
        "basis_inputs_checked": len(outputs),
        "actual_gate_propagations": len(transitions),
        "simulation_cache_hits": hits,
        "expanded_instructions_actually_propagated": sum(
            len(compiled[key]) for key, _ in transitions),
    }
