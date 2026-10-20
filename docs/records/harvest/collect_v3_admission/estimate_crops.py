"""Seeded stratified 2,000-row CROPS3 measurement. No full-scale mode."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
import os
from pathlib import Path
import random
import statistics
import subprocess
import time

from stage_crops import INTERPRETER, W2_PARENT, sha, stage

BASE = Path(__file__).resolve().parent
SNAPSHOTS = Path.home() / 'Projects/collect-v3-data/snapshots'
FEATURES = SNAPSHOTS / 'W2_features_20261018_0524.jsonl'
SEED = 20261019


def stamp():
    return subprocess.check_output(['date', '+%Y-%m-%dT%H:%M:%S%z'],
                                   env=dict(os.environ, TZ='Europe/Athens'), text=True).strip()


def inventory(root):
    result = {}
    for parent, directories, files in os.walk(root):
        for name in directories + files:
            path = Path(parent) / name
            st = path.lstat()
            result[str(path)] = (st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    out = args.out.resolve()
    if out.exists():
        raise ValueError('measurement requires a fresh output tree')
    expected = next(line.split()[0] for line in (SNAPSHOTS / 'SHA256_20261018_0524.txt').read_text().splitlines()
                    if line.split()[-1] == FEATURES.name)
    # Hash in the same read-only pass used to build source populations.
    groups = defaultdict(list)
    h = hashlib.sha256()
    for line in FEATURES.open('rb'):
        h.update(line)
        row = json.loads(line)
        groups[row['source']].append({k: row[k] for k in ('id', 'source', 'crop_bbox', 'crop_sha256', 'tranche')})
    if h.hexdigest() != expected:
        raise ValueError('snapshot checksum mismatch')
    counts = {s: len(v) for s, v in groups.items()}
    assert sum(counts.values()) == 219381
    # Proportional allocation, at least two observations per source, largest remainder.
    allocation = {s: max(2, int(2000 * n / 219381)) for s, n in counts.items()}
    while sum(allocation.values()) < 2000:
        s = max(counts, key=lambda s: (2000 * counts[s] / 219381 - allocation[s], s))
        allocation[s] += 1
    rng = random.Random(SEED)
    selected = []
    for source in sorted(groups):
        selected.extend(dict(row, row_id=row['id'], parent_id=W2_PARENT, split='train',
                             decision={'disposition': 'ADMIT'})
                        for row in rng.sample(groups[source], allocation[source]))
    # This is a measurement selection, not a scientific admission decision.
    out.parent.mkdir(parents=True, exist_ok=True)
    admission = out.parent / 'estimate_selection.jsonl'
    admission.write_text(''.join(json.dumps(r, sort_keys=True) + '\n' for r in selected))
    run = Path.home() / 'Projects/collect-v3-data/run'
    before = inventory(run)
    started = stamp()
    start = time.perf_counter()
    receipt = stage(admission, FEATURES, out, minimum_free_gb=10)
    elapsed = time.perf_counter() - start
    if receipt['failures'] or receipt.get('disk_deferred') or receipt['count'] != 2000:
        raise ValueError('sample did not complete: ' + json.dumps(receipt))
    manifest = out.parent / 'crops_manifest.jsonl'
    rows = [json.loads(line) for line in manifest.read_text().splitlines()]
    expected_rows = {r['id']: r for r in selected}
    assert all(sha(out.parent / r['path']) == r['sha256'] == expected_rows[r['row_id']]['crop_sha256'] for r in rows)
    staged_before = inventory(out)
    manifest_before = manifest.read_bytes()
    second = stage(admission, FEATURES, out, minimum_free_gb=10)
    assert second['new_count'] == 0 and inventory(out) == staged_before and manifest.read_bytes() == manifest_before
    assert inventory(run) == before, 'live run metadata changed during sample and rerun'
    per_source = []
    total, variance = 0, 0
    for source in sorted(groups):
        values = [r['bytes'] for r in rows if r['source'] == source]
        mean = statistics.mean(values)
        n, N = len(values), counts[source]
        total += N * mean
        variance += N*N * (1-n/N) * statistics.variance(values) / n
        per_source.append(dict(source=source, population=N, sample=n, mean_bytes=mean,
                               median_bytes=statistics.median(values), p95_bytes=sorted(values)[math.ceil(.95*n)-1]))
    delta = 1.96 * math.sqrt(variance)
    result = dict(started_at=started, finished_at=stamp(), seed=SEED, sample_count=2000,
                  snapshot_sha256=expected, snapshot_rows=219381, output_root=str(out),
                  requested_output_root=str(Path.home() / 'Projects/collect-v3-data/crops_w2_estimate'),
                  location_limitation='requested destination denied by filesystem sandbox; sample generated under /private/tmp',
                  sources=per_source, estimated_bytes=total, ci95_bytes=[total-delta, total+delta],
                  interval_method='stratified normal mean interval with finite-population correction; row-level sampling, not page-cluster bootstrap',
                  proxy_share=28798/101098, admitted_proxy_bytes=total*28798/101098,
                  seconds=elapsed, seconds_per_1000=elapsed/2, all_rows_seconds=elapsed/2000*219381,
                  admitted_proxy_seconds=elapsed/2000*219381*28798/101098,
                  sample_byte_exact=True, idempotent_rerun=True, live_run_unchanged=True,
                  live_run_inventory_entries=len(before), tests_measurement=3)
    (BASE / 'CROPS3_ESTIMATE.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
