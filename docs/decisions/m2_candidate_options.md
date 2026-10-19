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

## Recommendation for the advisor meeting

The original recommendation of A as the main claim is not adopted. A and B
remain possible evidence about the hybrid process, subject to a defensible
difference and relevance. They do not replace the paper's object. Keep C and D
as alternatives rather than declaring them impossible without evidence. Decide
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

## Approval

Advisor: pending. Author: pending. No experiment is started by this record.
