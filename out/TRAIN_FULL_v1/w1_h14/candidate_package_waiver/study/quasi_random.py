#!/usr/bin/env python3
"""Generate trials for an exploration-phase study by quasi-random search.

Implements the playbook's preferred sampler: a randomly shifted, scrambled
Halton sequence ("jittered, shuffled grid search", Bousquet et al. 2017).
Pure standard library, so it runs anywhere (login nodes, broken local envs).

Search-space spec (JSON):
{
  "learning_rate": {"min": 1e-4, "max": 1e-1, "scale": "log"},
  "beta1":         {"min": 0.8,  "max": 0.99, "scale": "one_minus_log"},
  "weight_decay":  {"min": 1e-6, "max": 1e-2, "scale": "log"},
  "warmup_steps":  {"min": 100,  "max": 5000, "scale": "log", "type": "int"},
  "dropout":       {"min": 0.0,  "max": 0.3,  "scale": "linear"},
  "label_smooth":  {"values": [0.0, 0.1]}
}
Scales: linear | log | one_minus_log (samples 1-x on a log scale; use for
momentum / Adam betas, whose interesting region is near 1).
"values" gives a categorical/discrete dimension (sampled uniformly).

List the most important hyperparameter FIRST (usually the learning rate): dimensions
are assigned primes in file order and the smallest bases give the most even coverage
(Bousquet et al. 2017, Remark 2).

Below 10 trials a Latin hypercube is used instead (Bousquet et al.: low-discrepancy
sequences lose to LHS for budgets under ~10); override with --method.

Usage:
  quasi_random.py SPACE.json --trials 32 --seed 0 [--fixed fixed.json] > trials.jsonl
"""
import argparse
import json
import math
import random
import sys

PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61,
          67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113]


def scrambled_halton(n, dims, seed):
    """n points in [0,1)^dims: random digit permutation per base + random shift."""
    if dims > len(PRIMES):
        sys.exit(f"at most {len(PRIMES)} dimensions supported")
    rng = random.Random(seed)
    perms, shifts = [], []
    for b in PRIMES[:dims]:
        p = list(range(b))
        # Keep 0 -> 0 so trailing zero digits stay zero (finite expansion).
        tail = p[1:]
        rng.shuffle(tail)
        perms.append([0] + tail)
        shifts.append(rng.random())
    start = rng.randrange(1, 10_000)  # skip a random prefix of the sequence
    points = []
    for i in range(start, start + n):
        pt = []
        for d, b in enumerate(PRIMES[:dims]):
            k, f, x = i, 1.0 / b, 0.0
            while k > 0:
                x += perms[d][k % b] * f
                k //= b
                f /= b
            pt.append((x + shifts[d]) % 1.0)
        points.append(pt)
    return points


def latin_hypercube(n, dims, seed):
    """n points, one per stratum in every dimension, jittered within the stratum."""
    rng = random.Random(seed)
    cols = []
    for _ in range(dims):
        strata = list(range(n))
        rng.shuffle(strata)
        cols.append([(k + rng.random()) / n for k in strata])
    return [list(p) for p in zip(*cols)]


def transform(u, spec):
    if "values" in spec:
        vals = spec["values"]
        return vals[min(int(u * len(vals)), len(vals) - 1)]
    lo, hi = float(spec["min"]), float(spec["max"])
    scale = spec.get("scale", "linear")
    if scale == "linear":
        v = lo + u * (hi - lo)
    elif scale == "log":
        v = math.exp(math.log(lo) + u * (math.log(hi) - math.log(lo)))
    elif scale == "one_minus_log":
        a, b = math.log(1 - hi), math.log(1 - lo)
        v = 1 - math.exp(a + u * (b - a))
    else:
        sys.exit(f"unknown scale {scale!r}")
    if spec.get("type") == "int":
        v = int(round(v))
    return v


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("space")
    ap.add_argument("--trials", type=int, required=True)
    ap.add_argument("--seed", type=int, default=0,
                    help="study seed; record it so the study is reproducible")
    ap.add_argument("--fixed", help="JSON of fixed hyperparameters merged into every trial")
    ap.add_argument("--method", choices=["auto", "halton", "lhs"], default="auto",
                    help="auto = scrambled Halton for >=10 trials, Latin hypercube below")
    args = ap.parse_args()

    space = json.load(open(args.space))
    fixed = json.load(open(args.fixed)) if args.fixed else {}
    names = list(space)  # file order: most important first
    method = args.method
    if method == "auto":
        method = "halton" if args.trials >= 10 else "lhs"
    sampler = scrambled_halton if method == "halton" else latin_hypercube
    print(f"# method={method} dims={names}", file=sys.stderr)
    for i, u in enumerate(sampler(args.trials, len(names), args.seed)):
        trial = {"trial_id": i, "study_seed": args.seed, "sampler": method, **fixed}
        trial.update({n: transform(x, space[n]) for n, x in zip(names, u)})
        print(json.dumps(trial))


if __name__ == "__main__":
    main()
