# ec-point-order-finding

Research code for reversible elliptic-curve point arithmetic, quantum order
finding, classical recovery, and an experimental signing application.

## Status

R5/R6 code is migrated into src/quantum_ec/, tests/, and experiments/.
Existing r5/ and r6/ remain unchanged, ignored local backups, not import paths.
M1 order admission is implemented and locally tested; manuscript integration
and author review are pending. R8 novelty remains open. See
docs/decisions/m1_signing_admission.md for the API, assumptions and error bound.

Do not use the signing example as a production cryptographic library.

## Layout

- src/quantum_ec/: reusable implementation, organized by responsibility.
- src/quantum_ec/baselines/: comparison adapters and reference circuit variants.
- tests/unit/: quick tests.
- tests/integration/: cross-component contracts.
- tests/exhaustive/: exhaustive or expensive checks, marked slow.
- tests/reference/: independently justified test arithmetic.
- experiments/configs/: reviewed, versioned experimental inputs.
- experiments/scripts/: entry points that call the package.
- data/reference/: small independently sourced reference data.
- data/fixtures/: small fixed test inputs.
- results/<experiment>/: tracked summaries and run metadata only.
- results/<experiment>/raw/: ignored large generated outputs.
- docs/audit/: novelty matrix, sources, and coverage audit.
- docs/decisions/: scope and experiment decisions recorded before main runs.
- paper/manuscript/: reviewed LaTeX sources and bibliography synchronized with Overleaf.
- paper/figures/: final generated manuscript figures.
- notebooks/: optional exploration, not the authoritative experiment workflow.

See docs/reproduction.md and docs/design/repository_structure.md.
No license grant or authorship metadata has been selected yet.

## Development

Use a dedicated virtual environment, not a global Python installation:

    python -m venv .venv
    python -m pip install -e ".[dev]"
    python -m pytest

The install commands must be run using the virtual environment's Python.
Default pytest excludes slow tests. Run them explicitly with:

    python -m pytest -m slow tests/exhaustive

Run all inherited tests, including slow tests, with:

    python -m pytest -o addopts=

Active files are stored with LF line endings (.gitattributes); historical artifacts keep
their original bytes. Assistant instruction files (CLAUDE.md, AGENTS.md) are local only.
See docs/audit/migration.md for the migration checks and their limitations.
See docs/audit/validation_followup.md for the later full validation and the
separate shared-recovery maintenance. Historical manifests describe snapshots;
the current ideal distribution and prefix recovery now live in the package.
Execute scripts from the repository root using python -m experiments.scripts.NAME.
Output paths are explicit. For example:

    python -m experiments.scripts.signature_integration --report results/legacy/r6/real_circuit_recovery.json --arrays results/legacy/r6/raw/real_circuit_recovery.npz --output results/signature-replay/raw/result.json

The NPZ is available in the local migration, but ignored by Git. A clean clone
needs the historical data archive; see docs/audit/historical_artifacts.json.
Historical drafts in paper/drafts/ are not the current Overleaf manuscript.
