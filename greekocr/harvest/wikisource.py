"""Pure T27 transcription cleaning, conservative line alignment and CER.

Unknown templates produce a visible sentinel and prevent affected gold lines
from matching. No spelling, orthography, accent or physical line is invented.
"""
from __future__ import annotations

from collections import Counter
import html
import re
import unicodedata as ud

MARKS = {'breathings': '\u0313\u0314', 'iota_subscript': '\u0345',
         'perispomeni': '\u0342', 'grave': '\u0300', 'dialytika': '\u0308'}
UNKNOWN = '⟦UNRESOLVED_TEMPLATE⟧'


def nfc(text):
    return ud.normalize('NFC', ' '.join(text.split()))


def _parts(text):
    """Split top-level template arguments, respecting nested braces/links."""
    return re.split(r'\|(?![^\[\]]*\]\])', text)


def strip_wikitext(text):
    """Keep source newlines; log explicit hyphenation/template decisions.

    noinclude headers/footers are excluded from body gold, not misattributed to
    its first/last printed line. Literal line-end hyphens remain unchanged.
    """
    joins, unknown, templates, variants = [], [], Counter(), []
    level = re.search(r'<pagequality\b[^>]*\blevel=["\']([0-4])["\']', text)
    text = re.sub(r'<!--.*?-->', '', text, flags=re.S)
    text = re.sub(r'<noinclude\b[^>]*>.*?</noinclude>', '', text, flags=re.S | re.I)
    text = re.sub(r'</?includeonly\b[^>]*>', '', text, flags=re.I)
    # In the frozen Balmont scan, poem № templates are editorial line counters
    # absent from the print (e.g. scan page 86); do not prepend them to gold.
    text = re.sub(r'(<poem\b[^>]*>)(.*?)(</poem>)',
        lambda m: m[1] + re.sub(r'\{\{№\|\d+\}\}', '', m[2]) + m[3], text, flags=re.S | re.I)
    # Formatting wrappers have transparent text parameters. Named CSS options
    # carry no transcription. The allowlist is deliberately conservative.
    transparent = {'c', 'center', 'centre', 'block center', 'block left', 'block right',
        'small', 'smaller', 'larger', 'large', 'x-small', 'xx-small', 'sc', 'sm', 'fs',
        'nowrap', 'sp', 'sperrung', 'разрядка', 'разр', 'курсив', 'мелко', 'мелким',
        'малый', 'центр', 'по центру', 'ц', 'right', 'left', 'r', 'l', 'δεξιά', 'αριστερά',
        'κέντρο', 'с', 'x-larger', 'xx-larger', 'xxx-larger', 'xxxx-larger',
        'x-smaller', 'xx-smaller', 'fine', 'fr', 'fine block', 'poem-title'}
    silent = {'nop', 'clear', '—', 'pagequality', 'rule', 'custom rule', 'gap', 'vgap',
              'block center/s', 'block center/e', 'cis', 'χεα', '0', 'ts',
              'indent', 'noindent', '^'}
    def template(m):
        parts = _parts(m.group(1)); name = parts[0].strip().replace('_', ' ').lower()
        positional = {}; next_arg = 1
        for part in parts[1:]:
            explicit = re.match(r'^\s*(\d+)\s*=(.*)$', part, flags=re.S)
            if explicit:
                positional[int(explicit[1])] = explicit[2]
            elif not re.match(r'^\s*[\w -]+\s*=', part):
                positional[next_arg] = part; next_arg += 1
        args = [positional[k] for k in sorted(positional)]
        templates[name] += 1
        if name in transparent:
            # fs uses its first argument for the size, its last for text.
            return args[-1] if name == 'fs' and args else '|'.join(args)
        if name in silent:
            return ''
        if name in {'вар', 'вар2'} and len(args) == 2:
            # The first branch is the original orthography in these frozen
            # Russian sources. Bind this to scan inspection, never OCR agreement.
            variants.append(dict(template=name, selected_argument=1,
                action='historical_scan_orthography', discarded_argument=2))
            return args[0]
        if name in {'κσγ', 'κενό στα γράμματα'} and args:
            return args[0]
        if name in {'sic', 'опечатка2', '№'} and args:
            return args[0]  # Literal printed typo, never the tooltip correction.
        if name == 'lang' and len(args) == 2:
            return args[1]
        if name == 'fsp':
            return ' '
        if name == 'перенос' and len(args) >= 2:
            fragment = args[0] + '-'
            joins.append(dict(template=name, arguments=args, output=fragment, joined=False,
                              action='marker_removed_fragment_preserved'))
            return fragment
        if name == 'перенос2' and len(args) >= 2:
            joins.append(dict(template=name, arguments=args, output=args[1], joined=False,
                              action='marker_removed_fragment_preserved'))
            return args[1]
        if name in {'hws', 'hwe', 'hyphenated word start', 'hyphenated word end',
                    'σλβα', 'σλβτ', 'συλλαβισμόςαρχή', 'συλλαβισμόςτέλος'} and args:
            # These describe cross-page words. Preserve the literal printed
            # fragment; do not replace it with a whole word on a single page.
            fragment = args[0]
            if name in {'hws', 'hyphenated word start', 'σλβα', 'συλλαβισμόςαρχή'} and not fragment.endswith('-'):
                fragment += '-'
            joins.append(dict(template=name, arguments=args, output=fragment,
                              action='marker_removed_fragment_preserved', joined=False))
            return fragment
        if name in {'буквица', 'dropinitial', 'dropinitial2'} and args:
            return ''.join(args[:2]) if len(args) > 1 else args[0]
        if name in {'rh', 'runningheader', 'κβ', 'κεφαλίδα'}:
            return '\n' + ' '.join(args) + '\n'
        unknown.append(dict(template=name, arguments=args))
        return UNKNOWN
    # Innermost-first replacement means outer templates see resolved content.
    for _ in range(40):
        changed = re.sub(r'\{\{([^{}]*)\}\}', template, text)
        if changed == text:
            break
        text = changed
    if '{{' in text or '}}' in text:
        unknown.append(dict(template='unbalanced_braces', arguments=[]))
        text = text.replace('{{', UNKNOWN).replace('}}', UNKNOWN)
    text = re.sub(r'\[\[(?:Category|Κατηγορία|Категория|File|Αρχείο|Файл):[^\]]*\]\]', '', text, flags=re.I)
    text = re.sub(r'\[\[([^\]|]+)(?:\|([^\]]*))?\]\]', lambda m: m[2] if m[2] is not None else m[1], text)
    text = re.sub(r'\[https?://\S+\s+([^\]]+)\]', r'\1', text)
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.I)
    text = re.sub(r'</(?:p|div|poem|tr|li)>', '\n', text, flags=re.I)
    text = re.sub(r'<ref\b[^>]*>.*?</ref>', '', text, flags=re.S | re.I)
    text = re.sub(r'<[^>]*>', '', text)
    text = re.sub(r"'{2,5}", '', text)
    text = re.sub(r'(?m)^\s*=+\s*(.*?)\s*=+\s*$', r'\1', text)
    if '\u00ad' in text:
        joins.extend(dict(action='soft_hyphen_removed', joined=True, source_offset=i)
                     for i, ch in enumerate(text) if ch == '\u00ad')
        text = text.replace('\u00ad', '')
    lines = [dict(text=nfc(html.unescape(line)), cleaned_line=i + 1)
             for i, line in enumerate(text.splitlines()) if nfc(html.unescape(line))]
    for i, line in enumerate(lines):
        line.update(index=i, usable=UNKNOWN not in line['text'])
    return dict(lines=lines, hyphenation=joins, unknown_templates=unknown,
                templates=dict(templates), variant_selections=variants,
                proofread_level=int(level[1]) if level else None,
                line_break_scope='source newlines and explicit block breaks; no reconstruction of printed rows')


def distance(a, b):
    """Exact unit-cost Levenshtein distance using Myers' bit-vector algorithm."""
    if not a:
        return len(b)
    peq = {}
    for i, ch in enumerate(a):
        peq[ch] = peq.get(ch, 0) | (1 << i)
    vp, vn, score, high = ~0, 0, len(a), 1 << (len(a) - 1)
    for ch in b:
        eq = peq.get(ch, 0)
        d0 = (((eq & vp) + vp) ^ vp) | eq | vn
        hp, hn = vn | ~(d0 | vp), vp & d0
        score += bool(hp & high) - bool(hn & high)
        hp = (hp << 1) | 1
        vp, vn = (hn << 1) | ~(d0 | hp), d0 & hp
    return score


def align_lines(docai, human, *, minimum_similarity=.65):
    """Monotone global alignment; explicit 1:2/2:1 blocks remain unaligned.

    Costs: normalized character edit distance, .45 per skipped line, .25
    split/merge penalty. Only a 1:1 block above the fixed threshold gets gold.
    All human line positions, including unresolved ones, remain in the trace.
    """
    d = [nfc(x) for x in docai]
    h = [nfc(x['text']) for x in human]
    n, m = len(d), len(h)
    costs = [[float('inf')] * (m + 1) for _ in range(n + 1)]
    trace = {}; costs[0][0] = 0
    def block(a, b):
        if any(not human[k].get('usable', True) for k in b):
            return None
        left, right = ' '.join(d[k] for k in a), ' '.join(h[k] for k in b)
        sim = 1 - distance(left, right) / max(len(left), len(right), 1)
        return sim if sim >= minimum_similarity else None
    for i in range(n + 1):
        for j in range(m + 1):
            options = []
            if i < n: options.append((1, 0, .45, None))
            if j < m: options.append((0, 1, .45, None))
            for di, dj in [(1, 1), (1, 2), (2, 1)]:
                if i + di <= n and j + dj <= m:
                    sim = block(range(i, i + di), range(j, j + dj))
                    if sim is not None:
                        options.append((di, dj, 1 - sim + (.25 if di != dj else 0), sim))
            for di, dj, delta, sim in options:
                if costs[i][j] + delta < costs[i + di][j + dj] - 1e-12:
                    costs[i + di][j + dj] = costs[i][j] + delta
                    trace[i + di, j + dj] = (i, j, di, dj, sim)
    result = [dict(alignment='unaligned', human_label=None, cer_docai_vs_human=None,
                   human_line_indices=[], alignment_reason='no_one_to_one_match') for _ in d]
    blocks = []; i, j = n, m
    while i or j:
        pi, pj, di, dj, sim = trace[i, j]
        blocks.append(dict(docai_indices=list(range(pi, i)), human_indices=list(range(pj, j)), similarity=sim))
        for k in range(pi, i):
            result[k].update(human_line_indices=list(range(pj, j)), alignment_similarity=sim)
            if di == dj == 1:
                errors = distance(h[pj], d[k])
                result[k].update(alignment='aligned', human_label=h[pj],
                    cer_docai_vs_human=errors / len(h[pj]) if h[pj] else None,
                    edit_distance=errors, human_characters=len(h[pj]), alignment_reason='one_to_one')
            elif di and dj:
                result[k]['alignment_reason'] = 'split_or_merged_lines'
        i, j = pi, pj
    return result, list(reversed(blocks))


def cer_summary(records):
    def aggregate(rows):
        aligned = [r for r in rows if r['alignment'] == 'aligned']
        chars = sum(r['human_characters'] for r in aligned)
        edits = sum(r['edit_distance'] for r in aligned)
        return dict(lines=len(rows), aligned=len(aligned), aligned_share=len(aligned) / len(rows) if rows else None,
                    human_characters=chars, edit_distance=edits, cer=edits / chars if chars else None)
    result = {}
    for lang in ('el', 'ru'):
        rows = [r for r in records if r['lang'] == lang]
        result[lang] = aggregate(rows)
        result[lang]['mark_classes'] = {name: aggregate([r for r in rows
            if r.get('human_label') and any(c in ud.normalize('NFD', r['human_label']) for c in marks)])
            for name, marks in MARKS.items()}
    return result


def splits(books, seed=20261015):
    import random
    dev = set()
    rng = random.Random(seed)
    for lang, count in [('el', 3), ('ru', 1)]:
        keys = sorted(b['key'] for b in books if b['lang'] == lang)
        if len(keys) < count:
            raise ValueError('insufficient works for required dev split')
        dev.update(rng.sample(keys, count))
    return [dict(book_key=b['key'], title=b['title'], year=b['year'], lang=b['lang'],
                 split='dev' if b['key'] in dev else 'test') for b in books]
