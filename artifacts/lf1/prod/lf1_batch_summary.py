import json,glob,collections,sys
pre=sys.argv[1]
L=[r for r in json.load(open('artifacts/lf1/ledger.json')) if r['context'].startswith(pre)]
last={}
for r in L: last[r['context']]=r
V={}
for c,r in last.items():
    p=f"artifacts/lf1/runs/{c}.attempt{r['attempt']}/verdicts.jsonl"
    if r["status"]!="VALID": continue
    for l in open(p):
        x=json.loads(l);V[(c,x['card_id'])]=x
v3={json.loads(l)['row_id']:json.loads(l) for l in open('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/bench02/census05/candidates_v3.jsonl')}
cls=collections.defaultdict(lambda:[0,0]);vc=collections.Counter();rs=collections.Counter();ctl=[0,0];bad=[];sc=collections.defaultdict(lambda:[0,0]);miss=0
for f in sorted(glob.glob(f'artifacts/lf1/keys/{pre}*.json')):
    ctx=f.split('/')[-1][:-5]
    for cid,k in json.load(open(f))['items'].items():
        r=V.get((ctx,cid))
        if r is None: miss+=1;continue
        if k['control']:
            e=k['expected'];g=r['verdict']==e['verdict'] and set(e.get('reasons',[]))<=set(r.get('reasons') or [])
            ctl[0]+=g;ctl[1]+=1
            if not g: bad.append((ctx,k['pool_id'],r['verdict'],r.get('reasons')))
            continue
        fl=r['verdict']!='OK';vc[r['verdict']]+=1
        for x in r.get('reasons') or []: rs[x]+=1
        c=k['draw_class'];cls[c][0]+=fl;cls[c][1]+=1
        s='in_quota' if v3[k['row_id']]['in_quota'] else 'reserve';sc[s][0]+=fl;sc[s][1]+=1
print('contexts',len(last),dict(collections.Counter(r['status'] for r in last.values())),'attempts',len(L),'VOID attempts',[(r['context'],r['attempt']) for r in L if r['status']!='VALID'])
print('missing',miss,'verdicts',dict(vc),'reasons',dict(rs))
print('controls',ctl,bad)
print(', '.join(f'{c} {a}/{b}' for c,(a,b) in sorted(cls.items())))
print({s:f'{a}/{b}' for s,(a,b) in sc.items()})
tot=sum(r['run']['usage']['total_tokens'] for r in L if r.get('run',{}).get('usage'));ca=sum(r['run']['usage'].get('cached_input_tokens',0) for r in L if r.get('run',{}).get('usage'))
cards=sum(r['cards'] for r in last.values())
print('tokens',tot,'cached%',round(100*ca/tot),'per100',round(tot/cards*100),'weekly',min(r['before']['weekly_used'] for r in L),max(r.get('after',{}).get('weekly_used',0) for r in L))
