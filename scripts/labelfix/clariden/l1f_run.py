"""L1F: receipt-bound E3 frames, without changing saved text or SF6c policy.

Production is allocation-only. --verify-only hashes inputs without inference;
--mock accepts at most 64 explicitly verification-only lines on CPU. All writes
are confined to a new output tree. Completed shards resume under exact bindings.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
import gzip
import hashlib
import io
import json
import math
import multiprocessing as mp
import os
from pathlib import Path
import sqlite3
import time

from greekocr.labelfix.ctc_align import Alignment, Recognizer, VENDOR_CODEC, recognition_fields
from greekocr.labelfix.release_gate import _recogniser_scored
from greekocr.labelfix.text import nfd
from scripts.labelfix.clariden.r1_common import rows, sha256, write_json, crop_key, crop_path
from scripts.labelfix.clariden.l1r_recompose_ext import atomic_json, digest, load, separate_output, verify_inputs

ROOT = Path(__file__).resolve().parents[3]
FROZEN = {
    'greekocr/labelfix/ctc_align.py': '3ecb1a208918fdc33b897c00c1848456a9480946a17fb88f7d9f5f400a646068',
    'greekocr/labelfix/release_gate.py': '9ef1d6467229e86c9464f428716c792f2a6fc4ffa1e709b798df82c504120408',
}
IDENTITY_KEYS = ('prediction', 'n_frames', 'scale', 'strip_width', 'spans')


def code_sources():
    paths = [*ROOT.joinpath('greekocr').rglob('*.py'), *ROOT.joinpath('scripts/labelfix').rglob('*.py'), VENDOR_CODEC]
    return {str(p.relative_to(ROOT)): sha256(p) for p in sorted(paths) if '__pycache__' not in p.parts}


def checked(path, wanted, inputs):
    path = str(Path(path))
    if sha256(path) != wanted:
        raise ValueError('hash mismatch: ' + path)
    if path in inputs and inputs[path] != wanted:
        raise ValueError('inconsistent input binding: ' + path)
    inputs[path] = wanted


def alignment_identity(record):
    """Exact saved geometry/text at the original to_record pixel precision.

    Confidence and frame posteriors are newly measured values, not alignment
    identity. The full NEW record is separately hashed by frozen SF6c code.
    """
    return {k: record[k] for k in IDENTITY_KEYS}


def crop_records(cfg, selected, inputs):
    receipt = load(cfg['crop_receipt'])
    if (not receipt.get('complete') or receipt['selection_sha256'] != sha256(cfg['selection'])
            or receipt['selected'] != len(selected)):
        raise ValueError('crop receipt population/selection mismatch')
    checked(cfg['crop_inventory'], receipt['inventory_sha256'], inputs)
    inventory = {}
    for row in rows(cfg['crop_inventory']):
        key = crop_key(row['crop'])
        if key in inventory:
            raise ValueError('duplicate crop inventory key')
        expected_path = crop_path(key, cfg['crop_root'], cfg['layout'])
        if Path(row['path']).resolve() != expected_path.resolve():
            raise ValueError('crop path differs from L1 inventory: ' + key)
        inventory[key] = row
    if set(inventory) != {crop_key(r['crop']) for r in selected}:
        raise ValueError('crop inventory differs from selection')

    def verify_crop(row):
        p = Path(row['path'])
        if p.stat().st_size != row['bytes'] or sha256(p) != row['sha256']:
            raise ValueError('crop receipt mismatch: ' + str(p))
        return row['bytes']

    with ThreadPoolExecutor(max_workers=4) as pool:
        total = sum(pool.map(verify_crop, inventory.values()))
    return inventory, dict(lines=len(inventory), bytes=total, all_sha256_verified=True,
        inventory_sha256=sha256(cfg['crop_inventory']),
        crop_map_sha256=digest({k: v['sha256'] for k, v in inventory.items()}))


def verify(cfg, mock=False):
    started = time.monotonic()
    for name, wanted in FROZEN.items():
        if sha256(ROOT / name) != wanted:
            raise ValueError('frozen SF6c source changed: ' + name)
    for name, wanted in cfg.get('historical_forward_sha256', {}).items():
        if sha256(ROOT / name) != wanted:
            raise ValueError('original E3 forward dependency changed: ' + name)
    inputs = {}
    for path, wanted in cfg['expected_sha256'].items():
        checked(path, wanted, inputs)
    selected = list(rows(cfg['selection']))
    if (len(selected) != cfg['lines'] or len({r['id'] for r in selected}) != len(selected)
            or len({crop_key(r['crop']) for r in selected}) != len(selected)):
        raise ValueError('selection population/uniqueness mismatch')
    if mock:
        if not cfg.get('verification_only') or len(selected) > 64:
            raise ValueError('mock needs <=64 verification-only lines')
        historical = [dict(runtime=p) for p in cfg['mock_runtime']]
    else:
        if cfg.get('verification_only') or len(selected) != 124669:
            raise ValueError('production must be the complete L1 population')
        audit, historical, _, binding, _ = verify_inputs(cfg['input_run'], cfg['selection'],
            cfg['binding_dir'], cfg['source'], expected=cfg['expected_sha256'], workers=4)
        inputs.update(audit['inputs'])
        if (binding['ctc_sha256'] != cfg['checkpoint_sha256']
                or binding['ctc_safetensors_sha256'] != cfg['safetensors_sha256']):
            raise ValueError('checkpoint differs from original L1 binding')
        top = load(Path(cfg['input_run']) / 'detector/detector_receipt.json')
        if {str(Path(s['alignments'])) for s in cfg['alignment_sources']} != set(top['alignment_sha256']):
            raise ValueError('alignment sources differ from L1 detector receipt')
        for path, wanted in top['alignment_sha256'].items():
            checked(path, wanted, inputs)
    checked(cfg['checkpoint'], cfg['checkpoint_sha256'], inputs)
    checked(Path(cfg['checkpoint']).with_suffix('.safetensors'), cfg['safetensors_sha256'], inputs)
    checked(cfg['selection'], cfg['selection_sha256'], inputs)
    checked(cfg['crop_receipt'], cfg['expected_sha256'][cfg['crop_receipt']], inputs)
    # Each alignment source preserves original rank::4, chunk=512, width-sort,
    # batch=16. Confidence was already computed from the same forward logits.
    for source in cfg['alignment_sources']:
        if not mock:
            summary = load(source['summary'])
            checked(source['alignments'], summary['output_sha256'], inputs)
            checked(source['selection'], summary['binding']['selection_sha256'], inputs)
            b = summary['binding']
            if (b['checkpoint_sha256'] != cfg['checkpoint_sha256']
                    or b['checkpoint_safetensors_sha256'] != cfg['safetensors_sha256']
                    or summary['counts']['aligned'] != b['lines']
                    or summary['counts'].get('failed', 0)):
                raise ValueError('incomplete or differently bound alignment source')
            for key in ('workers', 'chunk_size', 'batch_size'):
                if source[key] != b['arguments'][key]:
                    raise ValueError('original alignment batch layout changed: ' + key)
        else:
            for key in ('selection', 'alignments'):
                if str(source[key]) not in inputs:
                    raise ValueError('unbound mock source')
    inventory, crops = crop_records(cfg, selected, inputs)
    receipt = dict(schema='l1f-input-verification-v1', complete=True, lines=len(selected),
        historical_shards=len(historical), inputs=inputs, inputs_sha256=digest(inputs), crops=crops,
        checkpoint_sha256=cfg['checkpoint_sha256'], safetensors_sha256=cfg['safetensors_sha256'],
        codec_sha256=sha256(VENDOR_CODEC), frozen=FROZEN, elapsed_seconds=time.monotonic()-started)
    return receipt, selected, historical, inventory


def create_plan(cfg, selected, historical, inventory, out, binding):
    target = out / 'plan.sqlite'
    rp = out / 'plan_receipt.json'
    if rp.exists():
        rec = load(rp)
        if rec['binding'] != binding or sha256(target) != rec['sha256']:
            raise ValueError('resume plan binding/hash mismatch')
        return rec
    tmp = out / 'plan.sqlite.partial'
    # A crash before the plan seal can be retried without trusting partial data.
    db = sqlite3.connect(tmp)
    db.executescript('DROP TABLE IF EXISTS lines; CREATE TABLE lines '
        '(crop TEXT PRIMARY KEY, id TEXT UNIQUE, wave TEXT, crop_sha TEXT, '
        'saved TEXT, runtime TEXT, task INTEGER, ordinal INTEGER);')
    db.executemany('INSERT INTO lines(crop,id,wave,crop_sha) VALUES(?,?,?,?)',
        [(crop_key(r['crop']), r['id'], r['wave'], inventory[crop_key(r['crop'])]['sha256']) for r in selected])
    for source in cfg['alignment_sources']:
        for row in rows(source['alignments']):
            key = crop_key(row['crop'])
            cursor = db.execute('UPDATE lines SET saved=? WHERE crop=? AND saved IS NULL',
                (json.dumps(row['alignment'], ensure_ascii=False), key))
            if cursor.rowcount != 1:
                raise ValueError('unexpected/duplicate saved alignment: ' + key)
    for entry in historical:
        for row in rows(entry['runtime']):
            # Only fields used by recognition_evidence and the exact predicate.
            rt = dict(recogniser_text=row['recogniser_text'], detector=dict(slots=[
                {k: s.get(k) for k in ('start', 'base', 'locator_span')} | dict(
                    evidence=dict(window=s.get('evidence', {}).get('window')))
                for s in row['detector']['slots']]))
            cursor = db.execute('UPDATE lines SET runtime=? WHERE id=? AND runtime IS NULL',
                (json.dumps(rt, ensure_ascii=False), row['id']))
            if cursor.rowcount != 1:
                raise ValueError('unexpected/duplicate detector ID: ' + row['id'])
    tasks = []
    for sn, source in enumerate(cfg['alignment_sources']):
        original = list(rows(source['selection']))
        for rank in range(source['workers']):
            records = original[rank::source['workers']]
            for start in range(0, len(records), source['chunk_size']):
                number = len(tasks)
                chunk = records[start:start+source['chunk_size']]
                for i, row in enumerate(chunk):
                    cursor = db.execute('UPDATE lines SET task=?,ordinal=? WHERE crop=? AND task IS NULL',
                        (number, i, crop_key(row['crop'])))
                    if cursor.rowcount != 1:
                        raise ValueError('duplicate/unselected batch context')
                tasks.append(dict(shard=number, rank=rank, source=sn, start=start, lines=len(chunk),
                                  batch_size=source['batch_size']))
    if db.execute('SELECT COUNT(*) FROM lines WHERE saved IS NULL OR runtime IS NULL OR task IS NULL').fetchone()[0]:
        raise ValueError('plan has missing alignment/runtime/batch membership')
    db.commit(); db.close(); tmp.replace(target)
    receipt = dict(complete=True, binding=binding, sha256=sha256(target), tasks=tasks,
                   lines=len(selected), shards=len(tasks))
    atomic_json(rp, receipt)
    return receipt


def finite_score(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and 0 <= value <= 1


def score_failure(runtime, slot, mismatches):
    if mismatches:
        return 'alignment_identity_mismatch'
    if not finite_score(runtime['recognition_confidence']):
        return 'invalid_line_confidence'
    if runtime['recognition_confidence'] <= .5:
        return 'line_confidence_at_or_below_0.5'
    regions = [r for r in runtime['recognition_evidence']['regions'] if r['start'] == slot['start']]
    if not regions:
        return 'window_outside_native_image_or_scored_frames'
    if len(regions) != 1:
        return 'duplicate_region_start'
    if regions[0]['confidence'] <= .5:
        return 'regional_min_confidence_at_or_below_0.5'
    return 'source_locator_or_window_contract_failed'


def make_record(line_id, saved, runtime, alignment, image_width, provenance):
    new = alignment.to_record()
    mismatches = [k for k in IDENTITY_KEYS if saved[k] != new[k]]
    if saved.get('transferred'):
        mismatches.append('saved_transferred')
    if nfd(saved['prediction']) != nfd(runtime['recogniser_text']):
        mismatches.append('saved_runtime_text')
    evidence = alignment.recognition_evidence(runtime['detector']['slots'], image_width)
    if mismatches:
        evidence.update(scored=False, provenance='alignment_identity_mismatch', regions=[])
    record = dict(line_id=line_id, frame_confidences=alignment.frame_confidences,
        recognition_confidence=alignment.confidence, recognition_evidence=evidence, image_width=image_width,
        provenance=dict(provenance, alignment_identity_sha256=digest(alignment_identity(new)),
            saved_alignment_identity_sha256=digest(alignment_identity(saved)),
            alignment_identity_match=not mismatches, alignment_mismatches=mismatches,
            saved_text_sha256=hashlib.sha256(nfd(runtime['recogniser_text']).encode()).hexdigest()))
    scored = dict(runtime, **recognition_fields(record))
    counts = Counter(lines=1, lines_scored=int(finite_score(alignment.confidence)),
        above_floor_lines=int(finite_score(alignment.confidence) and alignment.confidence > .5),
        alignment_identity_matches=int(not mismatches), alignment_identity_mismatches=int(bool(mismatches)),
        slots=len(runtime['detector']['slots']), slots_with_regional_evidence=len(evidence['regions']))
    failures = Counter()
    for slot in runtime['detector']['slots']:
        if _recogniser_scored(scored, slot, slot.get('evidence', {}).get('window')):
            counts['sf6c_certified_slots'] += 1
        else:
            failures[score_failure(scored, slot, mismatches)] += 1
    counts['lines_with_sf6c_certified_slot'] = int(counts['sf6c_certified_slots'] > 0)
    counts['lines_failing_sf6c_predicate'] = int(bool(failures))
    counts['lines_without_detector_slots'] = int(not runtime['detector']['slots'])
    return record, counts, failures


def validate_shard(directory, binding, task):
    receipt = load(directory / 'receipt.json')
    if receipt['binding'] != binding or receipt['task'] != task or not receipt.get('complete'):
        raise ValueError('resume shard binding/task mismatch')
    if sha256(directory / 'frames.jsonl.gz') != receipt['output_sha256']:
        raise ValueError('resume output hash mismatch')
    return receipt


def worker(rank, cfg, out, plan, binding, mock):
    import torch
    from PIL import Image
    device = 'cpu' if mock else f'cuda:{rank}'
    if not mock:
        torch.cuda.set_device(rank)
        if 'GH200' not in torch.cuda.get_device_name(rank):
            raise ValueError('expected GH200 GPU')
    rec = None
    db = sqlite3.connect(f'file:{out / "plan.sqlite"}?mode=ro', uri=True)
    for task in plan['tasks']:
        if task['rank'] != rank:
            continue
        destination = out / 'shards' / f'shard-{task["shard"]:05d}'
        if destination.exists():
            validate_shard(destination, binding, task)
            continue
        if rec is None:
            rec = Recognizer(cfg['checkpoint'], device=device, threads=4 if mock else 8)
            if rec.meta.get('codec_sha256') and rec.meta['codec_sha256'] != sha256(VENDOR_CODEC):
                raise ValueError('checkpoint codec digest mismatch')
        started = time.monotonic()
        batch = db.execute('SELECT crop,id,wave,crop_sha,saved,runtime FROM lines '
                          'WHERE task=? ORDER BY ordinal', (task['shard'],)).fetchall()
        opened = []
        for crop, line_id, wave, wanted, saved, runtime in batch:
            data = crop_path(crop, cfg['crop_root'], cfg['layout']).read_bytes()
            if hashlib.sha256(data).hexdigest() != wanted:
                raise ValueError('crop changed before forward pass: ' + crop)
            image = Image.open(io.BytesIO(data)); image.load()
            opened.append((line_id, wave, image, json.loads(saved), json.loads(runtime)))
        # This is align_paths' original stable width sort, with the same
        # source chunk and companions, then the unmodified align_batch.
        opened.sort(key=lambda t: t[2].width / max(1, t[2].height))
        temp = out / 'shards' / f'.shard-{task["shard"]:05d}.partial'
        temp.mkdir(parents=True, exist_ok=True)
        counts, reasons, line_reasons = defaultdict(Counter), defaultdict(Counter), defaultdict(Counter)
        identities, mismatch_examples = [], []
        forward_seconds = 0.
        with gzip.open(temp / 'frames.jsonl.gz', 'wt', encoding='utf8', compresslevel=3) as dest:
            for start in range(0, len(opened), task['batch_size']):
                part = opened[start:start+task['batch_size']]
                tick = time.monotonic()
                alignments = rec.align_batch([item[2] for item in part])
                forward_seconds += time.monotonic()-tick
                if len(alignments) != len(part):
                    raise ValueError('incomplete forward batch')
                for (line_id, wave, image, saved, runtime), alignment in zip(part, alignments):
                    provenance = dict(checkpoint_sha256=cfg['checkpoint_sha256'],
                        safetensors_sha256=cfg['safetensors_sha256'], code_sha256=binding['code_sha256'],
                        input_binding_sha256=binding['input_binding_sha256'], device=device,
                        schema='l1f-frame-evidence-v1')
                    record, cc, rr = make_record(line_id, saved, runtime, alignment, image.width, provenance)
                    if (alignment.frame_confidences is None or len(alignment.frame_confidences) != alignment.n_frames
                            or not all(finite_score(v) for v in alignment.frame_confidences)
                            or not finite_score(alignment.confidence)):
                        raise ValueError('forward did not supply finite scored frames')
                    dest.write(json.dumps(record, ensure_ascii=False, allow_nan=False)+'\n')
                    counts[wave].update(cc); reasons[wave].update(rr); line_reasons[wave].update(rr.keys())
                    identities.append(line_id)
                    if record['provenance']['alignment_mismatches'] and len(mismatch_examples) < 20:
                        mismatch_examples.append(dict(line_id=line_id, **record['provenance']))
        for _, _, image, _, _ in opened:
            image.close()
        receipt = dict(schema='l1f-shard-v1', complete=True, binding=binding, task=task,
            lines=len(identities), line_ids_sha256=digest(sorted(identities)),
            coverage_per_wave=dict(counts), sf6c_failure_slots_per_wave=dict(reasons),
            sf6c_failure_lines_per_wave=dict(line_reasons), alignment_mismatch_examples=mismatch_examples,
            output_sha256=sha256(temp / 'frames.jsonl.gz'), elapsed_seconds=time.monotonic()-started,
            forward_seconds=forward_seconds, device=device, torch=torch.__version__,
            gpu=None if mock else torch.cuda.get_device_name(rank))
        atomic_json(temp / 'receipt.json', receipt); temp.rename(destination)
        print('L1F_SHARD '+json.dumps(dict(shard=task['shard'], lines=len(identities),
            mismatches=sum(c['alignment_identity_mismatches'] for c in counts.values()),
            seconds=receipt['elapsed_seconds'])), flush=True)
    db.close()


def run(cfg, out, mock=False, verify_only=False):
    started = time.monotonic()
    protected_inputs = [cfg['input_run'], cfg['binding_dir'], cfg['crop_root']]
    protected_inputs += [str(Path(p).parent) for p in cfg.get('mock_runtime', [])]
    separate_output(out, *protected_inputs)
    if not mock and not verify_only and not os.environ.get('SLURM_JOB_ID'):
        raise ValueError('production forward pass requires Slurm allocation')
    if mock != bool(cfg['verification_only']):
        raise ValueError('mock/production config mismatch')
    verification, selected, historical, inventory = verify(cfg, mock)
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    atomic_json(out / 'input_verification.json', verification)
    if verify_only:
        print('L1F_INPUTS '+json.dumps({k:v for k,v in verification.items() if k != 'inputs'}), flush=True)
        return verification
    sources = code_sources()
    binding = dict(config_sha256=digest(cfg), code_sha256=digest(sources),
        input_binding_sha256=digest(dict(inputs=verification['inputs'], crops=verification['crops'])))
    if (out / 'binding.json').exists() and load(out / 'binding.json') != binding:
        raise ValueError('resume input/code/config binding mismatch')
    atomic_json(out / 'binding.json', binding)
    atomic_json(out / 'code_sources.json', sources)
    plan = create_plan(cfg, selected, historical, inventory, out, binding)
    if mock:
        worker(0, cfg, out, plan, binding, True)
    else:
        ctx = mp.get_context('spawn')
        workers = [ctx.Process(target=worker, args=(i, cfg, out, plan, binding, False)) for i in range(4)]
        for process in workers: process.start()
        for process in workers: process.join()
        if any(p.exitcode != 0 for p in workers):
            raise RuntimeError('L1F worker failure; sealed shards can resume: '+str([p.exitcode for p in workers]))
    coverage, reasons, line_reasons = defaultdict(Counter), defaultdict(Counter), defaultdict(Counter)
    shards, seen, mismatches = [], set(), []
    for task in plan['tasks']:
        directory = out / 'shards' / f'shard-{task["shard"]:05d}'
        receipt = validate_shard(directory, binding, task)
        ids = []
        for row in rows(directory / 'frames.jsonl.gz'):
            if row['line_id'] in seen:
                raise ValueError('duplicate output line ID')
            seen.add(row['line_id']); ids.append(row['line_id'])
        if len(ids) != task['lines'] or digest(sorted(ids)) != receipt['line_ids_sha256']:
            raise ValueError('shard ID population mismatch')
        for key, target in [('coverage_per_wave', coverage), ('sf6c_failure_slots_per_wave', reasons),
                            ('sf6c_failure_lines_per_wave', line_reasons)]:
            for wave, values in receipt[key].items(): target[wave].update(values)
        mismatches.extend(receipt['alignment_mismatch_examples'])
        shards.append(dict(shard=task['shard'], receipt=str((directory/'receipt.json').relative_to(out)),
            receipt_sha256=sha256(directory/'receipt.json'), output=str((directory/'frames.jsonl.gz').relative_to(out)),
            output_sha256=receipt['output_sha256'], lines=len(ids)))
    if seen != {r['id'] for r in selected}:
        raise ValueError('output population differs from L1 selection')
    # Recheck every receipt-bound file and the plan. The pixels passed to the
    # model were separately hashed from the exact decoded bytes in each worker.
    for path, wanted in verification['inputs'].items(): checked(path, wanted, {})
    if code_sources() != sources or sha256(out/'plan.sqlite') != plan['sha256']:
        raise ValueError('code/plan changed during inference')
    total = Counter()
    for values in coverage.values(): total.update(values)
    final = dict(schema='l1f-final-v1', complete=True, verification_only=mock, lines=len(seen),
        job_id=os.environ.get('SLURM_JOB_ID'), binding=binding,
        input_verification_sha256=sha256(out/'input_verification.json'),
        plan_receipt_sha256=sha256(out/'plan_receipt.json'), code_sources_sha256=sha256(out/'code_sources.json'),
        shards=shards, totals=dict(total), coverage_per_wave=dict(coverage),
        sf6c_failure_slots_per_wave=dict(reasons), sf6c_failure_lines_per_wave=dict(line_reasons),
        alignment_identity_all_match=total['alignment_identity_mismatches']==0,
        alignment_mismatch_examples=mismatches[:40], never_replaces_saved_text=True,
        elapsed_seconds=time.monotonic()-started)
    atomic_json(out / 'receipt.json', final)
    print('L1F_COMPLETE '+json.dumps({k:v for k,v in final.items() if k not in ('shards','alignment_mismatch_examples')}), flush=True)
    return final


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--config', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--mock', action='store_true')
    ap.add_argument('--verify-only', action='store_true')
    a = ap.parse_args()
    run(load(a.config), a.out, a.mock, a.verify_only)


if __name__ == '__main__': main()
