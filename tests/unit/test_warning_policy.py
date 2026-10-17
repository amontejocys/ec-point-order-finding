"""Test pytest's project warning filters; direct unittest execution is skipped."""

import os
import unittest
import warnings


class WarningPolicyTests(unittest.TestCase):
    def setUp(self):
        if 'PYTEST_CURRENT_TEST' not in os.environ:
            self.skipTest('Requires pytest and the project filterwarnings configuration')

    def test_known_mcx_warning_only(self):
        message = ('The method ``qiskit.circuit.library.standard_gates.x.MCXGate.'
                   'get_num_ancilla_qubits()`` is pending deprecation as of Qiskit 1.3.')
        with warnings.catch_warnings(record=True) as caught:
            warnings.warn_explicit(message, PendingDeprecationWarning, 'dependency.py', 1,
                                   module='qiskit.circuit.library.standard_gates.x')
            warnings.warn_explicit('Different pending deprecation', PendingDeprecationWarning,
                                   'dependency.py', 2,
                                   module='qiskit.circuit.library.standard_gates.x')
        self.assertEqual([str(w.message) for w in caught], ['Different pending deprecation'])


if __name__ == '__main__':
    unittest.main()
