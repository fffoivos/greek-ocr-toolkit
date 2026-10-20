import gzip, json, unicodedata as ud, collections, sys
B='/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/'
sel={}
for l in open(B+'artifacts/labelfix_l1/binding/selection.jsonl'):
    r=json.loads(l); sel[r['id']]=(r['label'], r['wave'])
ACC={'́':'acute','̀':'grave','͂':'circumflex'}; BR={'̓':'psili','̔':'dasia'}
FAM={'acute':'accent','grave':'accent','circumflex':'accent','psili':'breathing','dasia':'breathing'}
def letters(t):
    out=[]
    for ch in ud.normalize('NFD', t):
        if ud.category(ch).startswith('M'):
            if out: out[-1][1].append(ch)
        elif ch.isalpha(): out.append([ch,[]])
    return out
T=collections.Counter(); W=collections.defaultdict(collections.Counter); lines=collections.defaultdict(set); ex=collections.defaultdict(list)
n=aligned=0
for l in gzip.open(B+'l1e_20261017/l1r_sf6_3680729/release/overlay_ensemble_ab.jsonl.gz','rt'):
    r=json.loads(l); n+=1
    lab,wave=sel[r['line_id']]
    G=letters(lab); gd=sorted(r['gate_decisions'], key=lambda g:g['start'])
    if len(G)!=len(gd) or any(a[0].lower()!=g['base'].lower() for a,g in zip(G,gd)): continue
    aligned+=1
    for (base,marks),g in zip(G,gd):
        A=g.get('r1_parts'); Bp=(g.get('peer_prediction') or {}).get('parts')
        if A is None or Bp is None or sorted(A)!=sorted(Bp): continue
        gm={FAM[x]:x for x in [ACC.get(m) or BR.get(m) for m in marks] if x}
        pm={FAM[x]:x for x in A if x in FAM}
        for fam in ('accent','breathing'):
            if fam in gm and fam in pm and gm[fam]!=pm[fam]:
                ink=bool(g['evidence']['above']); det=pm[fam] in (g.get('detector_parts') or [])
                tier='reader only' if not ink else ('reader + ink, detector names it' if det else 'reader + ink, detector names other/none')
                key=(fam, gm[fam]+'->'+pm[fam], tier)
                T[key]+=1; W[wave][tier]+=1; lines[tier].add(r['line_id'])
                if len(ex[tier])<6: ex[tier].append((r['line_id'], gm[fam]+'->'+pm[fam], ud.normalize('NFC', lab)[:70]))
print('records', n, 'letter-aligned', aligned)
tot=collections.Counter()
for (fam,ch,tier),v in T.items(): tot[tier]+=v
for t,v in tot.items(): print('TIER', t, 'slots', v, 'lines', len(lines[t]))
for k,v in sorted(T.items(), key=lambda x:-x[1])[:25]: print(k,v)
for w,c in sorted(W.items()): print('WAVE', w, dict(c))
for t,e in ex.items():
    for x in e: print('EX', t, x)
