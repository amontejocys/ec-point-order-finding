# P3: main numerical reliability evaluation

Date: 2026-10-18. Status: main evaluation completed; independent-reader review
pending. P4 saved-circuit anchors and P5 remain pending. This is supporting
characterization under the M2 decision, not a component-level novelty claim.

## Frozen execution and deliverables

- Source commit: `af324c647e705651759f3b8e33632ee9b9c03d3b` (P2 reviewed).
- Working tree clean when the main run began; recorded dirty status is empty.
- Frozen configuration SHA-256:
  `5ff39ebd13cb883526a064b32fdad8f1d6ea43c218f630028c9d9b1e819e1358`.
- 11 fields, two register sizes, 650 order/register laws and 66 field-level
  error-target budgets; 15,155 saved T-shot outcome rows.
- All 66 budgets have numerical first crossings; none is unresolved or unreached.
- Python 3.11.5, NumPy 2.1.3, mpmath 1.3.0; approximately 13.10 seconds offline
  on this environment. This is analytical runtime, not quantum hardware time.
- No Monte Carlo, new circuit execution, production change or manuscript edit.

Small versionable outputs in `results/m2-f/`: summary.json, budgets.csv and
orders.csv. The full 13,065,947-byte report is preserved at
`results/m2-f/raw/evaluation.json`, ignored under the existing raw-output policy.
Its SHA-256 is recorded in summary.json. Do not add the raw report to Git;
retain it for the eventual dataset release. Regeneration needs no external data.

## Main observations

For the baseline register choice Q > B squared, the numerically estimated
uniform recovery budgets are:

| p | Q | T for 90% | T for 99% | T for 99.9% | Worst r at 99% |
| --- | --- | --- | --- | --- | --- |
| 5 | 128 | 7 | 13 | 19 | 6 |
| 7 | 256 | 7 | 14 | 20 | 12 |
| 11 | 512 | 7 | 13 | 19 | 18 |
| 13 | 512 | 7 | 13 | 19 | 18 |
| 17 | 1024 | 7 | 14 | 21 | 24 |
| 19 | 1024 | 7 | 14 | 21 | 24 |
| 23 | 2048 | 8 | 16 | 24 | 30 |
| 29 | 2048 | 8 | 16 | 24 | 30 |
| 31 | 2048 | 8 | 16 | 24 | 30 |
| 37 | 4096 | 8 | 16 | 24 | 30 |
| 41 | 4096 | 8 | 16 | 24 | 30 |

These are worst cases over every integer r = 2..B, a conservative analytical
superset. No assertion is made that each reported worst order is realized by
a point on a particular curve, or that it is admissible for signing.

Doubling Q reduces the 99% budget from 13 to 12 for p=5 and from 14 to 13 for
p=7,17,19. It leaves that budget unchanged in the other seven fields. This is
an observed discrete tradeoff, not a universal monotonic-improvement claim or
a gate-cost advantage; the additional register/circuit work must not be ignored.

For p=29, Q=2048, B=40, the minimum exact-order probability is approximately
0.9867763896476266 at T=15 and 0.9900892456126702 at T=16. Thus 16 is the first
numerical crossing of 99% for this superset. The hardest order is 30, not the
example point's known reference order 5. Recovery of composite orders is
included even though they are rejected by the signing-admission policy.

Our existing conservative sufficient budget is 443 at this error target.
The ratio 443/16 = 27.6875 quantifies conservatism of that particular bound.
It is neither a speedup over classical point-order algorithms nor superiority
to Ekerå or another published post-processing method.

## Checks of the saved report

The new summarizer audits the report without importing the recovery model or
production code. In addition to complete-grid, threshold, predecessor, tie,
admission and provenance checks, it evaluates an independent scalar formula:

```text
P(g_T = r) = sum_(j=1..floor(B/r)) mu(j) * (F_(r*j)^T - w_0^T),
F_d = sum_(v: d divides v) w_v, including v=0.
```

This is standard Mobius inversion, not a new theorem. It is a separate
implementation check, not a substitute for independent human review.

| Diagnostic | Maximum absolute difference/residual |
| --- | --- |
| DP versus scalar Mobius audit | 5.551115123125783e-15 |
| DP versus original divisor inversion | 5.773159728050814e-15 |
| Recovery partition sum | 1.4788170688007085e-13 |
| Selected 80-digit T-shot reference | 3.697042672001771e-14 |
| Selected 80-digit one-shot reference | 1.9984014443252818e-15 |

All are below the frozen 1e-10 tolerance. The 80-digit checks cover all selected
numerical worst-order ties at T and T-1 for each target, not every order.
No certified uniform guarantee or certified minimum is claimed.

All reported admission partitions are exact for the configured small-prime
checks in this bounded grid; the stored actual-policy false-pass bounds are
kept separate. This does not establish cryptographic domain suitability.
Comparison to saved real-circuit distributions remains P4.

Operation totals: 17,302,204 CF denominators generated, 9,227,468 bounded
denominators/divisibility checks, 272,152 statistic gcd updates and 405,514 DP
gcd updates. These count the named fast-path operations only, not every
validation/high-precision instruction and not quantum gates. Offline wall time
includes reference checking. See the definitions in summary.json.

## Reproduction

One command from the repository, with mpmath 1.3.0 in the experiment environment:

```text
python experiments/scripts/summarize_bounded_reliability.py --run --root . --config experiments/configs/m2_f_main.json --output-dir results/m2-f-replay
```

Use a new output directory: the command refuses to overwrite an existing raw
report. It runs the committed-config-guarded driver, then audits and summarizes.
Numeric results should reproduce within the declared tolerances; timing and
provenance metadata depend on the environment/current checkout. For a saved
report, use --input instead of --run to regenerate only the small tables.

The main run preceded creation of the summarizer and its tests; their own
source hash is recorded separately in summary.json. Production and configuration
fingerprints remain unchanged. Full slow circuit tests were not rerun.
The quick suite passed: 109 tests, with 105 slow tests deselected. An actual
one-command replay in a separate workspace directory reproduced all 650 laws,
66 budgets, precision diagnostics and operation counts identically after
excluding wall-time fields and run provenance. The replay does not replace the
original clean-tree report or count as independent-reader review.

## Next gate

Independent reader: reproduce the 66 budgets, selected high-precision checks,
predecessor rows and interpretation, then review the auditor/tests. Ariel
commits the reviewed P3 delivery. Continue with P4 anchors and P5 assessment;
do not transfer claims to Overleaf or close R8 merely from these numbers.

## Independent reader review (Claude, 2026-10-18)

- Re-executed the main mode in the Python 3.12 Qiskit environment (19 s): all
  66 budgets, statuses, worst-order ties and operation counts identical to the
  versioned raw report; maximum outcome difference 1.1e-19. The auditor run on
  my report reproduces every diagnostic in summary.json and budgets.csv is
  identical apart from wall time.
- The 11 baseline budgets at 99% (13, 14, 13, 13, 14, 14, 16, 16, 16, 16, 16)
  coincide with the ad hoc worst-case values computed independently before P1
  for the six fields then examined, now obtained from the frozen pipeline.
- Provenance checked: run on the clean P2 commit af324c6 (empty dirty status),
  configuration identical to HEAD, raw report 13 MB ignored with hash recorded,
  tracked tables 108 KB. Quick suite 109/109; LF; no personal paths.
- Auditor design accepted: it imports neither the model nor production code
  and re-derives every exact-order probability through a scalar Mobius sum;
  the six corruption tests cover the failure modes that matter.
- Observation for P5 (not a claim): from p = 23 on, the worst order is 30, the
  most composite integer below B, and the budgets stop growing at 8/16/24. The
  worst case will move to 60 once B >= 60 (p >= 47, outside the grid). Budget
  growth with p is therefore governed by the most composite admissible order,
  which the phi(r)/r heuristic anticipates; this should be stated as an
  observed pattern on the grid, not extrapolated.
- Wording check passed: the note never calls the budgets certified, minimal or
  superior to published methods, and keeps composite-order recovery separate
  from signing admission.
