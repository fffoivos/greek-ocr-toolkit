"""Read-only release substitution census, seeded samples and single-line diagnostics."""
from __future__ import annotations
from collections import Counter, defaultdict
from collections.abc import Iterable
import random
import unicodedata as ud

__all__ = ['release_census', 'evidence_dump']
_MARKS = {'\u0301':'acute', '\u0300':'grave', '\u0342':'circumflex', '\u0313':'psili', '\u0314':'dasia'}
_FAM = {v: 'accent' if v in ('acute','grave','circumflex') else 'breathing' for v in _MARKS.values()}


def _letters(text: str) -> list:
    out = []
    for c in ud.normalize('NFD', text):
        if ud.category(c).startswith('M') and out:
            out[-1][1].append(c)
        elif c.isalpha():
            out.append([c, []])
    return out


def release_census(records: Iterable[dict], selection: dict[str, dict], *, seed: int = 20261017, sample_size: int = 20) -> dict:
    """Count agreeing-reader substitutions by tier/wave and sample lines per tier.

    Tier names match subst_sample.py: agree = ink + detector names the new mark;
    other = ink with another/no detector name; noink = reader-only. Mixed lines
    use noink first, then other, then agree. Input order is preserved before the
    historical seeded shuffles; pass a fixed shard ordering for reproducibility.
    """
    if type(sample_size) is not int or sample_size < 0:
        raise ValueError('sample_size must be a nonnegative integer')
    tiers, waves, transitions = Counter(), defaultdict(Counter), Counter()
    pools = defaultdict(list)
    tier_lines = defaultdict(set)
    n = aligned = 0
    for record in records:
        n += 1
        source = selection[record['line_id']]
        letters = _letters(source['label'])
        gates = sorted(record['gate_decisions'], key=lambda g: g['start'])
        if len(letters)!=len(gates) or any(b.lower()!=g['base'].lower() for (b,_),g in zip(letters,gates)):
            continue
        aligned += 1
        con = []
        for i, ((base, marks), g) in enumerate(zip(letters,gates)):
            a, b = g.get('r1_parts'), (g.get('peer_prediction') or {}).get('parts')
            if a is None or b is None or sorted(a)!=sorted(b):
                continue
            google = {_FAM[_MARKS[m]]:_MARKS[m] for m in marks if m in _MARKS}
            predicted = {_FAM[m]:m for m in a if m in _FAM}
            for head in ('accent','breathing'):
                if head not in google or head not in predicted or google[head]==predicted[head]:
                    continue
                ink = bool(g['evidence'].get('above'))
                tier = 'agree' if ink and predicted[head] in (g.get('detector_parts') or []) else 'other' if ink else 'noink'
                tiers[tier] += 1
                tier_lines[tier].add(record['line_id'])
                waves[source['wave']][tier] += 1
                transitions[head, google[head]+'->'+predicted[head], tier] += 1
                con.append(dict(letter=i, fam=head, google=google[head], ours=predicted[head], tier=tier, det=g.get('detector_parts') or []))
        if con:
            tier = 'noink' if any(c['tier']=='noink' for c in con) else 'other' if any(c['tier']=='other' for c in con) else 'agree'
            slots = [dict(base=g['base'], body=g['evidence'].get('body'),
                          above=[b['bbox'] for b in g['evidence'].get('above',[])],
                          below=[b['bbox'] for b in g['evidence'].get('below',[])]) for g in gates]
            pools[tier].append(dict(line_id=record['line_id'], wave=source['wave'], label=source['label'],
                                   crop=source.get('crop'), status=record.get('status'), con=con, slots=slots))
    rng = random.Random(seed)
    samples = {}
    for tier, pool in pools.items():
        rng.shuffle(pool)
        samples[tier] = pool[:sample_size]
    return dict(records=n, aligned=aligned, tiers=dict(tiers), tier_lines={t:len(ids) for t,ids in tier_lines.items()}, waves={w:dict(c) for w,c in sorted(waves.items())},
                transitions=[dict(head=h, change=c, tier=t, count=n) for (h,c,t),n in sorted(transitions.items())],
                sizes={t:len(p) for t,p in pools.items()}, sample=samples, seed=seed)


def evidence_dump(records: Iterable[dict], line_id: str) -> dict:
    """Return one saved line and active slot evidence without truncation/rounding."""
    found = None
    for row in records:
        if row['line_id'] == line_id:
            if found is not None:
                raise ValueError('duplicate line identity')
            found = row
    if found is None:
        raise KeyError(line_id)
    return dict(line_id=line_id, status=found.get('status'), composed_text=found.get('composed_text'),
                slots=[g for g in sorted(found['gate_decisions'], key=lambda g:g['start'])
                       if g.get('r1_parts') or (g.get('peer_prediction') or {}).get('parts') or g.get('detector_parts') or g.get('hold_reasons')])
