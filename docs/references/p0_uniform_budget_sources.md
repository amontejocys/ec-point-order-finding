# P0: antecedents for unknown-order reliability budgets

Date: 2026-10-18. Documentary audit only. Source inspection, not execution of
external implementations. This is a bounded search, not a proof of priority.
Read together with `docs/decisions/p0_f_assessment.md` and the F plan v2.

## Comparison object

The local policy processes every continued-fraction convergent denominator
v <= B, retains those satisfying vP = O, and accumulates their gcd across
independent measurements. Its success event is g_T = ord(P), not obtaining a
divisor of the order, a useful frequency, a factorization, or signing admission.
An empty candidate set contributes zero, with gcd(g, 0) = g.

For analysis only, the predicate vP = O becomes r | v. The induced one-shot
statistic is d(y) = gcd of all accepted denominators, or zero. Its distribution
w_d and the gcd recurrence determine the T-shot law. The finite expression is
mathematically exact; a float64 evaluation is not a certified exact number.

## Primary-source matrix

| Source and inspected location | Established result / event | Relation and limitation |
| --- | --- | --- |
| [Shor, quant-ph/9508027v2](https://arxiv.org/pdf/quant-ph/9508027v2), Section 5, PDF p. 19 | Continued fractions, coprime-phase success and repetition analysis; discussion of frequency searches, small multiples and combining samples by lcm | Unknown order does not prevent a repetition guarantee. This is not the local all-verified-convergents gcd law. The parity condition belongs to the factoring reduction. |
| [Ekerå, 2201.07791v2](https://arxiv.org/html/2201.07791v2), Sections 1.2, 1.5.1, 4.1.3-4.1.7, Theorem 3 in 4.2 | Exact finite measurement distribution; simulations; exact-order success bound with limited classical searches and smooth completion | Strong antecedent for reliability without knowing r. Different post-processing and classical work. Section 4.1.6 already uses gcd with a known order multiple: do not claim that Ekerå never uses gcd. Its search-window B is not our Hasse B. |
| [Bourdon and Williams, quant-ph/0607148](https://arxiv.org/pdf/quant-ph/0607148), PDF pp. 20-21, equations (27), (28), (43) and surrounding discussion | Explicit probability bounds, including removal of r dependence under stated parameter regimes | Some events recover a nontrivial divisor, not necessarily the full order. The stated regimes must be checked before using their numerical bounds on small fields. |
| [Peng et al., 2204.07112](https://arxiv.org/pdf/2204.07112), Appendix C.1, lemma Shor_OF_correct; Figure 4(c) | Formally proved exact-order lower bound in terms of the known modulus N; comparison of certified lower bounds and concrete success behavior | Direct antecedent for an order-independent sufficient budget. Different multiplicative-group implementation. Its formal certificate is not equivalent to agreement between floating-point calculations. PDF inspected as served on the audit date; URL not version-pinned. |
| [Magdon-Ismail and Dong, 2506.20527v1](https://arxiv.org/pdf/2506.20527v1), introduction equation (2), Theorems 1-2, Section 5.1 Theorem 10, Sections 5.4-5.5 | Finite period-finding probabilities and bounds with register-size tradeoffs; exact probability of a frequency-window event | Strong antecedent against first finite-law or first precision/reliability tradeoff claims. A window event or a recovered divisor cannot be substituted for exact-order success of our verified-gcd policy. |
| [Yang and Markidis, 2605.16074v1](https://arxiv.org/html/2605.16074v1), Section 2 equations (1)-(2) | Aggregate probability mass by verified continued-fraction denominator; infer the denominator with maximum verified mass | Aggregating probability by verified candidates is already explicit. Their noisy-distribution argmax policy is not our independent-shot gcd policy and supplies no noise guarantee for our circuit. |
| [Abbassi and Bayle, 2505.00433v2](https://arxiv.org/html/2505.00433v2), Sections 3-6 | Success conditions of the classical factoring reduction over random bases, including parity and half-power conditions | Different probability space from finite-Q exact-order recovery. A similar title is not evidence of an identical result. |
| [Fernandez and Fernandez, 1305.0536v1](https://arxiv.org/abs/1305.0536v1), abstract-level inspection only | Probability distributions of gcd/lcm of random integer tuples | General antecedent, not a verified match to arbitrary weighted verified-denominator distributions including zero. Full-paper comparison remains unperformed. Standard divisor/Mobius inversion is not a new contribution here. |

Knill, LA-UR-95-3350 (1995): direct report not retrieved in this pass. Shor
Section 5 and Ekerå Section 1.5 / Appendix C.1.3 provide a primary-source
citation trail for combining samples by lcm. This is an indirect attribution,
not a claim to have inspected Knill's full report.

## Search scope and reproducibility

Search date: 2026-10-18. Followed Shor/Ekerå citation trails and searched for
finite, uniform and worst-case success probabilities, verified denominators,
verified multiples, gcd accumulation and Markov models of order finding.
Representative queries:

- `"order finding" "worst-case" "success probability"`
- `"Shor" "exact" "success probability" "uniform"`
- `"order finding" "verified multiples" gcd probability analysis`
- `"order finding" "verified" "denominators"`
- `"order-finding" "gcd" "Markov"`
- `"quantum period finding" "success probability" 2025 bounds`
- `"LA-UR-95-3350" Knill`

Only primary papers support the matrix. No source-code comparison, external
experiment, systematic-review completeness or exhaustive absence claim is
implied. References are links for this audit, not proposed BibTeX keys. Older
component-level audits remain separate; P0 is about recovery reliability.

## What the comparison supports

1. Finite distributions, unknown-order guarantees, repetition amplification,
   and post-processing-aware probability aggregation all have antecedents.
2. No identical analysis of the complete local policy was located in the
   inspected passages. That observation does not establish novelty or value.
3. A fair numerical comparison must match the success event, register size,
   order bound, error target and classical work. A larger sufficient T for
   our existing conservative bound is not a lower bound on prior methods.
4. Direct inspection of Knill and a fuller gcd-probability comparison are
   unresolved source checks, not grounds to claim priority in their absence.

## Second-reader verification (2026-10-18)

Existence and abstract-level consistency checked for every row (arXiv listing
pages; bodies not re-read except Ekeraa's first half via HTML):

- Bourdon and Williams, quant-ph/0607148v3 (2006): "Sharp probability estimates
  for Shor's order-finding algorithm"; bounds for obtaining a nontrivial divisor
  of the order (0.7 for r > 39, asymptotically 0.7736; about 0.95 under extra
  conditions). Event is a divisor, not exact order: matrix row correct.
- Peng et al., 2204.07112 (2022): formally certified end-to-end Shor; the
  abstract does not state the order-finding probability lemma, so "Appendix C.1
  lemma Shor_OF_correct" rests on the body inspection by the first reviewer and
  is not re-verified here.
- Magdon-Ismail and Dong, 2506.20527 (v3, Dec 2025): "Tight success
  probabilities for quantum period finding and phase estimation"; finite bounds
  and circuit-size versus classical-work tradeoff; event is recovering a divisor
  of the period: row correct.
- Yang and Markidis, 2605.16074 (May 2026): "When noisy quantum order finding
  remains recoverable for Shor's algorithm"; 680 measured IBM distributions,
  continued fractions with modular verification, "dominant verified mass
  fraction" as a recoverability indicator. "Aggregate" in the row slightly
  overstates the abstract; the policy is a predictor, not our gcd law.
- Abbassi and Bayle, 2505.00433v2 (2025): "Success probability in Shor's
  algorithm"; exact per-step success for factoring with known factorization.
  Different probability space: row correct.
- Ekeraa, 2201.07791v2: Theorem 3 (Sec. 4.2) bounds single-run exact-order
  recovery as a function of search width B and parameter c, for continued
  fractions or lattice post-processing; Corollary 3.2 gives probability tending
  to one; m = 128 allows a guarantee above 1 - 10^-4 (Table 1). Section 1.5
  cites Knill's lcm combination of tentative orders over several runs. The gcd
  remark about Section 4.1.6 could not be confirmed from the first half of the
  HTML; it is not needed for the assessment.

Consequence confirmed by the second reader: the existing local bound (1/(16 nu_B)
per shot, T = 443 for p = 29) is already uniform in r, and Ekeraa already
provides single-run exact-order guarantees without knowing r. "Uniform budget"
is therefore not a difference. What remains policy-specific is the exact
outcome split (exact, none, nonminimal) of the all-verified-convergents gcd
policy and its interface with primality admission.
