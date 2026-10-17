"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

from collections import Counter
from unittest.mock import patch
from qiskit import QuantumCircuit
from quantum_ec.circuits.order_finding.elliptic_order_finding import inverse_qft_gate
import quantum_ec.baselines.trial_recovery as post
import quantum_ec.classical.curve as curve
import quantum_ec.recovery.continued_fractions as candidates


def qft_with_cx_swaps(width):
    if not isinstance(width, int) or isinstance(width, bool) or width < 1:
        raise ValueError("width must be a positive integer")
    wrapper = QuantumCircuit(width)
    wrapper.append(inverse_qft_gate(width), wrapper.qubits)
    qft = wrapper.decompose()
    if set(qft.count_ops()) - {"h", "cp", "swap"}:
        raise ValueError("Unexpected Qiskit IQFT definition")
    lowered = qft.copy_empty_like()
    for instruction in qft.data:
        mapped = [lowered.qubits[qft.find_bit(q).index] for q in instruction.qubits]
        if instruction.operation.name == "swap":
            left, right = mapped
            lowered.cx(left, right)
            lowered.cx(right, left)
            lowered.cx(left, right)
        else:
            lowered.append(instruction.operation, mapped)
    return qft, lowered


def quantum_overhead(m):
    original, lowered = qft_with_cx_swaps(m)
    counts = original.count_ops()
    if counts.get("h", 0) != m or counts.get("cp", 0) != m * (m - 1) // 2 or counts.get("swap", 0) != m // 2:
        raise AssertionError("IQFT counts disagree with exact circuit formula")
    angles = Counter(float(i.operation.params[0]) for i in lowered.data if i.operation.name == "cp")
    return {
        "identity_preparation_x": 1,
        "initial_h": m,
        "iqft_h": m,
        "iqft_cp": m * (m - 1) // 2,
        "iqft_swaps": m // 2,
        "iqft_cx_after_swaps": 3 * (m // 2),
        "cp_angles_radians": [{"angle": angle, "count": count} for angle, count in sorted(angles.items())],
        "measurements": m,
        "additional_qubits": 0,
    }


def complete_quantum_resources(arithmetic_report):
    if arithmetic_report["basis"] != "X,CX,CCX with exact full-Toffoli clean AND chains":
        raise ValueError("Unsupported arithmetic synthesis")
    m = arithmetic_report["parameters"]["m"]
    arithmetic = arithmetic_report["resources"]
    overhead = quantum_overhead(m)
    counts = {
        "x": arithmetic["x_count"] + overhead["identity_preparation_x"],
        "cx": arithmetic["cx_count"] + overhead["iqft_cx_after_swaps"],
        "ccx": arithmetic["ccx_count"],
        "h": overhead["initial_h"] + overhead["iqft_h"],
        "cp": overhead["iqft_cp"],
    }
    return {
        "scope": "one ideal zero-initialized order-finding circuit, excluding classical work and repetitions",
        "basis": "X,CX,CCX,H,CP(theta); controlled phases are exact ideal operations, not Clifford+T approximations",
        "gate_counts": counts,
        "unitary_instructions_in_this_mixed_basis": sum(counts.values()),
        "measurements": m,
        "logical_qubits": arithmetic["lowered_qubits"],
        "overhead": overhead,
        "limitations": "no T-count, hardware routing, error correction, depth, timing, or physical qubit estimate",
    }


def classical_trace(y, q, point, modulus, a):
    """Instrument real recovered_orders; wrappers delegate to the real functions.

    Counts one measurement's postprocessing, not the exhaustive simulator
    or the CLI's extra call to verified_candidates for printing.
    """
    with patch.object(post, "scalar_multiple", wraps=post.scalar_multiple) as scalar_calls, \
         patch.object(candidates, "scalar_multiple", scalar_calls), \
         patch.object(curve, "classical_add", wraps=curve.classical_add) as add_calls, \
         patch.object(post, "prime_factors_trial", wraps=post.prime_factors_trial) as factor_calls:
        orders = post.recovered_orders(y, q, point, modulus, a)
        scalars = [call.args[0] for call in scalar_calls.call_args_list]
        classifications = Counter()
        for call in add_calls.call_args_list:
            left, right, p, _ = call.args
            if left is None or right is None:
                classifications["identity_return"] += 1
            elif left[0] == right[0] and (left[1] + right[1]) % p == 0:
                classifications["opposite_return"] += 1
            elif left[0] == right[0]:
                classifications["doubling_formula"] += 1
            else:
                classifications["ordinary_formula"] += 1
        expected_calls = sum(k.bit_length() + k.bit_count() for k in scalars)
        if add_calls.call_count != expected_calls:
            raise AssertionError("Scalar double-and-add call count mismatch")
        return {
            "y": y,
            "orders": orders,
            "scalar_verification_calls": len(scalars),
            "scalars_checked": scalars,
            "classical_add_function_calls": add_calls.call_count,
            "classical_add_classification": dict(classifications),
            "field_inverse_calls_in_point_formulas": classifications["doubling_formula"] + classifications["ordinary_formula"],
            "factorization_inputs": [call.args[0] for call in factor_calls.call_args_list],
        }
