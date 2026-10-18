# M1: order admission before experimental signing

## Scope and status

Implement the signing boundary without changing recovery, reversible arithmetic,
QFT, or historical data. Code and tests are recorded in results/m1/. Ariel alone
integrates manuscript corrections in Overleaf and creates commits/tags. M1 is
not fully closed until the manuscript changes have been reviewed and integrated.
This correction does not close R8 or establish a new primality algorithm.

## Mathematical reason

Assume P is a valid nonidentity point on a nonsingular elliptic curve over a
prime field. If vP=O then r=ord(P) divides v. If v is prime, its only positive
divisors are 1 and v. Nonidentity excludes r=1, hence r=v. This needs neither
enumeration of the subgroup nor factoring the group order.

Every nonminimal multiple v=kr with k>=2 and r>=2 is composite. General recovery
is still permitted to return composite orders or multiples; signing rejects
them. True composite point orders remain legitimate order-finding test cases.

## Implementation and error contract

- classical/primality.py implements standard Miller-Rabin (HAC Algorithm 4.24).
  The listed small primes are accepted exactly and detected divisors rejected.
  Otherwise 64 independent uniform bases in [2,v-2] are drawn with secrets.
- For a fixed odd composite input, false acceptance is at most 4^-64 = 2^-128,
  under the independent uniform-base assumption (HAC Fact 4.25). This is NOT
  the posterior probability that an accepted candidate is composite. A union
  bound over N such tests is N*2^-128, capped at 1; keep it separate from the
  quantum recovery error budget. No arbitrary-size primality certificate is issued.
- signing/admission.py checks candidate type/range, nonidentity canonical point,
  the Hasse upper bound, primality and vP=O. If b is supplied it checks the curve
  equation and nonsingularity too. Field primality remains a caller precondition.
  If b is omitted, on-curve validity is also a precondition. The pipeline supplies b.
- Result status is admitted, recovery_failure or order_not_admissible_for_signing.
  Reason codes distinguish missing candidate, composite, wrong annihilator and
  invalid point/curve inputs. Exact small-prime admission and probable-prime
  admission have different order_assurance metadata.
- signing_attempt preserves (r_sigma,s) and None for nonce retry, but now raises
  OrderAdmissionError (a ValueError subtype) for recovery/admission failure,
  before nonce multiplication. Existing invalid-order callers still see ValueError.
- The toy function repeats admission per call, avoiding an unchecked bypass.
  It does not cache randomized primality results or claim constant-time behavior.
  Complete ECDSA domain generation, approved curves, secure nonces, key handling,
  hashing, and side-channel protections are outside this experimental helper.

## Evaluation boundary

signature_integration sends every recovered value to signing, including missing
and nonminimal values. The known reference order only scores recovery and checks
signatures; it is not used to decide whether signing runs. The former evaluator
skipped nonminimal candidates using the reference; that shortcut is removed.

The fixed p29 sample still uses z=2,d=2,k=1. The inadmissible candidate 10 now
fails before signing instead of producing (6,4); candidate 5 still gives (1,4).
Miller-Rabin is randomized, so general experiments must record rounds and method,
not claim a seed reproduces OS randomness. The finite validation here has candidate
values <=56: all composites have listed small factors, and primes always pass.

## Costs

For an O(ell)-bit candidate bounded by Hasse, verifying vP=O costs O(ell^4)
under the paper's conservative classical arithmetic model. Miller-Rabin costs
O(kappa*ell^3) with schoolbook modular arithmetic. The constant-point equation
checks add no higher-order term. With kappa=64 fixed, order admission plus one
signing attempt remains O(ell^4). Over T executions the previous classical
O(ell^4+T*ell^5) upper bound is unchanged. The explanation must mention admission;
no quantum gate/resource counts or recovery budget are changed by this step.

## Attribution

- Menezes, van Oorschot, Vanstone, Handbook of Applied Cryptography, Chapter 4,
  Algorithm 4.24 and Fact 4.25: https://cacr.uwaterloo.ca/hac/about/chap4.pdf
- FIPS 186-5, Section 6.1: ECDSA domain parameters use a prime-order base point:
  https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.186-5.pdf

The bound and test are existing results, not novel contributions. The choice
of 64 rounds is an explicit implementation policy, not a FIPS-conformance claim.
