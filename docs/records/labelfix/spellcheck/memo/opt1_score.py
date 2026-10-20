import json, sys
from collections import Counter
R = [json.loads(l) for l in open(sys.argv[1])]
truth = json.load(open(sys.argv[2])) if len(sys.argv) > 2 else None   # optional print-truth overrides: "line|w" -> printed word class per cluster
held = [r for r in R if not r['dev']]
print('clusters held-out', len(held), 'of', len(R), '; word-error clusters (g!=h):', sum(r['g'] != r['h'] for r in held))
ab = Counter(r.get('abstain') or 'read' for r in held); print('abstention', dict(ab))
for tau in (0.8, 0.9, 0.95, 0.99, 0.998):
    c = Counter()
    for r in held:
        err = r['g'] != r['h']
        c['err'] += err
        ok = r.get('abstain') is None and r.get('prob', 0) >= tau
        c['covered'] += ok
        if ok and r['pred'] != r['g']:
            if r['pred'] == r['h'] and err: c['fix'] += 1
            elif not err: c['break'] += 1
            else: c['wrongfix'] += 1
        if ok and err and r['pred'] == r['g']: c['reads_google_on_error'] += 1
    ch = c['fix'] + c['break'] + c['wrongfix']
    print(f"tau {tau}: coverage {100*c['covered']/len(held):.1f}%  changes {ch}  fixes {c['fix']}/{c['err']} errors  breaks {c['break']}  wrong-fix {c['wrongfix']}  precision {100*c['fix']/max(1,ch):.1f}%  (ink reads Google's mark on an error: {c['reads_google_on_error']})")
