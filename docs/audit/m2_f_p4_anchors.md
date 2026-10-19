# P4: saved circuit anchors and signing admission

Date: 2026-10-18. Status: evaluation completed; independent-reader review and
author commit pending. P5 remains pending. No manuscript edit or new circuit run.

## Inputs and provenance

The five cases are exactly the anchors frozen in P1. Both input SHA-256 values
match the committed configuration: historical report `1354d9b3...f26bbd` and
NPZ `77ae8604...cdceba`; full hashes are in the configuration and P4 summary.
The NPZ is read with allow_pickle=False. Missing or altered inputs fail;
the evaluator never regenerates gate outputs or draws new measurements.

The P4 script starts from commit `84afc4c` with its new script/tests uncommitted,
as recorded in the generated report's dirty status and exact script hash.
Production and frozen configuration remain unchanged. Results are in
`results/m2-f-p4/summary.json` and `results/m2-f-p4/budgets.csv`.

## What is compared

1. Every saved output label versus the independent classical sequence kP,
   including canonical identity and the full saved point/work label. No
   projection or mask hides nonzero high work bits.
2. The saved distribution versus an FFT reconstructed from those labels,
   grouping by complete labels, and versus the raw finite-fiber spectrum.
3. The statistic law induced by production verified_candidates on the saved
   probabilities versus the analytical order-divisibility model. Reference r
   is used only for analysis, not passed to production recovery or admission.
4. Full gcd-state distributions and the three recovery outcomes at T in
   {0,1,2,4,8,16,32,64}; the positive budgets come from the frozen report.
5. Actual production admit_signing_order decisions for each encountered gcd
   state versus the model's separate admission partition.

No sampling or signature generation is performed. The old 100-trial counts
are not compared to exact probabilities as if they had to be equal, and they
are not new M1 signing results. All actual admission decisions in these cases
use deterministic small-prime checks; no Miller-Rabin bases were sampled.
The model retains the general false-pass bound separately, zero here.

## Results

| p | Q | Reference r | Saved scalar outputs | Historical distinct gate transitions | Exact recovery at T=4 | Admitted at T=4 |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | 128 | 9 | 128 | 82 | 0.9763958861 | 0 |
| 7 | 256 | 2 | 256 | 2 | 0.9375 | 0.9375 |
| 7 | 256 | 3 | 256 | 12 | 0.9869139473 | 0.9869139473 |
| 11 | 512 | 7 | 512 | 42 | 0.9993893806 | 0.9993893806 |
| 29 | 2048 | 5 | 2048 | 40 | 0.9983424862 | 0.9983424862 |

Probabilities are numerical estimates under ideal independent executions.
In total: 3,200 saved scalar outputs and 40 budget rows checked. Maximum
saved/FFT/raw spectrum difference is 1.1102230246251565e-16; maximum one-shot
statistic difference is 4.440892098500626e-16. The maximum full T-shot law
difference is 3.930189507173054e-14. Actual admission and the model agree with
zero reported difference; partition residuals are at most
8.815170815523743e-14. All checks meet the frozen absolute tolerance 1e-10.

The order-9 case is the intended distinction, not a failure: recovery correctly
returns a composite order, while the admission gate rejects it. For the four
prime-order cases, exact recovery mass equals correct admission mass. This is
an arithmetic admission statement, not domain security or guaranteed signature
success for all inputs; these tiny orders are not cryptographic parameters.

## Coverage limits

These are historical phase-free arithmetic basis paths, with ideal IQFT
probabilities obtained by FFT, not fresh quantum hardware or dense-statevector
runs. Their original simulator checked scalar-control preservation and clean
work on cached gate transitions before saving outputs. P4 checks the saved
labels; it does not re-execute those gates or independently recertify cleanup.

The original Q=2048 p=29 run covered all scalar inputs from the initialized
identity, but only 40 distinct cached transitions: four adders, five subgroup
points and both controls. It does not exhaust all p=29 point encodings,
arbitrary work states, curves or adder constants. The Q=32 later test is a
separate record. See `docs/audit/coverage.md`.

Agreement extends the finite model's validation to these saved distributions
at the stated coverage. It is not a universal circuit proof, interval
certificate, new post-processing method, or speedup claim.

## Tests and reproduction

15 new tests use synthetic fixtures, not the ignored NPZ. They cover prime and
composite admission, nonminimal rejection, hashes, metadata, shapes/dtypes,
probability corruption, wrong/high-work labels, spectrum mismatch and missing
archives. Quick suite: 124 passed, 105 slow tests deselected. No full slow run.
A replay in a separate output directory reproduced every case and the budget
CSV identically; run timing/provenance remain separately recorded.

With the exact historical NPZ restored locally:

```text
python experiments/scripts/evaluate_saved_anchors.py --root . --config experiments/configs/m2_f_main.json --output-dir results/m2-f-p4-replay
```

Choose a new output directory; existing outputs are not overwritten. A fresh
clone needs the ignored historical NPZ from the archived dataset, with the
frozen checksum. Dataset publication remains a release task, not completed here.
No dependency changes are required beyond the existing NumPy environment.

## Next gate

Independent reader reproduces the five anchors, 40 outcome rows and actual
admission comparisons, checks coverage wording, then Ariel commits. P5 reviews
the combined F evidence and prepares only bounded manuscript proposals if
warranted. Ariel remains the sole editor of Overleaf.

The two P3 documentary issues identified during review were clarified without
changing data: its completed review status, and the unsupported extrapolation
to order 60 outside the grid. No new field or experiment was added to test it.

## Independent reader review (Claude, 2026-10-18)

- Re-executed the anchor evaluation in the Python 3.12 Qiskit environment:
  five cases, 3,200 saved outputs, 40 budget rows; recovery probabilities equal
  to the versioned report to 6.6e-24 (last-digit float summation order), the
  production admission decisions reached for every gcd state identical, the
  full-law difference 3.93e-14 reproduced. budgets.csv differs only in the
  last printed digits of three sub-1e-7 "nonminimal" entries.
- Frozen-input guards verified: both hashes match the committed configuration,
  the NPZ is read with allow_pickle=False, paths are confined to the repository,
  a missing archive fails without regeneration, and the run refuses an existing
  output directory and a configuration that differs from HEAD.
- Comparison design accepted: saved labels checked against the independent kP
  sequence without masking work bits; saved spectrum against both the FFT
  reconstruction and the raw ideal law; statistic law via production
  verified_candidates against the divisibility predicate; T-shot law against
  the ideal law; and, importantly, the actual production admit_signing_order
  decision for every reached gcd state against the model's partition, with a
  guard that fails if any decision would need randomized Miller-Rabin bases.
  All five anchors stayed within deterministic small-prime checks.
- Quick suite 124/124; LF; no personal paths; tracked outputs about 100 KB.
- Coverage wording is correct: saved initialized-scalar paths at the recorded
  40 (p = 29) transitions, no re-execution of gates, no universal adder-domain
  claim; composite order 9 recovered and rejected for signing as intended.
- Process note: the "Observation for P5" bullet in my signed P3 review was
  rewritten by the first reviewer rather than appended to. I accept the
  substance (the move to order 60 outside the grid was an untested hypothesis
  and "most composite" is imprecise), but reviewer notes should be amended by
  appending a dated correction, not by editing another reviewer's text.
