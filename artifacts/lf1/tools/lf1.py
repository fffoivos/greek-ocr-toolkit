"""LF1 answer mapping and draw-order replacement. No image/text inference."""
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
PACK_ROOT = Path('/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/lf1_packs')
SCANNER_SHA = 'e44f8c8a3c6d478c3dc299863478fcab210298f1c1429870d516c546f0f54ad1'
# Ordered table: question is phrased as a fault; yes means that named fault.
CROP_TABLE = (
    ('one_central_line', 'one_central_line'),
    ('text_ne_visible_line', 'text_ne_visible_line'),
    ('other_complete_line', 'other_complete_line'),
    ('gt2_whole_neighbour_words', 'gt2_whole_neighbour_words'),
    ('turned_or_clipped', 'turned_or_clipped'),
)
TEXT_ERRORS = {'wrong_letter', 'lookalike_script_letter', 'missing_word_or_span',
               'extra_text', 'punctuation', 'hyphen', 'digits'}

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def rows(p):
    return [json.loads(l) for l in Path(p).read_text().splitlines() if l.strip()]

def dump(p, value):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n')

def jsonl(p, value):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(''.join(json.dumps(v, ensure_ascii=False, allow_nan=False)+'\n' for v in value))

class Unresolved(ValueError):
    """No authorized verdict for incomplete/uncertain evidence; never auto-OK."""

def map_answer(answer, label):
    flags = answer.get('owner_crop', {})
    if set(flags) != {f for f, _ in CROP_TABLE}:
        raise Unresolved('missing or extra owner question fields')
    if any(v not in ('yes', 'no', 'uncertain') for v in flags.values()):
        raise Unresolved('invalid owner question value')
    faults = [reason for field, reason in CROP_TABLE if flags[field] == 'yes']
    evidence = {k: answer[k] for k in ('reading', 'detail', 'segmentation_detail') if k in answer}
    result = dict(card_id=answer['card_id'], evidence=evidence)
    # Positive crop fault precedes unknowns and text differences (gate2 ordering).
    if faults:
        return result | dict(verdict='CROP_VIOLATES', reasons=faults)
    if 'uncertain' in flags.values() or answer.get('letters') not in ('y', 'n'):
        raise Unresolved('uncertain crop or letters: handover section 8 human routing')
    errors = answer.get('errors')
    if not isinstance(errors, list):
        raise Unresolved('missing errors')
    # marks and crop_ok deliberately do not participate.
    if answer['letters'] == 'n' or TEXT_ERRORS.intersection(errors):
        where = answer.get('where')
        if not isinstance(where, list) or not where:
            raise Unresolved('TEXT_DIFFERS requires differing span')
        for span in where:
            if (set(span) != {'label', 'printed'} or
                not all(isinstance(v, str) for v in span.values()) or
                span['label'] not in label):
                raise Unresolved('where needs a literal label substring and printed string')
        return result | dict(verdict='TEXT_DIFFERS', where=where)
    return result | dict(verdict='OK')

def replace_flagged(flagged_ids, selected, overdraw, used_ids=()):
    """Take first unused same class+source, scanning the supplied list in order."""
    by_id = {r['line_id']: r for r in selected}
    used = set(used_ids) | set(by_id)
    records = []
    for old_id in flagged_ids:
        old = by_id[old_id]
        replacement = next((r for r in overdraw if r['line_id'] not in used and
                            (r['class'], r['source']) == (old['class'], old['source'])), None)
        rec = dict(flagged_id=old_id, **{'class': old['class']}, source=old['source'])
        if replacement is None:
            rec.update(status='UNFILLED', replacement_id=None)
        else:
            used.add(replacement['line_id'])
            rec.update(status='REPLACED', replacement_id=replacement['line_id'],
                       overdraw_index=overdraw.index(replacement))
        records.append(rec)
    return records

def require_budget(percent):
    if percent >= 90:
        raise RuntimeError('weekly usage >=90%; context refused (NIGHT_PLAN P6)')

def map_context(directory, key_file, destination):
    directory = Path(directory); destination = Path(destination)
    items = rows(directory/'items.jsonl'); answers = rows(directory/'answers.jsonl')
    if [r.get('card_id') for r in answers] != [r['card_id'] for r in items]:
        raise ValueError('answer coverage/order differs from items')
    key = json.loads(Path(key_file).read_text())['items']
    mapped = []; unresolved = []; control_checks = []
    for item, answer in zip(items, answers):
        try:
            verdict = map_answer(answer, item['google_text'])
        except Unresolved as exc:
            unresolved.append(dict(card_id=item['card_id'], reason=str(exc)))
            continue
        mapped.append(verdict)
        k = key[item['card_id']]
        if k['control']:
            expected = k['expected']
            correct = verdict['verdict'] == expected['verdict']
            if expected['verdict'] == 'CROP_VIOLATES':
                correct = correct and set(expected['reasons']).issubset(verdict.get('reasons', []))
            control_checks.append(dict(card_id=item['card_id'], correct=correct))
    jsonl(destination/'verdicts.jsonl', mapped)
    jsonl(destination/'unresolved.jsonl', unresolved)
    receipt = dict(answers_sha256=sha(directory/'answers.jsonl'),
                   items_sha256=sha(directory/'items.jsonl'), key_sha256=sha(key_file),
                   mapper_sha256=sha(__file__), verdicts_sha256=sha(destination/'verdicts.jsonl'),
                   mapped=len(mapped), unresolved=len(unresolved), control_checks=control_checks,
                   control_errors=sum(not x['correct'] for x in control_checks))
    receipt['control_flag'] = receipt['control_errors'] > 1  # HANDOVER section 4; diagnostic.
    dump(destination/'mapping_receipt.json', receipt)
    return receipt
