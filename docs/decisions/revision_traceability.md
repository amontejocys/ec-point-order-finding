# Revision traceability: R1-R8, mitigation and F

Status date: 2026-10-18. This is a consolidation, not a new research plan or a
change of scope. Historical entries and signed reviewer notes remain intact.
This index supersedes stale progress statements in the chronological register,
not their record of what was known at the time.

## Identifier families

- R1-R8 decompose the original reviewer objections into correction workstreams.
- The recovered eight-stage plan explicitly names only M1 (signing admission)
  and M2 (novelty audit). Earlier feedback also uses M4-M6, but those labels are
  not definitions of stages 4-6 in this plan.
- A-F are candidate contributions investigated during M2, not milestones.
- P0-P5 implement the selected F evidence subplan after the M2 decision.
- The eight numbered stages in the local working plan are a separate workflow:
  scope, M1, M2, diagnostics, decision, evidence, integration, final audit.
  In particular, stage 3 is not automatically M3 or R3.

Code validated, text integrated, and reviewer objection closed are three
different states. No global completion percentage is assigned.

## Original reviewer objections to R workstreams

| Original theme | Workstreams |
| --- | --- |
| Parity correction does not belong to general order finding | R1 |
| Numerical period, encoding, cardinality and register-size inconsistencies | R2, R3, R4 |
| Inconsistent arithmetic costs and oracle/circuit models | R5, R6 |
| Classical baseline, antecedents and novelty positioning | R7, R8 |

## R1-R8: correction and present status

The manuscript evidence below refers to the authorized Post_M1 snapshot,
identified in [paper/README.md](../../paper/README.md), not live Overleaf.
It is not a new line-by-line scientific audit of the whole article.

| R | Required correction | Trace and evidence | Present status / remaining gate |
| --- | --- | --- | --- |
| R1 | Remove parity toggle and its claimed contribution; distinguish factoring from general order finding | Snapshot Results states the encoded period is ord(P) for either parity; Appendix C states no correction was used | Correction present in snapshot. Final integrated-text audit must prevent obsolete parity claims from returning |
| R2 | Replace artificial period 4 by the genuine period 5; do not skip identity rows or compress the scalar domain | R5 arithmetic implements kP including identity; Appendix C uses r=5; [coverage inventory](../audit/coverage.md) and saved-anchor replay document the tested paths | Corrected numerical model present. P4 confirms saved-data/model agreement, not exhaustive coverage of every adder input |
| R3 | Separate group order, point order and cofactor | Appendix C: #E(F29)=30 including identity, ord(P)=5, h=6 | Correction present. Field 29 remains an example, not a fixed algorithm parameter |
| R4 | Replace unsupported Q=16 validation by justified register sizing | Q=32 was an intermediate circuit check; current example uses Hasse bound B=40, m=11, Q=2048. P1-P3 freeze and evaluate unknown-order budgets | Register correction present. New F calibration still needs Overleaf integration; numerical crossings are not certified minima |
| R5 | Replace the lookup with coherent reversible curve arithmetic, with canonical encoding and cleanup | Snapshot Methods/Appendix A; migrated circuits; [migration](../audit/migration.md), [coverage](../audit/coverage.md); P4 anchors | Implementation and qualified coverage documented. M2 found antecedents for completeness: this is not an established new point-addition construction |
| R6 | Distinguish controlled addition from scalar evaluation, account for all m steps, recovery, admission and repetitions | Snapshot Results/Appendix B uses C_add(l)=O(l^6), quantum O(T*l^7), classical O(l^4+T*l^5). M1 adds admission without changing the stated bound. Legacy resource files exist | Analysis present, with implementation-specific conservative bounds. P3 calibrates finite T but does not replace asymptotics or supply a same-model literature resource benchmark |
| R7 | Compare separately with enumeration, generic methods, and point counting plus factorization/order reduction | Snapshot classical comparison; [M2 decision](m2_decision.md) explicitly declines speedup over SEA plus factoring | Comparison corrected in snapshot. Motivation sentence and final claim audit remain; no full classical timing benchmark was run |
| R8 | Establish what is contributed relative to Proos-Zalka, Roetteler and other antecedents, rather than merely adding citations | [novelty matrix](../audit/novelty_matrix.md), [P0 assessment](p0_f_assessment.md), [M2 decision](m2_decision.md), [P5 assessment](m2_f_p5_assessment.md) | Component-level novelty not established. Author/advisor accept verified integration plus policy-specific reliability characterization. Evidence reviewed; text integration and formal response closure pending |

## Why the mitigation plan was introduced

The later review exposed two distinct gaps: admission of a recovered multiple
for signing, and evidence supporting the contribution. Correcting R1-R7 did not
by itself establish novelty under R8. M1 addresses the first gap; M2 and the
selected evidence plan address the second. Supporting maintenance, independent
references and coverage documentation make these claims reproducible.

## Recovered eight-stage plan and current disposition

Author supplied the earlier "Plan Final" in chat on 2026-10-18, after the first
version of this index. It defines eight stages and explicitly names only M1
and M2. This corrects this index's earlier assumption that a missing M3
definition had to be recovered from that plan. No M3 is defined there.
References to M4-M6 in older reviewer feedback remain historical terminology,
not an authoritative parallel sequence to reconstruct by inference.

| Original stage | Relation to R / mitigation | Current disposition |
| --- | --- | --- |
| 1. Agree scope with advisor | Preserve manuscript; agree contribution and effort | Author reports advisor accepts verified integration plus characterization. A specific venue/deadline is not established by that acceptance |
| 2. Signing admission: M1 | R5/R6 and signing correctness | Code, tests and author-integrated Post_M1 text completed; m1-complete records the milestone. Miller-Rabin acceptance remains probable, not a primality certificate |
| 3. Novelty audit: M2 | R8/R7, including questionable references | Audit and decision completed; E framing adopted. Reference corrections and formal R8 response closure still wait for integrated text |
| 4. Exploratory diagnostics | R5 coverage, R6 resources and potential exception study | Coverage inventory and own resource counts exist. Exact exception counts by stage/union and complete-vs-incomplete degradation were not completed as the chosen main evidence. Scope narrowed after the decision; do not mark every originally proposed diagnostic done |
| 5. Decision | Select bounded evidence for R8 without rewriting the paper | Recorded in m2_decision.md: E framing, F evidence; A parked, B existing coverage, C/D outside selected scope |
| 6. Produce selected evidence | F supports R4/R5/R6/R8 with policy-specific reliability | P0 is the antecedent gate across stages 3/5; P1-P4 freeze, build, evaluate and check F. P5 assesses evidence and prepares transition to stage 7. Evidence reviewed; author commit pending at this status date |
| 7. Minimal manuscript integration | R1-R8 consistency, references, errata and reproducibility | P5 reviewed proposals prepared. Author integrates in Overleaf; a new authorized export is still needed for verification |
| 8. Final audit and response | Final closure of corrections and supported contribution | Pending integrated manuscript, evidence/claim check and point-by-point response. Publication/release decisions belong to the author |

### What changed, and what did not

The eight-stage workflow and the preservation rules still apply. The open
choice of contribution in stages 5/6 is now resolved: verified integration
with finite reliability characterization, not new point arithmetic or a
demonstrated quantum speedup. F was a later candidate, absent from the recovered
initial alternatives. Its evidence supports that explicit reframing; it does
not retroactively prove component-level novelty under the initial candidate
test. The accepted interpretation and venue risk are recorded in m2_decision.md.

The historical correction baseline remains ZIP (12) plus two paragraph-break
corrections. Post_M1 is the later authorized comparison snapshot, not a deletion
or silent replacement of the original baseline. Audit deadlines in the initial
plan were planning constraints, not evidence that a target venue was selected.

Older feedback associated M4 with expanded/exception-effect validation, M5
with same-tool resource comparisons and M6 with prose. The underlying work is
accounted for above and below without treating those informal associations as
the recovered plan's numbering. In particular, a same-model reference resource
benchmark has not been performed and F does not establish a resource advantage.

## Candidate decision and P0-P5

Decision record: [m2_decision.md](m2_decision.md). A (exception-impact experiment)
is parked; B uses existing coverage and the bounded shared-domain probe; C
(post-processing comparison) and D (circuit optimization) are outside the selected
revision. E is the adopted integration framing. F supports it with a finite-law
characterization of the implemented recovery/admission policy.

| Step | Purpose and R linkage | Evidence / state |
| --- | --- | --- |
| P0 | Check antecedents before claiming unknown-order reliability novelty; R8 | [Assessment](p0_f_assessment.md). Completed and reviewed; no first-uniform-budget claim |
| P1 | Freeze fields, all-integer order superset, Q choices, error targets, precision and anchors; R4/R8 | [Freeze](m2_f_p1_freeze.md), commit 8bb346b. Completed and reviewed |
| P2 | Implement and independently check the finite recovery law against production predicates; R4/R5/R8 | [Validation](../audit/m2_f_p2_validation.md), af324c6. Completed and reviewed; numerical-only main branch |
| P3 | Evaluate the frozen grid and unknown-order budgets; R4/R6/R8 | [Results](../audit/m2_f_p3_results.md), 84afc4c. 650 laws, 66 resolved numerical budgets; independently reproduced |
| P4 | Compare the law with five frozen saved circuit distributions and actual M1 admission; R5/R8 and M1 | [Anchors](../audit/m2_f_p4_anchors.md), 118d7e1. Reviewed; no new gate execution or extension of all-domain adder coverage |
| P5 | Assess allowed claims and prepare minimal manuscript integration; R6/R7/R8 | [Assessment](m2_f_p5_assessment.md). Independent review appended and package approved; author commit and Overleaf integration pending at this status date |

P3 example: for p=29, B=40, Q=2048, the minimum success probability over
integer r=2..40 crosses 0.99 at T=16 numerically (0.9867763896476266 at T=15;
0.9900892456126702 at T=16). The comparison 443/16 concerns our own conservative
sufficient rule, not Ekeraa's method, best classical methods or a measured
quantum advantage. These are offline small-field numerical results, not an
efficient cryptographic-scale calibration algorithm or interval certification.

## Explicitly not completed by F

- Complete-vs-incomplete exception degradation experiments and a same-tool
  resource baseline: not run under the adopted scope.
- Gcd/lcm/published post-processing comparisons, circuit optimization, noise,
  physical resource estimation and full classical timing benchmarks: not run.
- All-input adder validation for p=29: not claimed. Q=2048 scalar paths are not
  the adder's entire computational-basis domain; see the coverage inventory.
- Cryptographic security or suitability of the tiny example for real ECDSA:
  not implied by signing admission or a correct recovered order.
- Component priority, a new Shor algorithm, or superiority over prior art:
  not demonstrated by the accepted integration/characterization framing.

These exclusions are scope decisions or limits, not completed experiments.

## What remains before closing the revision

1. Author commits the reviewed P5 package and this consolidation; agents do
   not stage, commit, tag or push.
2. Author integrates the reviewed minimal blocks in Overleaf, preserving the
   title, structure, circuit and signature application; only changed text blue.
3. Resolve the audited references [27]/[28]/[30], remaining errata, simulation
   wording and data availability. Release/tag/DOI, author statements and
   anonymity are author/venue decisions. See [reference audit](../audit/references_audit.md).
4. Receive an authorized new Overleaf export and compare with Post_M1. Check
   R1-R8, M1, finite-budget versus asymptotic claims, numerical labels and
   coverage restrictions together; do not infer integration from proposals.
5. Complete the point-by-point reviewer response from the integrated text and
   evidence. R8 remains a supported contribution positioning with acknowledged
   acceptance risk, not a guaranteed novelty verdict.

No scientific code, locked dependency, manuscript source or signed reviewer
entry is changed by this consolidation. The P5 quick-suite result (132 passed,
105 slow deselected) is previously recorded evidence, not a new test run here.
