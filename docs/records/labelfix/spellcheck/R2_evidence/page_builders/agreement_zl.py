import gzip, json, sys
from collections import Counter
exec(open('scripts/labelfix/r1_error_types.py').read().split("if __name__")[0])
from greekocr.labelfix.lexicon import load_all
from greekocr.labelfix.spellink import proposals
from greekocr.labelfix.text import tokenize, nfc
LEX = load_all('docs/labelfix/lexicons')
REG = {json.loads(l)['line_id']: json.loads(l)['regime'] for l in open('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/labelfix/validation_lines_s0.jsonl')}
LEXSTAT = Counter(); REJ = []
def r1_word_ok(r, st, gm_line):
    """R1's full word (recogniser letters + R1 marks for every letter of that word) attested, or the lexicon's proposal for Google's word."""
    rec = nfd(r['recogniser_text'])
    marks = {x['recogniser_start']: atomic(x.get('detected', [])) for x in r['slots'] if x.get('recogniser_start') is not None}
    inv = {v: k for k, v in NAME.items()}
    for t in tokenize(rec):
        if not (t.core_start <= st < t.core_start + len(t.core)): continue
        out = []
        for c in clusters(t.core):
            a = t.core_start + c.start
            m = marks.get(a)
            out.append(c.base + (''.join(inv[x] for x in sorted(m) if x in inv) if m is not None else c.marks))
        from greekocr.labelfix.constraints import normalise
        word = normalise(''.join(out))
        lex = LEX.get(REG.get(r['line_id'], 'poly19')) or LEX['poly19']
        if lex.attested(word): LEXSTAT['attested'] += 1; return True
        g = next((gt for gt, mt in pair_tokens(G[r['line_id']], rec) if mt is not None and mt.index == t.index), None)
        if g is not None:
            props, _ = proposals(g.core, lex)
            if any(nfd(p.form) == nfd(word).lower() or nfd(p.form) == nfd(word) for p in props): LEXSTAT['lexicon proposal'] += 1; return True
        LEXSTAT['unattested -> HOLD'] += 1; REJ.append((r['line_id'], nfc(word), g.core if g is not None else None, REG.get(r['line_id']))); return False
    LEXSTAT['no word'] += 1; return False
R1 = sys.argv[1]; MODE = sys.argv[2] if len(sys.argv) > 2 else 'full'
FLAGS = set()
if len(sys.argv) > 3:
    for l in gzip.open(sys.argv[3], 'rt'):
        q = json.loads(l)
        for f in q['constraint_flags']:
            if f.get('action') == 'flag' and f.get('reason') == 'impossible_by_rule': FLAGS.add((q['line_id'], f['start']))
def kinds(m): return {k for k, _ in m}
s6 = {json.loads(l)['line_id']: json.loads(l) for l in gzip.open('docs/labelfix/spellcheck/S6_lines.jsonl.gz', 'rt')}
c = Counter(); lines = Counter(); by_type = Counter(); rows = []
for l in gzip.open(R1, 'rt'):
    r = json.loads(l)
    if r.get('dev'): continue
    d6 = {s['slot']: s for s in s6[r['line_id']]['slots']}
    gm = google_marks(G[r['line_id']], nfd(r['recogniser_text']))
    flagged_starts={f['start'] for f in r.get('constraint_flags',[]) if 'start' in f}
    flagged_starts.update(a['start'] for f in r.get('constraint_flags',[]) for a in f.get('alternatives',[]) if 'start' in a)
    line_hold = line_corr = False
    wl = Counter(x.get('word') for x in r['slots'])
    for s in r['slots']:
        st = s.get('recogniser_start')
        if st not in gm or s['slot'] not in d6: continue
        g = gm[st]; R = atomic(s.get('detected', [])); D = atomic(d6[s['slot']].get('detected', []))
        known = s.get('truth') is not None; T = atomic(s['truth']) if known else None
        if (r['line_id'], st) in FLAGS: act = 'hold'
        if MODE in ('zone', 'zonelex'):
            sd = d6[s['slot']]
            agree = (bool(sd.get('above')) == bool({k for k, _ in R} & {'breathing', 'accent', 'dialytika'})) and \
                    (bool(sd.get('below')) == ('subscript' in {k for k, _ in R}))
        else:
            agree = (R == D) if MODE == 'full' else (kinds(R) == kinds(D))
        if s.get('hold') or s.get('label_status')=='HOLD' or st in flagged_starts: act='hold'
        elif R == g and agree: act = 'keep'
        elif R == g: act = 'hold' if MODE == 'full' else 'keep'
        elif agree and MODE == 'zonelex' and not r1_word_ok(r, st, gm): act = 'hold'
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
print('lexicon gate:', dict(LEXSTAT))
print(dict(lines)); print(sorted(by_type.items()))
print('examples where Google was right and agreement mode accepted a change:', [x for x in rows if x[-1].startswith('NEW')][:8])
print(len(REJ), REJ[:20])
