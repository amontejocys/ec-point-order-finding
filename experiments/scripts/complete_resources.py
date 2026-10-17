"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import argparse
import json
from pathlib import Path
from quantum_ec.resources.complete_resources import complete_quantum_resources
from quantum_ec.resources.complete_resources import classical_trace


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--arithmetic-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
    arithmetic = json.loads(args.arithmetic_report.read_text(encoding="utf-8"))
    parameters = arithmetic["parameters"]
    q = 1 << parameters["m"]
    rows = [classical_trace(y, q, tuple(parameters["point"]), parameters["p"], parameters["a"])
            for y in range(q)]
    result = {
        "parameters": parameters,
        "quantum": complete_quantum_resources(arithmetic),
        "classical_scope": "one recovered_orders call for each possible y; rows are NOT a shot-probability-weighted mean",
        "classical_limitations": "function-call counts are not field bit costs; trial factorization is not a scalable polynomial-time method",
        "classical_by_measurement": rows,
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["quantum"], indent=2))
    for y in (0, 3, 13, 15):
        if y < q:
            print(json.dumps(rows[y]))
    print(f"Recorded {q} classical postprocessing traces in {args.output}.")


if __name__ == "__main__":
    main()
