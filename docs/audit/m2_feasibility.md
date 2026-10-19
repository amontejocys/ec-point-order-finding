# M2 shared-domain feasibility probe

Date: 2026-10-18. Bounded engineering check authorized by the author.
Not the main evidence experiment or approval of any novelty candidate.
The paper remains about the existing hybrid process; no manuscript changes.

## Frozen inputs and implementation

- Config: experiments/configs/m2_shared_domain.json, recorded before the run.
- Driver: experiments/scripts/m2_shared_domain_probe.py.
- Curve y^2=x^3+7 mod 17, constants (15,13) and (3,0), seven selected cases.
- Cases include ordinary sum, doubling, opposites, identity and order-two inputs.
  They are not exhaustive over this curve, encodings or constants.
- Expected sums come from experiments/reference/curve.py:reference_add,
  independent of the production curve helper and Qualtran.
- The native shared domain excludes b=0: the reference uses (0,0) for infinity.
  Rejecting that unsupported domain in the driver is not a reference failure.
- Qualtran uses its tested n=7, window_size=1 configuration. Local coordinates
  use width 5. This is a semantic feasibility check, not a same-width benchmark.

The driver enforces hashes of installed ec_add.py/ec_point.py against the pinned
revision dc144806e9654e49398974fe2ccc7a24813a80f3. Source ZIP SHA-256:
4491f52ce89e1c622e178e7c1311e991cf93726f55342052f558938d5946c833.
File hashes and PR provenance are in m2_contract_comparison.md.

## Isolated reference environment

Qualtran 0.8.0.dev0 at this revision requires Python >=3.12. Used a separate
temporary Python 3.12.10 environment, not the project's Qiskit environment.
Installed the pinned source ZIP with --no-deps, then only the dependencies
needed for the selected import/simulation path. The environment is deliberately
partial: pip warns about uninstalled declared UI/notebook/other integrations.
Do not describe it as a fully dependency-complete Qualtran installation or
claim its full suite passes. Installed package versions are in qualtran.json.
No changes were made to pyproject.toml, requirements-lock.txt or global packages.

Reproduction uses a fresh isolated environment, the same source ZIP and the
versions recorded in results/m2-feasibility/qualtran.json (packages mapping).
Set PYTHONDONTWRITEBYTECODE=1; if needed set MPLCONFIGDIR and TEMP/TMP to writable
temporary directories outside the repository. Do not install into the project
environment. Exact commands for the probe, from the repository root:

```text
<isolated-qualtran-python> experiments/scripts/m2_shared_domain_probe.py --root . --config experiments/configs/m2_shared_domain.json --backend qualtran --output results/m2-feasibility/qualtran.json
<project-python> experiments/scripts/m2_shared_domain_probe.py --root . --config experiments/configs/m2_shared_domain.json --backend local --output results/m2-feasibility/local.json
```

Reports contain source/config/driver hashes, environments, checks and timings.
No username, local executable path or source ZIP filesystem URL is needed in the
versioned records. Source-tree fingerprint covers src only, not a whole commit.

## Verification levels

Qualtran runs three versions: top-level classical action, the six-step composed
action, and one further flattening of the step implementations. The latter
still has atomic modular multiplication/inversion blocks; report leaf_types
lists them. Cleanup assertions encountered in decomposed blocks are useful,
but this does not propagate every physical/logical primitive or verify phases.
Input point and precomputed slope registers are checked unchanged.

Local execution propagates actual positive-control X-family gates generated
by controlled_point_add with the compact evaluator. Both control values are
checked; full output equality includes zero-initialized work and control.
Qualtran's outer controlled wrapper is not tested by the native ECAdd probe.
These are deliberately different verification depths, not equal circuit proofs.

## Harness correction

The first reference invocation exposed a driver adapter mistake:
call_classically returns outputs as a tuple in signature order, not a dict.
Fixed call_outputs to name them using signature.rights and added a regression
test. The failed report is a temporary diagnostic, not evidence against Qualtran.
The corrected driver passes all 21 reference case/level checks. Six new unit
tests check configuration and representation/output adapters without Qualtran.

## Interpretation and next gate

Results: seven selected cases pass at all three reference levels (21 checks).
Local X-family propagation passes seven cases with both controls (14 checks),
including clean work. Reports: results/m2-feasibility/qualtran.json and local.json.
Six adapter/configuration unit tests pass separately; no full slow-suite rerun.
After integration, the project quick suite passed 61 tests in 1.36 seconds.
Run times in the two reports are not a performance comparison: verification
depth, register widths, controls and construction overhead differ.

No difference in mathematical outputs was observed in the corrected reference
probe. This does not prove universal correctness, novelty, gate-level cleanup,
noise resilience, resource superiority or full order-recovery behavior.

Use the feasible shared interface for a later common-depth comparison only
after specifying which subblocks must be decomposed. A full-domain local check
could improve artifact assurance, but is not automatically a research advance.
Do not expand to many curves or edit the manuscript based on this probe alone.
The finite-origin extension remains a contract difference requiring comparison
with a reference adaptation, not a demonstrated new algorithm. R8 is open.
