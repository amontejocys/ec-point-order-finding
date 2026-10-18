"""The numerical reference scores outcomes; it must not gate signing."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from experiments.scripts import signature_integration as replay


class SigningRecoveryGateTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.report = Path(self.directory.name) / 'report.json'
        self.arrays = Path(self.directory.name) / 'arrays.npz'
        self.report.write_text(json.dumps({'cases': [{
            'p': 29, 'a': 0, 'b': 7, 'point': [6, 7], 'q': 32,
            'reference_order_for_evaluation_only': 5,
        }]}), encoding='ascii')

    def test_nonminimal_candidate_reaches_the_gate_and_is_rejected(self):
        np.savez(self.arrays, measurements_0=np.asarray([[3, 15], [13, 0]]))
        with patch.object(replay, 'signing_attempt', wraps=replay.signing_attempt) as signer:
            result = replay.validate_saved_recoveries(self.report, self.arrays, shots=1)
        self.assertEqual(signer.call_count, 2)
        self.assertEqual([call.args[3] for call in signer.call_args_list], [10, 5])
        self.assertEqual(result['signing_admission']['counts'], {
            'admitted': 1, 'recovery_failure': 0, 'order_not_admissible_for_signing': 1})
        self.assertEqual(result['matching_verified_signatures'], 1)
        self.assertEqual(result['nonminimal_period'], 1)
        result = replay.validate_saved_recoveries(self.report, self.arrays, shots=2)
        self.assertEqual(result['signing_admission']['counts']['admitted'], 2)

    def test_absent_recovery_has_its_own_status(self):
        np.savez(self.arrays, measurements_0=np.asarray([[0, 0]]))
        result = replay.validate_saved_recoveries(self.report, self.arrays, shots=1)
        self.assertEqual(result['signing_admission']['counts']['recovery_failure'], 1)
        self.assertEqual(result['matching_verified_signatures'], 0)

    def test_saved_measurement_budget_is_enforced(self):
        np.savez(self.arrays, measurements_0=np.asarray([[13, 0]]))
        for shots in (0, -1, True, 1.5, 3):
            with self.assertRaises(ValueError):
                replay.validate_saved_recoveries(self.report, self.arrays, shots=shots)


if __name__ == '__main__':
    unittest.main()
