# M2: candidate evaluation for the novelty claim

Date: 2026-10-18. Status: PROPOSED, pending advisor decision (plan stage 5).
Owner approval required before any main evidence run. This record evaluates the
four pre-agreed candidates against the three pre-fixed conditions:
(1) identifiable difference from the checked antecedents, (2) checkable with our
means, (3) technical relevance supported by measurement or formal guarantee.
Evidence base: docs/audit/novelty_matrix.md, docs/references/m2_source_notes.md.
No threshold or metric below is final; they are proposals to be fixed with the
advisor before the run, as docs/decisions/README.md requires.

## Alternatives

### A. Exception impact in unknown-order finding (candidate: reversible completeness)

- Difference. Proos-Zalka 4.2 and Roetteler et al. 4.2 justify generic-only
  addition for ECDLP with a known large prime order (loss about 4 log q / q,
  invalid-scalar fraction about n/2^n). Our setting differs: the accumulator
  starts at O, the order is unknown and may be small or composite, and the first
  addition O + P is exceptional for every odd scalar. No antecedent quantifies the
  effect of generic-only addition in this setting. Condition 1: met.
- Check. Build the generic-only baseline as a real reversible circuit from the
  same arithmetic blocks (src/quantum_ec/baselines/, frozen for the comparison;
  equivalent initialization accounted for, as the technical notes require).
  Propagate both circuits on the five validated instances (p = 5, 7, 7, 11, 29)
  and on sampled instances; compute exact output distributions by permutation +
  FFT, grouping by the complete register content including ancillas; compare
  recovery rates by shot budget; relate the measured difference to delta = |S|/Q
  and the bound sqrt(2 delta - delta^2). Condition 2: met with existing tooling.
- Relevance. Measured, if the degradation at small or composite orders is
  material and the exact exception count per stage explains it. Must state
  honestly that at cryptographic sizes with prime order the fraction is again
  negligible; the relevance is correctness of the method across all instances
  and validity of small-instance experiments. Condition 3: to be measured.
- Also addresses the motivation observation partially: the object of study is
  the hybrid pipeline's correctness, not a speedup over SEA plus factoring.
- Effort: one to two weeks. Negative outcome (no material difference) is
  publishable as a limitation statement and closes the candidate.

### B. Verified artifact over the complete encoding domain (candidate: verified artifact)

- Difference. Our H_A is total on all 2^(2l+1) encodings with clean ancillas;
  current exhaustive coverage is width 3 complete and 34 encodings of p = 29 for
  one constant. Papa tests 12 selected points; Long et al. test random inputs and
  say so; Polimeni-Seidel use sparse-simulator checks. Condition 1: met as a
  verification-coverage difference, not an algorithmic one.
- Check. Bit-sliced basis propagation (each wire a big-integer mask over all
  4096 (control, encoding) pairs; one pass per gate) makes all 2048 encodings x
  2 controls x 4 adders of p = 29 feasible in minutes. Cross-check: run the
  Qualtran ECC bloqs (Papa, PRs 1489/1666) classically on the same small curve
  and record their domain and coverage. Condition 2: met.
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

Main claim: A. Supporting evidence: B. Keep C and D out of scope. Decide the
target venue and the role of the signing application at the same meeting, since
A reframes the paper around correctness of order finding with unknown order
rather than around the signing example.

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
