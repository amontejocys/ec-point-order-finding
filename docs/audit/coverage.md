# Validation coverage inventory

Status: inspected against tests and saved reports. Exhaustive test success is
recorded in validation_followup.md. This inventory does not imply universality.

| Component | Inputs/parameters covered | Valid/invalid/exceptional inputs | Controls | Scratch cleanup | Independent reference | Test and run |
| --- | --- | --- | --- | --- | --- | --- |
| Controlled addition, width 3, p=5 | All 128 point-register encodings for constants explicitly in tests | Finite, identity, invalid, exceptional | Both controls | Checked by full basis output comparison | tests/reference/encoding.py | test_controlled_point_add; compact scalar tests |
| In-place and XOR evaluators, width 3 | All 128 encodings for selected constants, including an order-two point | Valid and invalid | See controlled wrapper tests separately | Checked; inverse and selected arbitrary targets also tested | Encoded-point reference | test_point_add_inplace; test_point_sum_evaluator* |
| p=29 individual sum, A=(12,13) | 30 valid points and 4 invalid examples, out of 2048 encodings | All valid points for this constant, sampled invalid strings | Both controls in wrapper test | Checked | Encoded-point reference | test_controlled_point_add; point evaluator/in-place tests |
| p=29 compact scalar chain, Q=32 | All 32 scalars from canonical identity | Reachable subgroup states, not all point inputs | Determined by scalar bits | Checked after each update | Runtime classical helper: consistency check | test_real_p29_q32_scalar_chain; saved follow-up log |
| Historical p=29 run, Q=2048 | All 2048 scalars from canonical identity | 40 distinct cached transitions: 4 adders x 5 subgroup points x 2 controls | Both across transitions | Checked by arithmetic simulator | experiments/reference/curve.py | results/legacy/r6/real_circuit_recovery.json |

Enumerating scalar inputs from an identity accumulator does not enumerate every
input to a point adder. Distinguish exhaustive finite-domain checks, sampled
cases, and mathematical guarantees. Record basis phases as well as output bits.

The Q=32 chain has 221 qubits, 5 controlled additions, and 5,334,183 expanded
X-family instructions. They are not all Toffolis. The Q=2048 report is historical;
the later Q=32 test does not constitute a fresh Q=2048 run.

Permitted claim: exhaustive verification over the stated small encoding domains
and all scalar inputs of specified instances, plus selected p=29 adder checks.
Not supported: exhaustive verification of every p=29 point encoding for every
constant, every auxiliary initialization, every curve, or all quantum states.
Noiseless basis action extends linearly only when the implementation's phases
and initialized-subspace assumptions are accounted for. These tests do not test
hardware noise or establish novelty. No manuscript wording was changed here.
