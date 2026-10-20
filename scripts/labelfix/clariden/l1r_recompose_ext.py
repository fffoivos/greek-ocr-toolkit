"""Receipt-bound SF6c recomposition; no detector, inference or submission.

--verify-only streams SHA-256 reads in place. Independent shard workers write
atomic receipts and support exact-input reuse after a timeout.
"""
from __future__ import annotations
from greekocr.ops.data_root import input_path as _data_input
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import multiprocessing as mp
from pathlib import Path
import shutil
import time
import uuid
from greekocr.labelfix.release_gate import MODES, POLICY, ENSEMBLE_CAVEAT, compose_runtime, policy_binding
from difflib import SequenceMatcher
import unicodedata
from greekocr.labelfix.text import nfd, elision_alias_key
from greekocr.labelfix.release_gate import edit_guard, release_text, deletion_guard
from scripts.labelfix.clariden.l1_common import STATUSES, canonical, label_sha, hold_reason, rows, sha256, write_json
from scripts.labelfix.clariden.r1_common import write_rows

# Reconstructed from docs/records/archive/l1f_hashed_paths_20261017.patch applied
# to the frozen SF6c files. Keep its consumer additions outside policy_binding.
# overlay/_overlays/release below are the patched l1_common implementations;
# the remaining implementation is the patched l1r_recompose module.
def overlay(record, runtime, variant, binding):
    original = record['label']
    result = dict(line_id=record['id'], original_label_sha256=label_sha(original),
                  changes=[], hold_slots=[], detector_version=binding['detector'],
                  r1_sha=binding['r1_sha256'], policy_sha=binding['policy_sha256'])
    if record['script_class'] != 'greek_poly':
        return dict(result, status='out_of_scope')
    # Never trust previously composed decisions under an older policy.
    mode = compose_runtime(runtime,variant.upper())
    result.update(release_policy=POLICY,evidence_sha256=mode['evidence_sha256'],opening_quotes=mode['opening_quotes'],
        composed_text=mode['text'],
        gate_decisions=[{k:s.get(k) for k in ('start','base','parts','label_status','hold_reasons',
            'r1_coverage','segmentation_uncertain','localisation_unknown','unnamed',
            'detector_parts','r1_parts','peer_arm','peer_prediction','peer_coverage','evidence','constraint_flags','apostrophe')}
            for s in mode['slots']])
    for slot in mode['hold_slots']:
        for reason in slot['reasons']:
            result['hold_slots'].append(dict(start=slot['start'], letter=slot['base'],
                reason=hold_reason(reason), detail=reason))
    proposal, census = release_text(original, runtime['recogniser_text'], mode['text'])
    alias_only = (nfd(original)!=nfd(mode['text'])
                  and elision_alias_key(original)==elision_alias_key(mode['text']))
    result.update(alias_only=alias_only,elision_census=census)
    deletions=deletion_guard(original,proposal,runtime,mode)
    result['deletion_checks']=deletions
    for deletion in deletions:
        if not deletion['allowed']:
            result['hold_slots'].append(dict(start=deletion['start'],letter=deletion['character'],
                reason='deletion_uncertain',detail=deletion['reason']))
    for detail in edit_guard(original, runtime['recogniser_text']) + edit_guard(original,proposal):
        result['hold_slots'].append(dict(start=0,letter='',reason='edit_guard',detail=detail))
    if result['hold_slots']:
        return dict(result, status='hold')
    if nfd(original) == nfd(proposal):
        return dict(result, status='unchanged', label=original)
    old, new = nfd(original), nfd(proposal)
    for tag, i, j, lo, hi in SequenceMatcher(None, old, new, autojunk=False).get_opcodes():
        if tag == 'equal':
            continue
        # Evidence is recogniser-indexed; edits are original-label NFD offsets.
        evidence = dict(recogniser_text=runtime['recogniser_text'], agreement=variant,
            slots=[dict(start=s['start'], letter=s['base'], r1_coverage=s.get('r1_coverage'),
                        segmentation_uncertain=s.get('segmentation_uncertain'),localisation_unknown=s.get('localisation_unknown'),
                        hold_reasons=s.get('hold_reasons'),detector_parts=s.get('detector_parts'),
                        r1_parts=s.get('r1_parts'),peer_arm=s.get('peer_arm'),peer_prediction=s.get('peer_prediction'),
                        peer_coverage=s.get('peer_coverage'),locator_span=s.get('locator_span'),
                        mark_probabilities=s.get('mark_probabilities'), evidence=s.get('evidence'))
                   for s in mode['slots']],
            opening_quotes=mode.get('opening_quotes', []), detector_text=runtime['detector']['text'])
        context = i
        if (lo < hi and unicodedata.combining(new[lo])) or (i < j and unicodedata.combining(old[i])):
            context -= 1
        while context >= 0 and context < len(old) and unicodedata.combining(old[context]):
            context -= 1
        letter = old[context] if 0 <= context < len(old) and old[context].isalpha() else ''
        result['changes'].append(dict(start=i, letter=letter,
                                      **{'from': old[i:j], 'to': new[lo:hi]}, evidence=evidence))
    return dict(result, status='corrected', label=proposal)

def _overlays(task):
    record,runtime,variants,binding=task
    return runtime['id'],{v:overlay(record,runtime,v,binding) for v in variants}

def release(selection, runtime_paths, out, binding, source, input_receipt, variants=('presence','full'), workers=1,
            *, verified_source_sha256=None):
    """Stream both variants, with one explicit kept-line list shared by each control."""
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    # Shard orchestration verifies the complete source before and after all
    # shards. Avoid rereading that same full manifest twice per shard.
    original_sha = verified_source_sha256 or sha256(source)
    selected=list(rows(selection))
    records = {r['id']: r for r in selected}
    if len(records)!=len(selected):raise ValueError('duplicate selection IDs')
    import gzip
    handles = {v: gzip.open(out / f'overlay_{v}.jsonl.gz', 'xt', encoding='utf-8', compresslevel=3)
               for v in variants}
    counts = {v: Counter({s: 0 for s in STATUSES}) for v in handles}
    aliases = Counter()
    coverage = {v: {'wave': {}, 'source': {}} for v in handles}
    kept = {v: [] for v in handles}
    control = {v: gzip.open(out / f'ctrl_subset_{v}.jsonl.gz', 'xt', encoding='utf-8', compresslevel=3)
               for v in handles}
    seen = set()
    pool=None
    try:
        def tasks():
            for path in runtime_paths:
                for runtime in rows(path):
                    identifier = runtime['id']
                    if identifier not in records or identifier in seen:
                        raise ValueError('unexpected/duplicate L1 runtime: ' + identifier)
                    seen.add(identifier)
                    yield records[identifier],runtime,variants,binding
        if workers>1:
            import multiprocessing as mp
            from itertools import islice
            pool=mp.get_context('spawn').Pool(workers)
            def bounded_results():
                work=tasks()
                while batch:=list(islice(work,workers*8)):
                    yield from pool.imap(_overlays,batch,chunksize=8)
            results=bounded_results()
        else:results=map(_overlays,tasks())
        for identifier,values in results:
            record = records[identifier]
            for variant in handles:
                value = values[variant]
                handles[variant].write(canonical(value) + '\n')
                counts[variant][value['status']] += 1
                aliases[variant] += value.get('alias_only',False) and value['status']=='unchanged'
                for dim, key in [('wave', record['wave']), ('source', record.get('source', record.get('source_dataset', 'UNKNOWN')))]:
                    bucket = coverage[variant][dim].setdefault(key, Counter({s: 0 for s in STATUSES}))
                    bucket[value['status']] += 1
                    bucket['alias_only'] += value.get('alias_only',False) and value['status']=='unchanged'
                if value['status'] in ('corrected', 'unchanged'):
                    kept[variant].append(identifier)
                    control[variant].write(canonical(dict(line_id=identifier, label=record['label'],
                        original_label_sha256=value['original_label_sha256'])) + '\n')
    finally:
        if pool is not None:pool.terminate();pool.join()
        for f in [*handles.values(), *control.values()]:
            f.close()
    if seen != set(records):
        raise ValueError(f'incomplete runtime: {len(seen)}/{len(records)}')
    if verified_source_sha256 is None:
        assert original_sha == sha256(source), 'original labels changed'
    for variant in handles:
        op = out / f'overlay_{variant}.jsonl.gz'
        cp = out / f'ctrl_subset_{variant}.jsonl.gz'
        kp = out / f'kept_{variant}_line_ids.txt'
        kp.write_text(''.join(i + '\n' for i in sorted(kept[variant])))
        # Verify actual control payload, not just two aliases of an in-memory set.
        ctrl_ids = [r['line_id'] for r in rows(cp)]
        assert len(ctrl_ids) == len(set(ctrl_ids)) and set(ctrl_ids) == set(kept[variant])
        for dim in coverage[variant].values():
            for bucket in dim.values():
                bucket['total'] = sum(bucket[s] for s in STATUSES)
                bucket['kept'] = bucket['corrected'] + bucket['unchanged']
                bucket['kept_fraction'] = bucket['kept'] / bucket['total']
        suffix = '-r'
        release_name=variant.replace('_','-')
        manifest = dict(schema='l1r-release-v1', release_policy=POLICY, release=f'v2-corrected-{release_name}{suffix}',
            variant=variant, overlay=op.name, overlay_sha256=sha256(op),
            source_label_file=str(source), source_sha256=original_sha,
            selection_sha256=sha256(selection), counts_by_status=dict(counts[variant]),
            alias_only=aliases[variant],
            coverage_per_wave=coverage[variant]['wave'], coverage_per_source=coverage[variant]['source'],
            kept_line_ids=kp.name, kept_line_ids_sha256=sha256(kp), kept_lines=len(kept[variant]),
            exclusion_receipts=input_receipt['exclusions'], out_of_scope=input_receipt['out_of_scope'],
            r0_policy=input_receipt['r0_policy'], input_documents_sha256=input_receipt['input_documents_sha256'],
            code_commit=binding['code_commit'], detector_commit=binding['detector_commit'],
            detector_version=binding['detector'], r1_sha=binding['r1_sha256'], policy_sha=binding['policy_sha256'],
            hold_policy='HOLD and out_of_scope lines excluded; original source never modified',
            original_labels_unchanged=True, ensemble_caveat=ENSEMBLE_CAVEAT,
            checkpoint_sha256=binding.get('checkpoint_sha256',{'A':binding['r1_sha256']}),
            code_sha256=binding.get('code_sha256',{}),policy_binding=binding.get('policy_binding'))
        write_json(out / f'release_{variant}.json', manifest)
        write_json(out / f'release_ctrl_subset_{variant}.json', dict(manifest,
            release=f'v2-ctrl-subset-{release_name}{suffix}', labels='ORIGINAL',
            labels_file=cp.name, labels_sha256=sha256(cp),
            paired_release=f'v2-corrected-{release_name}{suffix}', corrected_and_control_line_sets_equal=True))
    return {v: dict(counts[v]) for v in handles}


VARIANTS = ('presence', 'full', 'ensemble_ab')
_RECORDS = {}


def load(path):
    return json.loads(_data_input(Path(path)).read_text())


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def atomic_json(path, value):
    path = Path(path)
    tmp = path.with_name(path.name + '.partial')
    write_json(tmp, value)
    tmp.replace(path)


def separate_output(out, *inputs):
    out = Path(out).resolve()
    for original in inputs:
        original = Path(original).resolve()
        if out == original or original in out.parents or out in original.parents:
            raise ValueError('output must be separate from historical inputs: ' + str(original))


def verify_inputs(input_run, selection, binding_dir, source, ensemble_run=None, *, expected=None, workers=4):
    """Verify the receipt DAG before creating releases; never loads pixels.

    L1E's downstream recomposition/run receipt is deliberately not required.
    Completion follows the complete inference receipt and every shard receipt.
    """
    started = time.monotonic()
    base, selection, source = Path(input_run), Path(selection), Path(source)
    inputs = {}

    def checked(path, wanted=None):
        path = Path(path)
        got = sha256(path)
        if wanted is not None and got != wanted:
            raise ValueError('hash mismatch: ' + str(path))
        if str(path) in inputs and inputs[str(path)] != got:
            raise ValueError('input changed: ' + str(path))
        inputs[str(path)] = got
        return got

    for name, wanted in (expected or {}).items():
        checked(name, wanted)
    checked(base / 'run_receipt.json')
    run = load(base / 'run_receipt.json')
    if not run.get('complete'):
        raise ValueError('incomplete historical run')
    bp = Path(binding_dir) / 'binding.json'
    checked(bp, run['binding_sha256'])
    binding = load(bp)
    for name, wanted in run['step_receipts'].items():
        checked(base / name, wanted)
    checked(selection)
    inp = load(base / 'input_receipt.json')
    # The saved L1E mock predates the source field in input_receipt. Its
    # source is byte-identical to its pinned, verification-only selection.
    if 'source_sha256' not in inp:
        if not (run.get('mock') and run.get('verification_only') and sha256(source) == inputs[str(selection)]):
            raise ValueError('missing historical source binding')
        inp['source_sha256'] = inputs[str(selection)]
    checked(source, inp['source_sha256'])
    if binding.get('source_sha256', inputs[str(source)]) != inputs[str(source)]:
        raise ValueError('binding source mismatch')
    top = load(base / 'detector/detector_receipt.json')
    if not top.get('complete') or top['selection_sha256'] != inputs[str(selection)]:
        raise ValueError('detector selection mismatch/incomplete')
    selected = list(rows(selection))
    ids = [r['id'] for r in selected]
    if len(ids) != len(set(ids)) or len(ids) != run['lines'] or top['lines'] != len(ids):
        raise ValueError('selection line count/uniqueness mismatch')
    entries = sorted(top['shards'], key=lambda e: e['shard'])
    numbers = [e['shard'] for e in entries]
    if numbers != list(range(len(entries))):
        raise ValueError('missing/duplicate detector shard')
    expected_files, tasks = {}, []
    for e in entries:
        n = e['shard']
        dp = base / 'detector' / f'shard-{n:05d}-receipt.json'
        if str(dp) not in inputs or load(dp) != e or not e.get('complete'):
            raise ValueError('unbound/incomplete detector shard: ' + str(n))
        for name, wanted in e['sha256'].items():
            expected_files[str(base / 'detector' / name)] = wanted
        rp = base / 'combined' / f'shard-{n:05d}-receipt.json'
        if str(rp) not in inputs:
            raise ValueError('unbound A shard: ' + str(n))
        ar = load(rp)
        if not ar.get('complete') or ar['lines'] != e['lines'] or ar['samples'] != e['windows']:
            raise ValueError('incomplete A inference shard: ' + str(n))
        p = base / 'combined' / ar.get('output', f'shard-{n:05d}-combined.jsonl.gz')
        expected_files[str(p)] = ar['output_sha256']
        tasks.append(dict(shard=n, lines=e['lines'], samples=e['windows'], historical=str(p), runtime=str(p)))
    if {p.name for p in (base / 'combined').glob('shard-*-combined.jsonl.gz')} != {Path(t['historical']).name for t in tasks}:
        raise ValueError('unexpected/missing A shard files')
    if sum(t['lines'] for t in tasks) != len(selected):
        raise ValueError('shard population differs from selection')
    peer = None
    if ensemble_run is not None:
        ep = Path(ensemble_run) / 'r1e_receipt.json'
        checked(ep)
        peer = load(ep)
        if not peer.get('complete') or peer['historical_run_receipt_sha256'] != inputs[str(base / 'run_receipt.json')]:
            raise ValueError('incomplete/unbound B/E inference')
        if peer['selection_sha256'] != inputs[str(selection)] or peer['lines'] != len(selected):
            raise ValueError('B/E selection mismatch')
        if set(peer['checkpoint_sha256']) != {'A', 'B', 'E'} or peer['checkpoint_sha256']['A'] != binding['r1_sha256']:
            raise ValueError('B/E checkpoint mismatch')
        bynumber = {}
        for e in peer['shards']:
            rp = Path(ensemble_run) / e['receipt']
            checked(rp, e['receipt_sha256'])
            sr = load(rp)
            n = sr['shard']
            if n in bynumber or n not in numbers or not sr.get('complete'):
                raise ValueError('missing/duplicate/incomplete B/E shard')
            t = tasks[n]
            if (sr['lines'], sr['samples']) != (t['lines'], t['samples']) or (e['lines'], e['samples']) != (t['lines'], t['samples']):
                raise ValueError('incomplete B/E inference population')
            si = sr['inputs']
            dr = base / 'detector' / f'shard-{n:05d}-receipt.json'
            if (si['historical_combined_sha256'] != expected_files[t['historical']]
                    or si['window_receipt_sha256'] != inputs[str(dr)]
                    or si['checkpoint_sha256'] != peer['checkpoint_sha256']
                    or si['code_sha256'] != peer['code_sha256']):
                raise ValueError('B/E shard input binding mismatch')
            p = Path(ensemble_run) / sr['output']
            expected_files[str(p)] = sr['output_sha256']
            bynumber[n] = str(p)
        if set(bynumber) != set(numbers) or peer['samples'] != sum(t['samples'] for t in tasks):
            raise ValueError('B/E inference incomplete for one or more shards')
        for t in tasks:
            t['runtime'] = bynumber[t['shard']]
        if {p.name for p in Path(ensemble_run).glob('shard-*-combined.jsonl.gz')} != {Path(p).name for p in bynumber.values()}:
            raise ValueError('unexpected/missing B/E shard files')

    def hash_file(item):
        name, wanted = item
        if sha256(name) != wanted:
            raise ValueError('hash mismatch: ' + name)
        return name, wanted

    with ThreadPoolExecutor(max_workers=workers) as pool:
        inputs.update(pool.map(hash_file, expected_files.items()))
    result = dict(schema='l1r-input-verification-v1', complete=True, lines=len(selected),
                  shards=len(tasks), samples=sum(t['samples'] for t in tasks),
                  inputs=inputs, inputs_sha256=digest(inputs), historical_run=str(base),
                  ensemble_run=str(ensemble_run) if ensemble_run else None,
                  checkpoint_sha256=peer['checkpoint_sha256'] if peer else {'A': binding['r1_sha256']},
                  historical_inference_code_sha256=peer['code_sha256'] if peer else {},
                  elapsed_seconds=time.monotonic() - started)
    return result, tasks, selected, binding, inp


def decision_record(runtime):
    return {m: compose_runtime(runtime, m) for m in MODES}


def validate_release(out, selected, variants):
    """Read actual overlay/control payloads, not aliases of an in-memory set."""
    out = Path(out)
    records = {r['id']: r for r in selected}
    for v in variants:
        m = load(out / f'release_{v}.json')
        c = load(out / f'release_ctrl_subset_{v}.json')
        name = v.replace('_', '-')
        if m['release'] != f'v2-corrected-{name}-sf6' or c['release'] != f'v2-ctrl-subset-{name}-sf6':
            raise ValueError('invalid SF5 release name')
        for manifest in (m, c):
            if manifest['release_policy'] != POLICY or manifest['ensemble_caveat'] != ENSEMBLE_CAVEAT:
                raise ValueError('invalid policy/caveat')
            if sha256(out / manifest['input_verification_file']) != manifest['input_verification_sha256']:
                raise ValueError('input verification receipt changed')
            for key, hk in [('overlay', 'overlay_sha256'), ('kept_line_ids', 'kept_line_ids_sha256')]:
                if sha256(out / manifest[key]) != manifest[hk]:
                    raise ValueError('release payload hash mismatch')
        if sha256(out / c['labels_file']) != c['labels_sha256']:
            raise ValueError('control hash mismatch')
        seen, accepted, counts = set(), set(), Counter()
        for r in rows(out / m['overlay']):
            i = r['line_id']
            if r['status'] not in STATUSES:
                raise ValueError('invalid release status')
            if i in seen or i not in records or r['original_label_sha256'] != label_sha(records[i]['label']):
                raise ValueError('overlay original label/ID mismatch')
            seen.add(i)
            counts[r['status']] += 1
            if r['status'] in ('corrected', 'unchanged'):
                if r['hold_slots']:
                    raise ValueError('HOLD line admitted')
                accepted.add(i)
            elif 'label' in r:
                raise ValueError('excluded line has release label')
        kept = (out / m['kept_line_ids']).read_text().splitlines()
        controls = list(rows(out / c['labels_file']))
        if (seen != set(records) or len(kept) != len(set(kept)) or set(kept) != accepted
                or len(controls) != len(accepted) or {r['line_id'] for r in controls} != accepted
                or m['kept_lines'] != len(accepted) or dict(counts) != {k: n for k, n in m['counts_by_status'].items() if n}):
            raise ValueError('release/control population mismatch')
        for r in controls:
            if r['label'] != records[r['line_id']]['label'] or r['original_label_sha256'] != label_sha(r['label']):
                raise ValueError('control label modified')
        for dimension in ('coverage_per_wave', 'coverage_per_source'):
            if sum(b['total'] for b in m[dimension].values()) != len(records):
                raise ValueError('coverage population mismatch')
    return dict(complete=True, lines=len(records), variants=list(variants),
                original_label_sha_every_line=True, hold_excluded=True, exact_control_pairing=True)


def _initialise(selection):
    global _RECORDS
    _RECORDS = {r['id']: r for r in rows(selection)}


def code_sources():
    root = Path(__file__).resolve().parents[3]
    paths = sorted((root / 'greekocr').rglob('*.py')) + sorted((root / 'scripts/labelfix').rglob('*.py'))
    paths.append(root / 'scripts/labelfix/clariden/l1r_job.sbatch')
    paths.extend(root / 'scripts/labelfix/clariden' / name for name in
                 ('l1r4_job.sbatch', 'l1r4_census_job.sbatch', 'l1r4_preflight.sh')
                 if (root / 'scripts/labelfix/clariden' / name).exists())
    return {str(p.relative_to(root)): sha256(p) for p in paths}


def _shard(task):
    t, out, binding, source, inp, audit = task
    started = time.monotonic()
    runtime = list(rows(t['runtime']))
    if any(r['id'] not in _RECORDS for r in runtime):
        raise ValueError('unexpected runtime ID')
    selected = [_RECORDS[r['id']] for r in runtime]
    dest = Path(out) / 'shards' / f'shard-{t["shard"]:05d}'
    reuse_binding = dict(runtime_sha256=sha256(t['runtime']), selection_sha256=digest(selected), binding=binding, audit=audit)
    rp = dest / 'receipt.json'
    if rp.exists():
        r = load(rp)
        if not r.get('complete') or r['inputs'] != reuse_binding:
            raise ValueError('stale recomposition shard receipt')
        for name, wanted in r['outputs'].items():
            if sha256(dest / name) != wanted:
                raise ValueError('recomposition shard output changed')
        return r
    historical = list(rows(t['historical']))
    byid = {r['id']: r for r in selected}
    if len(runtime) != t['lines'] or len(historical) != t['lines'] or len(byid) != t['lines']:
        raise ValueError('runtime shard count mismatch')
    if [r['id'] for r in runtime] != [r['id'] for r in historical] or {r['id'] for r in runtime} != set(byid):
        raise ValueError('runtime/selection shard identity mismatch')
    for r, old in zip(runtime, historical):
        for k in ('detector', 'recogniser_text', 'coverage', 'r1_predictions'):
            if r[k] != old[k]:
                raise ValueError('L1E historical evidence changed: ' + k)
        for k in ('recogniser_nfd', 'recognition_confidence', 'recognition_evidence', 'image_width'):
            if (k in r, r.get(k)) != (k in old, old.get(k)):
                raise ValueError('L1E historical evidence changed: ' + k)
        if 'ensemble_ab' in binding['variants']:
            want = [(p['start'], p['base']) for p in r['r1_predictions']]
            if len(want) != len(set(want)):
                raise ValueError('duplicate A prediction')
            for arm in ('B', 'E'):
                ps = r.get('peer_predictions', {}).get(arm)
                cov = r.get('peer_coverage', {}).get(arm)
                if ps is None or cov is None or [(p['start'], p['base']) for p in ps] != want or cov != r['coverage']:
                    raise ValueError('B/E inference incomplete: ' + r['id'] + ':' + arm)
    partial = dest.with_name(dest.name + '.partial-' + uuid.uuid4().hex)
    partial.mkdir(parents=True)
    sp = partial / 'selection.jsonl'
    write_rows(sp, selected)
    runtime_path = t['runtime']
    if 'l1f_join' in binding:
        from scripts.labelfix.clariden.l1r4_join import join_runtime
        runtime = join_runtime(runtime, Path(out) / 'l1f_join.sqlite')
        runtime_path = partial / 'joined-runtime.jsonl.gz'
        write_rows(runtime_path, runtime)
    counts = release(sp, [runtime_path], partial / 'release', binding, source, inp, binding['variants'], workers=1,
                     verified_source_sha256=inp['source_sha256'])
    # Packaging census only: consume the frozen composer's actual overlays.
    elisions = {}
    for variant in binding['variants']:
        fields = ('google', 'recogniser', 'both', 'google_only', 'recogniser_only',
                  'both_kept', 'both_deleted', 'google_only_kept', 'google_only_deleted',
                  'recogniser_only_kept', 'recogniser_only_deleted', 'added',
                  'spacing_breathings', 'spacing_breathings_attached', 'aligned_lines', 'unaligned_lines')
        all_rows, released = Counter(dict.fromkeys(fields, 0)), Counter(dict.fromkeys(fields, 0))
        for row in rows(partial / 'release' / f'overlay_{variant}.jsonl.gz'):
            c = row.get('elision_census')
            if c is None:
                continue
            summary = {k: v for k, v in c.items() if k != 'aligned'}
            summary.update(aligned_lines=int(c['aligned']), unaligned_lines=int(not c['aligned']))
            all_rows.update(summary)
            if row['status'] in ('corrected', 'unchanged'):
                released.update(summary)
        elisions[variant] = dict(elision_census=dict(all_rows), elision_census_released=dict(released))
    for p in (partial / 'release').glob('release_*.json'):
        m = load(p)
        m['release'] = m['release'].removesuffix('-r') + '-sf6'
        if 'paired_release' in m:
            m['paired_release'] = m['paired_release'].removesuffix('-r') + '-sf6'
        m.update(**elisions[m['variant']])
        m.update(input_verification_file='../../../input_verification.json',
                 input_verification_sha256=binding['input_verification_sha256'],
                 input_hashes_sha256=binding['input_hashes_sha256'],
                 historical_inference_code_sha256=binding['historical_inference_code_sha256'])
        write_json(p, m)
    validation = validate_release(partial / 'release', selected, binding['variants'])
    if audit:
        write_rows(partial / 'decisions.jsonl.gz', [dict(id=r['id'], decisions=decision_record(r)) for r in runtime])
    r = dict(schema='l1r-recomposition-shard-v1', complete=True, shard=t['shard'], lines=len(runtime),
             inputs=reuse_binding, counts=counts, validation=validation, elapsed_seconds=time.monotonic()-started,
             outputs={str(p.relative_to(partial)): sha256(p) for p in sorted(partial.rglob('*')) if p.is_file()})
    atomic_json(partial / 'receipt.json', r)
    partial.rename(dest)
    return r


def merge_shards(out, shards, selection, selected, variants):
    out = Path(out)
    if (out / 'release').exists():
        for v in variants:
            merged = load(out / 'release' / f'release_{v}.json')
            shard = load(out / 'shards' / f'shard-{shards[0]["shard"]:05d}' / 'release' / f'release_{v}.json')
            for key in ('policy_sha', 'input_hashes_sha256', 'code_sha256', 'input_verification_sha256'):
                if merged[key] != shard[key]:
                    raise ValueError('stale aggregated release')
        return validate_release(out / 'release', selected, variants)
    dest = out / ('release.partial-' + uuid.uuid4().hex)
    dest.mkdir()
    for v in variants:
        manifests = [load(out / 'shards' / f'shard-{r["shard"]:05d}' / 'release' / f'release_{v}.json') for r in shards]
        m = dict(manifests[0])
        for prefix in ('overlay_', 'ctrl_subset_'):
            name = prefix + v + '.jsonl.gz'
            with (dest / name).open('wb') as target:
                for r in shards:
                    with (out / 'shards' / f'shard-{r["shard"]:05d}' / 'release' / name).open('rb') as f:
                        shutil.copyfileobj(f, target, 1024 * 1024)
        kept = sorted(i for r in shards for i in (out / 'shards' / f'shard-{r["shard"]:05d}' / 'release' / m['kept_line_ids']).read_text().splitlines())
        (dest / m['kept_line_ids']).write_text(''.join(i + '\n' for i in kept))
        counts = Counter({s: 0 for s in STATUSES})
        for sub in manifests:
            counts.update(sub['counts_by_status'])
        m.update(input_verification_file='../input_verification.json',
                 selection_sha256=sha256(selection), counts_by_status=dict(counts), kept_lines=len(kept),
                 overlay_sha256=sha256(dest / m['overlay']), kept_line_ids_sha256=sha256(dest / m['kept_line_ids']))
        m['alias_only'] = sum(sub['alias_only'] for sub in manifests)
        for key in ('elision_census', 'elision_census_released'):
            total = Counter()
            for sub in manifests:
                total.update(sub[key])
            m[key] = dict(total)
        for dimension in ('coverage_per_wave', 'coverage_per_source'):
            combined = {}
            for sub in manifests:
                for name, b in sub[dimension].items():
                    combined.setdefault(name, Counter({s: 0 for s in STATUSES})).update({s: b[s] for s in (*STATUSES, 'alias_only')})
            for b in combined.values():
                b['total'] = sum(b[s] for s in STATUSES)
                b['kept'] = b['corrected'] + b['unchanged']
                b['kept_fraction'] = b['kept'] / b['total']
            m[dimension] = combined
        write_json(dest / f'release_{v}.json', m)
        cp = dest / f'ctrl_subset_{v}.jsonl.gz'
        write_json(dest / f'release_ctrl_subset_{v}.json', dict(m,
                   release=m['release'].replace('v2-corrected-', 'v2-ctrl-subset-'), labels='ORIGINAL',
                   labels_file=cp.name, labels_sha256=sha256(cp), paired_release=m['release'],
                   corrected_and_control_line_sets_equal=True))
    validation = validate_release(dest, selected, variants)
    dest.rename(out / 'release')
    return validation


def recompose(input_run, selection, binding_dir, source, out, ensemble_run=None, workers=1,
              *, expected=None, audit_decisions=False, code_commit='fbf491f5+L1R3-source-bound', l1f=None):
    started = time.monotonic()
    separate_output(out, input_run, *([ensemble_run] if ensemble_run else []), binding_dir, source, selection)
    verification, tasks, selected, binding, inp = verify_inputs(input_run, selection, binding_dir, source, ensemble_run,
                                                               expected=expected, workers=min(workers, 16))
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    join = None
    if l1f:
        from scripts.labelfix.clariden.l1r4_join import prepare_join
        separate_output(out, l1f['root'])
        join = prepare_join(l1f, selected, out, verification['inputs'])
        verification['inputs'].update(join['inputs'])
        verification['inputs_sha256'] = digest(verification['inputs'])
    vr = out / 'input_verification.json'
    if vr.exists() and load(vr)['inputs'] != verification['inputs']:
        raise ValueError('restart inputs changed')
    if not vr.exists():
        atomic_json(vr, verification)
    policy = policy_binding()
    variants = VARIANTS if ensemble_run else VARIANTS[:2]
    binding.update(historical_policy_sha256=binding['policy_sha256'], policy_sha256=policy['sha256'],
                   policy_binding=policy, code_sha256=code_sources(), code_commit=code_commit,
                   checkpoint_sha256=verification['checkpoint_sha256'], variants=list(variants),
                   input_verification_sha256=sha256(vr), input_hashes_sha256=verification['inputs_sha256'],
                   historical_inference_code_sha256=verification['historical_inference_code_sha256'],
                   audit_decisions=audit_decisions)
    if join:
        binding['l1f_join'] = dict(receipt_sha256=sha256(out / 'l1f_join_receipt.json'),
                                 index_sha256=sha256(out / 'l1f_join.sqlite'), spec=l1f)
    if (out / 'receipt.json').exists():
        prior = load(out / 'receipt.json')
        if not prior.get('complete') or prior['policy'] != policy or prior['binding'] != binding:
            raise ValueError('completed output binding changed')
        for name, wanted in prior['outputs'].items():
            if sha256(out / name) != wanted:
                raise ValueError('completed output changed')
        return prior
    work = [(t, str(out), binding, str(source), inp, audit_decisions) for t in tasks]
    if workers > 1:
        with mp.get_context('spawn').Pool(workers, initializer=_initialise, initargs=(selection,)) as pool:
            shards = []
            for r in pool.imap(_shard, work, chunksize=1):
                shards.append(r)
                print(f'L1R_SHARD {r["shard"]} lines={r["lines"]} seconds={r["elapsed_seconds"]:.3f}', flush=True)
    else:
        _initialise(selection)
        shards = list(map(_shard, work))
    validation = merge_shards(out, shards, selection, selected, variants)
    with ThreadPoolExecutor(max_workers=min(workers, 16)) as pool:
        for name, got in pool.map(lambda p: (p, sha256(p)), verification['inputs']):
            if got != verification['inputs'][name]:
                raise ValueError('input changed during recomposition: ' + name)
    if code_sources() != binding['code_sha256']:
        raise ValueError('recomposition code changed during run')
    receipt = dict(schema='l1r-recomposition-v2', complete=True, policy=policy, binding=binding,
                   inputs_sha256=verification['inputs_sha256'], input_verification_sha256=sha256(vr),
                   counts={v: load(out / 'release' / f'release_{v}.json')['counts_by_status'] for v in variants},
                   validation=validation, shards=[dict(shard=r['shard'], receipt=f'shards/shard-{r["shard"]:05d}/receipt.json',
                       receipt_sha256=sha256(out / 'shards' / f'shard-{r["shard"]:05d}' / 'receipt.json')) for r in shards],
                   outputs={str(p.relative_to(out)): sha256(p) for p in sorted((out / 'release').glob('*'))},
                   elapsed_seconds=time.monotonic()-started, network=False, detector_runs=0, r1_runs=0,
                   original_labels_unchanged=True)
    if join:
        receipt['outputs'].update({p: sha256(out / p) for p in ('l1f_join.sqlite', 'l1f_join_receipt.json')})
    atomic_json(out / 'receipt.json', receipt)
    return receipt


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for flag in ('input-run', 'selection', 'binding-dir', 'source', 'out'):
        ap.add_argument('--'+flag, type=Path)
    ap.add_argument('--config', type=Path)
    ap.add_argument('--ensemble-run', type=Path)
    ap.add_argument('--workers', type=int, default=1)
    ap.add_argument('--verify-only', action='store_true')
    ap.add_argument('--audit-decisions', action='store_true')
    a = ap.parse_args()
    cfg = load(a.config) if a.config else {}
    args = {k: cfg.get(k, getattr(a, k)) for k in ('input_run', 'selection', 'binding_dir', 'source', 'ensemble_run')}
    if not all(args[k] for k in ('input_run', 'selection', 'binding_dir', 'source')) or a.out is None or a.workers < 1:
        ap.error('input paths, --out and positive --workers required')
    expected = cfg.get('expected_sha256')
    if a.verify_only:
        separate_output(a.out, args['input_run'], args['binding_dir'], args['source'], args['selection'],
                        *([args['ensemble_run']] if args['ensemble_run'] else []))
        result = verify_inputs(**args, expected=expected, workers=a.workers)[0]
        a.out.parent.mkdir(parents=True, exist_ok=True)
        atomic_json(a.out, result)
    else:
        if not cfg.get('verification_only') and not __import__('os').environ.get('SLURM_JOB_ID'):
            ap.error('production recomposition requires a Slurm allocation')
        if cfg.get('verification_only') and load(Path(args['input_run']) / 'run_receipt.json')['lines'] != 64:
            ap.error('local mock must be the complete 64-line verification runtime')
        result = recompose(**args, out=a.out, workers=a.workers, expected=expected, audit_decisions=a.audit_decisions,
                           l1f=cfg.get('l1f'))
    print(json.dumps({k: v for k, v in result.items() if k not in ('inputs', 'outputs', 'shards', 'binding', 'historical_inference_code_sha256')}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
