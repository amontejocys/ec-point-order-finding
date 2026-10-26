# Stage 8, part 1: R1-R8 traceability on the Post_P snapshot

Date: 2026-10-26. Base: snapshot `paper/manuscript/` Post_P (export of
2026-10-26 13:44, ZIP SHA-256 `e412ec03934b6fc69d2fa40c0465ba0a1919fafe15b180fe78a8875a77a89d28`),
commit 369deb6, tag stage7-integrated. This replaces the Post_M1 evidence cited
in revision_traceability.md; that file keeps its historical statements. Method:
text searches and reading of the snapshot sections named below, plus the earlier
reviewed numerical evidence. It is not a line-by-line scientific audit of the
whole article, and it does not close any objection by itself. "Integrated"
means the text is present in the snapshot; the verdict of the reviewer is theirs.

Locations are given as file and subsection name, because section numbers depend
on the REVTeX build in Overleaf.

## R1-R8 on the Post_P snapshot

| R | Required correction | Where it stands in the text | State |
| --- | --- | --- | --- |
| R1 | No parity toggle or claimed parity contribution | `04-results_discussions.tex`, Period preservation: period is ord(P) "whether r is even or odd"; the even-order condition of Shor's factoring reduction "does not apply". `08-appendix.tex`, worked instance: "No parity correction was used". Scan for `parity`, `toggle`, `idx`: only those two hits | Integrated |
| R2 | Genuine period 5, no identity rows skipped, no domain compression | Worked instance (appendix): r = 5, "all scalar inputs are retained", outputs equal to O explicitly encoded, "No scalar-output lookup table or domain compression"; 2048 scalar inputs checked against independent group arithmetic. Scan for `Q16`, `period 4`, `lookup`: only the negation above | Integrated. Coverage is the initialized scalar path (40 adder transitions), stated in the same appendix |
| R3 | Separate group order, point order, cofactor | Worked instance: #E(F29) = 30 including O, ord(P) = 5, h = 6 | Integrated |
| R4 | Justified register sizing | Algorithm (Results, Pipeline): B from Hasse, m = ceil(log2(B^2+1)); worked instance: B = 40, m = 11, Q = 2048; finite reliability block uses Q0 = 2^ceil(log2(B^2+1)) and 2Q0 | Integrated. Unknown-order budgets are numerical estimates, labelled as such |
| R5 | Coherent reversible arithmetic instead of lookup; canonical encoding and cleanup | Methods, Point representation and Reversible evaluation; Appendix A (construction); appendix code correspondence and validation | Integrated. Antecedents for complete addition are acknowledged in the introduction; no claim of a new construction |
| R6 | Per-addition cost, all m steps, recovery, admission and repetitions | Results, Complexity analysis: Theorem (resource bound for the reference implementation) C_add = O(l^6), G_q = O(T l^7), O(l^2) qubits; classical O(l^4 + T l^5); admission cost sentence O(kappa l^3) + O(l^4); Scope of the asymptotic claim (bounds describe the reference circuit, not optimized constructions). Finite budgets enter only through T | Integrated. The theorem label is still `thm:speedup` (invisible to readers; rename optional) |
| R7 | Separate comparison with enumeration, generic methods, point counting plus factorization | Results, Classical baseline: enumeration, BSGS/rho, Schoof/SEA with prime-factor removal; classical comparison table; Scope of the asymptotic claim. Discussion states the comparison with point counting is made on the cost model of the complexity section only | Integrated. No classical timing benchmark exists, and none is claimed |
| R8 | State what is contributed relative to the antecedents | Introduction: antecedents (Cheung-Mosca, Proos-Zalka, Roetteler; resource-range sentence rewritten) and two-item contribution with the finite-characterization clause; Discussion, Position with respect to existing studies: Papa and Ekera named, contribution framed as integration plus reliability characterization; abstract and conclusion aligned. No "first", "novel" or "speedup" claims (scan) | Positioning integrated. Sufficiency of the contribution is the reviewer's judgment, as accepted in m2_decision.md |

## M1 (signing admission) and the F evidence in the text

| Item | Location | State |
| --- | --- | --- |
| Admission step in the algorithm | Results, Pipeline algorithm: primality test, NotAdmissible return, Ensure list; blue through `\color{blue}` | Integrated |
| Rationale and error bound | Results, Probabilistic order recovery: prime r-hat and r-hat P = O imply ord(P) = r-hat; 64 Miller-Rabin rounds, bases in {2,...,r-hat-2}, 2^-128 per fixed odd composite, HAC citation; no certificate claim; rejection is deterministic for small-prime detection | Integrated |
| Admission policy in reproducibility | Results, Reproducibility regime: exact small-prime checks, 64 rounds from an OS random source, outcome categories | Integrated |
| Finite recurrence and baseline rule | Appendix, after Recovery probability and resulting bounds: spectrum, accumulator recurrence, field-level budget definition, rule 16 nu_B ln(1/eps) giving 443 | Integrated |
| Finite reliability evaluation | Results, Reproducibility regime: 11 primes, 650 pairs, 66 budgets, p = 29 crossing at T = 16 versus 443, agreement within 3.93e-14, order 9 recovered and rejected | Integrated, no figure by the author's decision |
| Limits | Discussion, Limitations: small-field validation, finite budget, admission is probable-prime and not domain security, offline enumeration, circuit agreement only on the initialized scalar inputs | Integrated |

## Open items found by this pass

1. **Motivation is only implicit.** The text says the pipeline is not an
   acceleration of deployed ECDSA (Scope of the asymptotic claim) and that the
   aim is the reliability of the integrated process (Discussion), but no sentence
   answers directly why one would study quantum order finding when point counting
   plus factoring is practical. A one-sentence addition in Discussion would close
   this; a candidate is kept in the author's private notes if requested.
2. **Reference [30] (Endo) and Cerezo** remain, cited only for the general
   statement about hybrid quantum-classical algorithms in the introduction. The
   audited problem sentence was rewritten and the Discussion sentence that
   invoked a "hybrid pattern" was removed. Acceptable; confirm in the response.
3. **Data availability** names the repository and defers the code revision and
   data location to the release. The repository is private; the historical NPZ
   and the 13 MB P3 report are ignored local data. A release tag, dataset and
   licence are author decisions.
4. **Anonymity**: the snapshot contains author names and the repository URL;
   the published Git history contains a local directory name from an earlier
   commit. Relevant only if the venue is double blind.
5. **Overleaf compile**: the author confirms the clean compile; the local build
   fails inside `\end{algorithm}` for REVTeX/algorithm reasons that predate this work.
6. **Claims-to-evidence table** (each number in the text traced to a versioned
   file) is the next deliverable, then the point-by-point response.

## Not claimed

No new circuit execution, certified numerics, component priority, resource
benchmark against the literature, or security statement is introduced or implied
by this audit. R8 stays a supported positioning with acknowledged acceptance risk.

## Update after the final export (2026-10-26 14:12)

- Open item 1 (implicit motivation) is closed in the text: the Discussion now
  states that quantum order finding is studied as the quantum step of the signing
  pipeline, not as a faster route to the point order, citing the polynomial-time
  point-counting route.
- The theorem label `thm:speedup` was renamed `thm:resource_bound` in all
  occurrences (cosmetic); no unresolved references remain.
- Snapshot record: paper/README.md, section "Post_P final", ZIP SHA-256
  `581e6c9d4feecf1dc8e64495c8f7830aa648775e67b0c476ca2a43fefb87aa1f`. Items 2 to 5 (reference [30] wording, data release, anonymity,
  compile) are unchanged: author or venue decisions, not text defects.

## Second update (15:09 export)

The motivation sentence was reworded by the author: no speedup claim over
classical point-order methods, point counting polynomial in l, order reduction
polynomial given the factorization of the group cardinality, factorization cost
accounted for separately (C_fact(M) in the complexity section; verified). ZIP
SHA-256 `cb6e627ee168bffd612c7d72edbdcd87c913cb6b90e6336dd1dd31bd100f6630`. Tag stage8-text-final points to the 14:12 text; see the
revision log for the tagging decision.
