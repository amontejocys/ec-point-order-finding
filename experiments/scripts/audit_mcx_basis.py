"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import argparse
from collections import Counter
import json
from pathlib import Path
from quantum_ec.circuits.order_finding.elliptic_order_finding import EllipticOrderFinding
from quantum_ec.resources.mcx_basis import basis_resources, control_profile
from quantum_ec.resources.resource_model import compact_controlled_point_resources, compact_scalar_resources


class ReportingBuilder(EllipticOrderFinding):
    def _adder(self, point):
        fresh = point not in self._gates
        if fresh:
            print(f"Building real arithmetic for A={point}...", flush=True)
        gate = super()._adder(point)
        if fresh:
            print(f"Built A={point}: {len(gate.definition.data)} instructions.", flush=True)
        return gate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--small", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
    parameters = (3, 5, 1, 1, (2, 1)) if args.small else (5, 29, 0, 7, (6, 7))
    builder = ReportingBuilder(*parameters, evaluator_variant="compact")
    circuit = builder.scalar_update()
    active = [p for p in builder.powers if p is not None]
    if len(active) != len(circuit.data):
        raise AssertionError("Unexpected scalar chain")
    profiles = {}
    total = Counter()
    records = []
    for instruction, point in zip(circuit.data, active):
        definition = instruction.operation.definition
        if point not in profiles:
            profiles[point] = control_profile(definition)
        profile = profiles[point]
        expected = compact_controlled_point_resources(builder.width, builder.modulus,
                                                       builder.a, builder.b, *point)
        if sum(profile.values()) != expected["total_instructions"] or definition.num_qubits != expected["total_qubits"]:
            raise AssertionError("Analytic model does not match actual circuit")
        total.update(profile)
        records.append({"point": point, "resources": basis_resources(profile, definition.num_qubits)})
    expected = compact_scalar_resources(builder.width, builder.modulus, builder.a, builder.b, builder.powers)
    if sum(total.values()) != expected["total_instructions"] or circuit.num_qubits != expected["total_qubits"]:
        raise AssertionError("Scalar resources do not match")
    result = {
        "scope": "scalar_update arithmetic only; excludes preparation, H, IQFT, measurements, classical work, and shots",
        "basis": "X,CX,CCX with exact full-Toffoli clean AND chains",
        "method": "actual gate-arity histogram plus verified expansion formula, not a scheduled or materialized large lowered circuit",
        "parameters": {"m": builder.m, "p": builder.modulus, "a": builder.a, "b": builder.b, "point": builder.point},
        "control_profile": dict(sorted(total.items())),
        "resources": basis_resources(total, circuit.num_qubits),
        "per_addition": records,
    }
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
