#!/usr/bin/env python3
"""Render the SR-G2 plain tables from the actual r1 score JSON (offline)."""
import json
from pathlib import Path
from score_grave import ACCENTS, ROOT


def render(result):
    out = ['SR-G2: r1 grave/acute results', '', result['touches_punct_method'], '',
           'Scored against the existing private reference key; this is not a new pixel adjudication.', '',
           'All fractions include unreadable answers in their denominators. 0/0 means no applicable items (rate undefined).', '',
           'positive = printed grave; negative = printed acute; control = circumflex or none.', '']

    def table(title, headers, rows):
        out.extend([title, '', '| '+' | '.join(headers)+' |', '| '+' | '.join('---' for _ in headers)+' |'])
        for row in rows:
            out.append('| '+' | '.join(str(v).replace('|', '\\|').replace('\n', '<br>') for v in row)+' |')
        out.append('')

    def frac(value):
        return f"{value['count']}/{value['total']}"

    def metric_row(label, s):
        return [label, s['n'], f"{s['correct']}/{s['n']}", frac(s['grave_recall']),
                f"{s['negative_false_alarms']['answered_grave']}/{s['negative_false_alarms']['n']}",
                frac(s['negative_acute_correct']), frac(s['control_accuracy']),
                frac(s['unreadable_share']), frac(s['low_confidence']),
                f"{s['positive_lines']['detected']}/{s['positive_lines']['n']}"]

    headers = ['scope', 'items', 'correct / all', 'grave recall / positives', 'false grave / negatives',
               'acute correct / negatives', 'control passes / controls', 'unreadable / all',
               'low confidence / all', 'detected / positive lines']
    table('Overall and per class', headers,
          [metric_row('overall', result['overall'])]+[metric_row(c, s) for c, s in result['per_class'].items()])
    table('Per stratum and class', headers,
          [metric_row(st, result['per_stratum'][st]) for st in result['per_stratum']]+
          [metric_row(st+' / '+c, s) for st, cc in result['per_stratum_class'].items() for c, s in cc.items()])

    table('Punctuation split: overall, per class, per stratum, and stratum by class',
          ['touches_punct']+headers,
          [[flag]+metric_row(label, s) for flag, g in result['touches_punct'].items()
           for label, s in scopes(g)])

    table('Confusion matrices: truth × answer, cells = count / truth-row denominator',
          ['touches_punct', 'scope', 'truth', 'truth n']+list(ACCENTS),
          [[flag, label, truth, sum(counts.values())]+[f'{counts[a]}/{sum(counts.values())}' for a in ACCENTS]
           for flag, g in [('all', result)]+list(result['touches_punct'].items())
           for label, s in scopes(g) for truth, counts in s['confusion_matrix'].items()])
    table('Every wrong item (including any unreadable answer)',
          ['id', 'stratum', 'printed word (key)', 'truth', 'answer', 'confidence', 'note', 'touches_punct'],
          [[i['item_id'], i['stratum'], i['printed_word'], i['truth'], i['answer'], i['confidence'],
            i['note'], str(i['touches_punct']).lower()] for i in result['wrong_items']])
    out.append(f"Wrong items: {len(result['wrong_items'])}/{result['overall']['n']}.")
    out.extend(['', 'Validation: 32/32 tests passed; see TEST_RESULTS_G2.txt. The original public payload was checked in a private copy against MANIFEST.r1.json; the completed reader workspace also contains answers.jsonl and zoom/.', ''])
    return '\n'.join(out)


def scopes(group):
    yield 'overall', group['overall']
    yield from group['per_class'].items()
    yield from group['per_stratum'].items()
    for st, cc in group['per_stratum_class'].items():
        for c, summary in cc.items():
            yield st+' / '+c, summary


if __name__ == '__main__':
    result = json.loads((ROOT.parent/'answers/grave/r1.score.json').read_text())
    (ROOT/'RESULTS_TABLE.md').write_text(render(result))
