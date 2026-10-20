"""Offline, evidence-bound OS4 changes to the completed OS3 selection.

Run directly on OS3 outputs, or as the final step of build_owner_sheets_v2.
No selection, text, raster, Printed, note, or document-identity changes.
"""
from __future__ import annotations

import copy
import difflib
import re
import unicodedata

from scripts.review.build_owner_sheets_v2 import DEST, NAMES, OUT, dump, read
from greekocr.adjudicate.owner_sheet import render

OWNER = {
    'ia_poly1850--41e90f3ba967f920--s006-l0022': 'circumflex written as acute',
    'ia_poly1850--a89bd2c9bdb1ca6d--s005-l0038': 'circumflex written as diaeresis',
    'ia_poly1850--a89bd2c9bdb1ca6d--s007-l0016': 'circumflex written as grave',
    'nlg--1144074169f43992--s006-l0032': 'clipped at the edge',
}


def heading(group):
    return re.sub(r'\s*\(\d+ cards shown\)$', '', group['heading'])


def verdict(card):
    # Placement is based on the displayed evidence's stage; original C1 cards
    # must not inherit a masked T6b fault from a different displayed raster.
    stage = card.get('display_evidence', {}).get('stage', 'C1')
    ev = [e for e in card['evidence'] if e['stage'] == stage]
    return {code for e in ev for code in e.get('errors', [])}, '; '.join(
        dict.fromkeys(e.get('detail', '') for e in ev if e.get('detail')))


def mark_change(detail, before, after):
    for clause in detail.split(';'):
        if ' → ' in clause:
            left, right = clause.split(' → ', 1)
            left, right = unicodedata.normalize('NFD', left), unicodedata.normalize('NFD', right)
            for op, i, j, k, l in difflib.SequenceMatcher(None, left, right, autojunk=False).get_opcodes():
                if op == 'replace' and before in left[i:j] and after in right[k:l]:
                    return True
    return False


def supported(title, card):
    """Reject stratum/glyph-presence shortcuts; require card-level evidence."""
    codes, detail = verdict(card)
    if title.startswith('T6b masked cards: '):
        return title.split(': ', 1)[1] in codes
    if title in ('hard sign ъ flattened to ь', 'Adjudicated yer: hard sign ъ read as ь',
                 'Cyrillic faults: yer and dialogue punctuation (original coordinator group)'):
        return 'wrong_letter' in codes and mark_change(detail, 'ъ', 'ь')
    shifts = {
        'grave written as acute': ('\u0300', '\u0301'),
        'acute written as grave': ('\u0301', '\u0300'),
        'circumflex written as acute': ('\u0342', '\u0301'),
        'circumflex written as grave': ('\u0342', '\u0300'),
        'circumflex written as diaeresis': ('\u0342', '\u0308'),
    }
    if title in shifts:
        return 'wrong_mark' in codes and mark_change(detail, *shifts[title])
    if title == 'iota subscript dropped':
        return 'missing_mark' in codes and any(
            '\u0345' in unicodedata.normalize('NFD', clause.split(' → ')[0]) and
            '\u0345' not in unicodedata.normalize('NFD', clause.split(' → ')[1])
            for clause in detail.split(';') if ' → ' in clause)
    if title == 'Latin siglum labelled with a Greek lookalike':
        return 'lookalike_script_letter' in codes and 'Latin' in detail
    if title == 'em dash dropped or hyphenated':
        return bool(codes & {'punctuation', 'hyphen'}) and ('—' in detail or 'dash' in detail.lower()) and 'clipped dash' not in detail
    if title == 'superscript dropped or garbled':
        return bool(codes & {'digits', 'wrong_letter', 'missing_word_or_span'}) and ('superscript' in detail or any(ch in detail for ch in '²³¹⁰⁴⁵⁶⁷⁸⁹ⁿ'))
    if title == 'lunate sigma written as σ':
        return 'wrong_letter' in codes and ('ϲ' in detail or 'lunate' in detail)
    if title == 'breathing dropped on a capital':
        return 'missing_mark' in codes and any(ch in detail for ch in 'ἈἘἨἸὈὙὨἉἙἩἹὉὩῬ')
    required = {
        'mark dropped': 'missing_mark', 'mark misnamed': 'wrong_mark',
        'mark added where none is printed': 'extra_mark', 'letter misread': 'wrong_letter',
        'letter misread (unspecified)': 'wrong_letter', 'punctuation changed': 'punctuation',
        'number separator changed': 'punctuation', 'digits changed': 'digits',
        'span missing from the label': 'missing_word_or_span', 'clipped at the edge': 'crop_clipped',
    }
    if title in required:
        return required[title] in codes
    raise AssertionError(f'Unaudited fault heading: {title}')


def replacement(card):
    codes, detail = verdict(card)
    if 'wrong_mark' in codes:
        for title, pair in [('acute written as grave', ('\u0301', '\u0300')),
                            ('circumflex written as diaeresis', ('\u0342', '\u0308'))]:
            if mark_change(detail, *pair):
                return title
        return 'mark misnamed'
    if 'missing_mark' in codes:
        return 'mark dropped'
    if 'punctuation' in codes:
        return 'em dash dropped or hyphenated' if '—' in detail else 'punctuation changed'
    return 'letter misread (unspecified)'


def apply(specs):
    a, b = specs
    changes = []
    groups = {g['id']: g for g in a['groups']}
    # Every A card is checked, including OS2 top-ups and masked T6b cards.
    for c in a['lines']:
        oldgroup = groups[c['group']]
        old = heading(oldgroup)
        owner = c['line_id'] in OWNER
        if not owner and supported(old, c):
            continue
        new = OWNER[c['line_id']] if owner else replacement(c)
        assert supported(new, c), (c['line_id'], new, verdict(c))
        sid = oldgroup['section']
        target = next((g for g in a['groups'] if g['section'] == sid and heading(g) == new), None)
        if target is None:
            target = dict(id=f'{sid}_os4_{len(changes)}', section=sid, heading=new)
            a['groups'].append(target)
            groups[target['id']] = target
        oldtags = [t['text'] for t in c['tags']]
        # A class name remains in the section heading. On questioned cards it
        # must not masquerade as a Latin fault pill.
        c['tags'] = [t for t in c['tags'] if t['text'] not in (old, 'Mixed Greek + Latin')]
        c['tags'].append(dict(text=new))
        if new == 'clipped at the edge':
            c['tags'].append(dict(text='mark error'))
        c['group'] = target['id']
        _, detail = verdict(c)
        changes.append(dict(card=c['line_id'], kind='owner' if owner else 'audit',
                            old_tag=old, old_tags=oldtags, new_tag=new + ('; mark error' if new == 'clipped at the edge' else ''),
                            old_group=oldgroup['id'], new_group=c['group'], evidence=detail))
    # The same owner card already lives under the clipped edge in sheet B.
    for c in b['lines']:
        codes = set(c['fault_codes'])
        _, detail = verdict(c)
        expected = dict(g_fragment='missing_word_or_span', g_overrun='crop_overrun',
                        g_column='crop_overrun', g_clipped='crop_clipped',
                        g_rotated='rotated_vertical_line', g_missing_box='missing_admitted_box')
        if c['group'] == 'g_merged':
            assert 'merged_two_lines' in codes or 'crop holds three lines' in detail
        else:
            assert expected[c['group']] in codes
        if c['group'] == 'g_column':
            assert 'two table columns' in detail
        if c['line_id'] == 'nlg--1144074169f43992--s006-l0032':
            assert c['group'] == 'g_clipped'
            c['tags'] += [dict(text='clipped at the edge'), dict(text='mark error')]
    # Correct the legacy Russian shortcut's heading for its remaining actual
    # yer witnesses. The pure punctuation cards have moved to a dash group.
    groups['s7g0']['heading'] = 'hard sign ъ flattened to ь'
    a['groups'].sort(key=lambda g: int(g['section'][1:]))
    for g in a['groups']:
        count = sum(c['group'] == g['id'] for c in a['lines'])
        g['shown_count'] = count
        g['heading'] = heading(g) + f' ({count} cards shown)'
        g.pop('gap', None)
        if count < 3:
            g['gap'] = f'fewer than 3 cards in this subsection ({count}); no new witnesses selected in OS4'
        if 'dash' in heading(g):
            g['header'] = 'Owner ruling: tag only, no track. Tagged examples; no further work.'
    assert all(supported(heading(groups[c['group']]), c) for c in a['lines'])
    assert sum(c['kind'] == 'owner' for c in changes) == 4
    return changes


def main():
    specs = [read(DEST/name/'spec.json') for name in NAMES]
    if 'os4' in specs[0]:
        # Reapply from the exact OS3 snapshots, making repeated renders stable.
        specs = [read(DEST/'inputs'/f'os3_{name}.json') for name in NAMES]
    before = copy.deepcopy(specs)
    for name, s in zip(NAMES, before):
        dump(DEST/'inputs'/f'os3_{name}.json', s)
    changes = apply(specs)
    for old, new in zip(before, specs):
        assert [c['doc_id'] for c in old['lines']] == [c['doc_id'] for c in new['lines']]
        for prev, c in zip(old['lines'], new['lines']):
            assert {k:v for k,v in prev.items() if k not in ('group', 'tags')} == {k:v for k,v in c.items() if k not in ('group', 'tags')}
    receipt = dict(owner_retags=4, audit_retags=sum(c['kind'] == 'audit' for c in changes),
                   doc_ids_identical=True, audited_cards_A=len(specs[0]['lines']),
                   audited_cards_B=len(specs[1]['lines']), changes=changes,
                   dash_ruling='tag only, no track')
    dump(OUT/'os4_retag_audit.json', receipt)
    for name, s in zip(NAMES, specs):
        s['os4'] = dict(audit_path=str(OUT/'os4_retag_audit.json'), doc_ids_identical=True)
        dump(DEST/name/'spec.json', s)
        (OUT/f'{name}.html').write_text(render(s['lines'], s))
    report = DEST/'OS2_REPORT.md'
    content = report.read_text().split('\n## OS4:', 1)[0]
    content += '\n## OS4: owner re-tags and card-level placement audit\n\n'
    content += (f"Audited all {len(specs[0]['lines'])} failure-mode cards and {len(specs[1]['lines'])} segmentation cards. "
                f"Owner re-tags: 4; additional audit re-tags: {receipt['audit_retags']}. "
                'All OS3 line ids and document ids, card order, crops, text, Printed values, notes, and original checker codes are identical. '
                'Only classification tags, placement and associated subsection metadata change. '
                'Exact OS3 inputs are retained under `inputs/os3_*.json`; the complete transition ledger is '
                '`artifacts/owner_sheets/v2/os4_retag_audit.json`.\n\n'
                'The three IA cards were already under mark subsections in OS3, with a Mixed Greek + Latin class pill. '
                'That pill described the stratum, not a Latin fault; it is removed from these cards and replaced with their specific mark fault. '
                'Class sections remain intact. The table records the actual OS3 subsection, rather than inventing a former Latin fault tag.\n\n'
                'The renderer supports one placement per note document. The NLG dash witness is placed under clipped edge in A, '
                'retains its clipped-edge placement in B, and carries a mark error tag in both. '
                'Dashes: **tag only, no track**; retained as tagged examples with no further work.\n\n'
                'The audit rejects the Cyrillic р shortcut and checks mark direction on each side of the checker arrow. '
                'All six Serbian cards incorrectly grouped as yers and both pure Russian dash cards are listed below, '
                'along with reversed or unsupported mark subtype placements. '
                'All other cards have a placement supported by their own codes and detail; segmentation geometry and SG2 provenance remain unchanged.\n\n'
                '| Card | Old tag | New tag | Evidence |\n|---|---|---|---|\n')
    for c in changes:
        evidence = c['evidence'].replace('|', '&#124;').replace('\n', ' ')
        content += f"| `{c['card']}` | {c['old_tag']} | {c['new_tag']} | {evidence} |\n"
    report.write_text(content)
    return receipt


if __name__ == '__main__':
    main()
