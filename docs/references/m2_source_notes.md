# M2 primary-source notes

Checked 2026-10-18. Initial targeted reading, not a full-paper or code audit.
Use explicit arXiv versions; PDF page numbers below are one-based file pages.
No verbatim excerpts are reproduced. These notes do not edit the bibliography.

## PZ: Proos and Zalka

Shor's discrete logarithm quantum algorithm for elliptic curves.
https://arxiv.org/pdf/quant-ph/0301141v2

Sec. 2.2.1 describes general order finding; Sec. 2.2.2 explicitly allows finding
an initially unknown order. Sec. 3.1 discusses unique affine encodings. Sec. 4.2
(PDF p. 11) restricts addition to the generic branch, arguing negligible loss
from identity/equal/inverse inputs in its setting. Sec. 4.3 gives reversible
group-shift arithmetic. Do not infer that all such inputs are implemented.

## RNSL: Roetteler, Naehrig, Svore and Lauter

Quantum Resource Estimates for Computing Elliptic Curve Discrete Logarithms.
https://arxiv.org/pdf/1706.06752v3

Sec. 4.2 (PDF pp. 15-17) precomputes binary multiples, uses generic additions,
discusses offset initialization and counts scalars encountering exceptions.
Remark 1 (PDF p. 15) identifies representation and uncomputation obstacles for
projective coordinates; it does not prove their use impossible. Introduction
reports simulation/testing of Toffoli networks. Exact source-code coverage is
not established by reading those claims.

## HJNR S: Haener, Jaques, Naehrig, Roetteler and Soeken

Improved quantum circuits for elliptic curve discrete logarithms.
https://arxiv.org/abs/2001.09580v1
https://arxiv.org/html/2001.09580

Sec. 5 uses affine coordinates; App. A.4 discusses unique representations and
Fig. 11 converts an out-of-place point addition to an in-place operation using
inverse translation. Abstract reports a Q# implementation supporting tests and
resource estimation. These observations do not establish a complete input-domain
contract; inspect the implementation before claiming exceptions are omitted.

## Litinski

How to compute a 256-bit elliptic curve private key with only 50 million Toffoli gates.
https://arxiv.org/pdf/2306.08585v1

Sec. II, 'Elliptic curve point addition' (PDF p. 6), explicitly contrasts an
exact construction with RNSL's generic-only treatment. Flags handle identities,
inverse points and doubling; Figs. 5 and 10-12 describe computation/cleanup.
This defeats a broad first-complete-addition claim. It is not an audited proof
for all arbitrary encodings or order-two constants. Papa reports corrections,
so compare against the repaired construction rather than the original alone.

## Cheung and Mosca

Decomposing Finite Abelian Groups.
https://arxiv.org/pdf/cs/0101004v1

Sec. 4, Corollary 8 (PDF p. 3), states randomized quantum polynomial-time
element-order finding. Sec. 5 (PDF p. 4) assumes unique recognizable binary
encodings and efficient quantum group operations. Those assumptions are not a
concrete implementation of our EC representation or invalid-state extension.

## Papa: mandatory follow-up to Litinski

Validation of Quantum Elliptic Curve Point Addition Circuits.
https://arxiv.org/pdf/2506.03318v2

Secs. I-II describe a Qualtran implementation and computational-basis/resource
tests. Sec. II.B (PDF p. 2) describes selected p1707 points, not universal
exhaustive coverage. Sec. III reports four cleanup inconsistencies in Litinski's
construction and repairs, adding one ancilla without increasing leading gate
order. Verify its repository revision and actual tests next. This paper prevents
assuming that published exact diagrams were already correct or that validation
with cleanup is a new research direction by itself.

## Targeted follow-up queue (not yet audited)

Search leads only; do not use their resource or correctness claims as conclusions:

- https://arxiv.org/abs/2501.10228 (implementation lead; identify paper/version).
- https://arxiv.org/abs/2606.02235 (optimized point addition).
- https://arxiv.org/abs/2607.13816 (space-efficient point addition).
- https://arxiv.org/abs/2609.05625 (later ECDLP estimates).
- https://arxiv.org/abs/2609.28882 (record-and-replay arithmetic).

Prioritize corrected Litinski/Papa software before broadening the queue.
Locate original sources rather than treating search snippets as verified facts.

## Second-reader verification (2026-10-18)

Each statement above was checked against the arXiv PDF/HTML by a second reader.
PDF page numbers are one-based file pages. Nothing below is a novelty decision.

- PZ. Confirmed: Sec. 2.2.2 (p. 6) states that an unknown order can be found
  with the order-finding algorithm and factored; Sec. 4.2 (p. 11) uses only the
  generic branch, initializes the accumulator with a random multiple kP and bounds
  the fidelity loss by about 4 log q / q; Sec. 4.3 (pp. 11-12) uncomputes the slope
  stepwise. Addition: Sec. 4.3 also names the "standard procedure"
  |S,0> -> |S,S+A> -> |0,S+A> that uncomputes S by running the addition of -A
  backwards. This is the pattern used by point_add_inplace (compute H_A, swap,
  evaluate H_{-A}); cite PZ 4.3 together with HJNRS App. A.4 for it.
- RNSL. Confirmed: Algorithm 1 and Fig. 10 (pp. 14-15) are the generic controlled
  addition for P1,P2 != O, P1 != +-P2; Remark 1 (p. 15) on projective coordinates;
  Sec. 4.2 (pp. 15-17) precomputes 2^i P, adopts the PZ offset and counts invalid
  scalars, concluding a fraction of about n/2^n under the assumption that r is a
  large prime. The repository's exact exception count per stage (CLAUDE technical
  notes) refines this for small instances; it is not a new idea.
- HJNRS. Confirmed via arXiv HTML: Sec. 5 says the circuit is incorrect for the
  point at infinity and for P = +-Q and relies on PZ/RNSL for negligibility;
  App. A.4 Fig. 11 builds in-place addition from out-of-place using U_{-Q} at
  double cost; unique representation is stated as a requirement of Shor's algorithm.
- Litinski. Confirmed (p. 6): "we construct an exact circuit for the point
  addition operation, whereas the circuit in Ref. [6] ignores the exceptional
  cases"; flags f1..f4 for a = x, b = -y, P1 = O, P2 = O plus a ctrl flag; six
  steps in Figs. 10-12 with 5n+5 ancillas; Fig. 5 is the subroutine table.
  Additions: O is represented by the sentinel (0,0), not by a flag qubit; the
  second summand is a lookup-selected point in a window of 16, not a classical
  constant per bit; behaviour on bit strings that are not curve points is not
  defined because such states never arise in that algorithm.
- Papa. Confirmed: Qualtran implementation of Litinski's six steps; four
  inconsistencies in steps 2, 5 and 6, all in exceptional-case cleanup (lambda copy
  when f1 = 1, undefined inverse when a - x_r = 0, origin outputs); repairs add one
  ancilla and 18n-5 Toffolis, leading order 126 n^2 unchanged; tests use 12
  selected points of the "p1707" curve from the cited practical-cryptography text
  (apparently p = 17, a = 0, b = 7; confirm in the Qualtran test code), not an
  exhaustive domain. Code: Qualtran PRs 1489 and 1666.
- Cheung-Mosca. Confirmed: Corollary 8 in Sec. 4 (p. 3); Sec. 5 (p. 4) assumes a
  unique binary representation with efficient recognition and an efficient
  quantum network for the group action.
- Follow-up queue. All five identifiers exist: 2501.10228 Polimeni and Seidel,
  Qrisp end-to-end ECDLP implementation checked with a sparse simulator (Jan 2025);
  2606.02235 Schrottenloher, optimized point addition (Jun 2026); 2607.13816 Luo et
  al., space-efficient ECDLP with a new modular inversion, 835 logical qubits for
  256 bits (Jul 2026, v3 Sep 2026); 2609.05625 Haener et al., 256-bit ECDLP in about
  26 days on a trapped-ion architecture (Sep 2026); 2609.28882 Long et al.,
  record-and-replay arithmetic, tests on random inputs that the authors state do
  not establish correctness for all inputs, and a repaired circuit (Sep 2026).
  Abstracts only; bodies not audited.
