"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import argparse
import numpy as np
from qiskit.quantum_info import Operator
from quantum_ec.circuits.order_finding.elliptic_order_finding import EllipticOrderFinding, inverse_qft_gate
from quantum_ec.classical.curve import classical_add
from quantum_ec.simulation.sparse_order_finding import arithmetic_outputs
from quantum_ec.simulation.sparse_order_finding import fourier_probabilities
from quantum_ec.recovery.continued_fractions import verified_candidates
from quantum_ec.baselines.trial_recovery import recovered_orders


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--m", type=int, default=5)
    args = parser.parse_args()
    # No known point order, lookup table, or parity correction is supplied.
    builder = EllipticOrderFinding(args.m, 29, 0, 7, (6, 7), evaluator_variant="compact")
    print("Building and propagating real compact arithmetic...", flush=True)
    outputs, qubits = arithmetic_outputs(builder)
    probabilities = fourier_probabilities(outputs)
    q = len(outputs)
    np.testing.assert_allclose(
        np.fft.fft(np.eye(q), axis=0, norm="ortho"),
        Operator(inverse_qft_gate(args.m)).data, atol=1e-12,
    )
    # Classical comparison is performed after circuit propagation, for validation.
    expected = None
    for label in outputs:
        encoded = 1 if expected is None else (expected[0] << 1) | (expected[1] << (builder.width + 1))
        if label != encoded:
            raise AssertionError("Circuit output disagrees with classical validation")
        expected = classical_add(expected, builder.point, builder.modulus, builder.a)
    success = 0.0
    print(f"Q={q}; logical qubits={qubits}; occupied point labels={len(set(outputs))}")
    print("y  bitstring  exact_probability  verified_multiples  certified_orders")
    for y in range(q):
        candidates = verified_candidates(y, q, builder.point, builder.modulus, builder.a)
        orders = recovered_orders(y, q, builder.point, builder.modulus, builder.a)
        if orders:
            success += probabilities[y]
        print(f"{y:2d} {y:0{args.m}b} {probabilities[y]:.10f} {candidates} {orders}")
    print(f"Certified-order recovery probability per ideal shot: {success:.10f}")
    print("Candidate factoring uses trial division for this small reference experiment.")
    print("These are exact ideal probabilities, not sampled shots or hardware resource estimates.")


if __name__ == "__main__":
    main()
