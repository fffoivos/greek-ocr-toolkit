import json, statistics as st, collections, sys
rows=[json.loads(l) for l in open(sys.argv[1])]
print(len(rows),'lines | original box keeps median %.3f' % st.median(r['orig_keep'] for r in rows))
for mode in ('curve','box'):
    ok=[r for r in rows if 'keep' in r.get(mode,{})]
    errs=collections.Counter(r[mode].get('err') for r in rows if 'err' in r.get(mode,{}))
    if not ok: print(mode, 'errors', errs); continue
    k=sorted(r[mode]['keep'] for r in ok); f=sorted(r[mode]['foreign'] for r in ok)
    ol=max(r[mode]['over_l'] for r in ok); orr=max(r[mode]['over_r'] for r in ok)
    print('%-5s ok %d err %d | keep median %.3f p10 %.3f min %.3f | foreign median %.3f p90 %.3f max %.3f | keep<.95: %d foreign>.02: %d | overshoot max L %.1f R %.1f xh' % (
        mode, len(ok), sum(errs.values()), st.median(k), k[len(k)//10], k[0], st.median(f), f[int(.9*len(f))], f[-1],
        sum(x<.95 for x in k), sum(x>.02 for x in f), ol, orr))
