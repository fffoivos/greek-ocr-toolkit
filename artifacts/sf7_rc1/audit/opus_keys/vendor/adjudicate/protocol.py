"""Shared independent-reader protocol, adapters, gating and truth custody."""
from __future__ import annotations
from collections import Counter
from copy import deepcopy
import gzip
import json
import os
from pathlib import Path
from typing import Any
import unicodedata

__all__ = ['adapt_answer', 'deal', 'tiebreak_deck', 'controls_gate', 'resolve', 'write_truth']

INSTRUCTIONS = '''# Independent print reading

Open only the assigned items manifest and the images it lists. Do not open
other files, parent directories, keys, reports or another reader's answers.
Read the literal printed form from both target and full-line pixels, including
case, script, punctuation and all marks. ∅ means no printed text/sign. An offered
option is never presumed true. Choose its letter, or use literal with a complete
transcription, or unreadable. Report clipping, ligatures and uncertainty in note.
Return {id, answer, printed, confidence: high|medium|low, note} for each item.
Reader 1 follows items_blind.json; reader 2 follows reader_2.json (reverse order).
Work independently. Disagreements receive an independent third reading with
new option letters. Do not infer print truth from agreement or prior knowledge.
'''
ANSWER_SCHEMA = {
    'type': 'object', 'required': ['id', 'confidence', 'note'],
    'properties': {
        'id': {'type': 'string'}, 'answer': {'type': 'string'}, 'choice': {'type': 'string'},
        'printed': {'type': ['string', 'null']}, 'transcription': {'type': ['string', 'null']},
        'confidence': {'enum': ['high', 'medium', 'low']}, 'note': {'type': 'string'}},
    'anyOf': [{'required': ['answer']}, {'required': ['choice']}],
}
_UNKNOWN = {'unknown', 'unreadable', 'u', 'UNKNOWN'}
_HEADS = {'breathing': {'none', 'psili', 'dasia', 'unknown'},
          'accent': {'none', 'acute', 'grave', 'circumflex', 'unknown'},
          'diaeresis': {'none', 'present', 'unknown'}, 'subscript': {'none', 'present', 'unknown'}}


def _options(card):
    return card.get('options', {k: card[k] for k in ('A', 'B', 'C') if k in card})


def _id(card):
    return card.get('id', card.get('card_id'))


def _literal(text):
    # Spacing numeral/accent signs must not collapse into combining marks (R2C).
    import re
    return ''.join(ch if ch in ('\u0374', '\u0384') else unicodedata.normalize('NFC', ch)
                   for ch in re.split('([\u0374\u0384])', text))


def adapt_answer(answer: dict, card: dict, *, adapter: str = 'canonical') -> dict:
    """Adapt canonical/R0/S8/R2C field names, retaining explicit R2C unknown heads."""
    if adapter not in ('canonical', 'r0', 's8', 'r2c'):
        raise ValueError('unknown answer adapter')
    ident = answer.get('id', answer.get('card_id'))
    if ident != _id(card):
        raise ValueError('answer identity mismatch')
    choice = answer.get('answer', answer.get('choice'))
    if 'answer' in answer and 'choice' in answer and answer['answer'] != answer['choice']:
        raise ValueError('contradictory choice aliases')
    printed = answer.get('printed', answer.get('transcription'))
    if 'printed' in answer and 'transcription' in answer and answer['printed'] != answer['transcription']:
        raise ValueError('contradictory transcription aliases')
    confidence = answer.get('confidence')
    if adapter == 's8' and confidence is None and type(answer.get('uncertain')) is bool:
        confidence = 'low' if answer['uncertain'] else 'high'
    if confidence not in ('high', 'medium', 'low') or not isinstance(answer.get('note'), str):
        raise ValueError('confidence must be high/medium/low and note must be text')
    options = _options(card)
    if choice in options:
        form = options[choice]
        form = '' if form == '∅' else form
    elif choice in _UNKNOWN:
        form = None
    elif choice in ('literal', 'none of these', 'NEITHER', 'neither'):
        if not isinstance(printed, str) or not printed.strip():
            raise ValueError('literal correction requires complete transcription')
        form = printed
    else:
        raise ValueError('invalid option identity')
    form = _literal(form) if form is not None else None
    if choice in options and printed is not None and _literal(printed) != form:
        raise ValueError('option contradicts printed transcription; use literal')
    out = dict(id=ident, answer=choice, printed=form, confidence=confidence, note=answer['note'])
    if adapter == 'r2c':
        readability = answer.get('readability')
        ownership = answer.get('ownership_ok')
        if readability not in ('readable', 'partial', 'unreadable') or (ownership is not None and type(ownership) is not bool):
            raise ValueError('invalid readability/ownership')
        if choice == 'unreadable' and readability != 'unreadable':
            raise ValueError('unreadable choice contradicts readability')
        targets = {}
        supplied = deepcopy(answer.get('letter_heads', []))
        supplied.append(dict(index=card['anchor_index'], **answer['anchor_heads']))
        letters = [ch for ch in unicodedata.normalize('NFD', form or '') if unicodedata.category(ch) in ('Lu', 'Ll', 'Lt', 'Lo')]
        clusters = []
        for ch in unicodedata.normalize('NFD', form or ''):
            if unicodedata.combining(ch) and clusters: clusters[-1] += ch
            else: clusters.append(ch)
        printed_heads = [dict(breathing='dasia' if '\u0314' in c else 'psili' if '\u0313' in c else 'none',
                              accent='acute' if '\u0301' in c else 'grave' if '\u0300' in c else 'circumflex' if '\u0342' in c else 'none',
                              diaeresis='present' if '\u0308' in c else 'none', subscript='present' if '\u0345' in c else 'none')
                         for c in clusters if unicodedata.category(c[0]) in ('Lu', 'Ll', 'Lt', 'Lo')]
        for row in supplied:
            idx = row['index']
            missing_anchor = idx == card['anchor_index'] and all(row.get(h) == 'unknown' for h in _HEADS)
            if type(idx) is not int or idx < 0 or idx in targets or (form is not None and idx >= len(letters) and not missing_anchor):
                raise ValueError('invalid letter-head index')
            if any(row.get(h) not in values for h, values in _HEADS.items()):
                raise ValueError('invalid letter-head value')
            if form is not None and not missing_anchor and any(row[h] != 'unknown' and row[h] != printed_heads[idx][h] for h in _HEADS):
                raise ValueError('head tuple contradicts literal form')
            targets[idx] = {h: row[h] for h in _HEADS}
        out.update(readability=readability, ownership_ok=ownership, heads=targets)
    return out


def deal(deck: list[dict], reader: int = 1) -> list[dict]:
    """Return an independent assignment; reader 2 is emitted in reverse order."""
    if reader not in (1, 2, 3):
        raise ValueError('reader must be 1, 2 or tiebreak 3')
    return deepcopy(list(reversed(deck)) if reader == 2 else deck)


def tiebreak_deck(deck: list[dict], keys: list[dict], disagreements: list[str], *, image_root: str | Path, blind_dir: str | Path, seed: int = 20261018) -> dict:
    """Emit disagreements plus verified controls with fresh positions/options and its own key."""
    from .deck import build_deck
    by_id = {_id(c): c for c in deck}
    key_map = {k['id']: k for k in keys}
    if not set(disagreements) <= set(by_id) or set(by_id) != set(key_map):
        raise ValueError('tiebreak identity mismatch')
    selected = [k for k in keys if k['id'] in disagreements or k['control']]
    records = {False: [], True: []}
    for key in selected:
        card = by_id[key['id']]
        opts = _options(card)
        record = dict(image=str(Path(image_root)/card['img']), line_image=str(Path(image_root)/card['line_img']),
                      profile='line', options=list(opts.values()), free_text=not opts, previous_options=list(opts.values()),
                      private=dict(original_id=key['id'], original_options=opts),
                      public={k: card[k] for k in ('anchor_index', 'target_head') if k in card},
                      pixel_verified=key['control'], known_answer=key.get('known_answer'))
        records[key['control']].append(record)
    return build_deck(dict(blind_dir=str(blind_dir), seed=seed, items=records[False], controls=records[True]))


def controls_gate(batches: list[dict[str, dict]], keys: list[dict], spec: dict[str, Any]) -> dict:
    """Evaluate explicit control tolerances before votes; describe historical C1 gates with readers=1."""
    readers = spec.get('readers', 2)
    if readers not in (1, 2, 3) or len(batches) != readers:
        raise ValueError('gate reader count mismatch')
    controls = [k for k in keys if k.get('control')]
    if not controls and not spec.get('allow_no_controls', False):
        raise ValueError('no verified controls')
    if any(k.get('known_answer') is None for k in controls):
        raise ValueError('control truth missing')
    errors = []
    for batch in batches:
        misses = []
        for key in controls:
            answer = batch.get(key['id'])
            expected = '' if key['known_answer'] == '∅' else _literal(key['known_answer'])
            if answer is None or answer['printed'] != expected or any(json.dumps(answer.get(k), sort_keys=True) != json.dumps(v, sort_keys=True) for k, v in key.get('expected_fields', {}).items()):
                misses.append(key['id'])
        errors.append(misses)
    shared = sorted(set().union(*(set(errors[i]) & set(errors[j]) for i in range(len(errors)) for j in range(i+1, len(errors)))))
    tolerance = spec.get('max_errors', len(controls)-spec['min_correct'] if 'min_correct' in spec else 0)
    passed = all(len(e) <= tolerance for e in errors)
    if spec.get('no_shared_misses', True) and shared: passed = False
    # Historical C1 point-estimate gates are explicit descriptions, never a new-deck default.
    n = spec.get('n')
    if 'expected_controls' in spec: passed &= len(controls) == spec['expected_controls']
    if 'min_correct' in spec: passed &= all(len(controls)-len(e) >= spec['min_correct'] for e in errors)
    if 'exact_n' in spec: passed &= n == spec['exact_n']
    if 'min_n' in spec: passed &= n is not None and n >= spec['min_n']
    for metric, threshold in spec.get('minimum_rates', {}).items():
        passed &= spec.get('rates', {}).get(metric, -1) >= threshold
    return dict(passed=bool(passed), readers=readers, errors=errors, shared_misses=shared, spec=deepcopy(spec))


def resolve(deck: list[dict], keys: list[dict], reader1: list[dict], reader2: list[dict], *, reader3: list[dict] | None = None, tiebreak_keys: list[dict] | None = None, adapter: str = 'canonical', gate_spec: dict | None = None) -> dict:
    """Gate both readers first, then 2-of-2 or 2-of-3; unresolved/unknown remains UNKNOWN.

    Third answers use the private tiebreak key's public options and original_id
    map, never original option letters. Controls are excluded from truth.
    """
    by_id = {_id(c): c for c in deck}
    key_map = {k['id']: k for k in keys}
    if len(by_id) != len(deck) or len(key_map) != len(keys) or set(by_id) != set(key_map):
        raise ValueError('deck/key identity mismatch')
    order = list(by_id)
    def batch(rows, cards, expected):
        if [r.get('id', r.get('card_id')) for r in rows] != expected:
            raise ValueError('answer coverage/order mismatch')
        return {ident: adapt_answer(r, cards[ident], adapter=adapter) for ident, r in zip(expected, rows)}
    first = batch(reader1, by_id, order)
    second = batch(reader2, by_id, list(reversed(order)))
    spec = dict(gate_spec or {})
    if spec.get('readers', 2) != 2:
        raise ValueError('single-reader gate is historical description only')
    spec['readers'] = 2
    gate = controls_gate([first, second], keys, spec)
    if not gate['passed']:
        return dict(status='CONTROLS_FAILED', gate=gate, truth=[], disagreements=[])
    def signature(a):
        return (a['printed'], a.get('readability'), a.get('ownership_ok'), json.dumps(a.get('heads'), sort_keys=True))
    disagreements = [i for i in order if not key_map[i]['control'] and signature(first[i]) != signature(second[i])]
    third = {}
    third_gate = None
    if reader3 is not None:
        if not tiebreak_keys: raise ValueError('third reader requires its own private map')
        third_cards = {k['id']: k['public'] for k in tiebreak_keys}
        third_order = list(third_cards)
        third_raw = batch(reader3, third_cards, third_order)
        originals = []
        for key in tiebreak_keys:
            original = key['provenance']['original_id']
            if original not in key_map: raise ValueError('unknown tiebreak original')
            originals.append(original)
            if key['control'] != key_map[original]['control'] or key.get('known_answer') != key_map[original].get('known_answer'):
                raise ValueError('tiebreak control truth differs')
        required = set(disagreements) | {k['id'] for k in keys if k['control']}
        if len(set(originals)) != len(originals) or set(originals) != required:
            raise ValueError('tiebreak must cover disagreements and controls exactly')
        candidate = {original: third_raw[k['id']] for original, k in zip(originals, tiebreak_keys)}
        third_gate = controls_gate([first, second, candidate], keys, dict(spec, readers=3))
        if third_gate['passed']:
            third = candidate
    truth = []
    for ident in order:
        if key_map[ident]['control']: continue
        votes = [first[ident], second[ident]] + ([third[ident]] if ident in disagreements and ident in third else [])
        forms = Counter(v['printed'] for v in votes if v['printed'] is not None)
        form, count = forms.most_common(1)[0] if forms else (None, 0)
        decided = count >= 2
        row = dict(id=ident, printed=form if decided else None, status='AGREED' if decided and ident not in disagreements else 'MAJORITY_OF_3' if decided and len(votes) == 3 else 'UNKNOWN', votes=len(votes), control=False, verdict=form if decided else None, r1=deepcopy(first[ident]), r2=deepcopy(second[ident]))
        if ident in third: row['r3'] = deepcopy(third[ident])
        if adapter == 'r2c':
            selected = [v for v in votes if decided and v['printed'] == form]
            def majority(values, default):
                counts = Counter(values)
                value, n = counts.most_common(1)[0] if counts else (default, 0)
                return value if n >= 2 else default
            ownership = majority([v['ownership_ok'] for v in selected], None)
            readability = majority([v['readability'] for v in selected], 'unknown')
            indices = sorted({i for v in selected for i in v['heads']})
            heads = {i: {h: majority([v['heads'].get(i, {}).get(h, 'unknown') for v in selected if v['ownership_ok'] is True and v['readability'] in ('readable', 'partial')], 'unknown') for h in _HEADS} for i in indices}
            row.update(ownership_ok=ownership, readability=readability, heads=heads)
            if ownership is not True or not heads or any('unknown' in h.values() for h in heads.values()): row['status'] = 'UNKNOWN'
        truth.append(row)
    return dict(status='RESOLVED' if all(t['status'] != 'UNKNOWN' for t in truth) else 'PENDING', gate=gate, third_gate=third_gate, disagreements=disagreements, truth=truth)


def write_truth(path: str | Path, resolution: dict) -> dict:
    """Write gated truth once as JSONL (optionally deterministic gzip), preserving UNKNOWN."""
    if not resolution.get('gate', {}).get('passed'):
        raise ValueError('controls gate must pass before truth is written')
    path = Path(path)
    payload = ''.join(json.dumps(r, ensure_ascii=False, sort_keys=True, allow_nan=False)+'\n' for r in resolution['truth']).encode()
    if path.suffix == '.gz': payload = gzip.compress(payload, mtime=0)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as stream: stream.write(payload)
    return dict(path=str(path), rows=len(resolution['truth']), unknown=sum(r['status']=='UNKNOWN' for r in resolution['truth']), status_counts=dict(Counter(r['status'] for r in resolution['truth'])), gate=resolution['gate'], third_gate=resolution.get('third_gate'))

from .score import score
