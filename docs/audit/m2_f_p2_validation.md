# P2: bounded-order model and precision checks

Date: 2026-10-18. Based on P1 commit 8bb346b and the unchanged configuration
SHA-256 `5ff39ebd13cb883526a064b32fdad8f1d6ea43c218f630028c9d9b1e819e1358`.
Status: implementation and bounded validation delivered; independent-reader
review pending before P3. No main grid or new circuit execution performed.

## Review comments and disposition

| P1 comment | P2 action |
| --- | --- |
| Freeze the five saved circuit anchors | Retained the added anchors block byte-for-byte. Report and ignored NPZ hashes match the frozen configuration. Actual distribution/law comparison remains P4 |
| Define operation counts before P3 | Added OPERATION_COUNT_DEFINITION in bounded_recovery_law.py and included it in generated reports |
| Use a separate analytical driver, not the pilot driver | Added evaluate_bounded_reliability.py with validate-pilot default and an explicitly selected, committed-config-guarded main mode |
| Attempt interval evaluation | Added an optional interval reference and exercised it on the seven pilot rows and their saved T values. No precision-policy upgrade or uniform-budget certificate is claimed |

## Model and implementation boundary

`experiments/reference/bounded_recovery_law.py` accepts (Q, r, B) only for
offline analysis. For a point with true order r, vP = O iff r divides v.
The production solver continues to perform group verification without r.
The model enumerates every continued-fraction denominator, tests the bounded
ones, deduplicates accepted values as production does, and takes their gcd.
Zero denotes an empty accepted set, not a group point.

Finite spectrum: write Q = L*r + t and define

```text
P(y) = [t*S_(L+1)(y) + (r-t)*S_L(y)] / Q^2
S_n(y) = |sum_(k=0..n-1) exp(2*pi*i*k*r*y/Q)|^2.
```

This is the standard finite-fiber law, not a new quantum algorithm. The fast
path uses NumPy sinc. The independent reference uses integer-reduced phases
and squared sine ratios, with the exact removable-singularity value n^2.
It also computes CF denominators from quotient lists evaluated backwards,
rather than calling the production recurrence.

Unlike the existing normalized simulation helper, the new fast path returns
raw probabilities and checks their mass without renormalizing. Existing
production behavior is unchanged. Rational recurrence/inversion checks are
retained and new tests compare the spectrum against an explicit fiber DFT.

## Precision and certification limitation

Reference backend: mpmath 1.3.0, 80 decimal digits, isolated contexts. No
production dependency/lock change. Optional checks require this backend in the
experiment environment and fail clearly if unavailable. The interval path
uses [the versioned MPIntervalContext implementation](https://github.com/mpmath/mpmath/blob/1.3.0/mpmath/ctx_iv.py).

P2 computes diagnostic interval enclosures of exact-order probabilities on
selected pilot budgets. Their total one-shot mass encloses one, and the
T-shot intervals contain the independently evaluated high-precision points.
Saved decimal endpoints are display data, not inputs to guarantee decisions.
The report remains numerical_only, exactly as P1 specifies.

Important correction to the optional P1 suggestion: checking only the order
that is worst in float64 cannot certify a uniform budget. For a certified
sufficient T, every r in the frozen superset must have an outward-rounded lower
bound at least 1-epsilon. Certifying minimality additionally requires an order
with an upper bound strictly below 1-epsilon at T-1. No such all-orders
certificate was attempted. Interval checks here do not justify guarantee
wording for the eventual field-level budget.

The driver records unresolved threshold proximity at either T or T-1, all
numerical worst-order ties, raw residuals, and failure to cross within the cap.
It does not clip or renormalize failing data. The ratio to our existing bound
is not interpreted as superiority to Ekerå or another published method.

## Operation-count semantics

- CF denominators generated: every yielded denominator, including duplicates.
- Bounded denominators tested: every yielded value in [1,B], including repeats.
- Divisibility checks: one offline r-divides-v check per bounded denominator.
- Statistic gcd updates: one per distinct accepted denominator per y, from zero.
- DP gcd updates: one per state/statistic pair per recurrence step.

These are offline analytical operation counts, not quantum gates or counts of
production scalar multiplications. Wall time is recorded separately. No cache
saving is claimed as an online algorithmic improvement.

## Validation evidence

Report: `results/m2-f-p2/validation.json` (generated, not hand-edited).

- Seven frozen pilot rows; 11,904 complete per-outcome comparisons between
  order-divisibility acceptance and production point verification, all equal.
- 49 selected T-shot outcomes checked by DP versus divisor inversion.
- Maximum DP/inversion difference: 1.9984014443252818e-15.
- Maximum fast/high-precision one-shot difference: 9.71445146547012e-16.
- Maximum fast/high-precision T-shot difference: 4.39648317751562e-14.
- These residuals are below 1e-10; they are diagnostics, not roundoff proofs.
- 24 new tests; full quick suite: 94 passed, 105 slow tests deselected.
- Full slow circuit suite not rerun: no production circuit was modified.
- Both frozen P4 source-file hashes checked, not re-created or replaced.

Production source fingerprint remains
`3d2206e4b04e1b2f36687d43a32307ce490d21ca4567c9238cf401f12c4b884c`.
The validation report records dirty status because it was generated before
the author commit, and includes exact driver/model/config/source hashes.

## Reproduction and next gate

With the project environment, NumPy and mpmath 1.3.0 available:

```text
python experiments/scripts/evaluate_bounded_reliability.py --root . --config experiments/configs/m2_f_main.json --mode validate-pilot --output results/m2-f-p2/validation.json
python -m pytest -q
```

This replays P2 only. The small-field synthetic driver tests are fixtures, not
the 650-law main study. P3 requires independent review of these changes and
the author commit. The main command is intentionally not executed here.
P4 anchor comparisons, P5 independent re-derivation and manuscript proposals
remain pending. The only article editor is Ariel in Overleaf.

## Independent reader review (Claude, 2026-10-18)

- Reproduced the validation run in the Python 3.12 Qiskit environment: no
  numeric or count difference against results/m2-f-p2/validation.json; the
  report's figures (11,904 predicate matches, residuals 2.0e-15, 9.7e-16 and
  4.4e-14, config hash 5ff39ebd) confirmed. Quick suite 94/94; hygiene clean.
- Independent cross-checks with code that does not import the new model:
  raw_probabilities equals the FFT of the permutation (project simulator) on
  five (Q, r) pairs to 1e-12; one_shot_by_order equals my own enumeration on
  four (Q, r, B) triples to 1e-12; the 60-digit modular-phase reference agrees
  with a direct 60-digit geometric-sum DFT to 3e-61 on (64, 6, 10).
- End-to-end fixture of the main mode on p = 5, Q = 128, cap 64: budgets 7, 13
  and 19 shots for epsilon = 0.1, 0.01 and 0.001, worst order r = 6, status
  numerically_estimated_first_crossing; agrees with the earlier ad hoc value
  (13 at 0.01) and costs 0.02 s offline, so the full 650-law grid is minutes.
- The correction to my P1 suggestion is accepted: a certificate for a uniform
  budget needs outward-rounded lower bounds for every r in the superset at T,
  and an upper bound below 1 - epsilon for some r at T - 1 to certify
  minimality. Interval diagnostics on selected orders justify no guarantee
  wording; the numerical-only label stands.
- Design points approved: strict validate_config against the frozen grid, main
  mode refusing a configuration that differs from HEAD, raw (unnormalized)
  spectrum with mass check instead of the production helper's renormalization,
  explicit operation-count units, unresolved-threshold handling at T and T - 1.
- Minor, non-blocking: evaluate_main recomputes admission_summary for every
  order at every T (cheap); precision_weights re-enumerates all Q outcomes per
  selected order (also cheap at these sizes). No change requested.
