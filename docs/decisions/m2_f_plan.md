# M2 decision: pursue F (finite reliability of order recovery) as the main evidence

Date: 2026-10-18. Status: PROPOSED by the author; pending second-reviewer check
and advisor approval. Supersedes the recommendation section of
m2_candidate_options.md once approved. No experiment beyond the frozen pilot has
run; no manuscript text has been written.

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
  completely. Ad hoc worst-case budgets: 13-16 shots for epsilon = 0.01 at
  p = 5..41 versus the published 295-443.

## 2. Decision

- Main evidence: F. The paper keeps its object (the hybrid order-recovery and
  signing process), its title, structure and signing application. Framing E
  (explicit integration plus characterization) is adopted for the discussion.
- Support: B only as far as it already exists (coverage inventory, shared-domain
  probe). No new exhaustive-domain run unless time remains after F.
- Parked: A (exception impact with a fair offset baseline). Out: C, D.
- Antecedents to position against, by name: Shor's original success bound,
  Ekeraa 2201.07791 (exact spectrum and stronger post-processing), Fernandez and
  Fernandez (gcd of random integers), standard divisor inversion.

## 3. Narrative (storyline, not manuscript text)

1. The hybrid process recovers the order probabilistically and admits it for
   signing only when prime. The paper so far bounds the measurement budget with
   a conservative sufficient T (443 for p = 29).
2. Under ideal, independent executions the outcome of the recovery policy has a
   finite law that depends only on the order r, the register size Q and the
   Hasse bound B. We state and prove the recurrence (Markov chain on multiples
   of r, absorbing at r) and its independent divisor-inversion check.
3. From the law we obtain, exactly up to float64 and cross-checked at high
   precision: per-shot acceptance, P(exact order), P(no candidate) and
   P(nonminimal multiple) for every T, and the admission outcomes.
4. Because r is unknown but r <= B, taking the worst case over all r <= B gives
   an operational budget with the same guarantee form as the published bound
   (success >= 1 - epsilon over independent ideal shots) and one order of
   magnitude fewer shots. The hardest orders are even composites with many
   small factors, as phi(r)/r predicts.
5. We compare, on the same instances, with Shor's bound and with Ekeraa's
   analysis of a different post-processing, and state what the comparison does
   and does not show. We do not claim a better post-processing than Ekeraa.
6. Limits stated: ideal noiseless executions, independence, small fields,
   float64 evaluation with a high-precision cross-check, no hardware claim.

How this answers the reviewer. R8: the specific contribution becomes the exact
finite reliability characterization and rigorous unknown-order budget of this
pipeline, positioned against named antecedents, instead of an unsupported
"first complete construction". Motivation: the object is the correctness and
reliability of the hybrid process, not a speedup over SEA plus factoring; the
paper says so explicitly.

## 4. Claims allowed and forbidden

Allowed, if the runs confirm them: "exact finite law of the implemented policy";
"worst-case budget over all admissible orders with guarantee 1 - epsilon under
the stated model"; "the published sufficient bound is conservative by a factor
of about X on these instances"; "admission outcomes quantified exactly, with the
Miller-Rabin false-pass bound kept separate".

Forbidden: "new post-processing", "improvement over Ekeraa", "exact" without the
float caveat, "secure domain", any statement about noise or hardware, any
contribution wording in abstract or introduction before stage 7.

## 5. Work plan (two weeks, bounded)

| Stage | Deliverable | Acceptance criterion | Days |
| --- | --- | --- | --- |
| F0 Freeze | experiments/configs/m2_f_main.json: field sizes p in {5,7,11,13,17,19,23,29,31,37,41}, all r = 2..B per p, extra_bits in {0,1}, epsilon in {0.1,0.01,0.001}, budgets up to the first T meeting each epsilon; metrics listed below | Config committed before any main run; approvals recorded | 1 |
| F1 Model hardening | Law model with an optional high-precision path (mpmath, already installed) for p_y and the recurrence; exact-rational tests retained | float64 and 50-digit results agree to 1e-12 on the pilot; tests pass | 2 |
| F2 Main run | results/m2-f/: per (p, r, Q) law and T-shot outcomes; per p the worst r, worst-case T for each epsilon, comparison with the published sufficient T and with the lower bound 1-(1-w_r)^T | Provenance (config, script, model hashes, environment); every table reproducible by one command | 2 |
| F3 Antecedent comparison | Baseline in src/quantum_ec/baselines/: Shor-style bound per instance and a bounded implementation of Ekeraa-style lcm post-processing with small-factor search, frozen by hash; same instances | Both reported with their assumptions; no superiority claim unless measured; antecedent search for worst-case-over-r budgets recorded | 3 |
| F4 Admission layer | Exact admitted-correct, rejected-composite, rejected-nonminimal and recovery-failure masses per instance; aggregated false-pass bound | Partition sums to one; bound reported separately | 1 |
| F5 Anchoring to the circuit | Law evaluated from the saved real-circuit distributions of the five validated instances (results/legacy raw NPZ) versus the ideal law | Agreement to 1e-10; documents that the model describes the real arithmetic there | 1 |
| F6 Write-up proposals | Private before/after fragments for the probabilistic-recovery subsection, measurement-budget discussion, appendix and one figure (P(exact) versus T for the worst r and for p = 29; budgets versus published) | Reviewed by the second reader; blue only on new text | 2 |
| F7 Gates | Second-reviewer check of F2-F5; advisor approval; then stage 7 (Overleaf by the author, snapshot, references fix) and tag m2-decision | Recorded in docs/decisions/ and docs/revision_log.md | 1 |

Metrics (fixed now): per-shot acceptance w_r; P_T(exact), P_T(none),
P_T(nonminimal) for T up to the first T with P_T(exact) >= 1 - epsilon; worst
case over r <= B; ratio published T / exact worst-case T; float64 versus
high-precision maximum absolute difference; admission masses.

Negative outcomes are reported as results: if an antecedent already gives a
uniform-in-r budget of this kind, F is repositioned as an application of it; if
Ekeraa's post-processing dominates on these instances, that is stated; if the
high-precision check disagrees with float64 beyond 1e-12, the affected rows are
reported at high precision only.

## 6. Roles

- Author: approvals, Overleaf edits, commits and tags, advisor meeting.
- Implementing agent: F0-F5 code, runs and provenance records.
- Second reader (Claude): independent re-derivation of every reported number,
  antecedent check, review of F6 fragments, hygiene before each commit.

## 7. Risks

- Antecedent risk: a uniform-in-r exact budget may already exist in the
  order-finding literature (Ekeraa's bounds are in part uniform). Mitigation:
  antecedent search in F3 before any claim wording.
- Scope creep: no new circuit runs, no Qualtran benchmarking, no noise.
- Precision: float64 only; mitigated by the mpmath cross-check.
- Effort: two weeks hard cap; a third only for a named decision-changing issue.

## 8. Approval

Author: selected F on 2026-10-18 (pending confirmation after the second-reviewer
check). Second reviewer: pending. Advisor: pending. Until both are recorded,
only F0 (configuration freeze) may proceed.
