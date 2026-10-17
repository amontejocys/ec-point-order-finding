"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.circuit.library import QFTGate
from quantum_ec.circuits.points.controlled_point_add import controlled_point_add
from quantum_ec.classical.curve import classical_add


def inverse_qft_gate(width):
    gate = QFTGate(width).inverse()
    gate.name = "iqft"
    return gate


class EllipticOrderFinding:
    """Cache arithmetic adders and share clean work across scalar bits."""

    def __init__(self, m, modulus, a, b, point, *, evaluator_variant="reference"):
        if evaluator_variant not in ("reference", "compact"):
            raise ValueError("evaluator_variant must be reference or compact")
        if not isinstance(m, int) or isinstance(m, bool) or m < 1:
            raise ValueError("m must be a positive integer")
        if not isinstance(modulus, int) or isinstance(modulus, bool) or modulus <= 3 or modulus % 2 == 0:
            raise ValueError("modulus must be an odd prime greater than 3 (primality is assumed)")
        if any(not isinstance(c, int) or isinstance(c, bool) for c in (a, b)):
            raise ValueError("curve coefficients must be integers")
        if not isinstance(point, tuple) or len(point) != 2:
            raise ValueError("base point must be a finite coordinate pair")
        if any(not isinstance(c, int) or isinstance(c, bool) or not 0 <= c < modulus for c in point):
            raise ValueError("base coordinates must be canonical residues")
        a, b = a % modulus, b % modulus
        if (4*a**3 + 27*b*b) % modulus == 0:
            raise ValueError("curve must be nonsingular")
        x, y = point
        if (y*y-x**3-a*x-b) % modulus:
            raise ValueError("base point must satisfy the curve equation")
        self.m, self.modulus, self.a, self.b, self.point = m, modulus, a, b, point
        self.evaluator_variant = evaluator_variant
        self.width = (modulus - 1).bit_length()
        self.powers = [point]
        for _ in range(1, m):
            previous = self.powers[-1]
            self.powers.append(classical_add(previous, previous, modulus, a))
        self._gates = {}

    def _adder(self, point):
        if point not in self._gates:
            block = controlled_point_add(self.width, self.modulus, self.a, self.b, *point, evaluator_variant=self.evaluator_variant)
            gate = block.to_gate()
            gate.name = f"add_point_{point[0]}_{point[1]}"
            self._gates[point] = gate
        return self._gates[point]

    def scalar_update(self):
        """Preserve k, update valid R to R+kP, fix invalid encodings, clean work."""
        first = self._adder(self.point)
        size = 2*self.width + 1
        work_width = first.num_qubits - 1 - size
        k = QuantumRegister(self.m, "k")
        identity = QuantumRegister(1, "identity")
        x = QuantumRegister(self.width, "x")
        y = QuantumRegister(self.width, "y")
        work = QuantumRegister(work_width, "work")
        circuit = QuantumCircuit(k, identity, x, y, work, name="scalar_update")
        point_qubits = list(identity) + list(x) + list(y)
        for bit, point in enumerate(self.powers):
            if point is None:
                continue
            gate = self._adder(point)
            if gate.num_qubits != 1 + size + work_width:
                raise ValueError("adder scratch dimensions differ")
            circuit.append(gate, [k[bit]] + point_qubits + list(work))
        circuit.metadata = {"m": self.m, "Q": 1 << self.m, "coordinate_width": self.width, "powers": self.powers, "evaluator_variant": self.evaluator_variant}
        return circuit

    def periodic_evaluation(self):
        """For initially zero point/work registers, preserve k and write enc(kP)."""
        update = self.scalar_update()
        circuit = update.copy_empty_like()
        circuit.name = "evaluate_kP"
        circuit.x(circuit.qregs[1][0])
        circuit.append(update.to_gate(), list(circuit.qubits))
        circuit.metadata = dict(update.metadata)
        return circuit

    def order_finding(self):
        """Zero-initialized circuit: H, arithmetic evaluation, inverse QFT, measure k."""
        evaluation = self.periodic_evaluation()
        circuit = evaluation.copy_empty_like()
        circuit.name = "elliptic_order_finding"
        outcome = ClassicalRegister(self.m, "outcome")
        circuit.add_register(outcome)
        k = circuit.qregs[0]
        circuit.h(k)
        circuit.append(evaluation.to_gate(), list(circuit.qubits))
        circuit.append(inverse_qft_gate(self.m), list(k))
        circuit.measure(k, outcome)
        circuit.metadata = dict(evaluation.metadata)
        return circuit
