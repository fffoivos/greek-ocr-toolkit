import json
from collections import Counter
from greekocr.labelfix.candidates import pair_tokens
from greekocr.labelfix.markshape import mark_class
from greekocr.labelfix.text import MARK_BEARERS, clusters, nfd, strip_marks, tokenize
from greekocr.labelfix.validate import DEV_BOOKS, PRED_DIR, load_three_way
reg = {json.loads(l)['line_id']: json.loads(l)['regime'] for l in open('docs/labelfix/validation_lines_s0.jsonl')}
for seed in (0, 1):
    c = Counter()
    for l in load_three_way(seed):
        if reg.get(l['line_id'], 'mono') == 'mono' or l['doc'] in DEV_BOOKS:
            continue
        gh = {g.index: h for g, h in pair_tokens(l['google'], l['human'])}
        gm = {g.index: m for g, m in pair_tokens(l['google'], l['model'])}
        for g in tokenize(l['google']):
            h, m = gh.get(g.index), gm.get(g.index)
            if not g.core or h is None or m is None:
                continue
            if not (strip_marks(nfd(g.core)) == strip_marks(nfd(h.core)) == strip_marks(nfd(m.core))):
                continue
            for a, b, d in zip(clusters(g.core), clusters(h.core), clusters(m.core)):
                if a.base not in MARK_BEARERS:
                    continue
                G, H, M = mark_class(a.marks), mark_class(b.marks), mark_class(d.marks)
                c['n'] += 1; c['google_ok'] += G == H; c['model_ok'] += M == H
                c['agree'] += G == M; c['agree_ok'] += (G == M) and G == H
                if G == H: c['g_ok_n'] += 1; c['model_breaks'] += M != H
                else: c['g_err'] += 1; c['model_fixes'] += M == H
    print(seed, dict(c), 'google acc %.4f model acc %.4f agree %.3f label-noise-when-agree %.4f model-false-change-rate %.4f' % (
        c['google_ok']/c['n'], c['model_ok']/c['n'], c['agree']/c['n'], 1-c['agree_ok']/c['agree'], c['model_breaks']/c['g_ok_n']))
# free labels: v2_test lines where Google == model, polytonic
n_lines = n_cl = n_cl_agree = 0
for line in open(PRED_DIR / 'full_s0_v2_test.jsonl'):
    r = json.loads(line)
    if r.get('script_class') != 'greek_poly':
        continue
    n_lines += 1
    G, M = nfd(r['gt']), nfd(r['prediction'])
    for g, m in pair_tokens(G, M):
        if m is None or strip_marks(g.core) != strip_marks(m.core):
            continue
        for a, d in zip(clusters(g.core), clusters(m.core)):
            if a.base in MARK_BEARERS:
                n_cl += 1; n_cl_agree += a.marks == d.marks
print('v2_test polytonic lines', n_lines, 'mark-bearing clusters (same letters)', n_cl, 'agreeing', n_cl_agree, 'per line', round(n_cl_agree / max(1, n_lines), 2))
