#!/usr/bin/env python3
"""Run the playbook's post-study checklist on a finished study.

Answers, in this order (the order matters: fix the study before reading it):
  1. What fraction of trials are infeasible, and where in the space are they?
  2. Is the search space large enough? (best points near a boundary)
  3. Was it sampled densely enough? (bootstrap of best-of-k by budget)
  4. Is max_train_steps right? (where retrospective checkpoint selection lands)
  5. Isolation table for the scientific hyperparameter (best trial per value/bucket)

Input: one JSON object per line (or CSV) per trial, with the hyperparameters,
an objective column (the BEST validation value reached during the trial, not
the final one), and optionally:
  status      "ok" | anything else = infeasible (NaN/inf objective also counts)
  best_step   step of the retrospectively selected checkpoint
  max_steps   max_train_steps of the trial
Pass the same SPACE.json used by quasi_random.py so boundaries are judged on
the scale the search was run on (log for LR, etc).

Usage:
  analyze_study.py results.jsonl --space SPACE.json --objective val_error \
      [--goal min|max] [--scientific optimizer] [--buckets 6] [--plots outdir]
Pure standard library; plots only if matplotlib imports.
"""
import argparse
import csv
import json
import math
import random
import statistics


def load(path):
    if path.endswith(".csv"):
        with open(path) as f:
            rows = list(csv.DictReader(f))
        for r in rows:
            for k, v in r.items():
                try:
                    r[k] = float(v)
                except (TypeError, ValueError):
                    pass
        return rows
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def unit(v, spec):
    """Position of v in [0,1] on the scale the space was searched on."""
    lo, hi = float(spec["min"]), float(spec["max"])
    s = spec.get("scale", "linear")
    if s == "log":
        return (math.log(v) - math.log(lo)) / (math.log(hi) - math.log(lo))
    if s == "one_minus_log":
        a, b = math.log(1 - hi), math.log(1 - lo)
        return 1 - (math.log(1 - v) - a) / (b - a)
    return (v - lo) / (hi - lo)


def feasible(r, obj):
    v = r.get(obj)
    if not isinstance(v, (int, float)) or math.isnan(v) or math.isinf(v):
        return False
    return r.get("status", "ok") in ("ok", "", None)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("results")
    ap.add_argument("--space", required=True)
    ap.add_argument("--objective", required=True)
    ap.add_argument("--goal", choices=["min", "max"], default="min")
    ap.add_argument("--scientific", help="hyperparameter to build an isolation table for")
    ap.add_argument("--buckets", type=int, default=6)
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--edge", type=float, default=0.1,
                    help="fraction of a dimension counted as 'near the boundary'")
    ap.add_argument("--plots", help="directory for basic hyperparameter axis plots")
    a = ap.parse_args()

    rows, space, obj = load(a.results), json.load(open(a.space)), a.objective
    sign = 1 if a.goal == "min" else -1
    ok = [r for r in rows if feasible(r, obj)]
    bad = [r for r in rows if not feasible(r, obj)]
    ok.sort(key=lambda r: sign * r[obj])
    print(f"# Study: {len(rows)} trials, {len(ok)} feasible, "
          f"{len(bad)} infeasible ({100 * len(bad) / max(len(rows), 1):.0f}%)")
    if not ok:
        print("No feasible trials: suspect a pipeline bug or a search space far "
              "outside the stable region. Stop and debug before re-running.")
        return
    if len(bad) > 0.5 * len(rows):
        print("WARNING: >50% infeasible. Narrow/reparameterize the space, or check "
              "for a bug; a big infeasible region also signals instability "
              "(see references/stability.md).")

    print(f"\n## 1. Infeasible region per hyperparameter")
    for n, spec in sorted(space.items()):
        if "values" in spec or not bad:
            continue
        bu = [unit(r[n], spec) for r in bad if isinstance(r.get(n), (int, float))]
        if bu:
            print(f"- {n}: infeasible trials span unit-range "
                  f"[{min(bu):.2f}, {max(bu):.2f}] (median {statistics.median(bu):.2f})")

    print(f"\n## 2. Boundary check (best {a.top} feasible trials)")
    top = ok[:a.top]
    flagged = False
    for n, spec in sorted(space.items()):
        if "values" in spec:
            vals = [r.get(n) for r in top]
            print(f"- {n}: top values {vals}")
            continue
        us = [unit(r[n], spec) for r in top]
        best_u = us[0]
        edge = None
        if best_u <= a.edge or sum(u <= a.edge for u in us) > len(us) / 2:
            edge = "LOW"
        if best_u >= 1 - a.edge or sum(u >= 1 - a.edge for u in us) > len(us) / 2:
            edge = "HIGH"
        mark = f"  <-- near {edge} boundary: expand the range this way" if edge else ""
        flagged |= bool(edge)
        print(f"- {n}: best at unit {best_u:.2f} (value {top[0][n]:.4g}); "
              f"top-{len(us)} unit range [{min(us):.2f}, {max(us):.2f}]{mark}")
    if flagged:
        print("  A best point on the edge of an infeasible region means instability "
              "may be blocking better values (try warmup/clipping before trusting it).")

    print(f"\n## 3. Sampling density (bootstrap of best-of-k over feasible trials)")
    rng = random.Random(0)
    vals = [r[obj] for r in ok]
    for k in sorted({k for k in (3, 6, 10, 20, len(vals)) if k <= len(vals)}):
        bests = sorted(min(sign * v for v in rng.choices(vals, k=k)) * sign
                       for _ in range(2000))
        q = lambda p: bests[int(p * (len(bests) - 1))]
        print(f"- k={k:>3}: median {q(.5):.4g}, IQR [{q(.25):.4g}, {q(.75):.4g}]")
    print("  If the IQR at your actual budget is wider than the improvement you are "
          "trying to detect (or than retrain variance), sample more trials.")

    steps = [(r["best_step"], r["max_steps"]) for r in ok[:max(a.top, 10)]
             if isinstance(r.get("best_step"), (int, float))
             and isinstance(r.get("max_steps"), (int, float)) and r["max_steps"] > 0]
    if steps:
        fr = [b / m for b, m in steps]
        print(f"\n## 4. Retrospective best-checkpoint position (top trials)")
        print(f"- best_step / max_steps: median {statistics.median(fr):.2f}, "
              f"range [{min(fr):.2f}, {max(fr):.2f}]")
        if max(fr) <= 0.10:
            print("  All in first 10%: max_train_steps is far too high.")
        elif min(fr) >= 0.75:
            print("  All in last 25%: likely benefit from training longer "
                  "(and re-tuning the decay schedule).")

    if a.scientific:
        n = a.scientific
        spec = space.get(n, {"values": sorted({r.get(n) for r in ok}, key=str)})
        print(f"\n## 5. Isolation table for {n} (best trial per value, nuisance HPs optimized away)")
        groups = {}
        for r in ok:
            if "values" in spec:
                key = r.get(n)
            else:
                u = min(unit(r[n], spec), 1 - 1e-9)
                key = int(u * a.buckets)
            groups.setdefault(key, []).append(r)
        for key in sorted(groups, key=str):
            g = groups[key]
            label = key if "values" in spec else (
                f"bucket {key} [{key / a.buckets:.2f},{(key + 1) / a.buckets:.2f})")
            print(f"- {label}: best {g[0][obj]:.4g} over {len(g)} trials")
        print("  Compare gaps against retrain (trial) variance before calling a winner; "
              "a value with few trials may just be under-tuned.")

    if a.plots:
        try:
            import os
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
        except Exception as e:  # noqa: BLE001
            print(f"\n(plots skipped: matplotlib unavailable: {e.__class__.__name__})")
            return
        os.makedirs(a.plots, exist_ok=True)
        for n, spec in sorted(space.items()):
            fig, ax = plt.subplots(figsize=(5, 3.5))
            xs = [r[n] for r in ok]
            ax.scatter(xs, [r[obj] for r in ok], s=14)
            ymax = max(r[obj] for r in ok) if sign == 1 else min(r[obj] for r in ok)
            bx = [r[n] for r in bad if n in r]
            if bx:
                ax.scatter(bx, [ymax] * len(bx), marker="x", color="red", label="infeasible")
                ax.legend()
            if spec.get("scale") == "log":
                ax.set_xscale("log")
            ax.set_xlabel(n)
            ax.set_ylabel(obj)
            fig.tight_layout()
            fig.savefig(os.path.join(a.plots, f"axis_{n}.png"), dpi=120)
            plt.close(fig)
        print(f"\nAxis plots written to {a.plots}/")


if __name__ == "__main__":
    main()
