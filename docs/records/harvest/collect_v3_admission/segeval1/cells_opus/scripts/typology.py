"""Apply the visual typology labels (assigned by eye from contact sheets) and write samples.jsonl + typology tables."""
import json, sys
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
SP = Path(sys.argv[1]); OUTD = Path(sys.argv[2]).resolve()
W, C, A, R, P, N, H, F, M, WM, S, CUT, ML, TP = ('word_or_phrase', 'heading_caps_display', 'abbreviation_reference_label',
    'roman_numeral_lowercase', 'punctuation_only', 'noise_non_text', 'handwriting', 'foreign_script_printed',
    'map_figure_ornament_logo', 'scan_watermark', 'show_through_mirrored', 'cut_fragment', 'multi_line_crop', 'text_covers_part_of_crop')
LAB = [A, N, W, W, N, W, F, W, P, C,   W, H, W, C, W, F, P, A, P, W,   W, C, A, W, M, C, P, C, P, CUT,
       W, N, C, W, F, P, C, A, A, C,   W, W, C, A, P, M, A, N, C, S,   W, C, W, R, A, C, C, W, C, W,
       C, N, W, P, W, W, P, W, W, A,   TP, C, W, C, H, W, A, CUT, CUT, ML,  C, TP, W, C, W, W, P, A, A, W,
       W, N, W, C, W, W, A, W, H, W,   A, W, W, P, C, N, C, W, C, W,   W, CUT, N, C, W, W, W, R, P, P,
       H, N, C, TP, C, TP, H, C, A, W,   P, W, C, C, TP, TP, C, TP, TP, TP,   TP, TP, TP, C, C, C, WM, M, WM, N,
       TP, TP, TP, P, C, P, TP, TP, TP, TP,   TP, TP, TP, TP, M, TP, TP, TP, C, TP,   TP, C, C, C, C, C, C, C, C]
NOTE = {1: 'blob read as Arabic', 4: 'blobs read as Hebrew', 9: 'last letter at right edge', 13: 'ink of line above at top',
        16: 'ditto marks', 24: 'rotated map label', 26: 'ditto mark', 29: 'first letter clipped at left edge', 31: 'squiggle read as Arabic',
        44: 'closing quotes read as Arabic', 45: 'map label over map graphics', 47: 'illegible decorative/blurred script', 49: 'mirrored verso text',
        61: 'nearly blank faint crop', 70: 'crop holds a whole printed line; text is the tail of the next line',
        74: 'signature', 77: 'clipped illegible glyphs', 78: 'clipped at both edges', 79: 'three lines in crop; text = middle line',
        81: 'crop holds a whole line; text = last word of the line below', 86: 'ditto mark', 91: 'tiny blob', 98: 'scribble', 103: 'clipped symbol',
        105: 'scattered dots', 111: 'clipped at left', 112: 'ink blob/ornament', 118: 'clipped mark', 119: 'ditto mark', 120: 'signature',
        121: 'scattered dots', 126: 'small rotated handwriting', 128: 'ink of lines above/below', 131: 'blackletter Rede read as Kede',
        132: 'letter-spaced with frame lines', 133: 'letter-spaced, stamp over letters', 147: 'ornament pattern', 149: 'nearly blank faint crop',
        150: 'whole line in crop; text = last two words', 164: 'advertisement logo', 168: 'inverse (white on black) title', 172: 'outline display letters',
        174: 'letter-spaced Cyrillic caps read as Latin', 178: 'last letter misread'}
rows = [json.loads(l) for l in open(SP / 'chosen.jsonl')]
typ = [r for r in rows if r['set'].startswith('typology')]
assert len(LAB) == len(typ) == 179, (len(LAB), len(typ))
for i, (r, t) in enumerate(zip(typ, LAB)):
    r['type'] = t; r['sheet_index'] = i
    if i in NOTE:
        r['note'] = NOTE[i]
num = [r for r in rows if r['set'] == 'numeric_sample']
for i, r in enumerate(num):
    r['viewed'] = i < 20
    if i == 11: r['note'] = 'viewed: crop is a 3-line text block; Google text is only the line number 1050'
    if i == 17: r['note'] = 'viewed: last digit clipped at right edge'
    if i == 7: r['note'] = 'viewed: print reads 5.618.336, Google 5.618.335'
for r in typ: r['viewed'] = True
with open(OUTD / 'samples.jsonl', 'w') as o:
    for r in rows:
        o.write(json.dumps(dict(set=r['set'], population=r['population'], line_id=r['line_id'], crop_path=r['crop_path'],
            text=r['text'], width=r['width'], height=r['height'], chars=r['chars'], output_type=r['output_type'],
            verdict_05=r.get('verdict_05'), reason_05=r.get('reason_05'), verdict_08=r.get('verdict_08'), owner=r.get('owner'),
            source=r['source'], primary_class=r.get('primary_class'), type=r.get('type'), note=r.get('note'),
            crop_hash_verified=r.get('crop_hash_verified'), viewed=r.get('viewed', False)), ensure_ascii=False) + '\n')
json.dump([dict(i=r['sheet_index'], line_id=r['line_id'], type=r['type']) for r in typ], open(SP / 'labels.json', 'w'))
print(Counter(r['type'] for r in typ if r['set'] == 'typology_uniform'))
print(Counter(r['type'] for r in typ if r['set'] != 'typology_uniform'))
