# Independent validation follow-up and pre-M1 maintenance

The author supplied a clean-environment validation report: Python 3.12.10,
Qiskit 2.0.0, NumPy 2.1.3, pytest 8.3.5, using the pinned dependency versions.
This adds a Python version to validation; the lock's recorded Python 3.11.5
is migration provenance, not an interpreter constraint or an assertion that
all historical experiments used Python 3.12.

## Evidence inspected

- exhaustive.log / exhaustive.xml: 104 passed, 1 deselected, 1801.17 s.
- p29chain.log: 1 passed, 599.55 s pytest time (638 s reported wall time).
- The original 29 quick tests passed in the migration and were also reported
  passed by the external validator; no separate external quick log was supplied.

Archived logs are in results/validation-followup/raw/ with hashes and metadata
in its tracked summary.json. They contain local paths and must be reviewed for
anonymity before release. These runs were not re-executed when archiving them.
The total 134 refers to the migrated snapshot before current maintenance, not
automatically to subsequent code changes. pre_maintenance_snapshot.json hashes were
taken on the CRLF working copy; after LF normalization (see
docs/audit/source_provenance.md) they identify that state only, not current files. See the new maintenance report for
tests run after centralizing recovery.

The p29 chain confirms all 32 scalars, clean auxiliary work, 221 qubits, 5
controlled additions and 5,334,183 expanded instructions. It does not verify
every p29 adder input, run Q=2048 again, certify signing parameters, or close R8.

## Bounded maintenance (not M1)

The package iterator is the single gcd policy. The full-history API and prefix
API consume it; experiments reuse the latter instead of implementing a second
policy. Optional simulation-cache keys include Q, point, field, curve a and
outcome. Cached calls do not count as online resource savings. The ideal
distribution function was moved without changing its body.

migration_manifest.json remains the original migration snapshot, not a live
symbol index. Current overrides: ideal_probabilities is in
quantum_ec.simulation.ideal_distribution, recover_prefixes and the new
iter_verified_periods are in quantum_ec.recovery.factor_free_recovery.

The new core was checked against all 7000 instance/budget rows from the 1000
historical pilot instances, using saved samples without resampling. All counts
match; 9 instances have a nonminimal candidate in at least one recorded budget.
This reproduces postprocessing outcomes only. See
results/pre-m1-maintenance/expanded_pilot_replay.json and the replay script.

Only the exact MCXGate.get_num_ancilla_qubits pending-deprecation from the Qiskit
standard-gates x module is filtered in pytest. Other warnings remain enabled.
The filter does not change circuits. The old runs' large warning counts are
observed; no profiled causal timing improvement is claimed. Changing pytest
configuration requires refreshing the lock header hash, not dependency pins.

Git was initialized and the Linux CI quick-test workflow passed on commit c4edfbd;
the complete suite (143 tests) also passed on that code, see
results/full-validation/summary.json. Milestone tags and importing the reviewed
Overleaf snapshot remain pending. Historical notes are preserved unchanged; current
coverage and configuration indexes supersede their missing entries. The
manuscript, signing admission and circuit construction remain unchanged.
