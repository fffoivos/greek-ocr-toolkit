"""Offline T16 selection, bounded allocation, seeded positions and replacements.

No service clients are imported. Confidence is a selection proxy, not accuracy.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import difflib
import hashlib
import math
import random
import re
import unicodedata as ud


def letters(text, *, marks=True):
    text = ud.normalize('NFD', text)
    return ''.join(c for c in text if c.isalpha() or (marks and ud.category(c).startswith('M')))


def words(text):
    return re.findall(r'[^\W_][\w\u0300-\u036f]*', ud.normalize('NFD', text), re.UNICODE)


def base(text):
    return ''.join(c for c in ud.normalize('NFD', text).lower() if not ud.category(c).startswith('M'))


def script_counts(text):
    counts = Counter()
    for c in text:
        if c.isalpha():
            counts['greek' if 'GREEK' in ud.name(c, '') else 'other'] += 1
    return counts


def mixed_block(text):
    count = script_counts(text)
    total = sum(count.values())
    return total >= 20 and count['other'] / total >= .2


def substitution_fingerprints(vision, docai):
    """Line-level indicators; each kind votes at most once per paired line.

    Pair words within edit spans to avoid counting ordinary independent 'ου' and
    numerals. An unchanged numeral or unchanged final sigma at a word end does
    not vote. Literal historic glyph disagreements also vote.
    """
    result = set()
    av, bv = words(vision), words(docai)
    for text in (vision, docai):
        for word in words(text):
            chars = base(word)
            if re.search(r'ς(?=[α-ωΑ-Ω])', chars):
                result.add('final_sigma_mid_word')
            kinds = {('greek' if 'GREEK' in ud.name(c, '') else 'latin' if 'LATIN' in ud.name(c, '') else 'other')
                     for c in chars if c.isalpha()}
            if 'greek' in kinds and 'latin' in kinds:
                result.add('latin_inside_greek')
    va, da = [base(w) for w in av], [base(w) for w in bv]
    matcher = difflib.SequenceMatcher(None, va, da, autojunk=False)
    for tag, i, j, k, l in matcher.get_opcodes():
        if tag == 'equal':
            continue
        aa, bb = va[i:j], da[k:l]
        for a in aa:
            for b in bb:
                if a == b:
                    continue
                if a == 'και' and b in ('κ', 'κι', 'κα', 'κη'):
                    result.add('kai_k_mark')
                if any(c in a+b for c in 'ȣȢ8'):
                    def expand(s): return s.replace('ȣ', 'ου').replace('Ȣ', 'ου').replace('8', 'ου')
                    if expand(a) == expand(b):
                        result.add('ou_8_ligature')
                if any(c in a+b for c in 'ϛϚϙϘϟϞ'):
                    result.add('stigma_koppa')
    return sorted(result)


def pair_page_lines(vision, docai):
    """Conservative one-to-one native boxes, with unmatched DocAI lines retained.

    >=60% of shorter height and >=50% of shorter width; a Vision box touching
    two eligible DocAI rows is withheld, as are multiple candidates per row.
    """
    candidates = defaultdict(list)
    for vi, v in enumerate(vision):
        a = v['bbox']
        for di, d in enumerate(docai):
            b = d['bbox']
            height = max(0, min(a[3], b[3]) - max(a[1], b[1])) / max(1, min(a[3]-a[1], b[3]-b[1]))
            width = max(0, min(a[2], b[2]) - max(a[0], b[0])) / max(1, min(a[2]-a[0], b[2]-b[0]))
            if height >= .6 and width >= .5:
                candidates[di].append(vi)
    counts = Counter(vi for vs in candidates.values() for vi in vs)
    pairs = []
    for di, d in enumerate(docai):
        # Pure page numbers and ornaments supply no letters denominator.
        if not letters(d['text']):
            continue
        vs = candidates[di]
        v = vision[vs[0]] if len(vs) == 1 and counts[vs[0]] == 1 else None
        pairs.append(dict(docai=d['text'], vision=v['text'] if v else '', paired=v is not None,
                          docai_index=di, vision_index=vs[0] if v else None))
    return pairs


def book_signals(pairs, symbol_confidences, blocks):
    confidences = [float(c) for c in symbol_confidences if c is not None and math.isfinite(c)]
    pairs = list(pairs)
    agreed = sum(bool(p['paired'] and letters(p['vision']) and letters(p['vision']) == letters(p['docai'])) for p in pairs)
    counts = Counter()
    examples = defaultdict(list)
    any_count = 0
    for p in pairs:
        flags = substitution_fingerprints(p['vision'], p['docai']) if p['paired'] else substitution_fingerprints('', p['docai'])
        if flags:
            any_count += 1
        for flag in flags:
            counts[flag] += 1
            if len(examples[flag]) < 3:
                examples[flag].append(dict(vision=p['vision'], docai=p['docai'], page=p.get('page')))
    blocks = [b for b in blocks if sum(script_counts(b).values()) >= 20]
    return dict(docai_mean_symbol_confidence=sum(confidences)/len(confidences) if confidences else None,
                symbol_count=len(confidences), letters_agree_rate=agreed/len(pairs) if pairs else None,
                lines=len(pairs), paired_lines=sum(p['paired'] for p in pairs), agreed_lines=agreed,
                fingerprint_line_counts=dict(counts), fingerprint_line_shares={k:v/len(pairs) for k,v in counts.items()},
                any_fingerprint_line_share=any_count/len(pairs) if pairs else None,
                non_greek_mixed_block_share=sum(mixed_block(b) for b in blocks)/len(blocks) if blocks else None,
                blocks=len(blocks), fingerprint_examples=dict(examples))


def quintile(values):
    """Linear 20th percentile, with inclusive ties explicitly removed."""
    values = sorted(v for v in values if v is not None)
    if not values:
        raise ValueError('no measured values for the quintile')
    position = (len(values)-1)*.2
    lo, hi = math.floor(position), math.ceil(position)
    return values[lo] + (values[hi]-values[lo])*(position-lo)


def type_reasons(signal, confidence_cut, agreement_cut):
    reasons = []
    for key, threshold in [('docai_mean_symbol_confidence', confidence_cut), ('letters_agree_rate', agreement_cut)]:
        value = signal[key]
        if value is None:
            reasons.append('missing_'+key)
        elif value <= threshold:
            reasons.append(f'{key}={value:.6f} <= bottom-quintile {threshold:.6f}')
    for kind, share in sorted(signal['fingerprint_line_shares'].items()):
        if share > .05:
            reasons.append(f'{kind}={share:.3%} > 5% lines')
    share = signal.get('non_greek_mixed_block_share')
    if share is not None and share > .05:
        reasons.append(f'non_greek_mixed_blocks={share:.3%} > 5% blocks')
    return reasons


def allocate(books, budget=2000, nominal=13, cap=16, redistribute=False):
    """Equal nominal decade budgets, limited by per-book caps and half books.

    Dense decades split the common budget equally; thin decades stop at 16.
    Reduced books receive floor(half of their nominal integer allocation).
    Optional redistribution is explicit and recorded by the driver.
    """
    selected = [b for b in books if b['decision'] in ('IN', 'REDUCED')]
    groups = defaultdict(list)
    for b in selected:
        groups[b['decade']].append(b)
    if not groups:
        return {}, {}
    target = min(budget, nominal*len(selected))
    common, remainder = divmod(target, len(groups))
    targets = {d:common+int(i < remainder) for i,d in enumerate(sorted(groups))}
    capacity = {d:sum(cap//2 if b['decision']=='REDUCED' else cap for b in bs) for d,bs in groups.items()}
    if redistribute:
        actual = {d:min(targets[d], capacity[d]) for d in groups}
        spare = min(budget, sum(capacity.values())) - sum(actual.values())
        while spare > 0:
            eligible = [d for d in sorted(groups) if actual[d] < capacity[d]]
            if not eligible: break
            for d in eligible:
                actual[d] += 1; spare -= 1
                if not spare: break
        targets = actual
    allocation = {}
    for d, bs in sorted(groups.items()):
        bs = sorted(bs, key=lambda b:b['book'])
        # Find the largest common base whose half-adjusted total fits the budget.
        base_n = 0
        for n in range(1, cap+1):
            if sum(n//2 if b['decision']=='REDUCED' else n for b in bs) <= targets[d]: base_n = n
        for b in bs:
            allocation[b['book']] = base_n//2 if b['decision']=='REDUCED' else base_n
        spare = targets[d]-sum(allocation[b['book']] for b in bs)
        if base_n < cap:
            for b in bs:
                increment = (base_n+1)//2-base_n//2 if b['decision']=='REDUCED' else 1
                if increment and spare >= increment:
                    allocation[b['book']] += increment; spare -= increment
    assert sum(allocation.values()) <= budget
    return allocation, dict(targets=targets, capacities=capacity,
                            actual={d:sum(allocation[b['book']] for b in bs) for d,bs in groups.items()},
                            target_total=target, policy='redistributed' if redistribute else 'equal nominal budgets; capacity clipped')


def positions(total, count, excluded=(), *, seed=20261014, book=''):
    """Even inclusive 8%-95% anchors, seeded nonnegative 0-2 page nudges."""
    if count < 0 or total < 1:
        raise ValueError('positive total and nonnegative allocation required')
    if not count: return []
    lo, hi = math.ceil(.08*total), math.floor(.95*total)
    available = [p for p in range(lo, hi+1) if p not in set(excluded)]
    if count > len(available): raise ValueError('not enough non-pilot pages')
    rng = random.Random(int(hashlib.sha256(f'{seed}:{book}'.encode()).hexdigest(), 16))
    used, result = set(), []
    for i in range(count):
        anchor = round((lo+hi)/2) if count==1 else round(lo+(hi-lo)*i/(count-1))
        nudge = rng.randint(0, 2)
        desired = min(hi, anchor+nudge)
        page = min((p for p in available if p not in used), key=lambda p:(abs(p-desired), p<desired, p))
        used.add(page)
        result.append(dict(page=page, anchor=anchor, random_offset=nudge, exclusion_adjustment=page-desired))
    return sorted(result, key=lambda p:p['page'])


def replacement_candidates(page, total, excluded=(), reserved=()):
    """Initial page plus at most its next two physical neighbours.

    Pilot/reserved pages and the 95% boundary are skipped without extending the
    physical neighbourhood. Thus a blocked +1 never becomes an unbounded search.
    """
    blocked = set(excluded) | set(reserved)
    lo, hi = math.ceil(.08*total), math.floor(.95*total)
    return [p for p in range(page, min(page+2, hi)+1) if lo<=p<=hi and (p==page or p not in blocked)]


def title_flag(title):
    s = base(title)
    if re.search('λειτουργ|εκκλησι|ευαγγελ|ψαλμ|ακολουθ|μηνολογ|ωρολογ|συναξαρ|τριωδ|πατερ|θεολογ|ιερα|αγιου', s):
        return 'ecclesiastical/liturgical'
    if re.search('παλαι|βυζαντι|ομηρ|ηροδοτ|θουκυδ|αριστο|ξενοφων|πλατων|δημοσθεν|σοφοκλ|ευριπιδ', s):
        return 'older-style/classical edition'
    return ''
