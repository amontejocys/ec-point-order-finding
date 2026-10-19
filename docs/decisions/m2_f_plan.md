# M2 decision: pursue F (finite reliability of order recovery) as the main evidence

Version 2, 2026-10-18. Status: AGREED between the author and both reviewers;
pending advisor approval. Version 1 (same date) was revised by merging the six
adjustments of m2_f_plan_review.md, which is now adopted. Supersedes the
recommendation section of m2_candidate_options.md. No experiment beyond the
frozen pilot has run; no manuscript text has been written. Until the advisor
approves, only stage P0 (antecedents and claim) may proceed.

## 1. Progress to date (what is established)

- M1 closed: order admission by primality before signing, 160 tests, Linux CI
  green, manuscript integrated and reviewer-checked, snapshot 2026-10-18, tag
  m1-complete.
- M2 audit: all five antecedents plus Papa and the corrected Qualtran reference
  inspected at source level with pinned revisions and hashes. Result: complete
  exceptional-case addition, compute/swap/uncompute, unknown-order finding and
  exception counting all have antecedents. Verified contract differences (total
  domain, flagged identity, gate-level verification) are not relevance-weighted
  and are not a contribution by themselves. R8 open.
- Shared-domain probe: seven cases agree between the local adder and the
  corrected reference at their respective verification depths.
- References: [27] unverifiable, [28] not pertinent, [30] weak; fixes pending in
  Overleaf.
- F model: offline finite law of the existing gcd recovery policy, validated
  against exact enumeration, divisor inversion and a production replay; pilot of
  seven rows; independently re-derived by the second reader. Observation: the law
  depends only on (r, Q, B), so enumerating all r <= B characterizes a field size
  completely. Exploratory (not confirmatory) ad hoc numbers: worst-case budgets
  of 13-16 shots for epsilon = 0.01 at p = 5..41 versus the published 295-443,
  in float64 without certification.

## 2. Decision

- Main evidence: F. The paper keeps its object (the hybrid order-recovery and
  signing process), its title, structure, cost analysis and signing application.
  Framing E (explicit integration plus characterization) is adopted for the
  discussion. The cost analysis remains valid within its model; it is not a
  demonstrated advantage over the best classical methods.
- Support: B only as far as it already exists (coverage inventory, shared-domain
  probe). No new exhaustive-domain run inside this plan.
- Parked: A (exception impact with a fair offset baseline). Out: C, D.
- Antecedents to position against, by name: Shor's original success bound,
  Ekeraa 2201.07791 (exact spectrum and stronger post-processing), Fernandez and
  Fernandez (gcd of random integers), standard divisor inversion. The decisive
  antecedent search (uniform-in-r finite budgets) is the first stage, not the last.

## 3. Narrative (storyline, not manuscript text)

1. The hybrid process recovers the order probabilistically and admits it for
   signing only when prime. The paper bounds the measurement budget with a
   conservative sufficient T that scales with log p (443 for p = 29).
2. Under ideal, independent executions the outcome of the implemented recovery
   policy has a finite law that depends only on the order r, the register size Q
   and the Hasse bound B. We state and prove the recurrence (Markov chain on the
   multiples of r, absorbing at r) and its independent divisor-inversion check.
   The analysis predicate "r divides v" is equivalent to vP = O when r is the
   true order of P; no curve or point is fabricated for an arbitrary r.
3. From the law we evaluate, for every T, the recovery outcomes P(exact order),
   P(no candidate) and P(nonminimal multiple). Admission for signing is reported
   separately: prime versus composite true order, ideal rejection categories and
   the actual-policy Miller-Rabin false-pass bound. A correctly recovered
   composite order is not an admitted signing order.
4. Because r is unknown but r <= B, the maximum failure over all integers
   2..B (a conservative superset of the realizable orders) defines a single
   field-level budget: the smallest T whose worst-case failure meets epsilon.
   This is a bounded offline precomputation for small fields: enumeration over
   r <= B with Q about B^2 is not polynomial in log p and does not replace the
   scalable published bound. On the studied fields it shows how conservative
   that bound is and which orders are hardest (even composites with many small
   factors, as phi(r)/r predicts).
5. The budget is reported either as certified (interval arithmetic lower bound
   on P_T(exact) >= 1 - epsilon) or, if certification does not fit the effort,
   explicitly as numerically estimated. High-precision agreement alone is not a
   certificate and is never described as one.
6. We compare, on the same (r, Q, B) and error target, with Shor's bound and,
   documentarily, with Ekeraa's analysis of a different post-processing, stating
   assumptions, guarantee form and work of each. We do not claim a better
   post-processing than Ekeraa.
7. Limits stated: ideal noiseless executions, independence, small fields,
   offline construction cost reported separately, numerical status declared,
   no hardware claim.

How this addresses the reviewer. R8: the candidate contribution becomes the
finite reliability characterization and a uniform-in-order budget for this
implemented policy on bounded parameter ranges, positioned against named
antecedents. Whether it is a sufficiently distinct contribution is decided at
the P0 gate and the P5 assessment; it is not assumed. Motivation: the object is
the correctness and reliability of the hybrid process, not a speedup over SEA
plus factoring, and the paper says so explicitly.

## 4. Claims allowed and forbidden

Allowed, if the runs and the P0 gate confirm them: "finite law of the
implemented policy under the stated model"; "field-level budget uniform over
all orders up to the Hasse bound, with guarantee 1 - epsilon over independent
ideal executions" (certified) or "numerically estimated budget" (uncertified);
"the published sufficient bound is conservative by a factor of about X on these
instances"; "recovery outcomes and signing-admission outcomes quantified, with
the Miller-Rabin false-pass bound kept separate".

Forbidden: "new post-processing", "improvement over Ekeraa", "rigorous" or
"exact" for float64 results, "efficient procedure" for the enumeration,
"secure domain", any statement about noise or hardware, any contribution
wording in abstract or introduction before stage 7, and closing R8 on the basis
of passing tests or of a smaller number than our own loose bound.

## 5. Work plan (ten working days, hard cap)

| Stage | Deliverable and decision gate | Acceptance criterion | Days |
| --- | --- | --- | --- |
| P0 Antecedents and claim | Targeted review of uniform-in-r finite budgets for order finding and of analyses of the actual recovery policy (Shor, Ekeraa, repetition/LCM literature); record the precise difference or its absence; continue/reframe decision with the author | Sources with section references in docs/references/; decision recorded in docs/decisions/ before any main run | 2 |
| P1 Freeze and precision | experiments/configs/m2_f_main.json: p in {5,7,11,13,17,19,23,29,31,37,41}, all r = 2..B, extra_bits in {0,1}, epsilon in {0.1,0.01,0.001}; metrics and tolerances; precision status chosen (certified via interval arithmetic, or numerical-only); existing ad hoc numbers labelled exploratory | Config committed before the main run; approvals recorded | 1 |
| P2 Model hardening | Validate the r-divisibility predicate against production verified_candidates and reference group orders on the realizable instances; rational/combinatorial tests retained; interval-arithmetic path (mpmath.iv) or, if it does not fit, the numerical-only label | Tests pass; certified or labelled status fixed for P3 | 2 |
| P3 Main evaluation | results/m2-f/: per (p, r, Q) law and T-shot outcomes; per p the worst r and the field-level budget per epsilon; comparison with the published sufficient T and the lower bound 1-(1-w_r)^T; residuals and precision status | Provenance (config, script, model hashes, environment); one-command reproduction; unsupported claims rejected | 2 |
| P4 Admission and circuit anchors | Separate admission summaries with the MR bound; law evaluated from the saved real-circuit distributions of the five validated instances at their documented coverage; no new circuit runs | Partition sums to one; agreement with the ideal law to 1e-10 on those instances | 1 |
| P5 Review and minimal proposals | Independent re-derivation of reported numbers; advisor decision; only if warranted, bounded private before/after fragments and one figure; explicit R8 assessment | Recorded in docs/decisions/ and docs/revision_log.md | 2 |

Optional, outside this allocation and requiring separate approval: a faithful
implementation of Ekeraa's post-processing as a frozen baseline; a simplified
comparator, if any, is named by what it is (for example "lcm-of-denominators
post-processing"), never as Ekeraa's algorithm; expanded exhaustive circuit
verification (B). A third week requires a named decision-changing issue.

Metrics (fixed now): per-shot acceptance w_r; P_T(exact), P_T(none),
P_T(nonminimal) up to the first T with P_T(exact) >= 1 - epsilon; worst case
over r in 2..B; ratio published T / field-level T; certified lower bounds or
float64 versus high-precision maximum absolute difference; admission masses
with the MR bound; offline construction cost (operations and wall time) per p.

Negative outcomes are results: if P0 finds an established uniform-in-r budget
or shows this is a routine specialization, F is repositioned as an application
and the positioning is discussed with the advisor; if certification does not
fit, the numerical-only label is used; if Ekeraa's framework dominates on the
compared quantities, that is stated.

## 6. Conditions the final design must satisfy (adopted from the review)

- All integers 2..B form a conservative superset of realizable orders; the
  maximum over the superset is safe for recovery under the model but may be
  conservative. Do not claim every worst-case r is attained by a curve or that
  every integer is an admissible signing order.
- The analysis predicate r | v is proven equivalent to vP = O for the true
  order; no r is passed to the production solver or to signing.
- One field-level budget definition; certified lower bounds for any guarantee
  wording, otherwise "numerically estimated".
- Uniform recovery and prime-order signing summarized separately; restricting
  to prime r is an explicit precondition, never a silent replacement.
- Comparisons share r, Q, B, error target, policy and quantum work where
  applicable; known-r diagnostics and unknown-r budgets are not mixed.
- Only ideal independent executions are modelled; circuit anchors hold only on
  their recorded instances and verification level.
- Production sources, dependencies and manuscript unchanged during the plan;
  only the author commits, selects the Git identity and edits Overleaf.

## 7. Roles

- Author: approvals, Overleaf edits, commits and tags, advisor meeting.
- Implementing agent: P1-P4 code, runs and provenance records; P0 search shared.
- Second reader (Claude): P0 antecedent check, independent re-derivation of
  every reported number, review of P5 fragments, hygiene before each commit.

## 8. Risks

- Antecedent risk (main): a uniform-in-r finite budget may already exist;
  mitigated by placing the search first.
- Scope creep: no new circuit runs, no Qualtran benchmarking, no noise, no
  faithful comparator without separate approval.
- Precision: certification may not fit two days; fallback is the explicit
  numerical-only label.
- Effort: ten working days hard cap.

## 9. Approval

Author: selected F and accepted the six adjustments, 2026-10-18; final decision
recorded in m2_decision.md the same day (F continues as supporting evidence under
the narrow claim; R8 answered by framing E).
Second reviewer: adjustments proposed and adopted, 2026-10-18.
Second reader (Claude): validated the six adjustments and merged them, 2026-10-18.
Advisor: to be informed at the stage-5 meeting. P0 is complete; P1 may start once
m2_decision.md is committed.
