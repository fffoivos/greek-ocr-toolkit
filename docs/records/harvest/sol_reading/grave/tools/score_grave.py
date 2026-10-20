#!/usr/bin/env python3
"""Score ordered SR-G responses against the private key and C1 source lines."""
import argparse
import json
import re
import unicodedata as U
from pathlib import Path

ACCENTS = ('acute', 'grave', 'circumflex', 'none', 'unreadable')
ROOT = Path(__file__).resolve().parents[1]
C1 = Path.home()/'Projects/collect-v3-data/run/W1/c1'
PUNCT = ',.;·:!?»)…'
HYPHENS = '-‐‑'
FLAG_METHOD = ('touches_punct uses the C1 literal_label bound by stratum/card_id/line_id '
               'and the 1-based key word_index: true for punctuation (, . ; · : ! ? » ) …) '
               'immediately after the last letter, or a hyphen at that word\'s line end '
               '(including a hyphen-split word); a bare line ending is false.')


def letters(text):
    return ''.join(c for c in U.normalize('NFD', text) if c.isalpha())


def touches_punctuation(line_text, word_index, printed_word):
    """Use the source token position, never a substring search or accent spelling."""
    words = list(re.finditer(r'\S+', line_text))
    if not isinstance(word_index, int) or isinstance(word_index, bool) or not 1 <= word_index <= len(words):
        raise ValueError('Invalid source word index')
    token = words[word_index-1]
    if letters(token.group()) != letters(printed_word):
        raise ValueError('C1 source word does not match key printed word')
    # Normalize before indexing so a decomposed final accent is part of the letter.
    text = U.normalize('NFC', line_text)
    token = list(re.finditer(r'\S+', text))[word_index-1]
    positions = [i for i, c in enumerate(token.group()) if c.isalpha()]
    if not positions:
        raise ValueError('Source word has no letters')
    end = token.start()+positions[-1]+1
    while end < len(text) and U.category(text[end]).startswith('M'):
        end += 1
    suffix = text[end:]
    return bool(suffix and suffix[0] in PUNCT) or (bool(suffix.strip()) and suffix.strip() in HYPHENS)


def annotate_key(key, c1_root=C1):
    """Bind every source line, retain evidence, and fail on stale annotations."""
    sources = {}
    result = {}
    for iid, record in key.items():
        s = record['stratum']
        if s not in sources:
            path = Path(c1_root)/f'{s}_key.json'
            sources[s] = (path, json.loads(path.read_text()))
        path, rows = sources[s]
        source = rows[record['card_id']]
        if source['line_id'] != record['line_id']:
            raise ValueError('C1 source line id mismatch')
        text = source['literal_label']
        flag = touches_punctuation(text, record['word_index'], record['printed_word'])
        if 'touches_punct' in record and (type(record['touches_punct']) is not bool or record['touches_punct'] != flag):
            raise ValueError('Stale touches_punct annotation')
        result[iid] = dict(record, touches_punct=flag, c1_line_text=text,
                           touches_punct_source=str(path))
    return result


def load_answers(path):
    def unique_fields(pairs):
        obj = {}
        for name, value in pairs:
            if name in obj:
                raise ValueError('Duplicate JSON field: '+name)
            obj[name] = value
        return obj
    with Path(path).open() as f:
        return [json.loads(line, object_pairs_hook=unique_fields) for line in f if line.strip()]


def score(answers, key):
    if len(answers) != len(key):
        raise ValueError('Expected exactly one answer per item')
    for answer, iid in zip(answers, key):
        if not isinstance(answer, dict) or set(answer) != {'item_id', 'accent', 'confidence', 'note'}:
            raise ValueError('Answer fields must be exactly item_id, accent, confidence and note')
        if answer['item_id'] != iid:
            raise ValueError('Wrong item id/order or duplicate answer')
        if not isinstance(answer['accent'], str) or answer['accent'] not in ACCENTS:
            raise ValueError('Invalid accent')
        if not isinstance(answer['confidence'], str) or answer['confidence'] not in ('high', 'low'):
            raise ValueError('Invalid confidence')
        if not isinstance(answer['note'], str):
            raise ValueError('Invalid note: expected string')
        if type(key[iid].get('touches_punct')) is not bool:
            raise ValueError('Key requires a boolean touches_punct for every item')
    pairs = [(key[a['item_id']], a) for a in answers]

    def fraction(x, n):
        return dict(count=x, total=n, rate=x/n if n else None)

    def summary(rows):
        matrix = {t: {a: 0 for a in ACCENTS} for t in ACCENTS[:-1]}
        for m, a in rows:
            matrix[m['truth_accent']][a['accent']] += 1
        n = len(rows)
        correct = sum(a['accent'] == m['truth_accent'] for m, a in rows)
        controls = [(m, a) for m, a in rows if m['class'] == 'control']
        positives = [(m, a) for m, a in rows if m['class'] == 'positive']
        negatives = [(m, a) for m, a in rows if m['class'] == 'negative']
        false = sum(a['accent'] == 'grave' for _, a in negatives)
        lines = {}
        for m, a in positives:
            line = lines.setdefault(m['line_id'], dict(stratum=m['stratum'], items=0,
                                                      grave_answers=0, detected=False))
            line['items'] += 1
            line['grave_answers'] += a['accent'] == 'grave'
            line['detected'] |= a['accent'] == 'grave'
        detected = sum(v['detected'] for v in lines.values())
        return dict(n=n, confusion_matrix=matrix, correct=correct,
                    accuracy=correct/n if n else None,
                    unreadable=sum(a['accent'] == 'unreadable' for _, a in rows),
                    unreadable_share=fraction(sum(a['accent'] == 'unreadable' for _, a in rows), n),
                    control_passes=sum(a['accent'] == m['truth_accent'] for m, a in controls),
                    control_total=len(controls),
                    control_accuracy=fraction(sum(a['accent'] == m['truth_accent'] for m, a in controls), len(controls)),
                    grave_recall=fraction(sum(a['accent'] == 'grave' for _, a in positives), len(positives)),
                    negative_false_alarms=dict(n=len(negatives), answered_grave=false,
                                               rate=false/len(negatives) if negatives else None),
                    negative_acute_correct=fraction(sum(a['accent'] == 'acute' for _, a in negatives), len(negatives)),
                    low_confidence=fraction(sum(a['confidence'] == 'low' for _, a in rows), n),
                    positive_lines=dict(n=len(lines), detected=detected,
                                        detection_rate=detected/len(lines) if lines else None, lines=lines))

    classes = sorted({m['class'] for m in key.values()})
    strata = sorted({m['stratum'] for m in key.values()})

    def grouped(rows):
        return dict(overall=summary(rows),
                    per_class={c: summary([(m, a) for m, a in rows if m['class'] == c]) for c in classes},
                    per_stratum={s: summary([(m, a) for m, a in rows if m['stratum'] == s]) for s in strata},
                    per_stratum_class={s: {c: summary([(m, a) for m, a in rows if m['stratum'] == s and m['class'] == c])
                                           for c in classes} for s in strata})
    result = grouped(pairs)
    result['positive_lines'] = result['overall']['positive_lines']
    result['negative_false_alarms'] = result['overall']['negative_false_alarms']
    result['touches_punct_method'] = FLAG_METHOD
    result['touches_punct'] = {str(flag).lower(): grouped([(m, a) for m, a in pairs if m['touches_punct'] == flag])
                               for flag in (True, False)}
    result['items'] = [dict(item_id=a['item_id'], stratum=m['stratum'], **{'class': m['class']},
                            printed_word=m.get('printed_word'), truth=m['truth_accent'],
                            answer=a['accent'], confidence=a['confidence'], note=a['note'],
                            touches_punct=m['touches_punct'], correct=a['accent'] == m['truth_accent'],
                            c1_line_text=m.get('c1_line_text'), line_id=m['line_id'],
                            word_index=m.get('word_index')) for m, a in pairs]
    result['wrong_items'] = [item for item in result['items'] if not item['correct']]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('answers', type=Path)
    args = parser.parse_args()
    try:
        key = annotate_key(json.loads((ROOT/'keys/key.json').read_text()))
        result = score(load_answers(args.answers), key)
    except (ValueError, OSError, KeyError) as exc:
        parser.exit(2, f'Invalid answers or source key: {exc}\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
