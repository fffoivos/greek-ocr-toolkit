"""Job-2 inventory of saved SF6c evidence, per source and selected wave.

No inference or composition. Full-population decoding runs in the allocation;
only the complete 64-line verification fixture may run outside Slurm via CLI.
"""
import argparse
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import signal
import time

from scripts.labelfix.clariden import l1c_census as c

FIELDS = ('recognition_confidence', 'recognition_evidence', 'image_width')
STATES = ('missing_key', 'null', 'invalid', 'explicit')


def finite_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def field_state(record, key, valid):
    if key not in record:
        return 'missing_key'
    value = record[key]
    if value is None:
        return 'null'
    return 'explicit' if valid(value) else 'invalid'


def score_state(record):
    return field_state(record, 'recognition_confidence', lambda v: finite_number(v) and 0 <= v <= 1)


def empty_counts():
    keys = ['lines', 'slots', 'explicit_score_lines', 'explicit_score_slots',
            'above_floor_lines', 'above_floor_slots', 'regional_evidence_lines',
            'regional_evidence_slots', 'regional_evidence_regions',
            'sf6c_certified_slots', 'sf6c_certified_lines',
            'sf6c_predicate_error_slots', 'sf6c_predicate_error_lines']
    keys += [f'{field}_{state}_{unit}' for field in FIELDS for state in STATES for unit in ('lines', 'slots')]
    return Counter(dict.fromkeys(keys, 0))


def observe(record):
    # Call the frozen predicate for every slot, including omitted-score records.
    from greekocr.labelfix.release_gate import _recogniser_scored
    slots = record['detector']['slots']
    counts = empty_counts()
    counts.update(lines=1, slots=len(slots))
    states = {
        'recognition_confidence': score_state(record),
        'recognition_evidence': field_state(record, 'recognition_evidence',
            lambda v: isinstance(v, dict) and isinstance(v.get('regions'), list)
            and all(isinstance(r, dict) for r in v['regions'])),
        'image_width': field_state(record, 'image_width', lambda v: finite_number(v) and v > 0),
    }
    for key, state in states.items():
        counts[f'{key}_{state}_lines'] += 1
        counts[f'{key}_{state}_slots'] += len(slots)
    explicit = states['recognition_confidence'] == 'explicit'
    above = explicit and .5 < record['recognition_confidence'] <= 1
    counts['explicit_score_lines'] += explicit
    counts['explicit_score_slots'] += len(slots) if explicit else 0
    counts['above_floor_lines'] += above
    counts['above_floor_slots'] += len(slots) if above else 0
    regions = record['recognition_evidence']['regions'] if states['recognition_evidence'] == 'explicit' else []
    counts['regional_evidence_lines'] += bool(regions)
    counts['regional_evidence_regions'] += len(regions)
    starts = {r.get('start') for r in regions if isinstance(r.get('start'), int) and not isinstance(r['start'], bool)}
    counts['regional_evidence_slots'] += sum(s.get('start') in starts for s in slots)
    for slot in slots:
        try:
            eligible = _recogniser_scored(record, slot, slot.get('evidence', {}).get('window'))
        except (AttributeError, TypeError, KeyError, ValueError, IndexError, OverflowError):
            # Malformed saved structures remain visible, never get defaults.
            counts['sf6c_predicate_error_slots'] += 1
            eligible = False
        counts['sf6c_certified_slots'] += bool(eligible)
    counts['sf6c_certified_lines'] += bool(counts['sf6c_certified_slots'])
    counts['sf6c_predicate_error_lines'] += bool(counts['sf6c_predicate_error_slots'])
    return counts, states['recognition_confidence']


def summarize(counts):
    counts = dict(counts)
    percent = lambda n, d: 100 * n / d if d else 0.0
    return dict(counts=counts,
        confidence_states={s: counts[f'recognition_confidence_{s}_lines'] for s in STATES if counts[f'recognition_confidence_{s}_lines']},
        confidence_slot_states={s: counts[f'recognition_confidence_{s}_slots'] for s in STATES if counts[f'recognition_confidence_{s}_slots']},
        scored_confidence_line_percent=percent(counts['explicit_score_lines'], counts['lines']),
        scored_confidence_slot_percent=percent(counts['explicit_score_slots'], counts['slots']),
        sf6c_certified_line_percent=percent(counts['sf6c_certified_lines'], counts['lines']),
        sf6c_certified_slot_percent=percent(counts['sf6c_certified_slots'], counts['slots']))


def scan(directory, wave_by_id=None, expected=None):
    started = time.monotonic()
    paths = sorted(Path(directory).glob('shard-*-combined.jsonl.gz'))
    if not paths:
        raise ValueError('no saved runtime shards')
    if expected is not None:
        bound = {Path(p).resolve() for p in expected if Path(p).parent.resolve() == Path(directory).resolve()
                 and Path(p).match('shard-*-combined.jsonl.gz')}
        if {p.resolve() for p in paths} != bound:
            raise ValueError('inventory shard population differs from Job 1 inputs')
    counts = empty_counts(); waves = defaultdict(empty_counts); hashes = {}; seen = set()
    for path in paths:
        before = path.stat()
        digest = hashlib.sha256()
        class HashedReader:
            def read(self, size=-1):
                data = stream.read(size); digest.update(data); return data
        with path.open('rb') as stream, gzip.GzipFile(fileobj=HashedReader()) as zipped:
            for line in zipped:
                record = json.loads(line)
                lid = record['id']
                if lid in seen or (wave_by_id is not None and lid not in wave_by_id):
                    raise ValueError('duplicate/unselected inventory line: ' + lid)
                seen.add(lid)
                wave = wave_by_id[lid] if wave_by_id is not None else record.get('wave', 'unassigned')
                row, _ = observe(record)
                counts.update(row); waves[wave].update(row)
        after = path.stat()
        if (after.st_size, after.st_mtime_ns) != (before.st_size, before.st_mtime_ns):
            raise ValueError('runtime changed during evidence inventory')
        hashes[str(path)] = digest.hexdigest()
        if expected is not None and hashes[str(path)] != expected[str(path)]:
            raise ValueError('inventory differs from Job 1 input SHA-256: ' + str(path))
    if wave_by_id is not None and seen != set(wave_by_id):
        raise ValueError('inventory line population differs from selection')
    return dict(directory=str(directory), complete=True, shards=len(paths), **summarize(counts),
                per_wave={w: summarize(v) for w, v in sorted(waves.items())},
                compressed_sha256=hashes, elapsed_seconds=time.monotonic() - started)


def _scan_task(task):
    return scan(*task)


def audit(directories, out, seconds=900, *, selection, expected=None):
    if not 0 < seconds <= 900:
        raise ValueError('job-2 evidence inventory budget must be <= 900 seconds')
    selected = list(c.rows(selection))
    wave_by_id = {r['id']: r['wave'] for r in selected}
    if not selected or len(selected) != len(wave_by_id) or any(not isinstance(w, str) or w == '*' for w in wave_by_id.values()):
        raise ValueError('invalid inventory selection IDs/waves')
    selection_sha = c.sha256(selection)
    if expected is not None and expected.get(str(selection)) != selection_sha:
        raise ValueError('inventory selection differs from Job 1 input SHA-256')
    script_sha = c.sha256(__file__)
    from greekocr.labelfix import release_gate
    gate_sha = c.sha256(release_gate.__file__)
    if gate_sha != c.GATE_SHA256_BY_POLICY['sf6-release-v1']:
        raise ValueError('inventory requires frozen SF6c predicate')
    if not directories:
        raise ValueError('inventory requires saved runtime directories')
    def expired(*_):
        raise TimeoutError('job-2 evidence inventory exceeded budget')
    previous = signal.signal(signal.SIGALRM, expired); signal.alarm(seconds)
    started = time.monotonic()
    pool = ProcessPoolExecutor(max_workers=min(2, len(directories)))
    try:
        result = list(pool.map(_scan_task, [(d, wave_by_id, expected) for d in directories]))
    except BaseException:
        for process in pool._processes.values():
            process.terminate()
        raise
    finally:
        pool.shutdown(wait=True, cancel_futures=True)
        signal.alarm(0); signal.signal(signal.SIGALRM, previous)
    if c.sha256(selection) != selection_sha or c.sha256(__file__) != script_sha or c.sha256(release_gate.__file__) != gate_sha:
        raise ValueError('inventory selection/code changed')
    payload = dict(schema='l1r3-sf6c-evidence-availability-v2', complete=True,
                   measured_in='job2', slurm_job_id=os.environ.get('SLURM_JOB_ID'),
                   expected_production_scored_confidence_percent='~0% from first records; measured by this job',
                   selection=str(selection), selection_sha256=selection_sha,
                   seconds_budget=seconds, elapsed_seconds=time.monotonic() - started,
                   sources=result, inference_runs=0, detector_runs=0, gate_compositions=0,
                   predicate='greekocr.labelfix.release_gate._recogniser_scored',
                   gate_sha256=gate_sha, script_sha256=script_sha)
    c.atomic_json(out, payload)
    print(json.dumps({k:v for k,v in payload.items() if k != 'sources'}), flush=True)
    for source in result:
        print(json.dumps({k:v for k,v in source.items() if k not in ('compressed_sha256', 'per_wave')}), flush=True)
    return payload


def inventory_release(root, out, config):
    """Bind the first Job-2 stage to Job 1's verified raw-input hashes."""
    cfg = c.load(config)
    receipt = c.load(Path(root) / 'receipt.json')
    vp = Path(root) / 'input_verification.json'
    verification = c.load(vp)
    if (receipt.get('complete') is not True or verification.get('complete') is not True
            or c.sha256(vp) != receipt['input_verification_sha256']
            or c.digest(verification['inputs']) != receipt['inputs_sha256']
            or receipt['policy']['sources']['greekocr/labelfix/release_gate.py'] != c.GATE_SHA256_BY_POLICY['sf6-release-v1']):
        raise ValueError('inventory Job 1 binding mismatch')
    if not os.environ.get('SLURM_JOB_ID') and not (cfg.get('verification_only') and verification['lines'] == 64):
        raise ValueError('full-population evidence inventory requires a Slurm allocation')
    directories = [str(Path(cfg['input_run']) / 'combined'), cfg['ensemble_run']]
    if (Path(verification['historical_run']).resolve() != Path(cfg['input_run']).resolve()
            or Path(verification['ensemble_run']).resolve() != Path(cfg['ensemble_run']).resolve()):
        raise ValueError('inventory config differs from Job 1 sources')
    result = audit(directories, out, selection=cfg['selection'], expected=verification['inputs'])
    if c.sha256(vp) != receipt['input_verification_sha256']:
        raise ValueError('Job 1 verification changed during inventory')
    return result


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--config', type=Path, required=True)
    ap.add_argument('--input-dir', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    inventory_release(args.input_dir, args.out, args.config)
