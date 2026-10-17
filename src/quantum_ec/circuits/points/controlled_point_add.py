"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit.library import MCXGate
from quantum_ec.circuits.points.point_add_inplace import point_add_inplace


def controlled_point_add(width: int, modulus: int, a: int, b: int, u: int, v: int, *, evaluator_variant: str = "reference") -> QuantumCircuit:
    """Map (c,z,0) to (c,H_A(z),0) for c=1, and preserve z for c=0.

    Invalid point encodings are fixed in both branches. Register order:
    control,identity,x,y,work. All work must start and end at zero.
    A is finite and modulus is assumed prime >3. Controls are added to
    every operation, not only the initial evaluator or output transfer.
    """
    update = point_add_inplace(width, modulus, a, b, u, v, evaluator_variant=evaluator_variant)
    control = QuantumRegister(1, "control")
    identity = QuantumRegister(1, "identity")
    x = QuantumRegister(width, "x")
    y = QuantumRegister(width, "y")
    work = QuantumRegister(update.num_qubits - (2 * width + 1), "work")
    circuit = QuantumCircuit(control, identity, x, y, work, name="controlled_point_add")
    targets = list(identity) + list(x) + list(y) + list(work)
    for instruction in update.data:
        mapped = [targets[update.find_bit(q).index] for q in instruction.qubits]
        if instruction.operation.name == "swap":
            left, right = mapped
            # Three controlled CNOTs implement a controlled swap.
            circuit.ccx(control[0], left, right)
            circuit.ccx(control[0], right, left)
            circuit.ccx(control[0], left, right)
        elif instruction.operation.name in ("x", "cx", "ccx", "mcx"):
            if len(mapped) == 1:
                circuit.cx(control[0], mapped[0])
            else:
                circuit.append(MCXGate(len(mapped)), list(control) + mapped)
        else:
            raise ValueError("Unexpected gate in the reference point update")
    circuit.metadata = {"evaluator_variant": evaluator_variant}
    return circuit
