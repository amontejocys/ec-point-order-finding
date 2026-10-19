# Candidate figure: finite recovery budgets

`f_reliability_budgets.png` is the single P5 candidate visual. Its JSON sidecar
records the source tables, source commit, configuration, generator and image
hashes. Data are the already reviewed 66 P3 numerical budget rows, not a new
simulation. The mathematical model is exact; these plotted budgets are numerical
estimates over the conservative all-integer order superset.

Solid circles show the baseline Q0 > B squared, dashed open squares double Q0;
colors distinguish the three error targets. Lines connect sampled fields only,
not an extrapolation or a certificate. A proposed caption and bounded insertion
are in the author's ignored P5 proposals, not applied to the manuscript.

Regenerate with Matplotlib 3.10.7 in a separate plotting environment:

```text
python experiments/scripts/plot_reliability_budgets.py --root . --output-dir results/m2-f-figure-replay
```

Use a new output directory. The script checks CSV/summary/config agreement
before plotting. Plotting dependencies are optional and are not added to the
production lock or scientific environment. Backend/version differences may
change rendered PNG bytes; numerical CSV values must not change. Recompute the
sidecar on regeneration. Inspect the image at its intended column width before
Overleaf integration. No local manuscript source or figure in the snapshot is
replaced by this preparation.
