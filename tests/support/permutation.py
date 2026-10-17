"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""




def compile_x_permutation(circuit):
    gates = []
    for instruction in circuit.data:
        if instruction.operation.name not in ("x", "cx", "ccx", "mcx"):
            raise AssertionError("Basis checker only supports positive-control X gates")
        bits = [circuit.find_bit(q).index for q in instruction.qubits]
        gates.append((sum(1 << bit for bit in bits[:-1]), 1 << bits[-1]))
    return gates


def apply_basis(gates, index):
    for controls, target in gates:
        if (index & controls) == controls:
            index ^= target
    return index
