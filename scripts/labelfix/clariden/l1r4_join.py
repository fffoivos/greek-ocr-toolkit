"""L1R4 receipt/identity verification and line-ID-only join; no inference.

Metadata verification is login-safe. Frame decoding and index construction are
allocation work (or the explicitly authorized 64-line verification mock).
"""
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import math
from pathlib import Path
import sqlite3

from greekocr.labelfix.ctc_align import Alignment, recognition_fields
from greekocr.labelfix.text import nfd
from scripts.labelfix.clariden import l1c_census as c
from scripts.labelfix.clariden.l1r3_evidence import observe, summarize

IDENTITY = ('prediction', 'n_frames', 'scale', 'strip_width', 'spans')
FIELDS = ('recognition_confidence', 'recognition_evidence', 'image_width')


def anchor(rt):
    return dict(recogniser_text=rt['recogniser_text'], detector=dict(slots=[
        {k: s.get(k) for k in ('start', 'base', 'locator_span')} | dict(
            evidence=dict(window=s.get('evidence', {}).get('window')))
        for s in rt['detector']['slots']]))


def score(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and 0 <= v <= 1


def verify_receipt(spec, selected=None):
    root = Path(spec['root']); inputs = {}
    def checked(p, wanted=None):
        p = Path(p); got = c.sha256(p)
        if wanted is not None and got != wanted:
            raise ValueError('L1F SHA-256 mismatch: ' + str(p))
        inputs[str(p)] = got
        return c.load(p) if p.suffix == '.json' else got
    final = checked(root / 'receipt.json', spec.get('receipt_sha256'))
    if (final.get('schema') != 'l1f-final-v1' or final.get('complete') is not True
            or final['verification_only'] != spec['verification_only']
            or final['lines'] != spec['lines'] or str(final['job_id']) != str(spec['job_id'])
            or final.get('never_replaces_saved_text') is not True):
        raise ValueError('L1F incomplete/wrong population or job identity')
    binding = final['binding']
    if binding != checked(root / 'binding.json'):
        raise ValueError('L1F final binding mismatch')
    if binding['config_sha256'] != spec['config_sha256'] or binding['code_sha256'] != spec['code_sha256']:
        raise ValueError('L1F config/code differs from approved package')
    iv = checked(root / 'input_verification.json', final['input_verification_sha256'])
    code = checked(root / 'code_sources.json', final['code_sources_sha256'])
    plan = checked(root / 'plan_receipt.json', final['plan_receipt_sha256'])
    checked(root / 'plan.sqlite', plan['sha256'])
    if (iv.get('complete') is not True or iv['lines'] != final['lines']
            or c.digest(iv['inputs']) != iv['inputs_sha256']
            or c.digest(code) != binding['code_sha256'] or plan['binding'] != binding
            or plan.get('complete') is not True or plan['lines'] != final['lines']
            or binding['input_binding_sha256'] != c.digest(dict(inputs=iv['inputs'], crops=iv['crops']))
            or iv['checkpoint_sha256'] != spec['checkpoint_sha256']
            or iv['safetensors_sha256'] != spec['safetensors_sha256']):
        raise ValueError('L1F upstream/code/plan provenance mismatch')
    tasks = plan['tasks']
    if ([t['shard'] for t in tasks] != list(range(spec['shards']))
            or len(final['shards']) != len(tasks) or plan['shards'] != len(tasks)
            or sum(t['lines'] for t in tasks) != final['lines']):
        raise ValueError('L1F missing/extra/duplicate task shard')
    counts, waves = Counter(), defaultdict(Counter)
    payloads = {}
    for task, entry in zip(tasks, final['shards']):
        n = task['shard']
        if (entry['shard'] != n or entry['receipt'] != f'shards/shard-{n:05d}/receipt.json'
                or entry['output'] != f'shards/shard-{n:05d}/frames.jsonl.gz'):
            raise ValueError('L1F invalid shard identity/path')
        sr = checked(root / entry['receipt'], entry['receipt_sha256'])
        if (sr.get('complete') is not True or sr['binding'] != binding or sr['task'] != task
                or sr['lines'] != task['lines'] or entry['lines'] != task['lines']
                or sr['output_sha256'] != entry['output_sha256']):
            raise ValueError('L1F incomplete/mismatched shard')
        payloads[str(root / entry['output'])] = entry['output_sha256']
        for wave, values in sr['coverage_per_wave'].items():
            counts.update(values); waves[wave].update(values)
    actual = {str(p) for p in (root / 'shards').glob('*/frames.jsonl.gz')}
    if actual != set(payloads) or {str(p) for p in (root / 'shards').glob('*/receipt.json')} != {
            str(root / e['receipt']) for e in final['shards']}:
        raise ValueError('L1F missing/extra shard files')
    with ThreadPoolExecutor(max_workers=4) as pool:
        for path, got in pool.map(lambda p: (p, c.sha256(p)), payloads):
            if got != payloads[path]: raise ValueError('L1F payload SHA-256 mismatch: ' + path)
    inputs.update(payloads)
    if (dict(counts) != final['totals'] or dict(waves) != final['coverage_per_wave']
            or counts['lines'] != final['lines']
            or counts['alignment_identity_matches'] + counts['alignment_identity_mismatches'] != counts['lines']
            or final['alignment_identity_all_match'] != (counts['alignment_identity_mismatches'] == 0)):
        raise ValueError('L1F final alignment/population aggregate mismatch')
    if selected is not None:
        expected = Counter(r['wave'] for r in selected)
        if expected != Counter({w: v['lines'] for w, v in waves.items()}):
            raise ValueError('L1F wave population differs from runtime selection')
    return dict(complete=True, root=str(root), receipt_sha256=inputs[str(root / 'receipt.json')],
                lines=final['lines'], shards=len(tasks), totals=dict(counts),
                coverage_per_wave=dict(waves), inputs=inputs, final=final, plan=plan, upstream=iv)


def validate_record(row, saved, rt, spec, binding):
    """Reconstruct frozen evidence from the original saved alignment, not claims."""
    p = row['provenance']; evidence = row['recognition_evidence']
    sid = c.digest({k: saved[k] for k in IDENTITY})
    if (p['saved_alignment_identity_sha256'] != sid
            or p['saved_text_sha256'] != hashlib.sha256(nfd(rt['recogniser_text']).encode()).hexdigest()
            or p['checkpoint_sha256'] != spec['checkpoint_sha256']
            or p['safetensors_sha256'] != spec['safetensors_sha256']
            or p['code_sha256'] != binding['code_sha256']
            or p['input_binding_sha256'] != binding['input_binding_sha256']
            or p['schema'] != 'l1f-frame-evidence-v1'):
        raise ValueError('L1F per-line provenance differs from saved alignment/runtime')
    frames = row['frame_confidences']; confidence = row['recognition_confidence']
    width = row['image_width']
    if (not score(confidence) or not frames or not all(score(v) for v in frames)
            or not isinstance(width, int) or isinstance(width, bool) or width <= 0
            or not math.isclose(sum(frames)/len(frames), confidence, rel_tol=0, abs_tol=2e-7)):
        raise ValueError('L1F invalid actual scores/native width')
    matched = p['alignment_identity_match']
    if matched:
        if (p['alignment_mismatches'] or p['alignment_identity_sha256'] != sid
                or saved.get('transferred') or nfd(saved['prediction']) != nfd(rt['recogniser_text'])
                or len(frames) != saved['n_frames']):
            raise ValueError('L1F falsely claimed alignment identity')
        a = Alignment.from_record(saved); a.confidence = confidence; a.frame_confidences = frames
        if a.recognition_evidence(rt['detector']['slots'], width) != evidence:
            raise ValueError('L1F scored alignment/evidence reconstruction mismatch')
        return dict(recognition_fields(row), recognition_provenance=p)
    if (not p['alignment_mismatches'] or evidence.get('scored') is not False
            or evidence.get('provenance') != 'alignment_identity_mismatch' or evidence.get('regions') != []):
        raise ValueError('L1F mismatched identity was not withheld')
    # Explicitly withheld: no optional consumer fields, including native width.
    return {}


def prepare_join(spec, selected, out, upstream_inputs):
    if not spec['verification_only'] and not __import__('os').environ.get('SLURM_JOB_ID'):
        raise ValueError('production frame decoding requires Slurm allocation')
    if spec['verification_only'] and len(selected) != 64:
        raise ValueError('mock join requires complete 64-line verification population')
    verified = verify_receipt(spec, selected)
    out = Path(out); root = Path(spec['root'])
    target = out / 'l1f_join.sqlite'; rp = out / 'l1f_join_receipt.json'
    binding = dict(spec=spec, l1f_receipt_sha256=verified['receipt_sha256'],
                   selection_sha256=c.digest(selected), code_sha256=c.sha256(__file__))
    if rp.exists():
        prior = c.load(rp)
        if prior['binding'] != binding or c.sha256(target) != prior['index_sha256']:
            raise ValueError('L1F join resume binding/index changed')
        for path, wanted in prior['inputs'].items():
            if c.sha256(path) != wanted: raise ValueError('L1F join input changed')
        return prior
    plan = sqlite3.connect(f'file:{root / "plan.sqlite"}?mode=ro', uri=True)
    selected_by_id = {r['id']: r for r in selected}
    planned = {r[0]: r[1:] for r in plan.execute('SELECT id,crop,wave,task FROM lines')}
    if set(planned) != set(selected_by_id): raise ValueError('L1F exact ID population differs from selection')
    from scripts.labelfix.clariden.r1_common import crop_key
    for lid, (crop, wave, task) in planned.items():
        sel = selected_by_id[lid]
        if (('crop' in sel and crop_key(sel['crop']) != crop) or sel['wave'] != wave
                or ('crop' not in sel and not spec['verification_only'])):
            raise ValueError('L1F plan selection identity mismatch')
    # Compare every sealed plan alignment to its original receipt-bound source.
    alignment_paths = spec['alignment_sources']; original_seen = set()
    for path in alignment_paths:
        wanted = verified['upstream']['inputs'].get(str(path))
        if wanted is None or c.sha256(path) != wanted:
            raise ValueError('L1F original alignment source unbound/changed')
        verified['inputs'][str(path)] = wanted
        for r in c.rows(path):
            crop = crop_key(r['crop'])
            saved = plan.execute('SELECT id,saved FROM lines WHERE crop=?', (crop,)).fetchone()
            if saved is None or saved[0] in original_seen or json.loads(saved[1]) != r['alignment']:
                raise ValueError('L1F plan differs from original saved alignment')
            original_seen.add(saved[0])
    if original_seen != set(planned): raise ValueError('L1F original alignments incomplete')
    # Bind to job 1's independently verified original input DAG where shared.
    for path, wanted in verified['upstream']['inputs'].items():
        if path in upstream_inputs and upstream_inputs[path] != wanted:
            raise ValueError('L1F and runtime input DAG disagree')
    tmp = target.with_suffix('.partial'); tmp.unlink(missing_ok=True)
    db = sqlite3.connect(tmp)
    db.execute('CREATE TABLE evidence (id TEXT PRIMARY KEY, anchor_sha TEXT, fields TEXT)')
    seen = set(); counts = defaultdict(Counter); refused = []
    for entry in verified['final']['shards']:
        ids = []; actual_coverage = defaultdict(Counter)
        for row in c.rows(root / entry['output']):
            lid = row['line_id']
            if lid in seen or lid not in planned: raise ValueError('L1F duplicate/unselected line ID')
            seen.add(lid); ids.append(lid)
            crop, wave, task = planned[lid]
            if task != entry['shard']: raise ValueError('L1F wrong inference task membership')
            saved_json, runtime_json = plan.execute('SELECT saved,runtime FROM lines WHERE id=?', (lid,)).fetchone()
            saved, rt = json.loads(saved_json), json.loads(runtime_json)
            fields = validate_record(row, saved, rt, spec, verified['final']['binding'])
            db.execute('INSERT INTO evidence VALUES (?,?,?)', (lid, c.digest(anchor(rt)), c.canonical(fields)))
            obs, _ = observe(dict(rt, **fields)); counts[wave].update(obs)
            counts[wave]['identity_joined_lines' if fields else 'identity_withheld_lines'] += 1
            actual_coverage[wave].update(lines=1, alignment_identity_matches=int(bool(fields)),
                                         alignment_identity_mismatches=int(not fields))
            if not fields: refused.append(dict(line_id=lid, wave=wave, reasons=row['provenance']['alignment_mismatches']))
        sr = c.load(root / entry['receipt'])
        if len(ids) != entry['lines'] or c.digest(sorted(ids)) != sr['line_ids_sha256']:
            raise ValueError('L1F shard exact ID coverage mismatch')
        for wave, cc in actual_coverage.items():
            if any(sr['coverage_per_wave'][wave].get(k, 0) != v for k, v in cc.items()):
                raise ValueError('L1F shard identity counts differ from payload')
    plan.close()
    if seen != set(planned): raise ValueError('L1F missing output IDs')
    db.commit(); db.close(); tmp.replace(target)
    # Rehash the exact payloads consumed before sealing, including original alignments.
    for path, wanted in verified['inputs'].items():
        if c.sha256(path) != wanted: raise ValueError('L1F changed during join validation')
    result = dict(schema='l1r4-join-v1', complete=True, binding=binding, lines=len(seen),
                  inputs=verified['inputs'], index_sha256=c.sha256(target),
                  per_wave={w: summarize(v) for w,v in counts.items()}, withheld_lines=refused,
                  fields_missing_on_withheld=True, inference_runs=0)
    c.atomic_json(rp, result)
    return result


def join_runtime(records, index):
    db = sqlite3.connect(f'file:{index}?mode=ro', uri=True)
    result = []
    try:
        for rt in records:
            row = db.execute('SELECT anchor_sha,fields FROM evidence WHERE id=?', (rt['id'],)).fetchone()
            if row is None or row[0] != c.digest(anchor(rt)):
                raise ValueError('L1F runtime text/geometry identity mismatch: ' + rt['id'])
            copied = dict(rt)
            for key in (*FIELDS, 'recognition_provenance'): copied.pop(key, None)
            copied.update(json.loads(row[1])); result.append(copied)
    finally:
        db.close()
    return result
