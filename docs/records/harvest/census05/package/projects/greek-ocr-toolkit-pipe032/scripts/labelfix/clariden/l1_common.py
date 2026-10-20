"""SF2 L1r overlay/release consumer, derived from historical L1-v0 format."""
from __future__ import annotations

from collections import Counter
from difflib import SequenceMatcher
import hashlib
import json
from pathlib import Path
import unicodedata

from scripts.labelfix.clariden.r1_common import rows, write_rows, sha256, write_json
from greekocr.labelfix.text import nfd, elision_alias_key
from greekocr.labelfix.release_gate import compose_runtime, edit_guard, release_text, deletion_guard, POLICY, ENSEMBLE_CAVEAT

STATUSES = ('corrected', 'unchanged', 'hold', 'out_of_scope')


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def label_sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def hold_reason(reason):
    if reason.startswith(('ensemble_ab_mark_set_disagreement','ensemble_ae_mark_set_disagreement')):
        return 'ensemble_disagreement'
    if reason.startswith(('mark_kind_disagreement', 'mark_set_disagreement')):
        return 'kind_disagreement'
    if reason.startswith('K1:'):
        return 'k1_flag'
    if reason == 'r1_unsupported_letter':
        return 'recogniser_letter_problem'
    return 'localisation_unknown'


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
        gate_decisions=[{k:s.get(k) for k in ('start','base','label_status','hold_reasons',
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


def release(selection, runtime_paths, out, binding, source, input_receipt, variants=('presence','full'), workers=1):
    """Stream both variants, with one explicit kept-line list shared by each control."""
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    original_sha = sha256(source)
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
