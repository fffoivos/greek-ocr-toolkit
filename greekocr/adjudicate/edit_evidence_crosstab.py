"""Audit saved edits against their owning slots and literal print verdicts."""
from __future__ import annotations
from collections import Counter
import unicodedata as ud

__all__ = ['edit_evidence_crosstab']
_MARKS = {'\u0313': 'breathing', '\u0314': 'breathing', '\u0301': 'accent',
          '\u0300': 'accent', '\u0342': 'accent', '\u0308': 'diaeresis', '\u0345': 'subscript'}


def edit_evidence_crosstab(records: list[dict], verdicts: dict[str, dict]) -> dict:
    """Return per-change kind/head/slot/ink/verdict rows and aggregate counts.

    Offsets refer to NFD mark edits. Ownership uses STRICT start < edit.start:
    a mark at the next base's offset still belongs to the preceding base. Slots
    in the output are zero based. Verdicts are explicit per-line `ok` booleans or
    per-change `verdicts` lists, never inferred from an empty owner note here.
    """
    changes, counts = [], Counter()
    for record in records:
        lid = record['line_id']
        decisions = sorted(record['gate_decisions'], key=lambda g: g['start'])
        if len({g['start'] for g in decisions}) != len(decisions):
            raise ValueError('duplicate slot offsets')
        verdict = verdicts[lid]
        if 'verdicts' in verdict and len(verdict['verdicts']) != len(record['changes']):
            raise ValueError('verdict coverage mismatch')
        for index, change in enumerate(record['changes']):
            candidates = [(i, g) for i, g in enumerate(decisions) if g['start'] < change['start']]
            if not candidates:
                raise ValueError('edit has no preceding owning slot')
            slot, owner = candidates[-1]
            if owner['base'] != change['letter']:
                raise ValueError('edit/owner base mismatch')
            before, after = (ud.normalize('NFD', change[k]) for k in ('from', 'to'))
            added, removed = Counter(after)-Counter(before), Counter(before)-Counter(after)
            kind = 'substitution' if added and removed else 'addition' if added else 'deletion' if removed else 'unchanged'
            heads = sorted({_MARKS[c] for c in added.keys() | removed.keys() if c in _MARKS})
            if not heads:
                raise ValueError('edit contains no supported mark')
            value = verdict['verdicts'][index] if 'verdicts' in verdict else ('released_right' if verdict['ok'] else 'google_right')
            head = '+'.join(heads)
            ink = bool(owner['evidence'].get('below' if 'subscript' in heads else 'above'))
            row = dict(line_id=lid, change=index, start=change['start'], kind=kind, head=head,
                       heads=heads, slot=slot, ink=ink, verdict=value)
            changes.append(row)
            counts[kind, head, ink, value] += 1
    above = [r for r in changes if r['kind']=='addition' and 'subscript' not in r['heads'] and r['ink']]
    return dict(changes=changes, counts=[dict(kind=k, head=h, ink=i, verdict=v, count=n)
                for (k,h,i,v),n in sorted(counts.items())],
                above_additions_with_ink=dict(right=sum(r['verdict']=='released_right' for r in above), total=len(above)))
