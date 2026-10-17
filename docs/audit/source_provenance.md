# Source fingerprint and environment provenance

The maintenance source_tree_sha256 covers only src/**/*.py. It does not identify
the full repository or replace a Git commit. Reproduce it from the repository root:

```text
python -m experiments.scripts.audit_source_tree --expect 18a69d14e147ef4bfd3a7e6b035311675fbf8ecc3fab0bfab5a32e07b6a3bbf1 --output results/provenance-check/raw/manifest.json
```

Algorithm: sort repository-relative POSIX paths lexically; compute SHA-256 over
the raw bytes of each file; form records `path + " " + file_sha256`; join with LF
without a trailing LF; SHA-256 the UTF-8 payload. Changing checkout line endings
changes raw-file hashes. The manifest records every path and file digest.

The expected value describes the pre-M1 maintenance source code after line-ending
normalization (LF), not future changes. The earlier value 721b2873d8d0... was computed on
the Windows CRLF working copy before .gitattributes existed; it is superseded and is
kept only in the historical summaries that recorded it. Both correspond to the same
source text. File-byte equality is not a proof of algorithm correctness.

.gitattributes stores and checks out active files with LF on every platform, so the
fingerprint is reproducible from any clone. Historical artifacts under paper/drafts/,
docs/history/ and results/legacy/ are marked -text and keep their original bytes, so
docs/audit/historical_artifacts.json still verifies. The pre-maintenance snapshot in
results/validation-followup/pre_maintenance_snapshot.json records CRLF-era file hashes
and is evidence of that state, not a check against the normalized tree.

Python 3.11.5 was the isolated migration/maintenance interpreter outside this
repository, not necessarily registered with the Windows Python launcher. Its
sys.version and dependency versions are recorded under environment_observed_now in
results/pre-m1-maintenance/source_manifest.json. Interpreter paths are not recorded
because local paths contain user names. The
separate supplied exhaustive validation used Python 3.12.10. These observations
do not assert that every earlier run used an identical transitive environment.

Active configurations and summary artifact paths use repository-relative POSIX
strings. Python Path accepts them on Windows and Linux. Archived original logs,
historical notes and legacy hash manifests retain their original content and
may contain Windows paths; they are evidence, not cross-platform input configs.
Anonymize local paths in release copies only after preserving original evidence.
