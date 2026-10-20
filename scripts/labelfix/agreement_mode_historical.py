"""Historical component-proxy counterfactual; not an L1 release measurement.

This input format lacks R1 coverage and detector segmentation/observability.
The original diagnostic is retained for historical arithmetic only. Its flags
and disagreements now abstain. New consumers must use decide with real inputs.
"""
from greekocr.ops.data_root import input_path as _data_input
from greekocr.labelfix.release_gate import decide

def main():
    import gzip, json, sys
    from collections import Counter
    from scripts.labelfix.r1_error_types import G,google_marks,atomic,kind,nfd
    R1 = sys.argv[1]; MODE = sys.argv[2] if len(sys.argv) > 2 else 'full'
    FLAGS = set()
    if len(sys.argv) > 3:
        for l in gzip.open(sys.argv[3], 'rt'):
            q = json.loads(l)
            for f in q['constraint_flags']:
                if f.get('action') == 'flag' and f.get('reason') == 'impossible_by_rule': FLAGS.add((q['line_id'], f['start']))
    def kinds(m): return {k for k, _ in m}
    s6 = {json.loads(l)['line_id']: json.loads(l) for l in gzip.open(_data_input('docs/records/labelfix/spellcheck/S6_lines.jsonl.gz'), 'rt')}
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
            if MODE == 'zone':
                sd = d6[s['slot']]
                agree = (bool(sd.get('above')) == bool({k for k, _ in R} & {'breathing', 'accent', 'dialytika'})) and \
                        (bool(sd.get('below')) == ('subscript' in {k for k, _ in R}))
            else:
                agree = (R == D) if MODE == 'full' else (kinds(R) == kinds(D))
            if (r['line_id'], st) in FLAGS or s.get('hold') or s.get('label_status')=='HOLD' or st in flagged_starts: act='hold'
            elif R == g and agree: act = 'keep'
            elif R == g: act = 'hold'
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

if __name__=='__main__':main()
