# M2 decision (plan stage 5): how the novelty objection is answered

Date: 2026-10-18. Status: FINAL decision of the author for this revision, taken
after the M2 audit, the F model, the P0 antecedent search and both reviewers'
assessments. The advisor is informed and may request changes at the stage-5
meeting; until then this record governs the work. Tag proposed for the commit
that records it: m2-decision.

## 1. Decision

1. R8 (novelty) is answered by positioning, not by a new component. The paper
   is presented as an explicit, verified integration of reversible point
   arithmetic, standard order finding, probabilistic recovery with primality
   admission and classical signing, together with an exact finite reliability
   characterization of the implemented recovery policy and correctly positioned
   antecedents (framing E).
2. F continues as the supporting evidence under the narrow claim fixed in
   p0_f_assessment.md: policy-specific finite reliability of the implemented
   all-verified-convergents gcd policy, with recovery and signing-admission
   outcomes separated, on bounded field sizes, with certified-or-labelled
   precision. Plan: m2_f_plan.md version 2, stages P1-P5, ten working days.
3. A (exception impact with a fair offset baseline) stays parked. B is used only
   as it already exists (coverage inventory, shared-domain probe). C and D are
   out. Any component-level novelty search is a separately authorized
   investigation outside this revision.
4. Motivation (why quantum order finding when SEA plus factoring is practical)
   is answered explicitly: the object of the paper is the correctness and
   reliability of the hybrid process and its reproducible validation, not a
   speedup over classical point-order methods. The paper will say so.

## 2. What the audit established (basis of the decision)

- Complete exceptional-case addition (Litinski 2023, Papa 2025, corrected
  Qualtran), compute/swap/uncompute (Proos-Zalka 4.3, Haener App. A.4),
  unknown-order finding (Proos-Zalka 2.2.2, Cheung-Mosca Cor. 8) and exception
  counting (Roetteler 4.2) all have antecedents; the seven-case shared-domain
  probe agrees with the corrected reference.
- Unknown-order guarantees, finite success laws and verified-candidate mass
  have antecedents (Shor, Ekeraa, Bourdon-Williams, Peng et al.,
  Magdon-Ismail-Dong, Yang-Markidis); the local sufficient bound was already
  uniform in the order.
- Verified but not relevance-weighted local differences: total encoding domain
  with flagged identity, gate-level exhaustive verification on small complete
  domains, and the three-way outcome law of the implemented gcd policy with its
  admission interface. These support framing E; none is claimed as a first.

## 3. Consequences for the manuscript (planning only; text at stage 7)

- Title, structure, circuit sections, cost analysis and signing application
  unchanged.
- Contributions (introduction and abstract, adjusted at the end): "explicit
  integration" and "complexity analysis" remain; the numerical validation item
  gains the exact reliability characterization once F2-F4 exist. No "first",
  "novel construction", "improvement over Ekeraa" or "rigorous" without
  certification.
- Discussion: positioning paragraph naming Litinski, Papa, Proos-Zalka 4.3,
  Roetteler 4.2, Ekeraa; the motivation sentence; limitations extended with the
  model assumptions (ideal independent executions, small fields, offline cost).
- Bibliography: replace [27], remove [28], reconsider [30]; add Litinski's
  validation (Papa) and Ekeraa with verified keys.
- Data availability: current repository and permutation-plus-FFT method.
- All fragments are prepared privately by the author with the second reader
  and integrated manually in Overleaf; blue marks only new text.

## 4. Gates kept

- P1 starts only after this record is committed and the advisor is informed.
- Precision: certified lower bounds for any guarantee wording, otherwise
  "numerically estimated".
- R8 closure wording is written at stage 8, after F2-F5 and the independent
  re-derivation, and states that the contribution is integration plus
  characterization.
- Negative outcomes of F are reported as results and do not reopen the
  component-novelty route inside this revision.

## 5. Accepted risk

The reviewer or the venue may judge integration plus characterization
insufficient. The author accepts this risk knowingly; the alternative would be
a new research project, not a revision. The venue decision is taken with the
advisor on this basis.

## 6. Next steps

1. Author: commit this record (and the P0 files), tag m2-decision, inform the
   advisor.
2. Author (Overleaf, independent of F): references [27], [28], [30], abstract
   typos, data availability.
3. Implementing agent and second reader: P1 configuration freeze, then P2-P5
   per m2_f_plan.md v2.
4. Stage 7 integration and snapshot; stage 8 audit and point-by-point response.

## 7. Approval

Author: final, 2026-10-18.
Second reviewer: P0 assessment and decision rule 2 (recorded).
Second reader (Claude): concurs (recorded in p0_f_assessment.md).
Advisor: author confirmed in this chat on 2026-10-18 that the advisor is
informed. This records notification, not additional endorsement. Changes,
if any, requested at the stage-5 meeting will be recorded here.
