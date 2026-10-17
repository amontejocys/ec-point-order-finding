# Repository structure decision

One repository supports this article. Stages R1-R8 and M1-M6 are revision labels,
not package namespaces.

## Migration boundary

r5/ and r6/ remain unchanged local backups and are ignored by Git.
The external codigo_base_R5_R6_pre_M1.zip remains the pre-M1 backup.
Do not delete inputs until migration validation and a recoverable source
snapshot are confirmed. No Git repository or milestone tag was created by the
scaffold operation.

Migration moved modules, imports, CLI entry points, test helpers and artifacts.
No M1 behavior was added. See docs/audit/migration.md and the symbol manifest.
Qiskit 2.0.0 and NumPy 2.1.3 are declared runtime dependencies. The tested migration
environment is separate from historical runs and from the user's global Python.

## Module ownership

classical/: arithmetic used by the runtime pipeline.
circuits/arithmetic/: reversible arithmetic.
circuits/points/: encoding, validity, branches, clean controlled translations.
circuits/order_finding/: quantum circuit assembly.
recovery/: classical candidate recovery.
signing/: experimental signing and parameter admission.
simulation/: basis propagation and Fourier distributions.
resources/: counts and gate-basis lowering.
baselines/: comparison variants/adapters, attributed to sources.

A baseline is not automatically independent merely because it lives here.
Keep its algorithm, domain, initialization, ancillas, gate basis, and precision
documented. Freeze its version for a comparison. Never alter it silently while
optimizing the main implementation.

tests/reference/encoding.py: inherited independent encoded-point expectation.
experiments/reference/: inherited benchmark group law and signing expectation,
reused by tests via explicit re-exports in tests/reference/. These modules do not
call production arithmetic. This records implementation separation, not a proof
that the mathematical references are infallible. Historical tests that still use
runtime classical helpers remain labeled consistency checks.
