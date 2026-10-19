# F main numerical evaluation

- `summary.json`: provenance, residuals and 66 field-level budgets.
- `budgets.csv`: the same budget table for inspection/figures.
- `orders.csv`: 650 per-order one-shot/last-budget summaries and operation counts.
- `raw/evaluation.json`: full generated report, ignored by Git; its hash and
  size are in summary.json. Preserve for the dataset release; regenerate locally
  with the command in `docs/audit/m2_f_p3_results.md`.

Numerical estimates only, ideal independent executions. Recovery includes
composite orders; signing admission is separate. Ratios compare our own
conservative bound, not published algorithms. P4/P5 review remains pending.
