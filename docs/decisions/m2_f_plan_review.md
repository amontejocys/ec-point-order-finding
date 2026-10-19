# Review of the proposed F plan

Date: 2026-10-18. Status: ADOPTED. The six adjustments were validated by the
second reader and merged into m2_f_plan.md version 2 the same day; this file is
kept as the record of the review. Original header follows.
Original status: PROPOSED adjustments for author discussion.
Requested by the author: document the review, then discuss it. This is not
approval of new runs, thresholds, manuscript claims or a revised research scope.
Read together with m2_f_plan.md; do not silently treat its pending wording as
a verified guarantee or novelty result. The six adjustments below are proposed,
not yet adopted. R8 remains open.

## Scope retained

F studies the existing hybrid point-order recovery and signing process. Preserve
the title, structure, circuit and signing application. The cost analysis remains
valid within its model, not a demonstrated advantage over best classical methods.
The candidate result is a finite budget uniform in the unknown point order for
the implemented recovery policy, on explicitly bounded parameter ranges.
Whether this is a sufficiently distinct contribution still needs evidence.

## Six adjustments before approving the main plan

| Item | Issue in current plan | Proposed resolution |
| --- | --- | --- |
| 1. Numerical guarantee | Narrative 3-4, reviewer-response paragraph and allowed claims use rigorous/guaranteed language while F1 only compares float64 to 50 digits | Choose either a numerically validated budget with explicit non-certification, or certified error bounds/intervals before asserting a rigorous threshold. High precision agreement alone is not a certificate. |
| 2. Recovery versus admission | F4 asks for an exact partition while general MR can falsely admit composites | Report recovery failure, exact order and nonminimal mass first. For signing, distinguish prime/composite true order, ideal-prime rejection categories and actual-policy false-pass bounds. Correct composite-order recovery does not imply signing admission. |
| 3. Offline scalability | Enumerating all orders <=B can sound like an efficient operational procedure at cryptographic sizes | Call it bounded offline precomputation, usable without knowing the actual r once the table is produced. Enumeration in B, with Q roughly B^2, is not polynomial in log p. Report construction cost separately and do not transfer savings in shots into a total-runtime claim. |
| 4. Antecedent gate | F3 places the decisive originality search after the main run | Move the targeted uniform-in-r budget audit to the first stage; record the precise difference and continue/reframe decision before the main evidence run. |
| 5. Comparator identity | 'Ekeraa-style lcm with small-factor search' may not implement the cited algorithm | Start with a documentary comparison of algorithms, assumptions, guarantee and work. A simplified comparator must have its own accurate name. A faithful Ekeraa implementation is optional scope requiring separate approval, not a mandatory three-day task. |
| 6. Effort and closure | Planned stages total 13 days although the cap says two working weeks; narrative anticipates closing novelty | Rebudget the core to ten working days, explicitly defer optional work and keep R8 conditional. Passing numerical tests or finding a smaller value than our loose bound does not close novelty. |

## Proposed order and effort

This replaces the ordering only if adopted. Day allocations are an effort
proposal, not calendar appointments or a promise of completion.

| Stage | Deliverable and decision gate | Working days |
| --- | --- | --- |
| P0 Antecedents and claim | Targeted review of uniform-in-r finite budgets and the actual recovery policy; distinguish standard techniques from a possible contribution; continue/reframe decision | 2 |
| P1 Freeze and precision | Approve ranges, metrics, tolerances and precision status; commit configuration before the main run; label existing ad hoc data as exploratory, not unseen confirmation | 1 |
| P2 Model hardening | Validate r-divisibility acceptance against production checks and reference group orders; rational/combinatorial tests; high-precision checks or the separately chosen certification approach | 2 |
| P3 Main evaluation | Finite worst-case-over-r tables with provenance, residuals, precision status and comparison against applicable bounds; reject unsupported claims | 2 |
| P4 Admission and circuit anchors | Separate admission outcomes and MR bound; evaluate saved real-circuit distributions at their documented coverage, with no new circuit runs | 1 |
| P5 Review and minimal proposals | Independent check, advisor decision and, only if warranted, bounded Overleaf proposals; R8 closure assessed explicitly | 2 |

Total core allocation: ten working days. If certified numerics cannot fit P2,
choose the numerical-only claim or explicitly approve added effort before work.
Optional full comparator implementation and expanded exhaustive circuit tests
are not in this allocation. A third week requires a named decision-changing
issue and explicit approval; do not absorb scope creep silently.

## Conditions the final design must satisfy

- All positive r from 2 through B form a conservative superset of realizable
  orders for the chosen field. Do not call every integer an admissible signing
  order or claim every worst-case r is attained by a curve. A maximum over the
  superset is safe for recovery under the model, but may be conservative.
- For arbitrary r in that range, define the analysis predicate r divides v and
  prove its equivalence to vP=O when r is the true point order. Do not fabricate
  a curve/point realizing each r or provide r to the production solver.
- Define a single field-level budget as the smallest T whose worst-case failure
  over the declared order set meets epsilon. Use certified lower success bounds
  if claiming a guarantee; otherwise label the threshold numerically estimated.
- Uniform recovery and prime-order signing need separate summaries. Restricting
  a study to prime r requires an explicit precondition; it cannot replace the
  general-order result silently.
- Compare the same r/Q/B, error target, postprocessing policy and quantum work
  where applicable. A known-r diagnostic and an unknown-r budget have different
  information assumptions. Different algorithms may require separate accounting.
- State that only ideal independent executions are modeled. Saved circuit
  anchors establish agreement only on their recorded instances/verification level.
- Retain production sources, dependencies and manuscript unchanged during this
  plan review. Only the author commits, selects Git identity and edits Overleaf.

## Adoption and novelty gate

Pending decisions: accept this revised ordering; choose numerical-only versus
certified budget claims; fix admissible effort with the advisor; approve the
main configuration. No new experiment is authorized by this review document.

Close R8 only after identifying the actual difference from prior work, supporting
its usefulness and reviewing the evidence. If the uniform-budget analysis is
already established or a routine specialization with insufficient added value,
record that outcome and discuss positioning; do not relabel it a new method.
