# F: finite reliability of the existing hybrid process

Date: 2026-10-18. Author authorized model development and evaluation.
Status: model validated on bounded tests; research novelty NOT established.
Title, pipeline, cost model and signing application are retained. No TeX/Bib edits.

## Five qualifications agreed before evaluation

1. Exact finite formulas remove Monte Carlo error, not floating-point error.
   Current ideal probabilities use float64; no interval enclosure is supplied.
   Rational toy-law tests are exact arithmetic, not exact rational evaluations of
   general trigonometric quantum probabilities.
2. Under ideal injective arithmetic and this policy, the distribution depends
   on r, Q and B. The curve enters through these values and valid group action;
   changing a curve without changing those values is not an independent effect.
3. Include incorrect admission. Composite candidates can falsely pass MR;
   separate a deterministic ideal-prime partition from the actual policy bounds.
   Never describe a 2^-128 bound as a posterior probability or zero error.
4. Budgets computed with the true r are reference-conditioned diagnostics.
   They do not replace the unknown-order operational budget. No true order is
   passed to production recovery or signing, and enumerating Q outcomes is
   offline analysis, not a polynomial-time signing implementation.
5. Exact spectra, repetition analysis, Markov chains and gcd/divisor inversion
   are established techniques. An application-specific characterization must
   demonstrate its difference and usefulness; no claim of a new Shor algorithm,
   new probability tool or established novelty follows from this model.

## Assumptions and definitions

P is a valid nonidentity point of order r on a nonsingular curve over prime p>3.
All executions are independent, ideal, phase-correct, with canonical injective
point outputs and zero work. Q is a power of two, B>=r. The current uniform
choice has Q>B^2. Smaller Q can still be modeled but lacks that guarantee.

For outcome y define the production candidate set
C(y) = {v: v is a continued-fraction denominator of y/Q, 1<=v<=B, vP=O}.
Define d(y)=gcd(C(y)), with gcd(empty)=0. Do NOT select a single denominator
or assume every measurement yields a divisor of r. Every nonzero d(y) is a
multiple of r. A single measure may have several candidates, all processed.

With p_y the ideal IQFT probability, define w_d=sum_{y:d(y)=d} p_y.
The exact finite spectrum is the standard fiber formula:

```text
p_y = Q^(-2) sum_{a=0}^{r-1} |sum_{k<Q, k=a mod r} exp(2 pi i k y/Q)|^2.
```

The sign of the Fourier exponent does not change these magnitudes.
Our implementation calls the existing ideal_probabilities and verified_candidates;
it neither replaces the solver nor claims an independent proof of those helpers.

## Finite-state recurrence and proof

Let G_0=0 and G_{t+1}=gcd(G_t,d(Y_{t+1})). State space is
{0} union {r,2r,...,floor(B/r)r}. Associativity of gcd shows this is exactly the
production loop across all accepted denominators, including empty steps.
Independence gives the transition probabilities and recursion:

```text
K(g,h) = sum_d w_d [gcd(g,d)=h]
pi_0(g) = [g=0]
pi_{t+1}(h) = sum_g pi_t(g) K(g,h).
```

All nonzero states remain multiples of r. Once G_t=r, subsequent updates keep r,
so r is absorbing. The three disjoint recovery outcomes are pi_T(r), pi_T(0)
and sum_{g>r} pi_T(g). In particular pi_T(0)=w_0^T. Define w_0^0=1 at T=0.
The sufficient lower bound 1-(1-w_r)^T is not always an equality: distinct
nonminimal multiples can have gcd r even if neither equals r.

## Independent divisibility check (standard inversion, not a new theorem)

For positive g let F_g=sum_{d:g divides d} w_d, including d=0. Then
Pr(g divides G_T, G_T>0)=F_g^T-w_0^T. This follows because g must divide every
d, but the all-zero sequence must be removed. A positive gcd cannot exceed B.
Descending over positive g therefore recovers its mass by

```text
pi_T(g) = F_g^T - w_0^T - sum_{j>=2, j*g<=B} pi_T(j*g).
```

This is inversion on the divisibility poset (equivalently a Mobius sum).
It supplies a check independent of Markov transition iteration, not a second
physical simulation. Float cancellation is reported, never silently clipped.

## Admission and its distinct error

For prime r, true r always passes MR, and admitted-correct mass is pi_T(r).
Every nonminimal multiple is composite. For composite r, every recovered
positive multiple is composite; correct general order recovery is still possible,
but an ideal primality gate rejects it for signing.

Let u(g) be the actual MR false-pass probability of a fixed composite candidate.
Under independent uniform bases u(g)<=4^-64, and u(g)=0 when small-prime checks
detect a divisor. Incorrect admission is sum_{g composite} pi_T(g) u(g).
It is bounded above by 4^-64 times the mass of composites not rejected by the
small-prime filter. Ideal rejected-category masses are upper bounds for actual
rejection, with a reduction no greater than the corresponding false-pass bound.
The model labels these ideal categories explicitly; they are an exact policy
partition only when no uncertain composite mass exists. One final admission
test per attempt is modeled, not a test after every shot or nonce retry.

## Implementation and checks

- experiments/reference/gcd_recovery_law.py:one_shot_law builds w using the
  single production acceptance policy; gcd_law evaluates the recurrence.
- divisor_inversion_law checks the result through divisibility masses.
- admission_summary reports the ideal partition and actual false-pass bound.
- Tests compare both methods with exact Fraction enumeration for T=0..4,
  check recovery from 10 and 15 without observing 5, and replay all 64 two-shot
  sequences for a small actual EC recovery instance. These are consistency
  checks plus independent combinatorics, not a gate-level circuit validation.
- experiments/configs/m2_f_pilot.json fixes seven rows before execution,
  including prime/composite/even orders and a second Q for the p29 instance.
  Per-row reports have float residuals and provenance. No new real-circuit
  distribution is generated; ideal-oracle assumptions are not promoted to
  verified circuit behavior on every pilot curve.

No Monte Carlo draws, noise model, resource benchmark or production change.
The reference-conditioned target budget uses epsilon=0.01 and a finite search;
None would mean the search cap was reached, not impossible recovery.

Initial pilot results (numerical, not certified interval enclosures):

| p | r | Q | First T reaching 0.99, conditioned on known r | Unknown-order sufficient T |
| --- | --- | --- | --- | --- |
| 5 | 9 | 128 | 5 | 295 |
| 7 | 2 | 256 | 7 | 295 |
| 7 | 4 | 256 | 7 | 295 |
| 17 | 18 | 1024 | 13 | 369 |
| 29 | 5 | 2048 | 3 | 443 |
| 29 | 5 | 4096 | 3 | 443 |
| 41 | 53 | 4096 | 3 | 443 |

These columns have different information assumptions, not competing algorithms.
On p29/Q2048, exact-order probabilities evaluated numerically are 0.7982253317,
0.9592871308, 0.9983424862 and 0.9996655605 at T=1,2,4,5. The maximum observed
DP/inversion discrepancy over the seven pilot rows and configured budgets was
about 2.0e-15. It is a diagnostic, not a rigorous error bound. All composite
candidate values in this pilot have a listed small-prime divisor, so its
admission partition is exact for that policy conditional on the numeric law.

## Antecedents and novelty decision

- Ekeraa, arXiv:2201.07791v2, Secs. 1.2-1.5 and 4: finite spectrum,
  success bounds and improved classical postprocessing; Sec. 1.5 discusses
  repetition/LCM antecedents. This is not the same implemented policy, and we
  have not demonstrated a performance improvement over it.
  https://arxiv.org/html/2201.07791v2
- Fernandez and Fernandez, arXiv:1305.0536, studies distributions of gcd/lcm
  of random integer samples. This is a general mathematical antecedent, not
  proof that this EC-specific policy was already analyzed.
  https://arxiv.org/abs/1305.0536
- Standard divisor inversion: MIT 18.781, Lecture 14 (2012).
  https://ocw.mit.edu/courses/18-781-theory-of-numbers-spring-2012/a97051320da973caebacda06c3a74eac_MIT18_781S12_lec14.pdf

Targeted search 2026-10-18: 'quantum order finding gcd accumulation exact
probability Markov chain verified multiples', 'Shor order finding greatest
common divisor verified multiples success probability repeated measurements',
and 'probability gcd random integers distribution Mobius inversion finite
arbitrary distribution'. Search results are leads, not evidence of absence.
No matching full analysis of this exact policy was established in the inspected
sources, but neither was exhaustive priority. The formulas above follow standard
conditioning and divisor inversion. Different policy alone does not establish
an important advance, especially relative to stronger known postprocessing.

Decision now: F is mathematically viable and fits the existing paper. It is
not yet demonstrated research novelty. Before closing R8, identify a precise
useful result beyond routine application (for example a valid unknown-order
budget refinement with stated guarantees), audit its antecedents and measure
its effect. A large empirical gap from a conservative bound is not a speedup
claim or an asymptotic improvement. Do not rewrite contributions yet.

## Second-reader verification (2026-10-18)

- Model re-derived independently (own one-shot law, own Markov iteration, own
  divisor inversion with exact rationals): all seven pilot rows agree with
  pilot.json to the printed precision; the inversion identity holds exactly on
  random rational weights for T = 1..4. The evaluation script was rerun in the
  Python 3.12 Qiskit environment: no numeric difference above 1e-12.
- Quick suite 70/70. Fernandez and Fernandez, arXiv:1305.0536, exists with the
  stated topic. Ekeraa 2201.07791 is the closest antecedent and analyses a
  different post-processing; the note's positioning is correct.
- Qualification 2 (the law depends only on r, Q and B) has a direct consequence
  for the design of F: a parameter study does not need sampled curves. For each
  field size, enumerating every possible order r = 2..B gives the complete
  picture exactly, because ord(P) <= #E <= B for every point of every curve.

### Candidate precise result (ad hoc computation, to be frozen in a run)

Worst case over all r <= B of the exact T-shot law gives a valid unknown-order
budget under the model's assumptions (ideal, independent shots; float64):

| p | B | Q | worst one-shot P(accept r), at r | exact worst-case T for 0.99 | published sufficient T |
| --- | --- | --- | --- | --- | --- |
| 5 | 10 | 128 | 0.313 (r = 6) | 13 | 295 |
| 7 | 13 | 256 | 0.292 (r = 12) | 14 | 295 |
| 11 | 18 | 512 | 0.306 (r = 18) | 13 | 369 |
| 17 | 26 | 1024 | 0.291 (r = 24) | 14 | 369 |
| 29 | 40 | 2048 | 0.251 (r = 30) | 16 | 443 |
| 41 | 54 | 4096 | 0.258 (r = 30) | 16 | 443 |

The hardest orders are even composites with many small factors, as phi(r)/r
predicts. This is the kind of "valid unknown-order budget refinement with stated
guarantees" the decision above asks for: it keeps the same guarantee form
(probability >= 1 - epsilon over independent ideal shots) with a budget one
order of magnitude below the published sufficient T. It is not yet a result:
it must be produced by a frozen configuration and script with provenance,
compared with the Ekeraa-style bound for the same instances, and stated with
its float64 caveat. Antecedent check for worst-case-over-r budgets is pending.
