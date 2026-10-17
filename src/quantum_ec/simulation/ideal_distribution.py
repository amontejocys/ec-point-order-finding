"""Ideal periodic-output reference distribution; does not execute a circuit."""

import numpy as np


def ideal_probabilities(q, order):
    """Trace orthogonal periodic output labels after exact IQFT.

    Q = L*r+t: t output fibers have L+1 inputs, the others have L.
    Each geometric sum contributes its squared modulus divided by Q**2.
    sinc evaluates the continuous limit safely at integer phase multiples.
    """
    if not 1 <= order <= q:
        raise ValueError("Expected 1 <= order <= q")
    length, extra = divmod(q, order)
    phase = ((order * np.arange(q, dtype=np.int64)) % q) / q
    phase = np.where(phase > 0.5, phase-1, phase)
    def magnitude_squared(n):
        return (n*np.sinc(n*phase)/np.sinc(phase))**2
    probabilities = (extra*magnitude_squared(length+1)
                     + (order-extra)*magnitude_squared(length)) / q**2
    if not np.isclose(probabilities.sum(), 1, atol=1e-10):
        raise AssertionError("Ideal probability normalization failed")
    return probabilities / probabilities.sum()
