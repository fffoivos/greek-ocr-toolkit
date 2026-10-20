"""Bounded worker-only throughput pilot using the already-qualified pipeline.

This is not a serial speedup or a population-accuracy qualification.
"""
import argparse
from collections import Counter
import json
import os
from pathlib import Path
import sys
import time

p = argparse.ArgumentParser()
p.add_argument('--projects', type=Path, required=True)
p.add_argument('--root', type=Path, required=True)
p.add_argument('--configs', type=Path, nargs='+', required=True)
p.add_argument('--out', type=Path, required=True)
p.add_argument('--per-parent', type=int, default=2048)
a = p.parse_args()
sys.path.insert(0, str(a.projects / 'greek-ocr-toolkit-sol-recut'))
sys.path.insert(0, str(a.projects / 'greek-ocr-toolkit-sol-recut/scripts/harvest/clariden'))
from worker import sample, worker_guard, environment, scientific_decision
from greekocr.harvest.line_pipeline_census import run, atomic_json, file_sha, records
from greekocr.harvest.line_pipeline import canonical, digest

worker_guard()
assert 1 <= a.per_parent <= 4096
a.out.mkdir(parents=True, exist_ok=False)
parent, count = sample(a.root, a.out, a.per_parent, True)
timings = []
baseline = None
for config_path in a.configs:
    config = json.loads(config_path.read_text())
    qualification = json.loads((config_path.parent / 'qualification.json').read_text())
    assert qualification['status'] == 'PASS' and qualification['ordered_decisions_equal']
    assert any(v['workers'] == config['native_workers']
        and v['prefetch_factor'] == config.get('native_prefetch_factor', 2)
        for v in qualification['timings'])
    case = a.out / f'w{config["native_workers"]}_pf{config.get("native_prefetch_factor", 2)}'
    case.mkdir(exist_ok=False)
    config['parents'] = [dict(id='bound-native-qualification', format='canonical',
        path=str(parent), sha256=file_sha(parent), rows=count)]
    config['corrections'] = []
    atomic_json(case / 'config.json', config)
    started = time.monotonic()
    summary = run(config, case / 'measurement', execute=True)
    wall = time.monotonic() - started
    runtime = json.loads((case / 'measurement/runtime.json').read_text())
    segmentation = Counter()
    scientific = []
    for _, decision in records(case / 'measurement/decisions.jsonl'):
        scientific.append(scientific_decision(decision))
        for stage in decision.get('stages', []):
            if stage['stage'] == 'segmentation':
                segmentation[stage['result']['verdict']] += 1
    valid = (summary['complete'] and runtime['native_attempts'] == count
        and len(scientific) == count and sum(segmentation.values()) == count and segmentation['KEEP'] > 0
        and not any(runtime.get(k) for k in
            ['cached_measurements', 'invalid_cache_entries', 'unavailable', 'cleanup_errors']))
    entry = dict(status='PASS' if valid else 'FAIL', base_config_sha256=file_sha(config_path),
        config_sha256=file_sha(case / 'config.json'), workers=config['native_workers'],
        prefetch_factor=config.get('native_prefetch_factor', 2), wall_seconds=wall,
        rows_per_second=count/wall, segmentation_verdicts=dict(segmentation),
        dispositions=summary['dispositions'], runtime=runtime, decision_digest=digest(canonical(scientific)))
    timings.append(entry)
    atomic_json(a.out / 'timings.partial.json', timings)
    assert valid, 'Fresh pilot failed; inspect retained per-row decisions, do not promote throughput.'
    if baseline is None:
        baseline = scientific
    else:
        assert scientific == baseline, 'Pilot worker counts changed ordered scientific results'
result = dict(status='PASS', scope='longer fresh throughput pilot; no serial speedup or accuracy claim',
    source_manifest_sha256=file_sha(a.projects / 'SHA256SUMS'),
    pilot_script_sha256=file_sha(Path(__file__)), sample_sha256=file_sha(parent),
    environment=environment(a.root), affinity_cpus=len(os.sched_getaffinity(0)),
    rows=count, ordered_decisions_equal=True, timings=timings,
    equality_exclusions=['run_binding_sha256', 'segmentation.result.frame.orientation.evidence.seconds'])
atomic_json(a.out / 'throughput.json', result)
print(json.dumps(result), flush=True)
