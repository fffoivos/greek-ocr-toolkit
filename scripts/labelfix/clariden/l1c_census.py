"""Read-only HOLD census of completed, hash-verified L1R SF4/SF5/SF6c releases.

Standard library only. No gate/reader/detector imports, recomposition or network.
Exact reasons are overlay hold_slots[].detail, never the lossy .reason alias.
"""
from __future__ import annotations
from greekocr.ops.data_root import input_path as _data_input

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import gzip
import hashlib
import json
from pathlib import Path
import re
import time
import uuid

MODES = ('PRESENCE', 'FULL', 'ENSEMBLE_AB')
WAVES = ('round1', 'round2', 'parliament', 'vouli', 'mixed', 'openarchives')
STATUSES = ('corrected', 'unchanged', 'hold', 'out_of_scope')
FAMILIES = ('localisation/segmentation', 'clipping', 'K1', 'edit-guard',
            'A/B disagreement', 'kind disagreement', 'R1 uncertainty', 'other/unclassified')
GATE_SHA256 = 'fc3dc4b3370e8b1a205fe1a2acf55634b189c1cb49f57536a61f44f31a52598a'
GATE_SHA256_BY_POLICY = {'sf4-release-v1': GATE_SHA256,
                         'sf5-release-v1': 'b1137154ca1dce903967cd86974a83abae6e690dd818d21dc5ecf8eaf058a9c9',
                         'sf6-release-v1': '9ef1d6467229e86c9464f428716c792f2a6fc4ffa1e709b798df82c504120408'}
BASE = Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017')
METRICS = ('slots_per_exact_reason', 'line_guards_per_exact_reason',
           'hold_entries_per_exact_reason', 'lines_per_exact_reason',
           'lines_reason_alone', 'lines_per_reason_family', 'exact_reason_sets')


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def sha256(path):
    h = hashlib.sha256()
    with _data_input(Path(path)).open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def load(path):
    return json.loads(_data_input(Path(path)).read_text(encoding='utf-8'))


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.partial-' + uuid.uuid4().hex)
    tmp.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n', encoding='utf-8')
    tmp.replace(path)


def rows(path):
    path = Path(path)
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'rt', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def confined(root, name):
    root = Path(root).resolve()
    p = (root / name).resolve()
    if p == root or root not in p.parents:
        raise ValueError('receipt path escapes input directory: ' + str(name))
    return p


def resolve_input(job_id, base=BASE):
    if not re.fullmatch(r'[1-9][0-9]*', str(job_id)):
        raise ValueError('L1R job ID must be a positive integer')
    base = Path(base)
    candidates = [base / 'l1r_sf4' / ('output_' + str(job_id)),
                  base / 'l1e_20261017' / ('l1r_sf4_' + str(job_id))]
    found = {p.resolve() for p in candidates if p.is_dir()}
    if len(found) != 1:
        raise ValueError('expected exactly one L1R output directory: ' + str(candidates))
    return found.pop()


def reason_families(reason):
    """K1 wrappers also tag a known underlying observation family; lines dedup."""
    if reason.startswith('K1:'):
        child = reason.split(':', 2)[-1] if reason.count(':') >= 2 else ''
        underlying = reason_families(child) - {'other/unclassified'} if child else set()
        return {'K1'} | underlying
    if reason.startswith('edit_guard:'):
        return {'edit-guard'}
    if reason == 'ensemble_ab_mark_set_disagreement':
        return {'A/B disagreement'}
    if reason in ('mark_kind_disagreement', 'mark_set_disagreement'):
        return {'kind disagreement'}
    if reason.startswith(('r1_', 'r1:')):
        return {'R1 uncertainty'}
    if reason.startswith(('crop_UNSEEN:', 'detector_clipped_', 'clipped_', 'unseen_')):
        return {'clipping'}
    if reason.startswith(('detector_', 'localisation_', 'segmentation_', 'physical_',
                          'legacy_elision_', 'unnamed')):
        return {'localisation/segmentation'}
    return {'other/unclassified'}


def observation(row):
    """One count per (start, letter, exact reason); blank letter = line guard."""
    status = row['status']
    if status not in STATUSES:
        raise ValueError('unknown release status')
    events = row['hold_slots']
    if (status == 'hold') != bool(events):
        raise ValueError('HOLD status/reasons mismatch')
    slots, guards, entries = set(), set(), Counter()
    for event in events:
        reason = event.get('detail')
        if not isinstance(reason, str) or not reason:
            raise ValueError('missing exact HOLD detail; aliases are not exact reasons')
        entries[reason] += 1
        if not isinstance(event.get('start'), int) or not isinstance(event.get('letter'), str):
            raise ValueError('invalid HOLD slot identity')
        if event['letter']:
            slots.add((event['start'], event['letter'], reason))
        else:
            guards.add(reason)
    reasons = set(entries)
    return dict(status=status, slots=Counter(r for _, _, r in slots), guards=Counter(guards),
                entries=entries, reasons=reasons,
                families=set().union(*(reason_families(r) for r in reasons)) if reasons else set(),
                held_slots=len({(s, b) for s, b, _ in slots}))


def empty_bucket():
    return dict(total_lines=0, held_slots=0, status=Counter({s: 0 for s in STATUSES}),
                **{key: Counter() for key in METRICS})


def add(bucket, obs):
    bucket['total_lines'] += 1
    bucket['held_slots'] += obs['held_slots']
    bucket['status'][obs['status']] += 1
    for metric, field in (('slots_per_exact_reason', 'slots'), ('line_guards_per_exact_reason', 'guards'),
                          ('hold_entries_per_exact_reason', 'entries'), ('lines_per_exact_reason', 'reasons'),
                          ('lines_per_reason_family', 'families')):
        bucket[metric].update(obs[field])
    if len(obs['reasons']) == 1:
        bucket['lines_reason_alone'].update(obs['reasons'])
    if obs['reasons']:
        bucket['exact_reason_sets'][canonical(sorted(obs['reasons']))] += 1


def group_key(mode, wave='*', source='*'):
    return canonical([mode, wave, source])


def check_manifest(manifest, parent, hashes, binding, verification_sha, variant):
    if (manifest['release_policy'] != binding['policy_binding']['schema'] or manifest['variant'] != variant
            or manifest['policy_sha'] != binding['policy_sha256']
            or manifest['input_verification_sha256'] != verification_sha):
        raise ValueError('release policy/input binding mismatch')
    for key, hk in (('overlay', 'overlay_sha256'), ('kept_line_ids', 'kept_line_ids_sha256'),
                    ('labels_file', 'labels_sha256')):
        if key in manifest:
            p = confined(parent, manifest[key])
            if hashes.get(str(p)) != manifest[hk]:
                raise ValueError('unbound release payload: ' + str(p))


def verify_inputs(root, workers=4):
    """Verify all L1R output hashes before any census; upstream raw inputs stay closed."""
    root = Path(root).resolve()
    hashes = {}

    def checked(path, expected=None):
        got = sha256(path)
        if expected is not None and got != expected:
            raise ValueError('L1R SHA-256 mismatch: ' + str(path))
        hashes[str(Path(path).resolve())] = got
        return load(path)

    receipt = checked(root / 'receipt.json')
    if (receipt['schema'] != 'l1r-recomposition-v2' or receipt.get('complete') is not True
            or receipt['validation'].get('complete') is not True):
        raise ValueError('L1R is not complete')
    policy, binding = receipt['policy'], receipt['binding']
    if (policy['schema'] not in GATE_SHA256_BY_POLICY
            or policy['sources'].get('greekocr/labelfix/release_gate.py') != GATE_SHA256_BY_POLICY.get(policy['schema'])
            or policy['sha256'] != hashlib.sha256(json.dumps(policy['sources'], sort_keys=True).encode()).hexdigest()
            or binding['policy_binding'] != policy or binding['policy_sha256'] != policy['sha256']):
        raise ValueError('frozen SF4/SF5/SF6c policy mismatch')
    audit = checked(root / 'input_verification.json', receipt['input_verification_sha256'])
    if (audit.get('complete') is not True or digest(audit['inputs']) != receipt['inputs_sha256']
            or audit['inputs_sha256'] != receipt['inputs_sha256']
            or binding['input_verification_sha256'] != receipt['input_verification_sha256']
            or binding['input_hashes_sha256'] != receipt['inputs_sha256']):
        raise ValueError('L1R upstream verification binding mismatch')
    wanted = {}

    def register(parent, outputs):
        for name, expected in outputs.items():
            p = str(confined(parent, name))
            if p in wanted and wanted[p] != expected:
                raise ValueError('conflicting L1R output hashes')
            wanted[p] = expected

    register(root, receipt['outputs'])
    tasks, numbers, total = [], set(), 0
    for entry in receipt['shards']:
        n = entry['shard']
        if not isinstance(n, int) or n < 0 or n in numbers:
            raise ValueError('duplicate/invalid L1R shard')
        numbers.add(n)
        if entry['receipt'] != f'shards/shard-{n:05d}/receipt.json':
            raise ValueError('invalid shard receipt path')
        rp = confined(root, entry['receipt'])
        sr = checked(rp, entry['receipt_sha256'])
        if (sr['schema'] != 'l1r-recomposition-shard-v1' or sr.get('complete') is not True
                or sr['shard'] != n or sr['inputs']['binding'] != binding
                or sr['validation'].get('complete') is not True):
            raise ValueError('incomplete or mismatched L1R shard')
        register(rp.parent, sr['outputs'])
        required = ['selection.jsonl'] + [f'release/{name}' for m in MODES for name in (
            f'overlay_{m.lower()}.jsonl.gz', f'release_{m.lower()}.json',
            f'release_ctrl_subset_{m.lower()}.json', f'ctrl_subset_{m.lower()}.jsonl.gz',
            f'kept_{m.lower()}_line_ids.txt')]
        if any(name not in sr['outputs'] for name in required):
            raise ValueError('missing hash-bound L1R shard payload')
        tasks.append(dict(shard=n, directory=str(rp.parent), lines=sr['lines'],
                          receipt_sha256=entry['receipt_sha256']))
        total += sr['lines']
    if not tasks or total != audit['lines'] or len(tasks) != audit['shards'] or total != receipt['validation']['lines']:
        raise ValueError('L1R population mismatch')
    required_top = [f'release/{name}' for m in MODES for name in (
        f'overlay_{m.lower()}.jsonl.gz', f'release_{m.lower()}.json',
        f'release_ctrl_subset_{m.lower()}.json', f'ctrl_subset_{m.lower()}.jsonl.gz',
        f'kept_{m.lower()}_line_ids.txt')]
    if any(name not in receipt['outputs'] for name in required_top):
        raise ValueError('missing hash-bound aggregate release')
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for name, got in pool.map(lambda p: (p, sha256(p)), wanted):
            if got != wanted[name]:
                raise ValueError('L1R SHA-256 mismatch: ' + name)
            hashes[name] = got
    for parent in [root / 'release'] + [Path(t['directory']) / 'release' for t in tasks]:
        for mode in MODES:
            for prefix in ('release_', 'release_ctrl_subset_'):
                manifest = load(parent / f'{prefix}{mode.lower()}.json')
                check_manifest(manifest, parent, hashes, binding, receipt['input_verification_sha256'], mode.lower())
    return dict(schema='l1c-input-verification-v1', complete=True, input_directory=str(root),
                lines=total, shards=len(tasks), hashes=hashes,
                l1r_receipt_sha256=hashes[str(root / 'receipt.json')], policy=policy), tasks, receipt


def _shard(task):
    spec, out, run_binding = task
    directory = Path(spec['directory'])
    partial = Path(out) / 'partials' / f'shard-{spec["shard"]:05d}'
    receipt_path = partial / 'receipt.json'
    if receipt_path.exists():
        r = load(receipt_path)
        if r.get('complete') is not True or r['binding'] != run_binding or r['input'] != spec:
            raise ValueError('stale L1C partial receipt')
        if sha256(partial / 'counts.json') != r['counts_sha256']:
            raise ValueError('L1C partial counts changed')
        return r
    selected = list(rows(directory / 'selection.jsonl'))
    records = {r['id']: r for r in selected}
    if len(records) != len(selected) or len(selected) != spec['lines']:
        raise ValueError('selection duplicate/count mismatch')
    groups = defaultdict(empty_bucket)
    for mode in MODES:
        seen = set()
        for row in rows(directory / 'release' / f'overlay_{mode.lower()}.jsonl.gz'):
            lid = row['line_id']
            if lid not in records or lid in seen:
                raise ValueError('unexpected/duplicate overlay line')
            seen.add(lid)
            record = records[lid]
            if hashlib.sha256(record['label'].encode()).hexdigest() != row['original_label_sha256']:
                raise ValueError('overlay label binding mismatch')
            wave = record['wave']
            source = record.get('source', record.get('source_dataset', 'UNKNOWN'))
            if not isinstance(wave, str) or not isinstance(source, str) or wave == '*' or source == '*':
                raise ValueError('invalid wave/source dimension')
            obs = observation(row)
            for w, s in (('*', '*'), (wave, '*'), ('*', source), (wave, source)):
                add(groups[group_key(mode, w, s)], obs)
        if seen != set(records):
            raise ValueError('missing overlay lines')
        expected = load(directory / 'release' / f'release_{mode.lower()}.json')['counts_by_status']
        if groups[group_key(mode)]['status'] != Counter(expected):
            raise ValueError('shard status count mismatch')
    partial.mkdir(parents=True, exist_ok=True)
    atomic_json(partial / 'counts.json', dict(groups))
    result = dict(schema='l1c-partial-v1', complete=True, input=spec, binding=run_binding,
                  counts_sha256=sha256(partial / 'counts.json'), lines=len(records))
    atomic_json(receipt_path, result)
    return result


def merge(partials, out, l1r):
    groups = defaultdict(empty_bucket)
    for result in partials:
        path = Path(out) / 'partials' / f'shard-{result["input"]["shard"]:05d}' / 'counts.json'
        for key, counts in load(path).items():
            target = groups[key]
            target['total_lines'] += counts['total_lines']
            target['held_slots'] += counts['held_slots']
            for field in ('status',) + METRICS:
                target[field].update(counts[field])
    for mode in MODES:
        if groups[group_key(mode)]['status'] != Counter(l1r['counts'][mode.lower()]):
            raise ValueError('aggregate L1R status count mismatch')
        for wave in WAVES:
            groups[group_key(mode, wave)]  # explicit zero rows for absent requested waves
        for dimension, index in (('coverage_per_wave', 1), ('coverage_per_source', 2)):
            root = Path(load(Path(out) / 'input_verification.json')['input_directory'])
            coverage = load(root / 'release' / f'release_{mode.lower()}.json')[dimension]
            observed = {json.loads(k)[index]: b['status'] for k, b in groups.items()
                        if json.loads(k)[0] == mode and json.loads(k)[3-index] == '*'
                        and json.loads(k)[index] != '*' and b['total_lines']}
            wanted = {k: Counter({s: v[s] for s in STATUSES}) for k, v in coverage.items() if v['total']}
            if observed != wanted:
                raise ValueError('aggregate wave/source coverage mismatch')
    # Retain all exact sets until the FINAL merge; top-10 of shard top-10 is wrong.
    for counts in groups.values():
        ordered = sorted(counts['exact_reason_sets'].items(), key=lambda kv: (-kv[1], kv[0]))
        counts['top10_exact_reason_sets'] = [dict(reasons=json.loads(k), lines=v) for k, v in ordered[:10]]
        counts['distinct_exact_reason_sets'] = len(ordered)
        del counts['exact_reason_sets']  # full counters live in durable shard partials
        counts['lines_per_reason_family'] = {f: counts['lines_per_reason_family'][f] for f in FAMILIES}
    result = {m: dict(overall=groups[group_key(m)],
                     per_wave={json.loads(k)[1]: b for k, b in sorted(groups.items())
                               if json.loads(k)[0] == m and json.loads(k)[1] != '*' and json.loads(k)[2] == '*'},
                     per_source={json.loads(k)[2]: b for k, b in sorted(groups.items())
                                 if json.loads(k)[0] == m and json.loads(k)[1] == '*' and json.loads(k)[2] != '*'},
                     per_wave_source={w: {json.loads(k)[2]: b for k, b in sorted(groups.items())
                                          if json.loads(k)[0] == m and json.loads(k)[1] == w and json.loads(k)[2] != '*'}
                                      for w in sorted({json.loads(k)[1] for k in groups if json.loads(k)[0] == m} - {'*'})})
              for m in MODES}
    return result


def markdown(census):
    def cell(s):
        return str(s).replace('|', '&#124;').replace('\n', ' ')
    lines = ['# L1C HOLD census', '', 'Analysis only; exact reasons read from completed SF4/SF5 releases.', '',
             'Slot counts deduplicate (line, start, letter, exact detail). Blank-letter edit guards are',
             'line guards, not glyph slots. ALONE means the union of all exact reasons on the line',
             'is that singleton. Family counts deduplicate lines; families can overlap (K1 observation',
             'wrappers also tag their underlying family). Unknown reasons remain visible.', '',
             'JSON includes global top-10 exact sets and wave × source groups. Full exact-set',
             'counters are retained in shard partials for exact aggregation and restart.',
             'Clipping includes crop_UNSEEN; R1 uncertainty includes missing/unscored/unsupported',
             'reader evidence. Exact strings are preserved, without merging synonyms.', '']
    for mode, data in census.items():
        lines += [f'## {mode}', '', '| Wave | Source | Lines | HOLD | Held glyph slots |',
                  '|---|---|---:|---:|---:|']
        groups = [('ALL', 'ALL', data['overall'])]
        groups += [(w, 'ALL', b) for w, b in data['per_wave'].items()]
        groups += [('ALL', s, b) for s, b in data['per_source'].items()]
        groups += [(w, s, b) for w, sources in data['per_wave_source'].items() for s, b in sources.items()]
        for w, s, b in groups:
            lines.append(f'| {cell(w)} | {cell(s)} | {b["total_lines"]} | {b["status"]["hold"]} | {b["held_slots"]} |')
        for w, s, b in groups:
            if not b['total_lines']:
                continue
            lines += ['', f'### {cell(w)} / {cell(s)}', '',
                      '| Exact reason | Slots | Line guards | Lines | Lines ALONE |', '|---|---:|---:|---:|---:|']
            for r in sorted(b['lines_per_exact_reason']):
                lines.append('| ' + cell(r) + ' | ' + ' | '.join(str(b[k].get(r, 0)) for k in
                             ('slots_per_exact_reason', 'line_guards_per_exact_reason', 'lines_per_exact_reason', 'lines_reason_alone')) + ' |')
            lines += ['', '| Family | Lines held |', '|---|---:|']
            lines += [f'| {cell(f)} | {v} |' for f, v in b['lines_per_reason_family'].items()]
            lines += ['', '| Top exact reason set | Lines |', '|---|---:|']
            lines += [f'| {cell(canonical(r["reasons"]))} | {r["lines"]} |' for r in b['top10_exact_reason_sets']]
    return '\n'.join(lines) + '\n'


def census(root, out, workers=8, job_id=None):
    started = time.monotonic()
    root, out = Path(root).resolve(), Path(out).resolve()
    if workers < 1 or root == out or root in out.parents or out in root.parents:
        raise ValueError('positive workers and disjoint input/output directories required')
    verification, specs, l1r = verify_inputs(root, min(workers, 8))
    binding = dict(schema='l1c-counting-v1', l1r_job_id=job_id,
                   input_hashes_sha256=digest(verification['hashes']), code_sha256=sha256(__file__))
    if (out / 'binding.json').exists() and load(out / 'binding.json') != binding:
        raise ValueError('L1C restart binding changed')
    out.mkdir(parents=True, exist_ok=True)
    atomic_json(out / 'binding.json', binding)
    atomic_json(out / 'input_verification.json', verification)
    tasks = [(spec, str(out), binding) for spec in specs]
    partials = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for future in as_completed([pool.submit(_shard, t) for t in tasks]):
            r = future.result()
            partials.append(r)
            print(f'L1C_SHARD {r["input"]["shard"]} lines={r["lines"]}', flush=True)
    result = merge(partials, out, l1r)
    # Recheck the L1R output DAG and our code before sealing a complete aggregate.
    with ThreadPoolExecutor(max_workers=min(workers, 8)) as pool:
        for name, got in pool.map(lambda p: (p, sha256(p)), verification['hashes']):
            if got != verification['hashes'][name]:
                raise ValueError('L1R changed during census: ' + name)
    if sha256(__file__) != binding['code_sha256']:
        raise ValueError('L1C code changed during census')
    atomic_json(out / 'CENSUS.json', dict(schema='l1c-census-v1', modes=result))
    (out / 'CENSUS.md').write_text(markdown(result), encoding='utf-8')
    receipt = dict(schema='l1c-census-receipt-v1', complete=True, analysis_only=True,
                   detector_runs=0, reader_runs=0, gate_runs=0, binding=binding,
                   lines=verification['lines'], shards=verification['shards'],
                   elapsed_seconds=time.monotonic()-started,
                   partial_receipts={f'partials/shard-{r["input"]["shard"]:05d}/receipt.json':
                                     sha256(out / 'partials' / f'shard-{r["input"]["shard"]:05d}' / 'receipt.json')
                                     for r in sorted(partials, key=lambda r: r['input']['shard'])},
                   outputs={p: sha256(out / p) for p in ('CENSUS.json', 'CENSUS.md', 'binding.json', 'input_verification.json')})
    atomic_json(out / 'receipt.json', receipt)
    print('L1C_COMPLETE ' + canonical(receipt), flush=True)
    return receipt


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    source = ap.add_mutually_exclusive_group(required=True)
    source.add_argument('--l1r-job-id')
    source.add_argument('--input-dir', type=Path, help='explicit fixture or completed L1R directory')
    ap.add_argument('--base', type=Path, default=BASE)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--workers', type=int, default=8)
    a = ap.parse_args()
    root = resolve_input(a.l1r_job_id, a.base) if a.l1r_job_id else a.input_dir
    census(root, a.out, a.workers, a.l1r_job_id)


if __name__ == '__main__':
    main()
