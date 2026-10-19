"""Bounded semantic probe; Qualtran runs only in a separate audit environment."""

import argparse
from collections import Counter
import hashlib
import importlib.metadata
import inspect
import json
import math
from pathlib import Path
import platform
import sys
import time


def point_tuple(value):
    return None if value is None else tuple(value)


def validate_config(config):
    p, a, b = (config['curve'][key] for key in ('p', 'a', 'b'))
    if any(type(value) is not int for value in (p, a, b)) or p <= 3:
        raise ValueError('Use integer curve parameters with prime p > 3')
    if any(p % d == 0 for d in range(2, math.isqrt(p) + 1)):
        raise ValueError('Probe requires prime p')
    if (4*a**3 + 27*b*b) % p == 0:
        raise ValueError('Singular curve')
    if b % p == 0:
        raise ValueError('Shared native domain excludes finite-origin/sentinel collision')
    for key in ('local_width', 'qualtran_width', 'qualtran_window'):
        if type(config[key]) is not int or config[key] < 1:
            raise ValueError('Widths and window must be positive integers')
    if any((1 << config[key]) <= p for key in ('local_width', 'qualtran_width')):
        raise ValueError('Coordinate register too small')
    if config['qualtran_width'] % config['qualtran_window']:
        raise ValueError('Qualtran window must divide its width')
    seen = set()
    for case in config['cases']:
        if case['id'] in seen:
            raise ValueError('Case identifiers must be unique')
        seen.add(case['id'])
        if case['constant'] is None:
            raise ValueError('Local adder requires a finite constant')
        for value in (case['constant'], case['point']):
            if value is None:
                continue
            if (not isinstance(value, list) or len(value) != 2
                    or any(type(c) is not int or not 0 <= c < p for c in value)):
                raise ValueError('Noncanonical point')
            x, y = value
            if (y*y - x**3 - a*x - b) % p:
                raise ValueError('Point not on configured curve')


def decode_qualtran(x, y, dtype):
    point = (int(dtype.montgomery_to_uint(int(x))),
             int(dtype.montgomery_to_uint(int(y))))
    return None if point == (0, 0) else point


def encode_local(point, width):
    return 1 if point is None else (point[0] << 1) | (point[1] << (width + 1))


def call_outputs(circuit, inputs):
    names = [register.name for register in circuit.signature.rights()]
    return dict(zip(names, circuit.call_classically(**inputs), strict=True))


def source_hashes(root):
    files = sorted((path.relative_to(root).as_posix(), path)
                   for path in (root / 'src').rglob('*.py'))
    rows = [f'{name} {hashlib.sha256(path.read_bytes()).hexdigest()}'
            for name, path in files]
    return hashlib.sha256('\n'.join(rows).encode()).hexdigest()


def qualtran_variants(config):
    from qualtran import QMontgomeryUInt
    from qualtran.bloqs.cryptography.ecc import ec_add, ec_point

    observed = {}
    for module in (ec_add, ec_point):
        path = Path(inspect.getsourcefile(module))
        observed[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    if observed != config['reference_hashes']:
        raise ValueError('Installed reference files differ from pinned source hashes')
    n, p = config['qualtran_width'], config['curve']['p']
    bloq = ec_add.ECAdd(n=n, mod=p, window_size=config['qualtran_window'])
    six_steps = bloq.decompose_bloq()
    step_decompositions = six_steps.flatten_once()
    variants = [('classical_oracle', bloq), ('six_step_actions', six_steps),
                ('step_decompositions', step_decompositions)]
    census = {name: dict(sorted(Counter(type(i.bloq).__name__
              for i in circuit.bloq_instances).items()))
              for name, circuit in variants[1:]}
    return QMontgomeryUInt(n, p), variants, observed, census


def run(config, backend, root):
    from experiments.reference.curve import reference_add

    report = {'backend': backend, 'scope': config['purpose'],
              'python': platform.python_version(), 'platform': platform.system(),
              'project_source_sha256': source_hashes(root), 'cases': [],
              'packages': dict(sorted((d.metadata['Name'], d.version)
                                     for d in importlib.metadata.distributions()
                                     if d.metadata['Name']))}
    if backend == 'qualtran':
        dtype, variants, observed, census = qualtran_variants(config)
        report.update(reference_revision=config['reference_revision'],
                      reference_hashes=observed, leaf_types=census,
                      verification_level='Classical actions of blocks; not full gate propagation',
                      phases_verified=False, external_control_verified=False)
    else:
        from quantum_ec.circuits.points.controlled_point_add import controlled_point_add
        from tests.support.permutation import apply_basis, compile_x_permutation
        compiled = {}
        report.update(verification_level='X-family gate propagation with zero work',
                      phases_verified='X-family permutations have no relative phases')
    p, a, b = (config['curve'][key] for key in ('p', 'a', 'b'))
    for case in config['cases']:
        constant, point = point_tuple(case['constant']), point_tuple(case['point'])
        expected = reference_add(point, constant, p, a)
        row = {'id': case['id'], 'expected': expected, 'checks': []}
        if backend == 'qualtran':
            u, v = constant
            slope = 0 if v == 0 else (3*u*u+a)*pow(2*v, -1, p) % p
            x, y = (0, 0) if point is None else point
            inputs = dict(zip(('a', 'b', 'x', 'y', 'lam_r'),
                              (dtype.uint_to_montgomery(c) for c in (u, v, x, y, slope))))
            for name, circuit in variants:
                check = {'level': name}
                try:
                    output = call_outputs(circuit, inputs)
                    decoded = decode_qualtran(output['x'], output['y'], dtype)
                    preserved = all(output[k] == inputs[k] for k in ('a', 'b', 'lam_r'))
                    check.update(point=decoded, preserved_inputs=preserved,
                                 passed=decoded == expected and preserved)
                except Exception as error:
                    check.update(passed=False, error_type=type(error).__name__, error=str(error))
                row['checks'].append(check)
        else:
            width = config['local_width']
            if constant not in compiled:
                circuit = controlled_point_add(width, p, a, b, *constant,
                                               evaluator_variant='compact')
                compiled[constant] = compile_x_permutation(circuit)
            for control in (0, 1):
                initial = control | (encode_local(point, width) << 1)
                wanted = control | (encode_local(expected if control else point, width) << 1)
                output = apply_basis(compiled[constant], initial)
                row['checks'].append({'level': 'actual_gate_permutation', 'control': control,
                                      'passed': output == wanted,
                                      'work_clean': output >> (2*width+2) == 0})
        report['cases'].append(row)
        print(case['id'], all(c['passed'] for c in row['checks']), flush=True)
    report['passed'] = all(c['passed'] for row in report['cases'] for c in row['checks'])
    report['not_established'] = ['novelty', 'resource advantage', 'exhaustive coverage',
                                 'reference gate-level cleanup or phases', 'full order recovery']
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--backend', choices=('local', 'qualtran'), required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding='utf-8'))
    validate_config(config)
    sys.path.insert(0, str(args.root))
    sys.path.insert(0, str(args.root / 'src'))
    start = time.perf_counter()
    report = run(config, args.backend, args.root)
    report['wall_seconds'] = time.perf_counter() - start
    report['config_sha256'] = hashlib.sha256(args.config.read_bytes()).hexdigest()
    report['script_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    raise SystemExit(0 if report['passed'] else 1)


if __name__ == '__main__':
    main()
