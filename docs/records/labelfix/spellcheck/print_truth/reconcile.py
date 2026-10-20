import json, glob, unicodedata as u
from collections import Counter, defaultdict
key = json.load(open('key_SEALED.json'))
ans = defaultdict(dict)
for f in glob.glob('answers_b*_r*.jsonl'):
    r = f.split('_')[-1][:2]
    for l in open(f):
        l = l.strip()
        if not l: continue
        a = json.loads(l); ans[a['id']][r] = a
nfc = lambda s: u.normalize('NFC', s or '')
def form(k, a):
    if a['answer'] == 'A': return nfc(k['A'])
    if a['answer'] == 'B': return nfc(k['B'])
    if a['answer'] == 'NEITHER': return nfc(a.get('printed'))
    return None
out = {}; c = Counter(); ctrl = Counter()
for iid, k in key.items():
    rs = ans.get(iid, {})
    f1, f2 = (form(k, rs[r]) if r in rs else None for r in ('r1', 'r2'))
    if f1 and f2 and f1 == f2: printed, status = f1, 'agree'
    elif f1 and f2: printed, status = None, 'disagree'
    elif f1 or f2: printed, status = (f1 or f2), 'one_reader'
    else: printed, status = None, 'unreadable'
    g, h = nfc(k['google']), nfc(k['human'])
    if k['kind'] == 'control':
        ctrl['n'] += 1; ctrl[status] += 1
        if printed: ctrl['right' if printed == g else 'wrong'] += 1
        for r in ('r1', 'r2'):
            if r in rs: ctrl[r + ('_right' if form(k, rs[r]) == g else '_wrong_or_unread')] += 1
        continue
    verdict = ('google' if printed == g else 'human' if printed == h else 'other') if printed else status
    c[(status, verdict)] += 1
    out[f"{k['line_id']}|{k['w']}"] = dict(id=iid, google=g, human=h, printed=printed, status=status, verdict=verdict,
        r1=rs.get('r1', {}).get('answer'), r2=rs.get('r2', {}).get('answer'),
        conf=[rs.get(r, {}).get('confidence') for r in ('r1', 'r2')], reasons=[rs.get(r, {}).get('reason') for r in ('r1', 'r2')])
json.dump(out, open('print_truth_s0.json', 'w'), ensure_ascii=False, indent=0)
print('controls', dict(ctrl))
print('diffs', sum(c.values()))
for k_, v in sorted(c.items()): print(k_, v)
