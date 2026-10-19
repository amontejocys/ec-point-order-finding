# P0 assessment: candidate F after the antecedent search

Date: 2026-10-18. Status: bounded documentary pass completed; independent
reader concurred; the author's final decision is recorded in m2_decision.md
(decision rule 2: F continues as characterization under the narrow claim; R8
answered by framing E). P1 is authorized by that record, not by this note.
Source evidence: `docs/references/p0_uniform_budget_sources.md`.
Plan: `docs/decisions/m2_f_plan.md`, version 2.

## Finding

Uniformity in an unknown order r is not, by itself, a new contribution.
Shor and subsequent work already provide success/repetition guarantees without
requiring the true order as an operational input. Ekerå provides a much stronger
post-processing analysis. Finite probability laws and comparisons between
conservative bounds and concrete behavior also have antecedents.

The repository's existing conservative sufficient budget is itself uniform
over the supported orders. Candidate F therefore cannot be described as the
first way to choose a budget without knowing r. Nor does taking a maximum over
a finite set of orders constitute a new quantum algorithm.

The remaining candidate is narrower: a reproducible finite reliability
characterization of the *implemented* all-convergents, verified-denominator gcd
policy, with bounded-field calibration and separate signing admission. No
identical combined analysis was found in the inspected passages, but neither
priority nor sufficient scientific novelty has been established. In particular,
gcd distributions, Markov recurrences and divisor inversion are standard tools.

## Gate assessment against the agreed criteria

| Criterion | P0 result | What remains |
| --- | --- | --- |
| Identifiable difference | Policy differs from the inspected lcm, smooth-completion and verified-mass argmax procedures | Decide whether analyzing this existing policy is technically important, rather than merely a different choice |
| Checkable with local means | The frozen seven-row pilot checks the law and its production-policy correspondence | Existing numerical agreement is not interval certification; the main sweep has not run |
| Technical relevance backed by evidence | Exploratory gap against our own conservative bound motivates calibration | No demonstrated improvement over prior recovery methods, scalable advantage, or signed-domain security; R8 remains open |

## Recommendation for the author/advisor decision

Continue only with the narrow policy-characterization claim if the advisor
accepts that as a worthwhile contribution to the existing hybrid paper. Preserve
the title, paper object, circuit and signature integration. Do not silently
replace the original novelty objective with a claim about the first uniform
budget or with a claim of superiority to Ekerå.

The decision is not "novelty proved". It is a conditional continuation with an
explicit risk: the eventual result may be a useful reproducibility/calibration
artifact rather than a sufficient answer to the original novelty objection.
If that is insufficient for the agreed objective, stop before the main sweep
and choose a separately authorized investigation; do not expand scope here.

Before approving P1, the author and independent reader should confirm:

1. The target claim is policy-specific reliability, not novelty of uniformity,
   gcd combination or finite probability formulas alone.
2. Comparisons distinguish exact order from a useful frequency, divisor,
   annihilating multiple and factoring success; the classical work is stated.
3. Precision is either interval-certified or explicitly numerical. A sufficient
   certified T is not a certified minimum unless some order fails at T - 1.
4. The all-r sweep is a small-field offline calculation over a conservative
   superset, not efficient cryptographic-scale preprocessing. Composite-order
   recovery and prime-order signing admission are reported separately.
5. Remaining direct-source checks (Knill and general gcd-distribution results)
   are resolved or disclosed before any priority wording is proposed. Advisor
   approval, frozen parameters and a time limit are still required for P1-P5.

## Operational review: correctness and novelty are separate

Review two questions independently: is the analysis correct, and does it offer
something not supplied by the antecedents? The pilot supports the first within
its tested scope; it does not settle the second. P0 is an initial assessment,
not a conclusion that F has no value.

The author and independent reader should review the decisive source-matrix
rows using these four questions:

| Review question | Required check |
| --- | --- |
| Is the success event the same? | Exact-order recovery, not merely a useful frequency, a divisor, an annihilating multiple or factoring success |
| What actually differs? | Selection of all verified convergents and their gcd accumulation versus the published policies, including their classical work |
| Has that difference been studied? | Search for the actual policy and its analysis, not just the phrase uniform budget; resolve or disclose the outstanding source checks |
| Why does the difference matter? | Identify an additional capability, guarantee or measurable effect, rather than only a tighter evaluation of our own bound |

### Candidate statement for investigation, not for the manuscript

The reliability characterization of the implemented policy permits selection
of measurement budgets with controlled failure, distinguishing exact recovery,
no candidate and nonminimal multiples, without using the true order as an
operational input.

This defines a research target, not an established new result. Controlled
failure requires the declared numerical/certification status. Finite laws and
budget selection have antecedents; the missing question is what additional
capability this particular treatment supplies. Offline analysis may enumerate
r even though operational recovery must not receive it.

### Evidence worksheet

Complete this worksheet before proposing the main experiment. Record negative
findings as well as positive ones; do not choose the claim after seeing data.

| Field | Current candidate / evidence needed |
| --- | --- |
| Candidate claim | Policy-specific finite reliability and bounded-field budget calibration, with recovery and admission separated |
| Closest antecedent | Ekerå for exact-order success guarantees; Yang-Markidis for verified-candidate mass; other matrix rows for finite spectra and uniform bounds. Compare the relevant claim separately rather than selecting one convenient baseline |
| Concrete difference | The complete all-convergents, verified-denominator gcd policy and its T-shot outcome law; absence of an identical inspected analysis is not proof of priority |
| Evidence needed | Source-supported distinction, correspondence to the production policy, declared precision, and a technically relevant guarantee or measured effect |
| Fair comparison | Our existing sufficient bound, evaluation of our actual policy, and a pertinent published reference with success event, Q, B, error target and classical work made explicit |
| Possible confirmation | A previously unestablished policy-specific guarantee, a demonstrated parameter/failure relationship, or a favorable measurement/classical-work tradeoff. None is established yet; superior performance is not the only possible contribution |
| Possible disconfirmation | The same result is already covered, the difference has no supported technical consequence, or the result only recalibrates a loose local bound |
| Decision and approval | Pending author/independent-reader assessment and advisor approval; R8 remains open |

A result such as 16 executions versus 443 would quantify conservatism in our
own sufficient bound. It would not establish superiority to the literature.
Published bounds for a different event cannot be ranked as if they were budgets
for this policy. A faithful implemented comparator would need separate scope
approval; this worksheet does not authorize one.

### Decision rule

1. A source-supported difference with a relevant, backed consequence is a
   candidate incremental contribution, subject to independent/advisor review.
2. A correct analysis without an identified additional capability may be a
   useful reproducibility/calibration artifact, but is not sufficient novelty
   by itself.
3. If prior work already covers the result, F does not resolve the novelty
   objection. Any additional investigation requires an explicit, bounded
   decision rather than an automatic expansion of the paper.

The immediate next step is to review the decisive matrix rows and complete one
claim/antecedent/difference/evidence/decision record. Do not edit the paper or
launch the full experiment battery before that gate is resolved. This preserves
the manuscript while testing whether the candidate contribution is defensible.

## Consequences for the current plan

- P0 documentary output is available for review; its decision gate is not closed.
- Keep F plan v2 unchanged as the agreed baseline. This assessment qualifies
  its candidate contribution; it is not an adopted plan v3.
- P1 through P5 remain pending advisor approval. No new configuration freeze,
  main simulation, arithmetic implementation or manuscript edit is authorized
  by this audit.
- Exploratory 13-16-shot figures remain numerical pilot observations. They
  neither certify worst-case minimal budgets nor establish superiority to the
  literature. No new numbers were produced during P0.
- R8 and the motivation objection remain open. Reliability calibration does
  not establish an advantage over SEA plus factorization/classical reduction.

## Work performed

Read-only checks of the current plan, recovery-policy description and source
papers; documentary matrix and this recommendation. No code, results, circuit,
dependency, manuscript, commit or tag changed. Tests were not rerun because this
change is documentation-only. Only Ariel may create the next commit.

## Independent reader position (Claude, 2026-10-18)

I concur with the P0 finding and with decision rule 2 as the current state:
F is a correct, reproducible characterization of the implemented policy, and it
does not by itself resolve the novelty objection. Specific points:

1. Uniformity in r and finite laws are established (Shor, Ekeraa, Bourdon and
   Williams, Magdon-Ismail and Dong). Our own sufficient bound was already
   uniform. The 13-16 versus 295-443 comparison measures the looseness of our
   bound, nothing more, and must be worded that way if it is ever reported.
2. The only policy-specific element without an inspected antecedent is the
   three-way outcome law of the all-verified-convergents gcd policy together
   with the primality admission interface (composite true orders recovered but
   rejected; nonminimal multiples rejected). This is characterization of our
   pipeline, not a general capability; its value is for the paper's own claims
   about reliability and for reproducibility, and it fits framing E.
3. The honest route to the reviewer's objection is therefore E: present the
   paper as an explicit, verified integration with an exact reliability
   characterization and correctly positioned antecedents, and let the venue
   decision follow. If the advisor requires component-level novelty, that is a
   separately authorized investigation outside this revision's scope
   (mandatory corrections versus additional research, per the project rules).
4. Recommended gate outcome: proceed with P1-P5 only under the narrow
   characterization claim and the E framing, with the certification-or-label
   rule, and with the explicit statement in the decision record that R8 is
   answered by positioning, not by a new component. If the advisor rejects E,
   stop F before P1.
