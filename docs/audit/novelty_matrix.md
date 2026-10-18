# M2 novelty audit

Status: first source pass and second-reader verification on 2026-10-18. NOT a
novelty decision.
Local comparison baseline: m1-complete, commit
6e5a775e57f380d4650dd247bf39ed95fed3dcfb.
No circuit, recovery policy or manuscript changes are authorized by this audit.

## Scope and decision rules

The user authorized starting M2. Advisor agreement on target venue, application
versus circuit emphasis, and acceptable research effort is not recorded here.
Documentary work can proceed; an editorial reframe remains a separate decision.
Use the agreed two-working-week audit budget; a third week requires a named
issue capable of changing the decision. This is not a scheduled automation.

A candidate must have (1) an identifiable difference from checked antecedents,
(2) a check possible with available means, and (3) measured or formally supported
technical relevance. A missing statement is not evidence that a property is new.
Distinguish a proposed construction, tested implementation and universal proof.

Source identifiers and exact locations: ../references/m2_source_notes.md.
Pending means not yet established, not absent from the source.

| Source/version | Representation/domain | Exceptional cases | Invalid encodings | Cleanup | Implementation/coverage | Resources | Current implication |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PZ, quant-ph/0301141v2 | Unique affine points, Sec. 3.1 | Sec. 4.2 uses generic addition with random-offset initialization; loss about 4 log q / q | Not defined; states stay on the curve | Sec. 4.3 reverses slope arithmetic and names the standard compute/swap/uncompute-with-minus-A procedure | Code/coverage audit pending | Sec. 6; model comparison pending | Controlled constant additions and unknown-order finding are antecedents, not local inventions |
| RNSL, 1706.06752v3 | Affine, Secs. 4.1-4.2 | Generic law with offset initialization and exceptional-scalar analysis, Sec. 4.2 (fraction about n/2^n for large prime r) | Not defined; states stay on the curve | Reversible arithmetic; full contract audit pending | Paper reports simulated Toffoli networks; exact test coverage pending | Concrete counts exist; no local-model comparison yet | Exception frequency analysis already has an antecedent |
| HJNR S, 2001.09580v1 | Affine, Sec. 5; uniqueness discussed in App. A.4 | Complete-domain contract pending | Pending | App. A.4, Fig. 11 already describes out-of-place to in-place conversion | Paper reports Q# implementation; repository revision/tests pending | Optimized arithmetic, different accounting | Compute/swap/inverse cleanup is not itself novel |
| Litinski, 2306.08585v1 | Two affine quantum inputs, second one lookup-selected (window 16); O as the sentinel (0,0); Sec. II | Explicit exact-addition construction with flags for identity, inverse and doubling, Figs. 5, 10-12 (verified) | Not defined: domain is curve points plus (0,0); no claim for arbitrary bit strings or order-two constants | Explicit flag/slope reset construction; see Papa below | Diagram-level contract checked; code not audited | Do not equate amortized per-key counts with our per-addition counts | Handling these exceptional cases alone cannot support a first-construction claim |
| Cheung-Mosca, cs/0101004v1 | Unique recognizable encodings and efficient group action, Sec. 5 | Abstract group operation assumed | Recognition assumption, not our chosen fixed-point extension | Implementation details abstracted | Not a concrete EC circuit audit | Corollary 8 gives randomized quantum polynomial-time element-order finding | General group order finding is established |
| Papa, 2506.03318v2 | Qualtran implementation following Litinski, Sec. II | Four cleanup defects, all in exceptional paths (steps 2, 5, 6), repaired, Sec. III | Not tested: 12 selected curve points of one small curve | Reports four cleanup inconsistencies and repairs, Sec. III | Computational-basis and resource tests, Sec. II; code revision pending | Reports unchanged leading gate order, one extra ancilla | Validation and cleanup repair are also established research directions |
| Later works/software | Search leads recorded in source notes | Pending | Pending | Pending | Pending | Pending | No absence or priority claim permitted |

## Local evidence and limits

- controlled_point_add in src/quantum_ec/circuits/points/controlled_point_add.py
  controls every operation, not only an output swap.
- point_add_inplace in src/quantum_ec/circuits/points/point_add_inplace.py
  evaluates H_A, swaps and evaluates H_minus_A to clear the old point. H_A fixes
  invalid encodings. This is a local contract, not an originality conclusion.
- Coverage remains exactly docs/audit/coverage.md: complete small encoding
  domains for selected constants; p29 selected adder inputs; all scalar inputs
  in specified instances. Not all p29 point encodings or auxiliary inputs.
- M1 admission is a correctness boundary using standard primality testing,
  not evidence of novelty for the quantum circuit.

## Verified differences of the local artifact (not yet relevance-weighted)

Established by the second-reader pass; each needs condition 3 (measured or
formal relevance) before it can appear as a contribution.

1. Domain totality. H_A is a total function on all 2^(2l+1) encodings (invalid
   strings map to themselves), verified exhaustively for width 3 and on all 30
   points of p=29 for one constant (docs/audit/coverage.md). Litinski/Papa are
   exact on curve points plus (0,0) and are tested on 12 selected points; Long et
   al. test random inputs. No antecedent claims or tests off-curve behaviour. In
   ideal execution such states never occur, so relevance must be argued (robust
   verification contract, reusable component), not assumed.
2. Representation. Identity as a flag qubit with canonical (1,0,0) versus the
   (0,0) sentinel; classical constant per scalar bit versus windowed lookup.
   Descriptive differences, not advantages.
3. Setting. The antecedents target ECDLP with a known large prime order, where
   PZ/RNSL show exceptions are negligible. Order finding from the identity with an
   unknown, possibly small or composite order is the setting where that argument
   is weakest (the first addition O + P is exceptional for every odd k). No
   antecedent quantifies the exact effect of generic-only addition there.
4. Verification method. Exhaustive basis propagation of the real circuit over
   complete small domains with clean-ancilla checks, plus FFT of the permutation,
   is a reproducible artifact pattern; Papa and Long et al. use selected or random
   inputs. Comparable in kind to Polimeni-Seidel's sparse-simulator checks.

## First-pass decision impact

The broad candidate 'complete reversible addition plus clean-ancilla validation'
is insufficient as a novelty claim: Litinski and Papa must be compared directly.
This does not establish equivalence of all domain contracts or implementations.
It does not invalidate the existing artifact or require rewriting the paper.

Do not choose a large experiment yet. First inspect corrected reference software
and its actual domain/tests; then assess a narrower difference, an optimization,
a recovery study or an explicitly reproducible-artifact positioning with advisor.
An incomplete-reference comparison could be useful evidence, but cannot alone
establish an advance over a complete corrected reference.

## Next checks / closure gate

1. Pin reference code revisions and inspect tests, phases, initialized workspace,
   exceptional outputs and any invalid-encoding/order-two preconditions.
2. Follow the targeted later-work leads; no unbounded literature survey.
3. Done 2026-10-18: see docs/audit/references_audit.md. [27] Bhatia2020 does not
   resolve (DOI points to another article; no Crossref record); [28] Bittel2021
   exists but is not pertinent; [30] Endo2021 exists, weak pertinence.
4. Record candidate, comparator, testable claim, resource model and motivation.
   Agree measurable acceptance criteria before producing outcome data.
5. Decide continue/reframe with the advisor; record scope and evidence deadline.

R8 remains OPEN. No performance improvement, secure-domain guarantee, first
implementation claim or publication outcome is established by this first pass.
