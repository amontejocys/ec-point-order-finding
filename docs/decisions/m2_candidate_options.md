# M2: candidate evaluation for the novelty claim

Date: 2026-10-18. Status: PROPOSED, pending advisor decision (plan stage 5).
Owner approval required before any main evidence run. This record evaluates the
four pre-agreed candidates against the three pre-fixed conditions:
(1) identifiable difference from the checked antecedents, (2) checkable with our
means, (3) technical relevance supported by measurement or formal guarantee.
Evidence base: docs/audit/novelty_matrix.md, docs/references/m2_source_notes.md.
No threshold or metric below is final; they are proposals to be fixed with the
advisor before the run, as docs/decisions/README.md requires.

## Author clarification and source-audit update (2026-10-18)

The author confirmed that the paper remains about the existing hybrid process,
its cost analysis and a specific contribution to be identified and demonstrated.
It is not redirected to a standalone exception study and does not require a
general advantage over the best classical point-order algorithms. Preserve the
title, structure and signing application; editorial changes stay conditional.

The alternatives below are hypotheses, not approved contributions. In particular,
'no antecedent' and 'condition 1: met' in the original assessment are provisional,
not established priority. Software inspection now confirms reference order-two
tests and a second tested curve: see docs/audit/m2_contract_comparison.md.
Its pinned revision and coverage supersede simplified paper-only comparisons.
Estimated feasibility/runtime below is unbenchmarked, not a measured result.

## Alternatives

### A. Exception impact in unknown-order finding (candidate: reversible completeness)

- Difference. Proos-Zalka 4.2 and Roetteler et al. 4.2 justify generic-only
  addition for ECDLP with a known large prime order (loss about 4 log q / q,
  invalid-scalar fraction about n/2^n). Our setting differs: the accumulator
  starts at O, the order is unknown and may be small or composite, and the first
  addition O + P is exceptional for every odd scalar. A quantitative difference
  specific to this setting remains a hypothesis; absence from the inspected
  passages does not establish novelty. Condition 1: not yet established.
- Check. Build the generic-only baseline as a real reversible circuit from the
  same arithmetic blocks (src/quantum_ec/baselines/, frozen for the comparison;
  equivalent initialization accounted for, as the technical notes require).
  Propagate both circuits on the five validated instances (p = 5, 7, 7, 11, 29)
  and on sampled instances; compute exact output distributions by permutation +
  FFT, grouping by the complete register content including ancillas; compare
  recovery rates by shot budget; relate the measured difference to delta = |S|/Q
  and the bound sqrt(2 delta - delta^2). Condition 2: plausible with existing
  tooling; actual reference construction and runtime remain to be checked.
- Relevance. Measured, if the degradation at small or composite orders is
  material and the exact exception count per stage explains it. Must state
  honestly that at cryptographic sizes with prime order the fraction is again
  negligible; the relevance is correctness of the method across all instances
  and validity of small-instance experiments. Condition 3: to be measured.
- Also addresses the motivation observation partially: the object of study is
  the hybrid pipeline's correctness, not a speedup over SEA plus factoring.
- Effort: one to two weeks. Negative outcome (no material difference) is
  reportable as a limitation statement and closes the candidate; this is not
  a publication prediction.

### B. Verified artifact over the complete encoding domain (candidate: verified artifact)

- Difference. Our H_A is total on all 2^(2l+1) encodings with clean ancillas;
  current exhaustive coverage is width 3 complete and 34 encodings of p = 29 for
  one constant. The paper's selected-point description must be distinguished
  from the pinned software's tests, including a second curve and order-two
  inputs. A coverage difference is not an algorithmic advance. Condition 1:
  requires a common-domain, common-verification-depth comparison.
- Check. Bit-sliced basis propagation (each wire a big-integer mask over all
  4096 (control, encoding) pairs; one pass per gate) makes all 2048 encodings x
  2 controls x 4 adders of p = 29 a possible acceleration, with runtime unmeasured.
  Cross-check: run the
  Qualtran ECC bloqs (Papa, PRs 1489/1666) classically on the same small curve
  and record their domain and coverage. Condition 2: implementation feasibility
  remains to be verified in an isolated environment.
- Relevance. Positioning as a reproducible, exhaustively verified small-instance
  artifact. Supports A; alone it is not a novelty claim. Condition 3: partial.
- Effort: about one week.

### C. Post-processing comparison (candidate: gcd vs lcm vs Ekeraa)

- Difference and check exist (1000-instance pilot, saved samples), but Ekeraa's
  lattice post-processing is far stronger and the result would be incremental.
  Not recommended as the main claim.

### D. Circuit optimization (modular inversion bottleneck)

- Would reproduce Litinski/Haener-style or Luo et al. inversion circuits; no
  identifiable advance is in reach. Not recommended.

### F. Finite reliability characterization of order recovery (author proposal, 2026-10-18)

Author authorized developing/evaluating the model on 2026-10-18. Formalization,
the five qualifications, source comparison and bounded validation are in
docs/audit/m2_f_reliability_model.md. Exact finite formulas do not imply exact
floating-point arithmetic. Research novelty and manuscript integration remain
unapproved; the underlying techniques are standard.

- Question. For curves and points across parameter ranges (p, r prime or
  composite, r size, register size m, budget T), what is the probability that
  the pipeline returns the correct order, and how does M1 admission change the
  outcome? Measured by simulation and compared with theory.
- What exists. The 1000-instance pilot (results/expanded-pilot) estimates
  exact-order rates by sampling 100 trials per instance from the ideal
  distribution (T=1: 0.59; T=4: 0.93; T=16: 0.9995), with Wilson intervals.
  The finite bound 1/(16 nu_B) and T=443 for p=29 exist (success_budget.py).
  The real-circuit distribution equals the ideal one on the five validated
  instances, so ideal postprocessing is justified there and stated as such.
- Potential evidence, not established novelty. (i) Finite probabilities instead of sampling: per shot,
  P(accept r), P(any candidate); over T shots, the exact law of the gcd
  accumulator by a Markov chain on the multiples of r up to B, giving
  P(exact), P(no candidate), P(nonminimal) without Monte Carlo error.
  (ii) Comparison of the exact values with the conservative bound, which is
  loose by a large factor (p=29, r=5, Q=2048: exact per-shot probability of
  accepting r is 0.798, versus the bound 0.0104; the exact T-shot law gives
  P(exact) = 0.959, 0.998 and 0.9997 for T = 2, 4, 5). (iii) Parameter dependence: r, primality of r, p, m above the
  minimum, T. (iv) Admission outcomes: P(admitted and correct), P(rejected:
  composite true order), P(rejected: nonminimal), P(recovery failure).
- Conditions. Difference: exact finite analysis of gcd accumulation plus
  primality admission for EC point order finding; no antecedent found for this
  specific pipeline, but Shor-type success analyses and Ekeraa's post-processing
  theory are the antecedents and must be cited; this is characterization of the
  paper's object, not a new algorithm. Check: existing tooling suffices
  (ideal_distribution, verified_candidates, gcd chain); exact enumeration of all
  y for p up to about 41 is cheap, larger p sampled or vectorized. Relevance:
  direct, it quantifies the reliability the paper claims and supports the
  measurement-budget discussion; it also documents how conservative the
  published bound is.
- Fit. Compatible with the existing hybrid process and title; any eventual text goes into the probabilistic
  recovery subsection, the appendix and one figure. Effort: one to two weeks.
- Caveats. Noiseless ideal distribution; results for small fields; the exact
  Markov analysis assumes independent ideal shots.
- Second reader (2026-10-18): model verified independently. Because the law
  depends only on (r, Q, B), enumerating all r <= B per field size yields an exact
  worst-case unknown-order budget: 13-16 shots for epsilon = 0.01 at p = 5..41
  versus the published 295-443 (ad hoc numbers in docs/audit/m2_f_reliability_model.md,
  to be frozen in a run). This is the precise, useful result F should target.

## Recommendation for the advisor meeting

The original recommendation of A as the main claim is not adopted. A and B
remain possible evidence about the hybrid process, subject to a defensible
difference and relevance. They do not replace the paper's object. Keep C and D
as alternatives rather than declaring them impossible without evidence. F,
proposed by the author, characterizes the pipeline's reliability exactly and is
the evidence most directly aligned with the paper's object and title; it can be
combined with B at low cost. Decide
the target venue and admissible effort with the advisor before the main run.

## Manuscript impact if A+B are chosen (planning only)

Title, keywords, circuit sections, theorem, complexity tables and the signing
application stay as they are. Changes are additions or one-sentence edits in:
abstract (final sentence), introduction (contribution item 1 and the
methodological paragraph), methods (one paragraph defining the generic-only
baseline inside the reversible-evaluation subsection), results (one new
subsubsection before the complexity analysis, plus one sentence in the
reproducibility regime), discussion (positioning sentences and limitations),
concluding remarks (one sentence), appendix (coverage numbers in the code
correspondence subsection and measured values in the worked instance) and data
availability (repository and simulation method, needed regardless of A/B).
Text goes in only after the measurements exist; the author keeps the detailed
anchor map and draft fragments in private notes. Blue marks only the new text.

## Acceptance criteria to fix before the run (proposals)

- Metrics: total-variation distance between complete and generic output
  distributions; exact-order recovery rate per budget T in {1,2,4,8,16,32,64};
  exact exception count per stage and in union (delta).
- Instances: the five validated instances plus a sampled set from the existing
  pilot with small prime, composite and even orders; parameter ranges recorded in
  experiments/configs/ before inspecting results.
- Reference versions: baseline frozen by hash in baselines/; Qualtran revision
  pinned if B runs.
- Negative outcome handling: report the measured difference whatever its size;
  if it is immaterial, record the candidate as closed and keep the limitation text.
- Effort budget: two weeks for A, one for B; a third week only for a named issue.

## Final status (2026-10-18)

See m2_decision.md: framing E answers R8 by positioning; F continues as
supporting characterization under the narrow claim; A parked; B as existing;
C and D out.

## Status update (2026-10-18, later)

The author selected F as the main evidence; plan, narrative, allowed claims,
stages, acceptance criteria and roles are in docs/decisions/m2_f_plan.md,
pending second-reviewer check and advisor approval.

## Approval

Advisor: pending. Author authorized the F model and bounded evaluation, not
final contribution claims or a manuscript rewrite. A/B main runs remain pending.
