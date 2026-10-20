"""Line-complete numeric enumeration. Offsets always refer to original W1 text."""
from dataclasses import asdict
from .tokens import tokenize


def enumerate_line(row, locks):
    locks.assert_fit_rows([row['id']])
    return enumerate_slots(row)


def enumerate_locked_line(row, locks, locked_ids):
    if row['id'] not in locked_ids or row['id'] not in locks.reserved_line_ids:
        raise ValueError('line outside registered locked draw')
    return enumerate_slots(row)


def enumerate_slots(row):
    """Pure enumeration; callers enforce fit/evaluation/train population custody."""
    if row['text'] != row.get('label', row['text']):
        raise ValueError('W1 text/label mismatch: ' + row['id'])
    result = []
    for ti, token in enumerate(tokenize(row['text'])):
        for slot in token.slots:
            result.append(dict(asdict(slot), slot_id=f"{row['id']}:t{ti}:s{slot.index}",
                line_id=row['id'], token_index=ti, token_start=token.start,
                token_end=token.end, digit_count=token.digit_count, number=len(result)+1))
    return result


def select_lines(cards, valid_r1, frame, byid, locks):
    """Historical r1 evidence selects lines only; no r2 input accepted."""
    sheet = {c.get('line_id') or c['slot_id'].split(':t')[0] for c in cards}
    extra = {s['line_id'] for s in valid_r1 if s['glyph'] == '-' and s['digit_count'] >= 4}
    selected = sheet | extra
    locks.assert_fit_rows(selected)
    documents = {r['document'] for r in frame if r['partition'] == 'step1'}
    for lid in selected:
        row = byid[lid]
        if row['source'] + ':' + row['item'] not in documents:
            raise ValueError('phase A outside step1 documents: ' + lid)
    return sorted(selected), dict(owner_sheet_lines=sorted(sheet), valid_r1_hyphen_lines=sorted(extra))
