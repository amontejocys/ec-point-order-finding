# Saved circuit anchors (P4)

`summary.json` records input/code hashes, original coverage, complete comparison
diagnostics and admission decisions. `budgets.csv` contains 40 budget rows.
No new gates, sampling or signatures were executed. This reuses five historical
phase-free arithmetic/FFT distributions; it is not hardware simulation.

Numerical probabilities only. The composite-order instance recovers order 9 but
is not admitted for signing. Prime-order admission is not domain security.

Reproduction requires the exact ignored historical NPZ specified in the frozen
configuration. See `docs/audit/m2_f_p4_anchors.md`. Review and P5 remain pending.
