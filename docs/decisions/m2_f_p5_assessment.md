# P5: evidence assessment and bounded integration plan

Date: 2026-10-18. Author confirmed in this chat that the advisor accepts framing
E: verified integration plus reliability characterization, without requiring
component-level novelty. This records the author's report, not an independent
message from the advisor. P5 package prepared; final package review and author
commit pending. No manuscript edits or new scientific experiments.

## Decision

Recommend advancing to stage 7, bounded Overleaf integration, after review of
this package. The F evidence collection and its independent numerical checks
are complete within the frozen scope. The defensible contribution is the
explicit, tested hybrid implementation and characterization of its implemented
recovery/admission policy, alongside the existing cost analysis.

This is not a new Shor algorithm, point-addition construction, probability
technique or established performance improvement over prior work. The reviewer
may judge integration plus characterization insufficient; the accepted venue
risk in m2_decision.md remains. R8 has a response supported by evidence, not a
priority proof or guaranteed reviewer acceptance. Formal closure waits for the
author's manuscript integration and the stage-8 response audit.

## Claim/evidence assessment

| Claim | Evidence | Allowed interpretation | Excluded interpretation |
| --- | --- | --- | --- |
| Explicit hybrid process | Existing reversible arithmetic, production recovery, M1 admission and classical signing | Reproducible integration with explicit contracts and stated test coverage | New arithmetic, first integration, quantum-secure signature scheme |
| Finite law of the implemented recovery policy | Proof and rational checks in m2_f_reliability_model.md; P2 production-predicate correspondence; DP/divisor/Mobius checks | Exact mathematical recurrence with numerically evaluated probabilities | New probability theorem or certified float64 values |
| Unknown-order calibration on bounded fields | P3: 650 laws, 66 budgets over a conservative all-integer order superset | Numerical offline calibration, including absent/nonminimal outcomes | Efficient cryptographic-scale preprocessing or a first uniform guarantee |
| p29 budget 16 at the 99% target | P3 minimum 0.9867763896476266 at T=15 and 0.9900892456126702 at T=16 over 2..40 | First numerical crossing, Q=2048, ideal independent executions | Certified minimum; order-5-conditioned budget; 16 versus Ekerå |
| Existing sufficient bound 443 is conservative here | Same P3 policy/parameters, ratio 443/16=27.6875 | Comparison to our own explicit sufficient bound | Speedup over SEA, factoring or optimized published post-processing |
| Link to saved circuit outputs | P4: five hash-frozen instances, 3200 labels, 40 budget rows; maximum full-law difference 3.93e-14 | Agreement at the historical initialized-scalar coverage | New gate run, hardware/noise result or all-domain adder proof |
| Signing admission is distinct | Actual M1 replay agrees with P4 partition; order 9 recovered but rejected | Exact small-prime classification on these anchors; general MR error remains separate | Domain security or zero false-acceptance error for arbitrary-size candidates |

## Independent checks already on record

- P2, commit af324c6: second reader reproduced the seven-row validation and
  separately checked finite spectra, statistics and high-precision arithmetic.
- P3, commit 84afc4c: second reader reran the frozen grid in Python 3.12,
  reproduced all 66 budgets/ties/counts, with maximum outcome difference 1.1e-19.
- P4, commit 118d7e1: second reader reran all five saved anchors, reproduced
  admission decisions, and obtained maximum recovery difference 6.6e-24.
- These are the recorded reader checks, not new reruns by the P5 author.
  Final review of this interpretation and the proposed fragments remains open.

Production source SHA-256 remains
`3d2206e4b04e1b2f36687d43a32307ce490d21ca4567c9238cf401f12c4b884c`.
Frozen configuration SHA-256 remains
`5ff39ebd13cb883526a064b32fdad8f1d6ea43c218f630028c9d9b1e819e1358`.

## Minimal manuscript map (proposals, not applied edits)

| Target in current Post_M1 snapshot | Bounded action | Preserve |
| --- | --- | --- |
| Appendix B, after Recovery probability and resulting bounds | Add the policy-specific recurrence, three outcomes, and offline budget definition | All existing sufficient-bound and complexity derivations |
| III.A.4 Probabilistic order recovery | One cross-reference sentence; qualify general MR rejection wording | Algorithm, admission test and recovery policy |
| III.F Reproducibility regime, before Discussion | One short numerical-results block and one figure from frozen tables | Existing experimental method and historical trials |
| Appendix C, after empirical recovery counts | Short model/coverage clarification | The 77/96/100 counts, seed, example parameters and signature (1,4) |
| III.G Discussion | A few positioning/motivation sentences and numerical/offline limitations | Title, structure, circuit exposition and classical comparison |
| Abstract, contribution item 2, concluding contribution sentence | Update only the numerical-validation phrases, after body integration | Tone, twofold contribution and surrounding correct prose |

Concrete before/after blocks are kept in the author's private working notes,
outside version control. They refer to the
current snapshot and must be rechecked against live Overleaf before use. They
do not rewrite a section, change the circuit, or substitute empirical budgets
into the asymptotic analysis. Formula derivation stays in the appendix; results
appear in Results. Only new/replaced text is blue.
The explicit baseline giving 443 uses the looser rule
ceil(16*(1+floor(log2 B))*ln(1/epsilon)), not the preceding tighter asymptotic
budget. Its short totient-bound derivation is included in the private appendix
proposal so that 443 has an explicit manuscript basis. Parametric resource
costs retain T; no empirical/coarse rule is silently given the tighter rule's
asymptotic scaling.

## Figure and traceability

One candidate figure, `paper/figures/f_reliability_budgets.png`, is generated
from the existing 66 budget rows, not by rerunning F. It shows the three error
targets and both register choices. Lines only connect sampled primes; there
is no extrapolation to untested fields. Caption explicitly says numerical,
ideal-independent and conservative order superset.

Generator: `experiments/scripts/plot_reliability_budgets.py`. Its manifest
records the input/config/script/image hashes and plotting-only environment.
Matplotlib is isolated outside the project; production dependencies/lock are
unchanged. The plotted values come from the NumPy-2.1.3 scientific run; the
plotting environment does not recompute those values. A small figure is the
only planned new visual, not a new results section or resource benchmark.

## Reference boundary

Existing Proos-Zalka, Roetteler, Haener, Litinski and Cheung-Mosca keys were
located in the snapshot. Ekerå's inspected preprint (2201.07791v2, Sections
1.2 and 4.2) and Papa's validation (2506.03318v2) are relevant antecedents;
candidate BibTeX records are proposed privately with explicitly new keys, not
inserted into main.bib. No first-use/absence claim depends on unresolved direct
inspection of Knill or on the abstract-only general-gcd comparison.

## Still required before resubmission

- Author integrates reviewed blocks in Overleaf, compiles there, and supplies
  an explicitly authorized export for the final comparison. No export imported
  or manuscript file edited during P5.
- References [27]/[28]/[30] and existing typos remain stage-7 tasks. Replace
  unverifiable/irrelevant citations, not just their numbering.
- Update the old data-availability repository and dense-statevector wording;
  choose the exact release/tag/DOI at publication. The historical NPZ and full
  P3 raw report are still ignored local data awaiting dataset release.
- Acknowledgments, author contributions, keywords and any double-blind version
  remain author/venue decisions, not supplied by numerical success.
- This is not a fresh global audit declaring R1-R8 or all prose 100% corrected.
  Stage 8 checks the integrated text and reviewer response against evidence.

## Review-note ownership

Accept the P4 reader's process observation: from now on amend signed review
notes with an appended, dated, attributed correction, never by rewriting
another reviewer's entry. P5 does not modify any signed P3/P4 review text.
The previous editorial change is preserved in Git history and acknowledged
by the P4 reader; it is not silently rewritten again here.

## Closure state

Package checks: 132 quick tests passed, 105 slow tests deselected; no full slow
rerun. All 11 before/anchor fragments match the Post_M1 snapshot after whitespace
normalization, and the 16 snapshot files still match their recorded SHA-256
values. New citation keys are explicitly proposed and absent from the current
bibliography; all other proposal keys already exist. The figure was visually
inspected for readable labels/legend and checked against its input/hash manifest.
These are preparation checks, not an Overleaf compilation or a new snapshot.

P0-P4 evidence: completed and reviewed within scope. P5: assessment, figure and
private proposals prepared, advisor framing accepted as confirmed by author;
final package review/author commit pending. Stage 7: manual integration next.
Stage 8 and formal R8 response closure: pending. No publication or security
outcome is promised.

## Independent reader review (Claude, 2026-10-18)

- Every "before" anchor of the author's private fragments was located in the
  Post_M1 snapshot after whitespace normalization (11 anchors across abstract,
  introduction, results and appendix); the labels they reference
  (app:complexity, app:instance, eq:app_r6_success_lower_bound, alg:hybrid)
  exist; the proposed new BibTeX keys are absent from main.bib as stated.
- The appendix derivation chain is valid: the snapshot's Equation
  (app_r6_success_lower_bound) gives alpha >= phi(r)/(16 r); with
  phi(r)/r >= 1/(s+1) >= 1/nu_B for r <= B this yields exactly the implemented
  rule ceil(16 nu_B ln(1/epsilon)) and the value 443, so the manuscript gains an
  explicit basis for the baseline it already uses in code.
- Numbers quoted in the fragments match the reviewed results (0.9867764 /
  0.9900892 at T = 15/16; 0.9983424862 at T = 4; 443/16). One rounding slip was
  corrected in the private file: the P4 maximum T-shot difference is
  3.930e-14, written as 3.93e-14, not 3.94e-14.
- Figure: inputs validated against budgets.csv, summary.json and the frozen
  configuration (hash-guarded; status must be a resolved numerical crossing);
  rendered at 3.5 x 2.65 in, 500 dpi; values read from the image agree with the
  66-row table; legend and axis labels legible at column width. Plotting runs
  in a separate environment (Matplotlib 3.10.7, NumPy 2.5.4) and never
  recomputes scientific values; the locked environment is unchanged.
- Quick suite 132/132; LF; no personal paths; PNG stored as binary.
- Rule compliance fix applied before commit: two tracked files (this record
  and docs/revision_log.md) named the author-only proposals file by path; the
  references were replaced by "the author's private notes". Versioned documents
  must not point to that file.
- Wording check of the fragments: no "certified", "rigorous", "first",
  "improvement over Ekeraa" or speedup statements; composite-order recovery and
  signing admission kept separate; offline small-field framing present. The
  response inventory is correctly labelled as evidence, not a rebuttal.
