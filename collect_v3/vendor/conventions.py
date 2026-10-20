"""Text-only conventions. Geometry is used solely to bind the next column row.

No crop is changed. Unknown printed glyphs/dashes are never inferred from an
already-normalized label. Fragment evidence is an attested joined word on two
other pages, with the tail unattested as a non-final token anywhere in this
fixed-label corpus. Remaining lowercase continuations are explicitly unknown.
"""
from collections import Counter, defaultdict
import re
import unicodedata as ud

ROMAN_TABLE = {'Ι': 'I', 'Χ': 'X', 'Μ': 'M', 'Ϲ': 'C',
               'І': 'I', 'Х': 'X', 'С': 'C', 'М': 'M', 'Ѵ': 'V'}
ROMAN = set('IVXLCMD')
# These shapes have no permitted one-to-one Latin Roman counterpart.
AMBIGUOUS_ROMAN = set('ΛΔДЛПӀ')
WORD = re.compile(r'[^\W\d_]+', re.UNICODE)


def key(s):
    return ''.join(c for c in ud.normalize('NFD', s.casefold()) if not ud.category(c).startswith('M'))


def roman_convention(text):
    fixes, ambiguous = [], []
    def convert(m):
        token = m.group()
        mapped = ''.join(ROMAN_TABLE.get(c, c) for c in token)
        if any(c in ROMAN_TABLE for c in token) and set(mapped) <= ROMAN:
            # A single Greek/Cyrillic initial with a period is not established
            # as a Roman numeral (e.g. Χ. in a Greek person's name). Withhold
            # this ambiguous line instead of silently changing its script.
            if len(token)==1 and text[m.end():m.end()+1]=='.':
                ambiguous.append(token+'.')
                return token
            fixes.append(dict(old=token, new=mapped))
            return mapped
        mixed = any(c in ROMAN for c in token) and any(c in ROMAN_TABLE for c in token)
        shape = set(token) <= ROMAN | set(ROMAN_TABLE) | AMBIGUOUS_ROMAN and any(c in AMBIGUOUS_ROMAN for c in token)
        if mixed or shape:
            ambiguous.append(token)
        return token
    fixed = WORD.sub(convert, text)
    return fixed, fixes, ambiguous


def apply_conventions(features, context=None):
    bypage = defaultdict(list)
    occurrences, nonfinal = defaultdict(set), Counter()
    if context:
        for word, pages in context['occurrences'].items():
            occurrences[word].update(tuple(p) for p in pages)
        nonfinal.update(context['nonfinal'])
    for r in features:
        bypage[(r['track'], r['page_id'])].append(r)
        words = [key(m.group()) for m in WORD.finditer(r['fixed_label'])]
        for w in words:
            occurrences[w].add((r['track'], r['page_id']))
        nonfinal.update(words[:-1])
    for r in features:
        text, fixes, ambiguous = roman_convention(r['fixed_label'])
        long_s = text.count('ſ')
        text = text.replace('ſ', 's')
        r.update(label_after_conventions=text, roman_fixes=fixes, roman_ambiguous=ambiguous,
                 long_s_label_count=long_s, text_exclusions=[], hyphen_test='not_applicable',
                 next_column_line_id=None, join_evidence=None)
        if ambiguous:
            r['text_exclusions'].append('ambiguous_roman_numeral')
        tail = re.search(r'([^\W\d_]+)$', text, flags=re.UNICODE)
        if not tail:
            continue
        box = r['crop_bbox']
        # Existing Google crop rectangles bind column and reading order. No ink.
        possible = []
        for q in bypage[(r['track'], r['page_id'])]:
            qb = q['crop_bbox']
            if q['id'] == r['id'] or qb[1] <= box[1]+.30*(box[3]-box[1]):
                continue
            if qb[1]-box[3] > 2*(box[3]-box[1]):
                continue
            shared = max(0, min(box[2], qb[2])-max(box[0], qb[0]))
            if shared/max(1, min(box[2]-box[0], qb[2]-qb[0])) < .5:
                continue
            if abs(qb[0]-box[0]) > 1.5*r['page_median_row_height']:
                continue
            possible.append(q)
        if not possible:
            r['hyphen_test'] = 'next_column_row_unavailable'
            continue
        q = min(possible, key=lambda q: (q['crop_bbox'][1], q['id']))
        head = re.match(r'\s*([^\W\d_]+)', q['fixed_label'], flags=re.UNICODE)
        r['next_column_line_id'] = q['id']
        if not head or not head.group(1)[0].islower():
            r['hyphen_test'] = 'next_not_lowercase'
            continue
        a, b = key(tail.group(1)), key(head.group(1))
        other_pages = occurrences[a+b]-{(r['track'], r['page_id'])}
        if len(a) >= 2 and len(b) >= 2 and len(other_pages) >= 2 and nonfinal[a] == 0:
            r['hyphen_test'] = 'dropped_end_hyphen_attested_join'
            r['join_evidence'] = dict(tail=tail.group(1), head=head.group(1), joined_key=a+b,
                                      other_pages=[list(p) for p in sorted(other_pages)])
            r['text_exclusions'].append('dropped_line_end_hyphen')
        else:
            r['hyphen_test'] = 'lowercase_continuation_fragment_unknown'
    return features
