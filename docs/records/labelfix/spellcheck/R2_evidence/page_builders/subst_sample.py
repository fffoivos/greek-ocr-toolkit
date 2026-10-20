import gzip, json, unicodedata as ud, random, collections
B='/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/'
sel={}
for l in open(B+'artifacts/labelfix_l1/binding/selection.jsonl'):
    r=json.loads(l); sel[r['id']]=r
ACC={'́':'acute','̀':'grave','͂':'circumflex'}; BR={'̓':'psili','̔':'dasia'}
FAM={'acute':'accent','grave':'accent','circumflex':'accent','psili':'breathing','dasia':'breathing'}
def letters(t):
    out=[]
    for ch in ud.normalize('NFD', t):
        if ud.category(ch).startswith('M'):
            if out: out[-1][1].append(ch)
        elif ch.isalpha(): out.append([ch,[]])
    return out
pool=collections.defaultdict(list)
for l in gzip.open(B+'l1e_20261017/l1r_sf6_3680729/release/overlay_ensemble_ab.jsonl.gz','rt'):
    r=json.loads(l); s=sel[r['line_id']]
    G=letters(s['label']); gd=sorted(r['gate_decisions'], key=lambda g:g['start'])
    if len(G)!=len(gd) or any(a[0].lower()!=g['base'].lower() for a,g in zip(G,gd)): continue
    con=[]
    for i,((base,marks),g) in enumerate(zip(G,gd)):
        A=g.get('r1_parts'); Bp=(g.get('peer_prediction') or {}).get('parts')
        if A is None or Bp is None or sorted(A)!=sorted(Bp): continue
        gm={FAM[x]:x for x in [ACC.get(m) or BR.get(m) for m in marks] if x}
        pm={FAM[x]:x for x in A if x in FAM}
        for fam in ('accent','breathing'):
            if fam in gm and fam in pm and gm[fam]!=pm[fam]:
                ink=bool(g['evidence']['above']); det=pm[fam] in (g.get('detector_parts') or [])
                tier='agree' if ink and det else ('other' if ink else 'noink')
                con.append(dict(letter=i, fam=fam, google=gm[fam], ours=pm[fam], tier=tier, det=g.get('detector_parts') or []))
    if not con: continue
    tiers={c['tier'] for c in con}
    t='agree' if tiers=={'agree'} else ('noink' if 'noink' in tiers else 'other')
    slots=[dict(base=g['base'], body=g['evidence'].get('body'), above=[b['bbox'] for b in g['evidence']['above']],
                below=[b['bbox'] for b in g['evidence']['below']]) for g in gd]
    pool[t].append(dict(line_id=r['line_id'], wave=s['wave'], crop=s['crop'], label=s['label'], status=r['status'], con=con, slots=slots))
rng=random.Random(20261017); out={}
for t,v in pool.items():
    rng.shuffle(v); out[t]=v[:20]
print(json.dumps(dict(sizes={t:len(v) for t,v in pool.items()}, sample=out), ensure_ascii=False))
