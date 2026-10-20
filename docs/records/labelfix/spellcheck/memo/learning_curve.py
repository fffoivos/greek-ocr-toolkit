import gzip, json, random
import numpy as np
from collections import Counter
from greekocr.labelfix.markshape import fit_mlp
S = [json.loads(l) for l in gzip.open('docs/labelfix/markshape_samples.jsonl.gz', 'rt')]
docs = sorted({s['doc'] for s in S}); rng = random.Random(0)
res = []
for rot in range(3):
    rng.shuffle(docs)
    n = len(docs); calib = set(docs[:n // 5]); test = set(docs[n // 5: 2 * n // 5])
    pool = [s for s in S if s['doc'] not in calib | test]
    C = [s for s in S if s['doc'] in calib]; T = [s for s in S if s['doc'] in test]
    classes = sorted(c for c, k in Counter(s['label'] for s in S).items() if k >= 15)
    keep = lambda L: [s for s in L if s['label'] in classes]
    pool, C, T = keep(pool), keep(C), keep(T)
    rng.shuffle(pool)
    for frac in (0.125, 0.25, 0.5, 1.0):
        tr = pool[:int(len(pool) * frac)]
        m = fit_mlp([s['x'] for s in tr], [s['label'] for s in tr], classes)
        def run(L):
            P = m.probs(np.asarray([s['x'] for s in L], float)); pred = P.argmax(1); conf = P.max(1)
            truth = np.asarray([classes.index(s['label']) for s in L]); return pred, conf, truth
        pc, cc, tc = run(C); pt, ct, tt = run(T)
        row = dict(rot=rot, n_train=len(tr), test_acc=float((pt == tt).mean()))
        for target in (0.99, 0.999):
            tau = None
            for t in sorted(set(np.round(cc, 5)))[::-1]:
                sel = cc >= t
                if sel.sum() >= 30 and (pc[sel] == tc[sel]).mean() >= target:
                    tau = t
            if tau is None:
                row[f'cov{target}'] = 0.0; continue
            sel = ct >= tau
            row[f'cov{target}'] = float(sel.mean()); row[f'prec{target}'] = float((pt[sel] == tt[sel]).mean()) if sel.any() else None
        res.append(row); print(row, flush=True)
json.dump(res, open('/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/memo/learning_curve.json', 'w'))
