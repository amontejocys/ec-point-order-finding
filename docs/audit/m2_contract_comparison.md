# M2: local contract versus corrected Qualtran reference

Date: 2026-10-18. Status: source inspection, not a novelty decision.
Object of the paper: the existing hybrid point-order recovery and signing process.
The cost analysis remains part of its characterization, not a demonstrated
general speed advantage over the best classical routes. Title and manuscript
structure remain unchanged; no experiment or contribution is approved here.

## Reproducible reference

Repository: https://github.com/quantumlib/Qualtran
Revision: dc144806e9654e49398974fe2ccc7a24813a80f3.
GitHub path history identifies it as the latest ec_add.py change at inspection.
The revision is fixed for this comparison, not a claim about future main.
The paper links corrective PRs 1489 and 1666; GitHub reports both merged:
6cc6523f63ca55ec27be0a9c6a73e91bbac139f2 and
0f88a0bd72e09a99a24b152e2e491123fe200bcb, respectively.

Downloaded four files without installing or executing Qualtran. SHA-256:

| File under qualtran/bloqs/cryptography/ecc/ | SHA-256 |
| --- | --- |
| ec_add.py | faa6b44f15f6a7aa16c9392fd360ad73431fb5eff4330ad06a0dcd24657ea8c1 |
| ec_add_test.py | 6ab55a6433e790c6206d54c948f9373a47e13c43005e2caf7555d1249a758202 |
| ec_point.py | bae414df2950c34204d265741288ebcd14ce6525edf2f8211b29a0098fa51ae3 |
| ec_point_test.py | 4156ce8614a4c195dcef8b34642ef268facce627d460bfc2e5b287e77ea83bfd |

Pinned source base:
https://github.com/quantumlib/Qualtran/tree/dc144806e9654e49398974fe2ccc7a24813a80f3/qualtran/bloqs/cryptography/ecc

## Reference findings (static inspection only)

- ec_add.py: ECAdd (1045), build_composite_bloq (1091),
  on_classical_vals (1144). Montgomery-valued point/slope registers and six-step
  decomposition; flags use zero-coordinate sentinels. The top-level classical
  action computes a group sum, so calling it alone would not validate cleanup
  in the decomposed circuit. No local fixed-invalid-encoding contract is stated.
- ec_point.py: ECPoint.inf (48-50) assigns (0,0) to infinity. This encoding
  cannot also distinguish the finite point (0,0) on curves containing it.
  This is a representation boundary, not a bug on the intended domain.
- ec_add_test.py: helpers at 36 and 158 compare classical and decomposed
  actions. Tests at 251 and 277 use a 12-by-7 point grid, including (3,0),
  on y^2=x^3+7 mod 17. Fast tests at 210 and 221 add a second curve.
  Therefore 'no order-two tests' and 'only one curve' are incorrect descriptions
  of this pinned software. These are source observations, not tests run here.

The paper's test description is not a substitute for inspecting a later revision
of its software. Do not infer complete coverage from any selected-input test.

## Local contract and witnesses

Local baseline: m1-complete, 6e5a775; circuit source unchanged by M1.

- point_encoding_check.py:point_encoding_check separates finite (0,x,y) from
  the canonical identity (1,0,0), and checks finite coordinates/curve membership.
- point_addition_cases.py:point_addition_cases makes valid branches disjoint,
  giving opposite priority when A=-A, and rejects invalid constant points.
- point_sum_evaluator_compact.py:point_sum_evaluator_compact handles v=0
  without inverting 2v and fixes invalid encodings. point_add_inplace clears
  the old point through inverse translation; controlled_point_add controls all
  operations. These are existing local contracts, not newly invented methods.
- tests/exhaustive/test_point_add_inplace.py:test_order_two_constant already
  uses p=5, a=1, b=0, A=(0,0). Its five selected encodings include finite
  (0,0), identity, other valid points and a noncanonical identity.
  This is not exhaustive coverage of that curve's full encoding domain.

Re-executed the existing local test, without cache/bytecode writes:
`python -m pytest tests/exhaustive/test_point_add_inplace.py::PointAddInplaceTests::test_order_two_constant -m slow -p no:cacheprovider -q`.
Result: 1 passed in 35.22 seconds, Python 3.11.5 / pinned migration environment.
An initial invocation without `-m slow` deselected the test; it was not a pass.
No new coverage or full-suite rerun is implied by this focused check.

Mathematical witness for relevance inside order recovery (not a circuit run):
on E/F7: y^2=x^3+x, P=(1,3) satisfies 2P=(0,0), 4P=O and P has order four.
Indeed the doubling slope is 4/6=3 mod 7, giving (0,0). Thus an orbit needed
for unknown-order recovery can contain both the finite origin and infinity.
An injective encoding must distinguish them. This example belongs to general
order recovery; M1 correctly rejects its composite order for signing. It is
not evidence of a useful secure signing domain or a new group-theoretic result.

## Decision implications

1. Remove order-two handling as a proposed difference in itself: the reference
   has such tests. Arbitrary invalid encodings and a finite-origin/identity
   distinction remain narrower contract differences to investigate.
2. A flag bit or a fixed-invalid extension alone is not established novelty.
   Off-domain behavior is not encountered in the ideal orbit; it does not imply
   noise correction, fault tolerance or a recovery advantage.
3. A possible supporting result is a reusable-domain contract verified on the
   real circuit and on full small domains, with explicit overhead and orbit
   checks. It must be compared to other representations/adaptations before
   calling it an advance. Sentinel replacement is an obvious competing option.
4. If investigating exception impact, compare fair initialization and include
   a corrected complete reference. Failure of a generic-only circuit does not
   establish superiority over an existing complete construction.

## Common semantic interface for the next comparison

Use a nonsingular curve over prime p>3, a finite constant A on it and abstract
points R in E(Fp), including infinity. For control c, the target action is
(c,R) -> (c,R+cA), preserving c and restoring initially zero workspace.
Translate abstract points to each implementation's native representation;
Montgomery conversion and any identity adapter are part of the interface.
Do not feed the same raw bit strings to incompatible encodings.

- Shared domain: curves/points encodable injectively by both native interfaces;
  compare ordinary, equal, opposite and identity inputs there.
- Extension domain: curves with a finite (0,0) require a changed sentinel,
  coordinate transform or identity flag in the reference. Account for that
  adaptation; do not report rejection outside its native domain as a defect.
- Invalid strings: assess separately. They are not part of a comparison of
  abstract group addition unless both sides explicitly promise an extension.
- Verification levels: distinguish top-level classical action, composed steps,
  primitive decomposition and actual reversible gates, including phases.
  Comparing our gates only with a reference's mathematical shortcut is not a
  common-depth correctness or resource comparison.
- Resources: report adapters, control construction, workspace and cleanup in
  the same gate basis; do not subtract published ECDLP/amortized costs from
  local single-addition costs. No such counts were measured in this pass.

Next bounded check: identify which pinned reference decompositions can be run
on this shared domain. Freeze parameters and acceptance criteria before the main run.
Do not install Qualtran into the locked project environment. No reference suite,
reference resource counts or external quantum phases were executed in this pass.
R8 remains open; no manuscript change follows from this note alone.

## Second-reader verification (2026-10-18)

- Commit dc144806 exists (2026-08-11, "Fix various typos in different files
  (#1931)"). PR 1489 "Fix bugs in ECAdd bloq" merged 2025-03-06 as 6cc6523f;
  PR 1666 "Fix additional bug in ECAdd" merged 2025-08-22 as 0f88a0bd, that is,
  after Papa v2 (2025-07-14): the paper does not describe the last repair.
- The four files were re-downloaded at the pinned revision; all SHA-256 values
  above reproduce. Anchors confirmed: ECAdd 1045, build_composite_bloq 1091,
  on_classical_vals 1144; ECPoint.inf returns (0,0) at 48-50; helpers at 36 and
  158; slow grids at 251 and 277 use 12 (a,b) pairs including infinity (0,0) and
  the order-two point (3,0) against 7 (x,y) points on y^2 = x^3 + 7 mod 17
  (comment at 182 names the p1707 source); fast second-curve tests at 210 and
  221 use y^2 = x^3 + 9 mod 17 with (0,0) as infinity.
- On both tested curves (b = 7 and b = 9) the finite point (0,0) does not exist,
  so the sentinel is unambiguous there; the F7 witness below (b = 0) is where it
  is not. Witness recomputed: P = (1,3), 2P = (0,0), 3P = (1,4), 4P = O.
- The reference tests compare the top-level classical action with the composed
  step actions; they are not gate-level reversible propagation. The verification
  levels listed in the common interface therefore matter for any comparison.
- The downgrade of candidate A in docs/decisions/m2_candidate_options.md is
  accepted by the second reader: with the Proos-Zalka random offset the first
  addition is no longer exceptional even when the order is unknown, so the fair
  baseline must include that offset. Exceptional inputs R_j = +-P_j still occur
  at roughly one scalar in r per stage, so the hypothesis survives for small or
  composite r, but only as a hypothesis to be measured against a fair baseline.
