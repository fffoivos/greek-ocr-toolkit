"""Local CPU readback digest. No inference, network, submission or git mutation."""
from collections import Counter, defaultdict
import json
from pathlib import Path
import numpy as np
from scripts.labelfix.clariden.r1_common import HEADS, rows, sha256
from scripts.labelfix.clariden.r2a_run import witness_comparison
from scripts.labelfix import r2_score

ROOT=Path('artifacts/labelfix_r2/output_3683130')
OUT=Path('docs/labelfix/spellcheck/R2')
E=OUT/'evidence/r2a'
ARMS=['A16','BASEs17','BASEs18','R2a20261016','R2a20261017','R2a20261018']
PAIRS=list(zip(ARMS[:3],ARMS[3:]))
REPS=50000
SEED=20261017
TARGET={'capitals','omicron_monotonic','subscript'}

def dump(name,obj):
    (E/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n')

def ratio(a,b):return float(a/b) if b else None

def assert_close(a,b):
    if isinstance(a,dict):
        assert a.keys()==b.keys()
        for k in a:assert_close(a[k],b[k])
    elif isinstance(a,(int,float)) and isinstance(b,(int,float)):
        assert np.isclose(a,b,rtol=1e-12,atol=1e-10),(a,b)
    else:assert a==b,(a,b)

def table(headers,rs):
    return ['| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|']+['| '+' | '.join(map(str,r))+' |' for r in rs]

def fmt(x):return 'undefined' if x is None else f'{x:.3f}'

def pct(x):return fmt(None if x is None else 100*x)

def witness_union(rr):
    # Deduplicate overlapping cards within a slice by physical slot. Keep ambiguous
    # starts as separate UNKNOWN witnesses, never manufacture slot identities.
    seen={};out=[]
    for r in rr:
        if r['control']:continue
        key=(r['line_id'],r['start'],r['slice']) if r['start'] is not None else (r['card_id'],r['letter_index'])
        if key in seen:
            assert seen[key]['truth']==r['truth'] and seen[key]['prediction']==r['prediction']
            continue
        seen[key]=r
        out.append(dict(r,id=str(key),inclusion_weight=1.,inserted_prediction=False,coverage=r['prediction'] is not None,
            localisation=False,fused=False,clipped=False,unmatched_print=False,
            unknown=list(HEADS) if r['prediction'] is None else r['unknown'],prediction=r['prediction'] or [0]*4))
    return out

def paired_slots(a,b):
    aa={r['id']:r for r in a};bb={r['id']:r for r in b};assert aa.keys()==bb.keys()
    out=[]
    for k,x in aa.items():
        y=bb[k];assert x['truth']==y['truth'] and x['unknown']==y['unknown']
        if x['prediction']!=y['prediction']:
            known=[h for h,n in enumerate(HEADS) if n not in x['unknown']]
            ar=all(x['truth'][h]==x['prediction'][h] for h in known);br=all(y['truth'][h]==y['prediction'][h] for h in known)
            out.append(dict(id=k,line_id=x['line_id'],doc=x['doc'],slice=x.get('slice'),base=x['base'],truth=x['truth'],
                unknown=x['unknown'],old=x['prediction'],new=y['prediction'],
                direction='UNKNOWN' if not known else 'regression' if ar and not br else 'recovery' if br and not ar else 'both_wrong_changed',
                head_regressions=[n for h,n in enumerate(HEADS) if h in known and x['prediction'][h]==x['truth'][h]!=y['prediction'][h]],
                disposition='observed model regression; retained, not waived' if ar and not br else 'retained paired change'))
    return out

def counts_by_doc(a,b,h=None,value=None):
    aa={r['id']:r for r in a};bb={r['id']:r for r in b};assert aa.keys()==bb.keys()
    d=defaultdict(lambda:np.zeros(6))
    for k,x in aa.items():
        y=bb[k];assert x['truth']==y['truth']
        for j,n in enumerate(HEADS):
            if h is not None and j!=h:continue
            if n in x['unknown'] or n in y['unknown']:continue
            for v in ([value] if value is not None else range(1,len(HEADS[n]))):
                t=x['truth'][j]==v;p=x['prediction'][j]==v;q=y['prediction'][j]==v;w=x['inclusion_weight']
                d[x['doc']]+=w*np.array([t and p,not t and p,t and not p,t and q,not t and q,t and not q])
    return np.asarray(list(d.values()))

def noninfer(a,b,label,h=None,value=None):
    v=counts_by_doc(a,b,h,value);total=v.sum(0)
    rng=np.random.default_rng(SEED)
    # Multinomial counts resample whole documents, preserving paired arms and seeds.
    weights=rng.multinomial(len(v),np.full(len(v),1/len(v)),size=REPS)
    draws=weights@v
    out=[]
    for metric,den,margin in [('P',1,-.20),('R',2,-.50)]:
        old=ratio(total[0],total[0]+total[den]);new=ratio(total[3],total[3]+total[den+3]);delta=None if old is None or new is None else 100*(new-old)
        ok=(draws[:,0]+draws[:,den]>0)&(draws[:,3]+draws[:,den+3]>0)
        dd=100*(draws[ok,3]/(draws[ok,3]+draws[ok,den+3])-draws[ok,0]/(draws[ok,0]+draws[ok,den]))
        errors=dd-delta if delta is not None else np.array([])
        p=(1+np.sum(errors>=delta-margin))/(len(errors)+1) if len(errors) else 1.
        out.append(dict(label=label,metric=metric,support=float(total[0]+total[2]),old=old,new=new,delta_pp=delta,margin_pp=margin,
            documents=len(v),defined_bootstrap=len(errors),p_noninfer=float(p),_errors=errors,
            ci95_pp=[float(delta-np.quantile(errors,.975)),float(delta-np.quantile(errors,.025))] if len(errors) else None))
    return out

def holm(tests):
    ordered=sorted(tests,key=lambda t:t['p_noninfer']);m=len(ordered);active=True;adjusted=0.
    for rank,t in enumerate(ordered):
        threshold=.05/(m-rank);adjusted=max(adjusted,min(1.,t['p_noninfer']*(m-rank)))
        errors=t.pop('_errors');delta=t['delta_pp']
        lb=float(delta-np.quantile(errors,1-threshold)) if len(errors) else None
        ub=float(delta-np.quantile(errors,.05/m)) if len(errors) else None
        t.update(holm_rank=rank+1,holm_family_size=m,holm_alpha=threshold,holm_p=adjusted,holm_lower_pp=lb,simultaneous_upper_pp=ub)
        passed=active and t['p_noninfer']<threshold and lb is not None and lb>t['margin_pp']
        if not passed:active=False
        t['verdict']='PASS' if passed else 'FAIL' if ub is not None and ub<=t['margin_pp'] else 'INCONCLUSIVE'
    return tests

def pool(cohort,names,data):return [dict(r,id=str(i)+':'+r['id']) for i,n in enumerate(names) for r in data[n][cohort]]

def main():
    receipt=json.loads((ROOT/'READBACK_RECEIPT.json').read_text());assert not receipt['failures'] and receipt['sha256_verified']==receipt['file_count']
    for f in receipt['files']:assert sha256(ROOT/f['path'])==f['sha256']
    overlay=json.loads((OUT/'truth_overlay_v1_1.json').read_text())
    scoring=json.loads((ROOT/'D/scoring_receipt.json').read_text());assert scoring['heldout_overlay_sha256']==sha256(OUT/'truth_overlay_v1_1.json')
    data={a:{c:list(rows(ROOT/'D'/a/(c+'_ledger.jsonl.gz'))) for c in ['heldout','witness','dev']} for a in ARMS}
    # Independently rescore saved held-out predictions, including symmetric overlay.
    truth=[l for l in r2_score.truth_lines('docs/labelfix/spellcheck/S4_lines.jsonl.gz') if not l['dev']]
    assert len(truth)==666
    truth,overlay_result=r2_score.apply_overlay(truth,overlay)
    metadata={r['id']:r for r in rows('tests/labelfix/fixtures/r2/heldout_lines.jsonl.gz')}
    for a in ARMS:
        pp=list(rows(ROOT/'D'/a/'heldout_predictions.jsonl'))
        coverage={lid:{c['start']:c for c in m['coverage']} for lid,m in metadata.items()}
        for p in pp:p['coverage']=coverage[p['line_id']][p['start']]
        ll=r2_score.union_records(truth,pp)
        assert ll==data[a]['heldout'],a+' rescore differs'
        for c in ['heldout','dev']:
            assert_close(r2_score.summarize(data[a][c]),json.loads((ROOT/'D'/a/(c+'_scores.json')).read_text())['micro'])
        for r in data[a]['heldout']+data[a]['dev']:
            if r['inserted_prediction']:assert r['truth']==[None]*4 and set(r['unknown'])==set(HEADS)
    dump('r2rb2_rescore.json',dict(arms=ARMS,heldout_lines=666,overlay=overlay_result,overlay_sha256=sha256(OUT/'truth_overlay_v1_1.json'),exact_ledger_reproduction=True,inserted_slots='UNKNOWN'))
    targets={};changes={};wu={a:witness_union(data[a]['witness']) for a in ARMS}
    for old,new in PAIRS:
        s=new[-2:];targets[s]=witness_comparison(data[old]['witness'],data[new]['witness'],REPS)
        changes[s]={c:paired_slots(data[old][c],data[new][c]) for c in ['heldout','dev']}
        changes[s]['witness']=paired_slots(wu[old],wu[new])
    # Pool seed observations while retaining the original document as the cluster.
    pooled_old=[];pooled_new=[]
    for old,new in PAIRS:
        pooled_old += [dict(r,card_id=old+':'+r['card_id']) for r in data[old]['witness']]
        pooled_new += [dict(r,card_id=old+':'+r['card_id']) for r in data[new]['witness']]
    targets['pooled']=witness_comparison(pooled_old,pooled_new,REPS)
    # Add percentage reduction bootstrap, not just absolute-count interval.
    for s,z in targets.items():
        docs=defaultdict(lambda:np.zeros(2))
        for r in z['ledger']:
            if r['truth']==0:docs[r['doc']]+=np.array([r['old']!=0,r['new']!=0])
            else:docs[r['doc']]+=0
        v=np.asarray(list(docs.values()));rng=np.random.default_rng(SEED)
        draws=rng.multinomial(len(v),np.full(len(v),1/len(v)),size=REPS)@v
        valid=draws[:,0]>0;red=(draws[valid,0]-draws[valid,1])/draws[valid,0]
        z['reduction_ci95']=np.quantile(red,[.025,.975]).tolist();z['reduction_defined_replicates']=int(valid.sum())
        z['positive_slices']={}
        for sl in TARGET:
            rr=[r for r in z['ledger'] if r['slice']==sl and r['truth']!=0]
            z['positive_slices'][sl]=dict(support=len(rr),old_correct=sum(r['old']==r['truth'] for r in rr),new_correct=sum(r['new']==r['truth'] for r in rr),
                old_recall=ratio(sum(r['old']==r['truth'] for r in rr),len(rr)),new_recall=ratio(sum(r['new']==r['truth'] for r in rr),len(rr)))
    dump('r2rb2_target.json',targets);dump('r2rb2_paired_slots.json',changes)
    comparisons=PAIRS+[('pooled','pooled')];common=[];sparse=[];nt=[]
    for old,new in comparisons:
        label=new[-2:] if new!='pooled' else 'pooled'
        aa=pool('heldout',ARMS[:3],data) if old=='pooled' else data[old]['heldout']
        bb=pool('heldout',ARMS[3:],data) if new=='pooled' else data[new]['heldout']
        for h,(name,values) in enumerate(HEADS.items()):
            for value in range(1,len(values)):
                support=sum(r['truth'][h]==value and name not in r['unknown'] for r in data[ARMS[0]]['heldout'])
                tests=noninfer(aa,bb,label+'/'+name+'/'+values[value],h,value)
                if support>=200:common+=tests
                else:
                    sparse.append(dict(comparison=label,head=name,value=values[value],support_per_seed=support,verdict='unestablished',
                        old_errors=sum(t['fp']+t['fn'] for t in [r2_score.summarize(aa)['heads'][name]['values'][values[value]]]),
                        new_errors=sum(t['fp']+t['fn'] for t in [r2_score.summarize(bb)['heads'][name]['values'][values[value]]])))
        for sl in sorted(set(r['slice'] for r in wu[ARMS[0]])-TARGET):
            aa=[dict(r,id=str(i)+':'+r['id']) for i,a in enumerate(ARMS[:3] if old=='pooled' else [old]) for r in wu[a] if r['slice']==sl]
            bb=[dict(r,id=str(i)+':'+r['id']) for i,a in enumerate(ARMS[3:] if new=='pooled' else [new]) for r in wu[a] if r['slice']==sl]
            nt+=noninfer(aa,bb,label+'/'+sl)
    common=holm(common);nt=holm(nt)
    dump('r2rb2_noninferiority.json',dict(common=common,sparse=sparse,non_target=nt,replicates=REPS,seed=SEED,
        method='paired document cluster bootstrap; basic one-sided bounds; null-centered bootstrap p-values; Holm step-down over all seed and pooled endpoints within each protection family; undefined denominators excluded and counted'))
    ownerfiles=[Path('docs/labelfix/spellcheck')/p for p in ['owner_slot_expectations.jsonl','owner_examples_expectations.jsonl','S5_review_expectations.jsonl','owner_notes_db_20261016.jsonl','owner_notes_examples_20261016.jsonl','owner_notes_review_v16_20261016.jsonl','owner_notes_examples_v10_20261016.jsonl']]
    ownerlines={r['line_id'] for p in ownerfiles for r in rows(p) if 'line_id' in r}
    owner={s:[r for r in c['heldout'] if r['line_id'] in ownerlines and (r['direction']=='regression' or r['head_regressions'])] for s,c in changes.items()}
    named_owner_slots={f"{r['line_id']}:s{r.get('mapped_slot',r['slot'])}" for r in rows(ownerfiles[0])}
    for rr in owner.values():
        for r in rr:r['named_owner_slot']=r['id'] in named_owner_slots
    dump('r2rb2_owner_regressions.json',dict(scope='all known held-out slots on any owner-note line, a conservative superset of named owner slots',sources={str(p):sha256(p) for p in ownerfiles},owner_line_ids=sorted(ownerlines),regressions=owner,
        outside_heldout=sorted(ownerlines-set(metadata)),disposition='all listed regressions retained, no new visual adjudication or waiver'))
    # S8 item accuracy alongside weighted union-slot accuracy. Preserve all census states.
    states={a:list(rows(ROOT/'D'/a/'dev_item_states.jsonl')) for a in ARMS};assert all(v==states[ARMS[0]] for v in states.values())
    assert len(states[ARMS[0]])==1793
    dev={};itemledgers={}
    for a in ARMS:
        by=defaultdict(list)
        for r in data[a]['dev']:by[r['line_id']].append(r)
        items=[]
        for item in states[a]:
            rr=by[item['id']];known=[r for r in rr if not r['unknown']]
            status='excluded_control' if item['control'] else 'excluded_unresolved' if item['status']!='resolved' or item['truth'] is None else 'scored' if known else 'unscored'
            correct=all(r['truth']==r['prediction'] for r in known) if known else None
            items.append(dict(item,score_status=status,known_slots=len(known),unknown_slots=len(rr)-len(known),correct=correct,
                doc=rr[0]['doc'] if rr else None))
        eligible=[r for r in items if r['score_status']=='scored']
        dev[a]=dict(states=dict(Counter(r['score_status'] for r in items)),items_correct=sum(r['correct'] for r in eligible),items=len(eligible),
            item_accuracy=ratio(sum(r['correct'] for r in eligible),len(eligible)),weighted_item_accuracy=ratio(sum(r['weight']*r['correct'] for r in eligible),sum(r['weight'] for r in eligible)),
            union=r2_score.summarize(data[a]['dev'])['composed_tuple'],waves={w:dict(n=sum(r['wave']==w for r in eligible),correct=sum(r['correct'] for r in eligible if r['wave']==w)) for w in {r['wave'] for r in eligible}})
        itemledgers[a]=items
    devpaired={}
    for old,new in PAIRS:
        paired=[];docs=defaultdict(lambda:np.zeros(2))
        for x,y in zip(itemledgers[old],itemledgers[new]):
            assert x['id']==y['id'] and x['score_status']==y['score_status']
            if x['score_status']!='scored':continue
            delta=int(y['correct'])-int(x['correct']);docs[x['doc']]+=np.array([delta*x['weight'],x['weight']])
            if delta:paired.append(dict(id=x['id'],line_id=x['line_id'],doc=x['doc'],weight=x['weight'],old_correct=x['correct'],new_correct=y['correct']))
        v=np.asarray(list(docs.values()));rng=np.random.default_rng(SEED);d=rng.multinomial(len(v),np.full(len(v),1/len(v)),size=REPS)@v
        devpaired[new[-2:]]=dict(item_changes=paired,weighted_item_delta=ratio(v[:,0].sum(),v[:,1].sum()),ci95=np.quantile(d[:,0]/d[:,1],[.025,.975]).tolist(),
            recoveries=sum(not r['old_correct'] for r in paired),regressions=sum(r['old_correct'] for r in paired))
    dump('r2rb2_dev_items.json',itemledgers);dump('r2rb2_dev_summary.json',dict(arms=dev,paired=devpaired,census_lines=600,census_items=1793))
    metrics={}
    for a in ARMS:
        m=r2_score.summarize(data[a]['heldout'])['atomic'];p=m['precision'];r=m['recall'];metrics[a]=dict(P=100*p,R=100*r,F1=200*p*r/(p+r))
    spread={k:max(metrics[a][k] for a in ARMS[3:])-min(metrics[a][k] for a in ARMS[3:]) for k in ['P','R','F1']}
    churn={s:{sl:sum(r['slice']==sl for r in c['witness']) for sl in sorted({r['slice'] for r in wu[ARMS[0]]})} for s,c in changes.items()}
    dump('r2rb2_spread_churn.json',dict(heldout=metrics,r2a_spread_pp=spread,job1_base_spread_pp=dict(P=.13,R=.54,F1=.35),witness_churn_by_slice=churn,
        heldout_churn={s:len(c['heldout']) for s,c in changes.items()},dev_churn={s:len(c['dev']) for s,c in changes.items()}))
    def verdict(ts):return 'FAIL' if any(t['verdict']=='FAIL' for t in ts) else 'PASS' if all(t['verdict']=='PASS' for t in ts) else 'INCONCLUSIVE'
    cv=verdict(common);nv=verdict(nt);sv='FAIL' if any(r['new_errors']>r['old_errors'] for r in sparse) else 'INCONCLUSIVE'
    ov='FAIL' if any(r['named_owner_slot'] for rr in owner.values() for r in rr) else 'INCONCLUSIVE' if ownerlines-set(metadata) else 'PASS'
    z=targets['pooled'];reduction=z['false_addition_reduction'];benefit=sum(targets[s]['counts']['new_false_additions']<targets[s]['counts']['old_false_additions'] for s in ['16','17','18'])
    positive=all(v['new_correct']>=v['old_correct'] for s in ['16','17','18'] for v in targets[s]['positive_slices'].values())
    tv='PASS' if reduction is not None and reduction>=.3 and z['net_fewer_wrong']>=5 and z['net_fewer_wrong_document_ci95'][0]>0 and z['reduction_ci95'][0]>0 and benefit>=2 and positive else 'FAIL'
    final='FAIL' if 'FAIL' in [tv,cv,nv,sv,ov] else 'PASS' if all(v=='PASS' for v in [tv,cv,nv,sv,ov]) else 'INCONCLUSIVE'
    L=[receipt['coordinator_accepted_deviation'],'','# R2a digest — job 3683130','',
       'Job COMPLETED, exit 0:0; Slurm elapsed 23:29. The log ends with STAGE_DONE C and STAGE_DONE D. Readback finished '+receipt['pull_end_time']+'. '+str(receipt['file_count'])+' files / '+str(receipt['total_bytes'])+' bytes verified; 153 stage-bound and seven remote-envelope-bound. No crops, arrays, windows or shards were pulled. The archived failed first run was not read or scored.',
       '', 'The branch is `opus/r2-prep`. Package verifier binds commit `ee9d7a9757fe8f9b9e2bf50ee299cb587c246c72`; current checkout HEAD is `5080db4a80b00d138e4ff333cae0d862b4ea61c4` (later lead history; `a0ec0c1f4` is the accepted VERIFY_OK receipt commit). No git writes, certificate refresh, inference or submission in this readback.',
       '', 'Scorer: R2S, inserted recogniser slots UNKNOWN. Overlay v1.1 is applied symmetrically; local regeneration reproduces all six held-out ledgers exactly. Saved DEV ledgers independently reproduce their score summaries. Six arms: R1-A s16, BASE s17/s18, R2a s16/s17/s18. “BASE” pooled below uses R1-A as the seed-16 baseline, not a newly trained BASE s16.',
       '', '## (a) Timings','']
    ts=[json.loads((ROOT/f'stage_{s}.json').read_text())['elapsed_seconds']/60 for s in 'ABCD']
    L+=table(['Stage','Actual min','Forecast min','Actual − forecast min'],[[s,fmt(v),f,fmt(v-f) if f else 'not separately forecast'] for s,v,f in zip('ABCD',ts,[0,15.9,17.5,20])])
    L+=['',f'Stage total {sum(ts):.3f} min; Slurm {1409/60:.3f} min versus 53.4 min forecast ({1409/60-53.4:.3f} min, {100*(1-1409/60/53.4):.1f}% shorter). Stage A receipt times the post-validation closure (approximately zero), not complete startup/validation. Unattributed Slurm/startup overhead: {1409/60-sum(ts):.3f} min. Forecast components are rounded (sum 53.4 min).',
        '', '## (b) Target witnesses','', 'Anchor target heads only, noncontrol T4 capitals / omicron_monotonic / subscript. Unknown truth or missing/ambiguous predictions remain excluded and counted. Pooled totals are seed-observations, not three times as many independent witnesses. Document resampling keeps all seeds for the same document together. Fifty thousand bootstrap replicates; fixed seed 20261017. Both absolute false-addition reduction and percentage reduction intervals are reported.','']
    L+=table(['Pair','Known / UNKNOWN','False additions BASE → R2a','Reduction % [95% CI]','Wrong BASE → R2a','False-addition count reduction CI','Net fewer wrong [95% CI]'],[[s,f"{t['counts']['known']} / {t['counts'].get('unknown',0)}",f"{t['counts']['old_false_additions']} → {t['counts']['new_false_additions']}",f"{pct(t['false_addition_reduction'])} [{pct(t['reduction_ci95'][0])}, {pct(t['reduction_ci95'][1])}]",f"{t['counts']['old_wrong']} → {t['counts']['new_wrong']}",t['false_additions_document_ci95'],f"{t['net_fewer_wrong']} {t['net_fewer_wrong_document_ci95']}"] for s,t in targets.items()])
    L+=['','Per-slice negatives and positive exact-target recall:','']
    L+=table(['Pair','Slice','Negative / positive','False additions BASE → R2a','Positive correct BASE → R2a','Recall % BASE → R2a'],[[s,sl,f"{v['negative']} / {v['positive']}",f"{v['old_false_additions']} → {v['new_false_additions']}",f"{t['positive_slices'][sl]['old_correct']} → {t['positive_slices'][sl]['new_correct']}",f"{pct(t['positive_slices'][sl]['old_recall'])} → {pct(t['positive_slices'][sl]['new_recall'])}"] for s,t in targets.items() for sl,v in t['by_slice'].items()])
    L+=['',f'False-addition benefit occurs in {benefit}/3 seeds; mean count reduction {(z["counts"]["old_false_additions"]-z["counts"]["new_false_additions"])/3:.3f} per seed. Only seed 17 reaches the 30% threshold. Positive slice recall is nondecreasing in every seed: {positive}; individual positive regressions remain in the paired ledger. Target verdict **{tv}**: pooled reduction is below 30%, and its interval includes no improvement. Net wrong-slot improvement alone does not pass the target criterion.',
        '', '## (c) Common-class noninferiority','', 'Exact named one-vs-rest head classes with ≥200 printed positive slots per seed. Paired document bootstrap, original weights retained. Basic one-sided bounds and null-centered bootstrap p-values, Holm step-down over all seed and pooled P/R endpoints in this family. P margin −0.20 pp; R margin −0.50 pp. Holm lower bounds are at the displayed step alpha; after a step fails, later steps cannot pass. FAIL requires a simultaneous Bonferroni upper bound at or below the margin; other unproven rows are INCONCLUSIVE. Bootstrap inference is approximate; undefined resampled denominators are excluded and recorded.','']
    def nirows(tests):return [[t['label'],t['metric'],int(t['support']),pct(t['old']),pct(t['new']),fmt(t['delta_pp']),fmt(t['holm_lower_pp']),fmt(t['simultaneous_upper_pp']),fmt(t['holm_p']),t['verdict']] for t in tests]
    headers=['Pair/class or slice','Metric','Support','BASE %','R2a %','Δ pp','Holm lower pp','Simultaneous upper pp','Holm p','Verdict']
    L+=table(headers,nirows(common))
    L+=['',f'Common-class verdict **{cv}**.','', 'Sparse classes remain **unestablished**, including after seed pooling. Exact-name errors count FP + FN; a wrong-name substitution can count twice. Every changed paired slot, including each head regression, is in [paired ledgers](evidence/r2a/r2rb2_paired_slots.json).','']
    L+=table(['Pair','Class','Support/seed','Errors BASE → R2a','Status'],[[r['comparison'],r['head']+'/'+r['value'],r['support_per_seed'],f"{r['old_errors']} → {r['new_errors']}",r['verdict']] for r in sparse])
    L+=['','Every sparse-class paired regression (exact-name correctness lost; no waiver):','']
    L+=table(['Seed','Class','Line / slot','Truth','BASE → R2a'],[[seed,name+'/'+HEADS[name][v],r['id'],r['truth'],f"{r['old']} → {r['new']}"] for seed,c in changes.items() for r in c['heldout'] for h,name in enumerate(HEADS) for v in range(1,len(HEADS[name])) if name in ['dialytika','subscript'] and name not in r['unknown'] and ((r['truth'][h]==v)==(r['old'][h]==v)) and ((r['truth'][h]==v)!=(r['new'][h]==v))])
    L+=['',f'Sparse protection verdict **{sv}**; no adoption from sparse evidence.','', '## (d) Non-target and owner protection','', 'Random, specks and exact_names T4 slices: exact named-head micro P/R, paired by physical slot within each slice (overlapping cards deduplicated). Same margins; one Holm family over the three slices × four comparisons × two metrics. Original per-seed positive supports are only 114, 144 and 171; these slices remain unestablished despite larger pooled observation counts. Full churn and every paired regression are retained, including regressions that a net count would hide.','']
    L+=table(headers,nirows(nt));L+=['',f'Non-target margin verdict **{nv}**.','',f'Owner-note protection verdict **{ov}**. Conservative scope: every known held-out slot on any owner-note line from seven frozen note files, rather than only the named owner slots. Every paired regression on that superset is shown below, including a head lost while another head improves. Disposition: observed regression retained, not waived; no new print adjudication. The FAIL is supported by the explicitly named preserved slot `602cc72e-p000167-l0027:s10`: seed 18 changes correct grave-only to psili+grave. Other regressions in the broader line scope are also retained. Missing owner lines remain unestablished; see [owner ledger](evidence/r2a/r2rb2_owner_regressions.json).','']
    L+=table(['Seed','Line id / slot','Truth','BASE → R2a','Head regressions','Named owner slot','Disposition'],[[s,r['id'],r['truth'],f"{r['old']} → {r['new']}",','.join(r['head_regressions']),r['named_owner_slot'],'retained; not waived'] for s,rr in owner.items() for r in rr])
    L+=['','## (e) DEV','', 'S8 census: 600 lines, 1,793 items. Controls and unresolved truth excluded from accuracy, with all item states retained. “Item accuracy” means all known union slots correct for a resolved noncontrol item; UNKNOWN slots are excluded, so this is mark accuracy conditional on known aligned truth, not whole OCR transcription accuracy. Weighted figures retain S8 inclusion weights.','']
    L+=table(['Arm','Correct / scored items','Item accuracy %','Weighted item %','Weighted slot %','Exclusions'],[[a,f"{v['items_correct']} / {v['items']}",pct(v['item_accuracy']),pct(v['weighted_item_accuracy']),pct(v['union']['accuracy_all']),v['states']] for a,v in dev.items()])
    L+=['','Paired item results (R2a − baseline), clustered by original document:','']
    L+=table(['Seed','Recoveries / regressions','Weighted Δ pp','95% CI pp'],[[s,f"{v['recoveries']} / {v['regressions']}",pct(v['weighted_item_delta']),[round(100*x,4) for x in v['ci95']]] for s,v in devpaired.items()])
    L+=['','The closing DEV figure is the mean weighted item accuracy across the three paired seeds (96.594% → 96.771%). All 1,793 per-arm item states, wave counts and paired per-item changes are in [DEV items](evidence/r2a/r2rb2_dev_items.json) and [DEV summary](evidence/r2a/r2rb2_dev_summary.json). No prospective DEV noninferiority margin was specified, so DEV is descriptive and does not independently authorize adoption.','', '## (f) Seed spread and churn','']
    L+=table(['Arm','Held-out P %','R %','F1 %'],[[a]+[fmt(metrics[a][k]) for k in ['P','R','F1']] for a in ARMS])
    L+=['']
    L+=table(['Metric','R2a max−min pp','Job-1 BASE spread pp'],[[k,fmt(spread[k]),b] for k,b in zip(['P','R','F1'],[.13,.54,.35])])
    L+=['','The comparison is observed range across three R2a seeds, not a confidence interval or causal variance estimate. Job-1 reference ranges (P 0.13, R 0.54, F1 0.35 pp) are the supplied reference figures; the table above also exposes all baseline metrics under the current R2S/v1.1 instrument.','']
    L+=table(['Seed','Slice','Changed physical slots'],[[s,sl,n] for s,cc in churn.items() for sl,n in cc.items()])
    L+=['','Churn counts any prediction tuple change, including UNKNOWN truth; overlapping T4 cards are deduplicated within slice. Held-out and DEV churn and full old/new tuples are in [spread/churn](evidence/r2a/r2rb2_spread_churn.json) and [paired slots](evidence/r2a/r2rb2_paired_slots.json).','', '## (g) Verdict','']
    L+=table(['Check','Verdict'],[['R2a target benefit',tv],['Common-class noninferiority',cv],['Sparse exact-name protection',sv],['Non-target witness margins',nv],['Preserved owner witness protection',ov],['DEV','INCONCLUSIVE (descriptive; no adoption margin)'],['Overall R2a adoption',final]])
    L+=['',f'R2a does not meet the target false-addition criterion. Protection results are limited to their table rows; an INCONCLUSIVE result does not adopt. Overall **{final}**.','', 'Validation: **76 passed in 24.08s** (R2, population, readback, package, digest and frozen-policy suites); results in `evidence/r2a/r2rb2_tests.log`. Readback receipt: `artifacts/labelfix_r2/output_3683130/READBACK_RECEIPT.json`.','']
    oldacc=np.mean([dev[a]['weighted_item_accuracy'] for a in ARMS[:3]]);newacc=np.mean([dev[a]['weighted_item_accuracy'] for a in ARMS[3:]])
    last=f"R2RB2 READY: readback {receipt['file_count']} sha ok; R2a target false additions BASE {z['counts']['old_false_additions']} → R2a {z['counts']['new_false_additions']} ({pct(reduction)}%, CI {pct(z['reduction_ci95'][0])}..{pct(z['reduction_ci95'][1])}%); seeds benefit {benefit}/3; noninferiority common {cv}, sparse {sv}, non-target {nv}, owner {ov}; DEV {pct(oldacc)}%→{pct(newacc)}%; verdict {final}"
    L+=[last];(OUT/'R2A_DIGEST.md').write_text('\n'.join(L)+'\n');print(last,flush=True)

if __name__=='__main__':main()
