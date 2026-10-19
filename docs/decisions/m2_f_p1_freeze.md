# P1: main configuration and numerical precision

Date: 2026-10-18. Prepared under the committed M2 decision, 98f4a3e.
The author confirmed in this chat that the advisor has been informed.
This is notification, not a claim of advisor endorsement of the results.
Status: configuration prepared for review and author commit; no main run.

## Frozen target

`experiments/configs/m2_f_main.json` specifies the planned 11 prime fields,
all integer orders 2..B, two register sizes, and three failure targets.
These orders are a conservative analytical superset; they are not claimed to
occur on every field or to be admissible for signing. The true order enters
only the offline model, never production recovery or signing.

For each p, B = p + 1 + isqrt(4*p), m0 = (B*B).bit_length(), and
Q = 2**(m0 + extra_bits). Thus Q is strictly above B squared even when B
squared is a power of two. The baseline budget is the existing sufficient_budget
function, unchanged. Its ratio to the estimated budget only measures local
bound conservatism, not superiority to prior post-processing.

Search T = 1..2048, with a separate T = 0 check. For each epsilon, report
the first numerical threshold crossing of min_r P_T(exact) and its T-1 row,
all worst-order ties within the declared tolerance, and any unresolved
near-threshold case. If no crossing occurs, report that fact without extending
the range after seeing the data.

## Precision decision

Choose the numerical-only branch already allowed by plan v2. Primary values
are float64 estimates, not certified probabilities or minimal budgets. The
finite mathematical law may be exact while its evaluated values are numerical.
No "rigorous guarantee" wording follows from this experiment.

P2 must provide an 80-decimal-digit reference check on the seven frozen pilot
rows and, before reporting the main results, every selected worst-order
threshold pair (T-1, T). Agreement is diagnostic, not an interval enclosure.
The reference backend, version and method must be documented; production
dependencies remain unchanged. Its implementation is pending, not asserted
to exist in the pilot driver.

Absolute tolerances are 1e-10 for mass, recurrence/inversion agreement,
monotonicity, threshold proximity, ties and high-precision differences. Record
raw residuals. Do not silently clip negative masses or renormalize a failing
distribution. Stop on failed checks. A near-threshold estimate is unresolved,
not a certified crossing. Any precision-policy change is a documented amendment
before the affected main run, not an undocumented adjustment to obtain a result.

## Reporting and implementation gates

- Recovery: exact order, no candidate and nonminimal multiple sum to one.
- Admission: prime/composite true orders are separate; use existing small-prime
  checks and the 64-round Miller-Rabin false-pass bound. No security claim.
- Quantify the single-shot-exact-event bound 1 - (1 - w_r)**T separately from
  the full gcd law, which can also recover r by combining nonminimal multiples.
- Record offline time and defined operation counts separately from quantum
  execution cost. Do not treat exhaustive r enumeration as scalable preprocessing.
- P4 uses saved circuit distributions only, at their recorded coverage.
- No Monte Carlo, new circuit runs or implemented literature baseline.
- Pilot/ad hoc observations remain exploratory; no existing result is rewritten.

The current pilot script accepts explicit curve/point cases. It does not yet
consume this all-orders configuration. P2 must add and test the analytical
driver/predicate correspondence without changing the production solver. Do not
pass this configuration to the pilot script and claim the main study ran.

## What is needed next

1. Author and independent reader review this configuration, especially the
   numerical-only choice and threshold handling; Ariel makes the freeze commit.
2. P2: harden the order-divisibility model, rational checks, production-policy
   correspondence and independent high-precision path. No main grid evaluation.
3. P3 starts only after the configuration commit and P2 checks. Record the
   actual config hash, code hashes, environment, commit and dirty status.

## Preparation checks

Read-only configuration checks passed against production uniform_register_size
and sufficient_budget: 650 (p, r, Q) laws, 1950 order/size/error-target entries,
and 66 field/size/error-target summaries. The largest Q is 8192. The largest
existing sufficient budget in this grid is 664, within the 2048 search cap.
These are grid/baseline checks, not evaluated reliability outcomes.

Prepared configuration SHA-256 (after the independent-reader addition of the
P4 anchors block): `5ff39ebd13cb883526a064b32fdad8f1d6ea43c218f630028c9d9b1e819e1358`.
Future runs must recompute the hash of the committed file rather than copy this
value. The read-only check did not enumerate measurement distributions or run
circuits. The scientific test suite was not rerun for this configuration/doc
change; P2 requires focused tests of its new implementation.

No results, circuit, dependency or manuscript changes are part of P1.
The accepted contribution remains integration plus characterization; this
configuration is not evidence that the novelty objection is resolved.

## Independent reader review (Claude, 2026-10-18)

- Verified against production functions: 650 (p, r, Q) laws, 1950 entries, 66
  summaries, largest Q = 8192, largest existing sufficient budget 664 (within the
  2048 cap), Q > B^2 for every row, decision commit 98f4a3e exists, configuration
  hash reproduced before the addition below. Quick suite 70/70; hygiene clean.
- Added an `anchors` block to the configuration so that P4 is frozen too: the
  five saved real-circuit instances, their array names, and the SHA-256 of the
  legacy report and of the ignored NPZ (matching historical_artifacts.json).
  No other field changed.
- Precision: the numerical-only choice is allowed by plan v2 and acceptable. The
  interval path is cheap here (mpmath 1.3.0 with `mpmath.iv` is already in the
  locked environment), so P2 should attempt a certified lower bound on
  P_T(exact) for each reported worst-order pair (T-1, T); if it succeeds, the
  guarantee wording becomes available for those rows, otherwise everything stays
  "numerically estimated". This is an optional amendment, to be recorded before
  P3 if adopted.
- Still to fix in P2 before P3: the `operation_count_definition` (proposal:
  number of continued-fraction denominators verified, number of divisibility
  checks and number of gcd updates per (p, r, Q), plus wall time).
- Agreed: the pilot driver must not be fed this configuration; P2 adds the
  all-orders driver with its own tests.
