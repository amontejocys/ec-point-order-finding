# Reproduction status

Scientific source migration is complete. Full reconstruction of all historical
transitive dependency versions remains distinct from validating this migration.

## Dependency policy

pyproject.toml is the dependency specification.
requirements-lock.txt records the resolved migration validation environment.
It is generated, not hand-edited, and records the pyproject.toml hash.
Install with python -m pip install -r requirements-lock.txt, then
python -m pip install --no-deps -e . (or pip install -c requirements-lock.txt -e '.[dev]').
Use experiments/scripts/lock_environment.py to regenerate it only after reviewing
pyproject changes and resolving dependencies in a clean, dedicated environment.
The lock was validated on Windows with Python 3.11 and 3.12 (identical pins); the
Linux CI remains to be exercised. Active files use LF line endings via .gitattributes.

Historical documentation reports Qiskit 2.0.0. Saved Monte Carlo metadata reports
Python 3.11.5 and NumPy 2.1.3. The migration uses these versions, but freshly
resolved transitive dependencies; do not claim a historical full-environment lock.

## Milestones

For the source fingerprint recipe, scope and interpreter evidence, see
docs/audit/source_provenance.md. The interpreter is not assumed to be discoverable
through the system Python launcher.

Initialize Git deliberately after reviewing what will be committed.
Tag actual validated commits, not planned work:
baseline-pre-m1, structure-migration, m1-complete, m2-decision.
If a milestone is not validated, record it as pending instead of creating its tag.
Use a new run directory for every execution; do not overwrite supporting evidence.

## Publication

Confirm license with the authors/supervisors before adding LICENSE.
Populate CITATION.cff from verified author metadata at release.
Before a double-blind submission, follow the selected venue rules and review
repository history, metadata, PDFs, links, and datasets for identity leakage.
A renamed directory alone does not anonymize an artifact.
