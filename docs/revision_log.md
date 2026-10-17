# Revision register

| Item | Evidence | Minimal change | Location | Status |
| --- | --- | --- | --- | --- |
| Structure | Existing R5/R6 files and migration manifests | Modules, imports, scripts and artifact paths migrated; originals retained | Repository | See docs/audit/migration.md for completed and pending checks |
| M1 signing admission | Nonidentity P, prime candidate annihilating P implies exact order | Admission check and tests | signing/, manuscript algorithm | Pending |
| R8 novelty | Comparative audit and evidence required | Determined after M2 | docs/audit/, manuscript | Open |
| Motivation | Assess why the selected capability matters | Decision with advisor | docs/decisions/ | Open |
| References [27], [28], [30] | Verify primary sources | Correct only supported entries | Manuscript bibliography | Pending |
| Migration slow validation | Supplied logs: 104 slow plus p29 chain passed | Preserve evidence and qualify snapshot | docs/audit/validation_followup.md | Evidence inspected; not rerun here |
| Adder coverage | Small complete domains vs p29 selected inputs | Populate coverage inventory | docs/audit/coverage.md | Documented; manuscript untouched |
| Duplicate recovery | Experiments and package shared gcd policy | Central iterator and shared prefix API | recovery/, experiments/ | Validation recorded in maintenance summary |
| MCX warnings | Exact known warning, Qiskit 2.0.0 | Narrow pytest filter only | pyproject.toml | Other warnings remain enabled |
| Non-argparse CLI syntax | Recovery example had an incorrectly indented header/import | Fix placement; compile all active Python and execute example in tests | experiments/scripts/factor_free_recovery.py | Corrected; validation in results/audit-fixes/summary.json |
| Overleaf-only author workflow | Author retains manual editing | Restore explicit rule; proposals only, no TeX/Bib edits | CLAUDE.md | Restored |
| Provenance and portability | Recipe/manifest for source hash; isolated interpreter metadata | Version reproducible auditor; normalize active metadata paths | docs/audit/source_provenance.md | No dependency or scientific-code changes |
| Pre-commit hygiene | CRLF working copy vs LF clones broke fingerprints; interpreter paths leaked user names; AI instruction files were about to be versioned | .gitattributes with LF policy and -text historical artifacts; active files converted to LF; fingerprint regenerated; interpreter path no longer recorded; CLAUDE.md/AGENTS.md ignored | .gitattributes, .gitignore, results/eol-normalization/ | Done before first commit; no scientific-code changes |
