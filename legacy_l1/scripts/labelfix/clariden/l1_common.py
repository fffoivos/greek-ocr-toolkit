"""L1 overlay/release policy. Original labels are read-only inputs."""
from __future__ import annotations

from collections import Counter
from difflib import SequenceMatcher
import hashlib
import json
from pathlib import Path
import unicodedata

from scripts.labelfix.clariden.r1_common import rows, write_rows, sha256, write_json
from greekocr.labelfix.text import nfd

DETECTOR_COMMIT = 'efdf5756'
R1_SHA = '719a06'  # Full checkpoint digest is frozen by prepare, never prefix-checked at runtime.
WAVES = dict(round1=43869, parliament=27224, vouli=23088, round2=17026, mixed=13227)
STATUSES = ('corrected', 'unchanged', 'hold', 'out_of_scope')
PUNCTUATION = frozenset("'’ʼ᾽“”«»„\"")


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def label_sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def skeleton(text):
    return ''.join(c for c in nfd(text) if not unicodedata.combining(c) and c not in PUNCTUATION).strip()


def hold_reason(reason):
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
    mode = runtime['modes'][variant.upper()]
    for slot in mode['hold_slots']:
        for reason in slot['reasons']:
            result['hold_slots'].append(dict(start=slot['start'], letter=slot['base'],
                reason=hold_reason(reason), detail=reason))
    proposal = mode['text']
    if skeleton(original) != skeleton(runtime['recogniser_text']) or skeleton(original) != skeleton(proposal):
        result['hold_slots'].append(dict(start=0, letter='', reason='recogniser_letter_problem',
            detail='original/recogniser/proposal base letters or non-mark punctuation differ'))
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
            slots=[dict(start=s['start'], letter=s['base'], detector_parts=s.get('detector_parts'),
                        r1_parts=s.get('r1_parts'), locator_span=s.get('locator_span'),
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


def parity_projection(runtime):
    """Exact UTF-8 reading/HOLD decisions; floating probabilities are not decisions."""
    return dict(id=runtime['id'], recogniser_text=runtime['recogniser_text'],
        detector=dict(text=runtime['detector']['text'],
            slots=[dict(start=s['start'], base=s['base'], parts=s['parts'],
                        localisation_unknown=s.get('localisation_unknown', False),
                        unnamed=s.get('unnamed', False), apostrophe=s.get('apostrophe', False))
                   for s in runtime['detector']['slots']]),
        modes={m: dict(text=r['text'],
            slots=[dict(start=s['start'], base=s['base'], parts=s['parts'], hold=s['hold'],
                        hold_reasons=s['hold_reasons']) for s in r['slots']],
            hold_slots=r['hold_slots']) for m, r in runtime['modes'].items()})


def release(selection, runtime_paths, out, binding, source, input_receipt):
    """Stream both variants, with one explicit kept-line list shared by each control."""
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    original_sha = sha256(source)
    records = {r['id']: r for r in rows(selection)}
    import gzip
    handles = {v: gzip.open(out / f'overlay_{v}.jsonl.gz', 'xt', encoding='utf-8', compresslevel=3)
               for v in ('presence', 'full')}
    counts = {v: Counter({s: 0 for s in STATUSES}) for v in handles}
    coverage = {v: {'wave': {}, 'source': {}} for v in handles}
    kept = {v: [] for v in handles}
    control = {v: gzip.open(out / f'ctrl_subset_{v}.jsonl.gz', 'xt', encoding='utf-8', compresslevel=3)
               for v in handles}
    seen = set()
    try:
        for path in runtime_paths:
            for runtime in rows(path):
                identifier = runtime['id']
                if identifier not in records or identifier in seen:
                    raise ValueError('unexpected/duplicate L1 runtime: ' + identifier)
                seen.add(identifier)
                record = records[identifier]
                for variant in handles:
                    value = overlay(record, runtime, variant, binding)
                    handles[variant].write(canonical(value) + '\n')
                    counts[variant][value['status']] += 1
                    for dim, key in [('wave', record['wave']), ('source', record.get('source', record.get('source_dataset', 'UNKNOWN')))]:
                        bucket = coverage[variant][dim].setdefault(key, Counter({s: 0 for s in STATUSES}))
                        bucket[value['status']] += 1
                    if value['status'] in ('corrected', 'unchanged'):
                        kept[variant].append(identifier)
                        control[variant].write(canonical(dict(line_id=identifier, label=record['label'],
                            original_label_sha256=value['original_label_sha256'])) + '\n')
    finally:
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
        suffix = '' if binding['detector'] == 's6' else '-' + binding['detector']
        manifest = dict(schema='l1-release-v1', release=f'v2-corrected-{variant}{suffix}',
            variant=variant, overlay=op.name, overlay_sha256=sha256(op),
            source_label_file=str(source), source_sha256=original_sha,
            selection_sha256=sha256(selection), counts_by_status=dict(counts[variant]),
            coverage_per_wave=coverage[variant]['wave'], coverage_per_source=coverage[variant]['source'],
            kept_line_ids=kp.name, kept_line_ids_sha256=sha256(kp), kept_lines=len(kept[variant]),
            exclusion_receipts=input_receipt['exclusions'], out_of_scope=input_receipt['out_of_scope'],
            r0_policy=input_receipt['r0_policy'], input_documents_sha256=input_receipt['input_documents_sha256'],
            code_commit=binding['code_commit'], detector_commit=binding['detector_commit'],
            detector_version=binding['detector'], r1_sha=binding['r1_sha256'], policy_sha=binding['policy_sha256'],
            hold_policy='HOLD and out_of_scope lines excluded; original source never modified',
            original_labels_unchanged=True)
        write_json(out / f'release_{variant}.json', manifest)
        write_json(out / f'release_ctrl_subset_{variant}.json', dict(manifest,
            release=f'v2-ctrl-subset-{variant}{suffix}', labels='ORIGINAL',
            labels_file=cp.name, labels_sha256=sha256(cp),
            paired_release=f'v2-corrected-{variant}{suffix}', corrected_and_control_line_sets_equal=True))
    return {v: dict(counts[v]) for v in handles}
