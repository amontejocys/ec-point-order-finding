# Results policy

Organize summaries as results/<experiment>/.
Track small reviewed CSV/JSON tables plus provenance; raw/, cache/, logs/ and
NPZ/NPY outputs are ignored. Archive large evidence separately with checksums and
link it from the summary. Zenodo publication occurs after stabilization.

Retain exact counts separately from sampling estimates and confidence intervals.
Count computational-basis coverage separately from complete adder input coverage.
Historical R5/R6 data retain their historical provenance; do not relabel them.

Metadata must include effective configuration, seed when applicable, command,
source commit and dirty status, environment, and artifact hashes.
