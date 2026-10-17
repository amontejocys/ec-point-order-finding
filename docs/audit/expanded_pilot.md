# Historical expanded pilot

The indexed experiment is IDEAL noiseless postprocessing only, not execution of
the arithmetic circuit. Configuration: experiments/configs/expanded_curve_validation.json.
Its local report/NPZ live in results/legacy/r6/raw/ and are ignored by Git.
Hashes and summary are indexed in results/expanded-pilot/summary.json.
Retrieval of the large archive must be arranged at publication; no DOI is set.

Recorded sampling seed: 429931; 100 distinct sampled nonsingular curves per
prime, 10 primes, 100 recovery trials per instance, budgets 1,2,4,8,16,32,64.
The historical generation environment records Python 3.11.5 and NumPy 2.1.3.
Sampling is not a uniform distribution over curve isomorphism classes or point
orders, and aggregate rates are descriptive, not universal guarantees.

This experiment supplies examples of nonminimal gcd candidates. It does not
implement M1, validate a secure signature scheme, or demonstrate quantum speedup.
Do not replace the historical result with a new run under the same identifier.
