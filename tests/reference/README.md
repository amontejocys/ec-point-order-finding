# Independent references

encoding.py contains the inherited expected_sum_encoding implementation.
curve.py and signature.py expose the independent benchmark implementations in
experiments/reference/ without duplicating them. Neither benchmark calls the
production group law. Moving code does not itself prove independence or correctness.

Document the source and algorithm of each reference. Expected arithmetic must
not call the circuit under test or silently reuse the pipeline implementation.
Shared encoding or parsing helpers must be identified and justified.
For external group orders, record tool version, full curve parameters, and method.
Tests using the same arithmetic as the pipeline are consistency checks, not
independent arithmetic validation.
