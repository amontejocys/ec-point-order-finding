"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

from collections import Counter
from qiskit import QuantumRegister


def control_profile(circuit):
    profile = Counter()
    for instruction in circuit.data:
        if instruction.operation.name not in ("x", "cx", "ccx", "mcx"):
            raise ValueError("Only flat positive-control X-family circuits are supported")
        profile[len(instruction.qubits) - 1] += 1
    return profile


def basis_resources(profile, original_qubits):
    if any(not isinstance(k, int) or k < 0 or not isinstance(v, int) or v < 0
           for k, v in profile.items()):
        raise ValueError("Profile keys and counts must be nonnegative integers")
    maximum = max((k for k, count in profile.items() if count), default=0)
    extra = max(0, maximum - 2)
    toffoli = sum((2 * k - 3) * count for k, count in profile.items() if k >= 2)
    return {
        "input_instructions": sum(profile.values()),
        "x_count": profile.get(0, 0),
        "cx_count": profile.get(1, 0),
        "ccx_count": toffoli,
        "maximum_controls": maximum,
        "extra_clean_ancillas": extra,
        "original_qubits": original_qubits,
        "lowered_qubits": original_qubits + extra,
        "lowered_instructions": profile.get(0, 0) + profile.get(1, 0) + toffoli,
    }


def append_clean_mcx(circuit, controls, target, work):
    """Ancillas start and finish zero; target and controls may be coherent."""
    count = len(controls)
    if len(work) < max(0, count - 2):
        raise ValueError("Insufficient clean auxiliary qubits")
    if len(set([*controls, target, *work])) != len(controls) + 1 + len(work):
        raise ValueError("Controls, target and scratch must be disjoint")
    if count == 0:
        circuit.x(target)
    elif count == 1:
        circuit.cx(controls[0], target)
    elif count == 2:
        circuit.ccx(controls[0], controls[1], target)
    else:
        circuit.ccx(controls[0], controls[1], work[0])
        for index in range(2, count - 1):
            circuit.ccx(work[index - 2], controls[index], work[index - 1])
        circuit.ccx(work[count - 3], controls[-1], target)
        for index in reversed(range(2, count - 1)):
            circuit.ccx(work[index - 2], controls[index], work[index - 1])
        circuit.ccx(controls[0], controls[1], work[0])


def lower_x_family(circuit):
    """Use a separate scratch pool; do not assume existing scratch is idle."""
    resources = basis_resources(control_profile(circuit), circuit.num_qubits)
    output = circuit.copy_empty_like()
    output.name = circuit.name + "_clean_ccx"
    if resources["extra_clean_ancillas"]:
        work = QuantumRegister(resources["extra_clean_ancillas"], "mcx_clean_work")
        output.add_register(work)
        scratch = list(work)
    else:
        scratch = []
    for instruction in circuit.data:
        mapped = [output.qubits[circuit.find_bit(q).index] for q in instruction.qubits]
        append_clean_mcx(output, mapped[:-1], mapped[-1], scratch)
    output.metadata = resources
    return output
