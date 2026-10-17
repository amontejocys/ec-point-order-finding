# Experiments

Keep reviewed inputs in configs/ and entry points in scripts/.
Scripts import quantum_ec; do not duplicate production arithmetic.
Exploratory runs are labeled exploratory. Freeze main-study acceptance criteria
in docs/decisions/ before inspecting main-study results.

Each run records: experiment ID, configuration (and hash), random generator and
seed when used, command, code commit, dirty-tree status, Python and dependency
versions, hardware, timestamps, metrics, and artifact paths/checksums.
Never assign an old result to the current commit without rerunning it.
