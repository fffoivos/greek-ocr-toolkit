"""Option 1 (image only) scored against PRINT truth: per cluster, the printed class = adjudicated printed word where adjudicated,
else the human class (Google = human words assumed printed). Held-out books only."""
import json, sys
from collections import Counter
from greekocr.labelfix.markshape import mark_class
from greekocr.labelfix.text import clusters, nfd
R = [json.loads(l) for l in open(sys.argv[1])]
pt = json.load(open(sys.argv[2]))
def printed_class(r):
    v = pt.get(f"{r['line_id']}|{r['w']}")
    if v is None:
        return r['h']
    if not v.get('printed'):
        return None
    cl = clusters(nfd(v['printed']))
    return mark_class(cl[r['c']].marks) if r['c'] < len(cl) else None
for split in ('held-out', 'all'):
    rows = [r for r in R if (not r['dev']) or split == 'all']
    for r in rows: r['p'] = printed_class(r)
    rows = [r for r in rows if r['p'] is not None]
    err = sum(r['g'] != r['p'] for r in rows)
    print(f'== {split}: clusters {len(rows)}, Google mark errors vs print {err} (base rate {100*err/len(rows):.2f}%)')
    for tau in (0.9, 0.99, 0.998):
        c = Counter()
        for r in rows:
            ok = r.get('abstain') is None and r.get('prob', 0) >= tau
            if ok and r['pred'] != r['g']:
                c['fix' if r['pred'] == r['p'] else 'break' if r['g'] == r['p'] else 'wrong'] += 1
        ch = sum(c.values())
        print(f"  tau {tau}: changes {ch}, fixes {c['fix']}/{err} ({100*c['fix']/max(1,err):.1f}%), breaks {c['break']}, wrong {c['wrong']}, precision {100*c['fix']/max(1,ch):.1f}%")
