"""Migrated from R5/R6; see docs/audit/migration_manifest.json. No M1 changes."""

import argparse
import json
import math
from pathlib import Path
import platform
import numpy as np
from quantum_ec.recovery.factor_free_recovery import uniform_register_size, recover_prefixes
from quantum_ec.simulation.ideal_distribution import ideal_probabilities
from experiments.reference.curve import reference_order


def sample_instances(rng, primes, per_prime):
    if not primes or len(set(primes)) != len(primes):
        raise ValueError("Provide distinct primes")
    if not isinstance(per_prime, int) or isinstance(per_prime, bool) or per_prime < 1:
        raise ValueError("per_prime must be positive")
    for p in primes:
        if (not isinstance(p, int) or isinstance(p, bool) or not 3 < p <= 101
                or any(p % d == 0 for d in range(2, math.isqrt(p)+1))):
            raise ValueError("This enumeration benchmark supports primes 5..101 only")
        available = sum((4*a**3+27*b*b) % p != 0 for a in range(p) for b in range(p))
        if per_prime > available:
            raise ValueError("Requested more distinct curves than available")
    instances = []
    for p in primes:
        selected = set()
        while len(selected) < per_prime:
            a, b = map(int, rng.integers(0, p, size=2))
            if (a, b) in selected or (4*a**3+27*b*b) % p == 0:
                continue
            points = [(x, y) for x in range(p) for y in range(p)
                      if (y*y-x**3-a*x-b) % p == 0]
            if not points:
                continue
            selected.add((a, b))
            point = points[int(rng.integers(len(points)))]
            instances.append({"p": p, "a": a, "b": b, "point": point,
                              "reference_group_size": len(points)+1,
                              "reference_order": reference_order(point, p, a),
                              **uniform_register_size(p)})
    return instances


def wilson_interval(successes, trials):
    """Approximate 95% interval for repeated trials on ONE fixed instance."""
    z = 1.959963984540054
    rate = successes/trials
    denominator = 1+z*z/trials
    center = (rate+z*z/(2*trials))/denominator
    radius = z*math.sqrt(rate*(1-rate)/trials+z*z/(4*trials*trials))/denominator
    return [max(0.0, center-radius), min(1.0, center+radius)]


def run_pilot(per_prime=20, trials=100, seed=20261008, primes=None):
    if trials < 1:
        raise ValueError("trials must be positive")
    primes = [11, 17, 23, 29, 41] if primes is None else primes
    budgets = [1, 2, 4, 8, 16, 32, 64]
    streams = np.random.SeedSequence(seed).spawn(2)
    instances = sample_instances(np.random.default_rng(streams[0]), primes, per_prime)
    sampler = np.random.default_rng(streams[1])
    measurements_all = []
    rows = []
    for index, instance in enumerate(instances):
        p, a, point, q, order = (instance[k] for k in
                               ("p", "a", "point", "q", "reference_order"))
        measurements = sampler.choice(q, size=(trials, max(budgets)),
                                      p=ideal_probabilities(q, order))
        measurements_all.append(measurements)
        counts = {t: {"exact": 0, "nonminimal_multiple": 0, "no_candidate": 0}
                  for t in budgets}
        cache = {}
        for trial in measurements:
            for t, period in recover_prefixes(trial, q, point, p, a, budgets, cache).items():
                if period is None:
                    category = "no_candidate"
                elif period == order:
                    category = "exact"
                else:
                    if period % order:
                        raise AssertionError("Recovery invariant failed")
                    category = "nonminimal_multiple"
                counts[t][category] += 1
        results = [{"shots": t, **counts[t],
                    "exact_rate": counts[t]["exact"]/trials,
                    "fixed_instance_wilson_95": wilson_interval(counts[t]["exact"], trials)}
                   for t in budgets]
        rows.append({**instance, "results": results})
        print(f"Instance {index+1}/{len(instances)}: p={p}, r={order}", flush=True)
    summary = []
    for t in budgets:
        totals = {name: sum(next(r for r in row["results"] if r["shots"] == t)[name]
                            for row in rows)
                  for name in ("exact", "nonminimal_multiple", "no_candidate")}
        rates = [next(r for r in row["results"] if r["shots"] == t)["exact_rate"]
                 for row in rows]
        summary.append({"shots": t, **totals, "trials": len(rows)*trials,
                        "exact_rate": totals["exact"]/(len(rows)*trials),
                        "worst_instance_exact_rate": min(rates)})
    report = {"scope": "Ideal noiseless postprocessing only; no circuit execution",
              "seed": seed, "numpy": np.__version__, "python": platform.python_version(),
              "primes": primes, "curves_per_prime": per_prime, "trials_per_instance": trials,
              "sampling": "Uniform nonsingular (a,b), distinct per p; uniform finite P per curve",
              "minimality_certified_by_recovery": False,
              "interval_scope": "Per-instance Wilson only; pooled rate is descriptive, not a universal guarantee",
              "cache_scope": "Simulation acceleration only; do not treat cached verification as per-run resource savings",
              "summary": summary, "instances": rows}
    strata = []
    for dimension in ('p', 'order_parity', 'order_type'):
        groups = {}
        for row in rows:
            order = row['reference_order']
            value = (row['p'] if dimension == 'p' else
                     ('even' if order % 2 == 0 else 'odd') if dimension == 'order_parity' else
                     ('prime' if all(order % d for d in range(2, math.isqrt(order)+1)) else 'composite'))
            groups.setdefault(value, []).append(row)
        for value, group in groups.items():
            for t in budgets:
                results = [next(r for r in row['results'] if r['shots'] == t) for row in group]
                totals = {name: sum(r[name] for r in results)
                          for name in ('exact', 'nonminimal_multiple', 'no_candidate')}
                strata.append({'dimension': dimension, 'value': value, 'shots': t,
                               'instances': len(group), 'trials': len(group)*trials, **totals,
                               'exact_rate': totals['exact']/(len(group)*trials),
                               'worst_instance_exact_rate': min(r['exact_rate'] for r in results)})
    report['descriptive_strata'] = strata
    return report, np.asarray(measurements_all)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--per-prime", type=int, default=20)
    parser.add_argument("--trials", type=int, default=100)
    parser.add_argument("--seed", type=int, default=20261008)
    parser.add_argument("--primes", type=int, nargs='+')
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
    report, measurements = run_pilot(args.per_prime, args.trials, args.seed, args.primes)
    args.output.write_text(json.dumps(report, indent=2)+"\n", encoding="ascii")
    np.savez_compressed(args.output.with_suffix(".npz"), measurements=measurements)
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
