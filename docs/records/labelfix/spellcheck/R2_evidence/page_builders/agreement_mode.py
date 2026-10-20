import gzip, json, sys
from collections import Counter
exec(open('scripts/labelfix/r1_error_types.py').read().split("if __name__")[0])
R1 = sys.argv[1]; MODE = sys.argv[2] if len(sys.argv) > 2 else 'full'
def kinds(m): return {k for k, _ in m}
s6 = {json.loads(l)['line_id']: json.loads(l) for l in gzip.open('docs/labelfix/spellcheck/S6_lines.jsonl.gz', 'rt')}
c = Counter(); lines = Counter(); by_type = Counter(); rows = []
for l in gzip.open(R1, 'rt'):
    r = json.loads(l)
    if r.get('dev'): continue
    d6 = {s['slot']: s for s in s6[r['line_id']]['slots']}
    gm = google_marks(G[r['line_id']], nfd(r['recogniser_text']))
    line_hold = line_corr = False
    wl = Counter(x.get('word') for x in r['slots'])
    for s in r['slots']:
        st = s.get('recogniser_start')
        if st not in gm or s['slot'] not in d6: continue
        g = gm[st]; R = atomic(s.get('detected', [])); D = atomic(d6[s['slot']].get('detected', []))
        known = s.get('truth') is not None; T = atomic(s['truth']) if known else None
        agree = (R == D) if MODE == 'full' else (kinds(R) == kinds(D))
        if R == g and agree: act = 'keep'
        elif R == g: act = 'hold' if MODE == 'full' else 'keep'
        elif agree: act = 'correct'
        else: act = 'hold'
        line_hold |= act == 'hold'; line_corr |= act == 'correct'
        c[('all slots', act)] += 1
        if not known: c[('truth unknown', act)] += 1; continue
        if g != T:
            k = kind(s, T, g, wl[s.get('word')])
            res = 'corrected' if act == 'correct' and R == T else 'HOLD' if act == 'hold' else 'wrong correction' if act == 'correct' else 'missed (kept Google)'
            c[('google error', res)] += 1; by_type[(k, res)] += 1
        else:
            res = 'kept' if act == 'keep' else 'HOLD' if act == 'hold' else 'NEW ERROR (accepted)'
            c[('google right', res)] += 1
            if res != 'kept': rows.append((r['line_id'], s['slot'], s['base'], sorted(g), sorted(R), sorted(D), res))
    lines['lines'] += 1; lines['lines with a HOLD'] += line_hold; lines['lines with a correction'] += line_corr
    lines['clean lines (no HOLD)'] += not line_hold
for k, v in sorted(c.items()): print(k, v)
print(dict(lines)); print(sorted(by_type.items()))
print('examples where Google was right and agreement mode accepted a change:', [x for x in rows if x[-1].startswith('NEW')][:8])
