"""Interface checks need neither Qualtran nor its optional dependencies."""

import copy
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    'm2_shared_domain_probe', ROOT / 'experiments/scripts/m2_shared_domain_probe.py')
probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe)


@pytest.fixture
def config():
    return json.loads((ROOT / 'experiments/configs/m2_shared_domain.json').read_text())


def test_shared_configuration(config):
    probe.validate_config(config)
    assert len(config['cases']) == 7


def test_reject_sentinel_collision(config):
    config['curve'] = {'p': 7, 'a': 1, 'b': 0}
    with pytest.raises(ValueError, match='sentinel collision'):
        probe.validate_config(config)


def test_reject_wrong_point_or_duplicate_id(config):
    wrong = copy.deepcopy(config)
    wrong['cases'][0]['point'] = [1, 1]
    with pytest.raises(ValueError, match='not on'):
        probe.validate_config(wrong)
    config['cases'][1]['id'] = config['cases'][0]['id']
    with pytest.raises(ValueError, match='unique'):
        probe.validate_config(config)


def test_reject_composite_modulus_or_bad_window(config):
    wrong = copy.deepcopy(config)
    wrong['curve']['p'] = 15
    with pytest.raises(ValueError, match='prime'):
        probe.validate_config(wrong)
    config['qualtran_window'] = 2
    with pytest.raises(ValueError, match='divide'):
        probe.validate_config(config)


def test_identity_adapters_are_not_raw_bit_comparisons():
    assert probe.encode_local(None, 5) == 1
    assert probe.encode_local((0, 0), 5) == 0
    class IdentityMontgomery:
        @staticmethod
        def montgomery_to_uint(value):
            return value
    assert probe.decode_qualtran(0, 0, IdentityMontgomery()) is None
    assert probe.decode_qualtran(15, 13, IdentityMontgomery()) == (15, 13)


def test_classical_output_tuple_uses_signature_order():
    circuit = SimpleNamespace(
        signature=SimpleNamespace(rights=lambda: [SimpleNamespace(name='x'),
                                                  SimpleNamespace(name='a')]),
        call_classically=lambda **inputs: (inputs['a'] + 1, inputs['a']))
    assert probe.call_outputs(circuit, {'a': 4}) == {'x': 5, 'a': 4}
