"""Whole-line population CER: recogniser vs Google against two-reader full-line print truth, per stratum."""
import json, gzip, sys, unicodedata as ud
from collections import defaultdict
sys.path.insert(0, '/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck')
from greekocr.labelfix.validate import load_three_way
S = sys.argv[1]; R0 = '/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck-r0'
key = {x['id']: x for x in json.load(open(f'{S}/wl_key.json'))}
def load(p): return {json.loads(l)['id']: json.loads(l) for l in open(p) if l.strip()}
r1, r2 = load(f'{S}/wl_r1.jsonl'), load(f'{S}/wl_r2.jsonl')
tb = load(f'{S}/wl_r3.jsonl') if len(sys.argv) > 2 else {}
APO = str.maketrans({"᾽": "’", "᾿": "’", "'": "’", "ʼ": "’"})
def norm(s): return ' '.join(ud.normalize('NFC', (s or '').translate(APO)).split())
def letters(s): return ''.join(c for c in ud.normalize('NFD', s) if ud.category(c)[0] == 'L')
def withmarks(s): return ''.join(c for c in ud.normalize('NFD', s) if ud.category(c)[0] in 'LM')
def lev(a, b):
    p = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        c = [i]
        for j, y in enumerate(b, 1): c.append(min(p[j] + 1, c[j - 1] + 1, p[j - 1] + (x != y)))
        p = c
    return p[-1]
three = {l['line_id']: l for l in load_three_way(0)}
ib = {json.loads(l)['line_id']: json.loads(l) for l in open(f'{R0}/docs/records/labelfix/spellcheck/R0_locked_ib.jsonl')}
ibrec = {json.loads(l)['line_id']: json.loads(l)['alignment']['prediction'] for l in open(f'{R0}/.cache/labelfix/r0/align_locked_ib.jsonl')}
ii = {json.loads(l)['line_id']: json.loads(l) for l in open(f'{R0}/docs/records/labelfix/spellcheck/R0_newsource_locked.jsonl')}
def sources(it):
    lid = it['line_id']
    if it['stratum'] == '666': return three[lid]['model'], three[lid]['google']
    if it['stratum'] == 'ii': return ii[lid]['model'], ii[lid]['google']
    return ibrec[lid], ib[lid]['google']
acc = defaultdict(lambda: defaultdict(int)); status = defaultdict(int); rows = []
for i, it in key.items():
    t1, t2 = norm(r1[i]['text']), norm(r2[i]['text'])
    if t1 == t2: truth = t1; st = 'agreed'
    elif i in tb and norm(tb[i]['text']) in (t1, t2): truth = norm(tb[i]['text']); st = 'majority'
    else: status['unresolved'] += 1; rows.append(dict(id=i, status='unresolved')); continue
    if '⟨?⟩' in truth or '⟨cut⟩' in truth: status['partial'] += 1
    status[st] += 1
    truth_c = truth.replace('⟨cut⟩', '').replace('⟨?⟩', '')
    rec, goo = sources(it)
    for name, hyp in (('recogniser', rec), ('google', goo)):
        for kind, f in (('letters', letters), ('letters+marks', withmarks)):
            T, H = f(truth_c), f(norm(hyp))
            acc[(it['stratum'], name, kind)]['err'] += lev(H, T); acc[(it['stratum'], name, kind)]['n'] += len(T)
    rows.append(dict(id=i, stratum=it['stratum'], line_id=it['line_id'], status=st, truth=truth, recogniser=rec, google=goo))
print(dict(status))
for k in sorted(acc): v = acc[k]; print(k, f"{v['err']}/{v['n']} = {100*v['err']/max(1,v['n']):.2f}%")
json.dump(rows, open(f'{S}/wl_scored.json', 'w'), ensure_ascii=False, indent=1)
