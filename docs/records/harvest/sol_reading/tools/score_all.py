#!/usr/bin/env python3
"""Offline SR-B2 tables; absent observations stay missing, VOID runs excluded."""
import csv,importlib.util,itertools,sys
from collections import Counter
from b2_common import *

def load_scorer():
    sys.path.append(str(EFF))
    spec=importlib.util.spec_from_file_location('efficiency_score',EFF/'score.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def official_score(scorer,bed,name,data,truth):
    # Use the unchanged scorer for every actual reader, with its answered IDs
    # and (r3 yer only) answered slots as the scoring scope.
    scoped={b:dict(t) for b,t in truth.items()}
    scoped[bed]={i:copy_value(truth[bed][i]) for i in data}
    if bed=='yer':
        for i in data:scoped[bed][i]['slots']={s:truth[bed][i]['slots'][s] for s in data[i]['slots']}
    pack=dict(bed=bed,arm=name,reader='r1',item_ids=list(data),items_per_reader=len(data),path=str(EFF/'packs'/bed/('E0a' if bed=='owner39' else 'E1')/'r1'))
    manifest={'arms':{name:1},'packs':[pack]+[dict(bed=b,arm=name,reader='r1',item_ids=list(truth[b]),items_per_reader=len(truth[b])) for b in ('bsb','yer') if b!=bed]}
    if bed=='owner39':manifest['owner39']={'truth':'keys/owner39/truth.json'}
    result=scorer.score(manifest,scoped,[(bed,name,'r1',list(data.values()))],root=EFF)['beds'][bed]['arms'][name]
    return result['readers']['r1'] if bed=='owner39' else result

def copy_value(v):return json.loads(json.dumps(v,ensure_ascii=False))

def normalized(bed,data,items):
    return {i:normalize(r,items[i]) for i,r in data.items()} if bed=='owner39' else data

def flat(bed,data,truth):
    out={}
    for i,r in data.items():
        if bed=='bsb':out.update({i+'/'+f:r[f] for f in BSB})
        elif bed=='yer':out.update({i+'/'+s:v for s,v in r['slots'].items()})
        else:
            out[i+'/base']=r['base']
            for h in truth[i]['scored_heads']:out[i+'/'+h]=r['heads'][h]
            out[i+'/anchor']=(r['base'],*(r['heads'][h] for h in truth[i]['scored_heads']))
    return out

def metric(correct,n,expected=None):return dict(correct=correct,n=n,expected=n if expected is None else expected,rate=correct/n if n else None)
def accuracy_metrics(bed,actual,truth):
    result={};ids=set(actual)&set(truth)
    if bed=='bsb':
        for f in BSB:result[f]=metric(sum(actual[i][f]==truth[i][f] for i in ids),len(ids),len(truth))
        result['joint']=metric(sum(all(actual[i][f]==truth[i][f] for f in BSB) for i in ids),len(ids),len(truth))
    elif bed=='yer':
        pairs=[(i,s) for i in ids for s in actual[i]['slots'] if s in truth[i]['slots']]
        result['slot']=metric(sum(actual[i]['slots'][s]==truth[i]['slots'][s] for i,s in pairs),len(pairs),sum(len(t['slots']) for t in truth.values()))
        result['item']=metric(sum(all(actual[i]['slots'][s]==truth[i]['slots'][s] for s in actual[i]['slots']) for i in ids),len(ids),len(truth))
    else:
        for h in ('base',*HEADS):
            eligible=[i for i in ids if h=='base' or h in truth[i]['scored_heads']]
            def value(r):return r['base'] if h=='base' else r['heads'][h]
            result[h]=metric(sum(value(actual[i])==value(truth[i]) and value(actual[i])!='unknown' for i in eligible),len(eligible),sum(h=='base' or h in t['scored_heads'] for t in truth.values()))
        result['joint_anchor']=metric(sum(actual[i]['base']==truth[i]['base'] and actual[i]['base']!='unknown' and all(actual[i]['heads'][h]==truth[i]['heads'][h] and actual[i]['heads'][h]!='unknown' for h in truth[i]['scored_heads']) for i in ids),len(ids),len(truth))
    return result

def paired_agreement(scorer,bed,left,right,truth):
    if bed=='owner39':
        import owner39_score
        return owner39_score.agreement(left,right,truth)
    # Partial slot readers (r3) can be compared without pretending they read all slots.
    ids=set(left)&set(right)&set(truth);scoped={i:copy_value(truth[i]) for i in ids}
    if bed=='yer':
        for i in scoped:scoped[i]['slots']={s:v for s,v in scoped[i]['slots'].items() if s in left[i]['slots'] and s in right[i]['slots']}
        left={i:{**left[i],'slots':{s:left[i]['slots'][s] for s in scoped[i]['slots']}} for i in ids};right={i:{**right[i],'slots':{s:right[i]['slots'][s] for s in scoped[i]['slots']}} for i in ids}
    return scorer.agreement(left,right,scoped,bed)

def agreement_matrix(scorer,bed,norm,names,truth):
    return {a+' | '+b:paired_agreement(scorer,bed,norm[a],norm[b],truth)
            for a,b in itertools.combinations_with_replacement(names,2)}

def undecided(bed,data,unresolved=0):
    if bed=='bsb':values=[r[f] for r in data.values() for f in BSB]
    elif bed=='yer':values=[v for r in data.values() for v in r['slots'].values()]
    else:values=[v for r in data.values() for v in (r['base'],*r['heads'].values())]
    c=Counter(values)
    return dict(**{v:c[v] for v in ('u','unknown')},unreadable=sum(r.get('readability')=='unreadable' for r in data.values()),unresolved=unresolved,units=len(values),items=len(data))

def opus_inputs(bed):
    ref=ROOT/'opus_reference';result={}
    for arm in ('E0a','E0b','E1'):
        paths=sorted(ref.glob(f'{bed}_{arm}_*.jsonl'))
        if bed=='owner39':
            for p in paths:result['Opus '+p.stem.removeprefix('owner39_').replace('_',' ')]=index(rows(p),bed)
        elif paths:
            result['Opus '+arm]=index([r for p in paths for r in rows(p)],bed)
    return result

def cost_tables(statuses,bed_results):
    ledger=read_json(ROOT/'usage_ledger.json') if (ROOT/'usage_ledger.json').exists() else []
    sol=[];by={}
    for record in ledger:
        bed,reader=record['bed'],record['reader'];status=statuses.get(bed,{}).get('Sol '+reader,'MISSING')
        if status!='OK':continue
        r=copy_value(record);r['status']=status;r['meter']='Sol';sol.append(r);by[bed,reader]=r
    aggregates=[]
    for bed in FIELDS:
        if statuses[bed].get('Sol S2','').startswith('VOID'):continue
        active=bed_results[bed]['readers'];receipt=ROOT/f'answers/{bed}/S2.unresolved.json';used=read_json(receipt).get('used_readers',[]) if receipt.exists() and 'Sol S2' in active else []
        # Missing r3 on a disputed bed is incomplete S2 cost even if an undecided S2 exists.
        if used and read_json(receipt).get('r3_status')!='OK':
            disputes=disagreements(bed,active.get('Sol r1',{}).get('raw',{}),active.get('Sol r2',{}).get('raw',{}),source_items(bed))
            if disputes:used=used+['r3']
        costs=[by.get((bed,r)) for r in used];complete=bool(used) and all(c is not None for c in costs)
        total={f:sum(c['tokens'][f] for c in costs) if complete else None for f in ('input','cached_input','output','reasoning','total')}
        totals={f:sum(c[f] for c in costs) if complete and all(c.get(f) is not None for c in costs) else None for f in ('items','wall_seconds','total_tool_calls','weekly_delta')}
        n=len(source_items(bed));ratios={}
        for reader in ('r1','r2'):
            base=by.get((bed,reader));ratios[reader]={f:(total['total']/base['tokens']['total'] if f=='tokens' and complete and base and base['tokens']['total'] else totals['wall_seconds']/base['wall_seconds'] if f=='wall' and complete and base and base['wall_seconds'] else totals['weekly_delta']/base['weekly_delta'] if f=='weekly' and complete and base and base['weekly_delta'] else None) for f in ('tokens','wall','weekly')}
        aggregates.append(dict(bed=bed,reader='S2',complete=complete,used_readers=used,tokens=total,**totals,unique_items=n,tokens_per_item={f:v/n if v is not None else None for f,v in total.items()},weekly_points_per_100_items=totals['weekly_delta']*100/n if totals['weekly_delta'] is not None else None,weekly_used_before=costs[0]['weekly_used_before'] if complete else None,weekly_used_after=costs[-1]['weekly_used_after'] if complete else None,credits_balance_before=costs[0]['credits_balance_before'] if complete else None,credits_balance_after=costs[-1]['credits_balance_after'] if complete else None,S2_over_S1=ratios))
    opus=[];p=ROOT/'opus_reference/usage_log.tsv'
    if p.exists():
        for r in csv.DictReader(p.open(),delimiter='\t'):
            if r['arm'] not in ('E0a','E0b','E1'):continue
            answer=ROOT/'opus_reference'/f"{r['bed']}_{r['arm']}_{r['reader']}.jsonl"
            n=len(rows(answer)) if answer.exists() else None
            vals={f:int(r[f]) for f in ('total_tokens','tool_uses','duration_ms')}
            opus.append(dict(bed=r['bed'],arm=r['arm'],reader=r['reader'],items=n,partial=r['bed']=='owner39',**vals,per_item={f:v/n if n else None for f,v in vals.items()}))
    opus_arms=[]
    for bed in ('bsb','yer'):
        for arm in ('E0a','E0b','E1'):
            records=[r for r in opus if r['bed']==bed and r['arm']==arm]
            if not records:continue
            n=sum(r['items'] for r in records) if all(r['items'] is not None for r in records) else None
            totals={f:sum(r[f] for r in records) for f in ('total_tokens','tool_uses','duration_ms')}
            opus_arms.append(dict(bed=bed,arm=arm,reader='arm total',items=n,partial=False,**totals,per_item={f:v/n if n else None for f,v in totals.items()}))
    return dict(sol=sol,S2=aggregates,opus=opus,opus_arms=opus_arms)

def run():
    scorer=load_scorer();truth=read_json(EFF/'keys/truth.json');truth['owner39']=read_json(EFF/'keys/owner39/truth.json')
    result={'schema_version':3,'scorer':str(EFF/'score.py'),'scorer_sha256':sha(EFF/'score.py'),'beds':{},'status':{}}
    for bed in FIELDS:
        items=source_items(bed);data={};status={};controls={};scans={}
        for reader in ('r1','r2','r3','S2'):
            records,state=load_run(bed,reader);name='Sol '+reader;status[name]=state
            p=ROOT/f'answers/{bed}/{reader}.scan.json'
            if p.exists():scans[name]=read_json(p)
            if state=='OK':
                data[name]=records;c=ROOT/f'answers/{bed}/{reader}.controls.json'
                if c.exists():controls[name]=read_json(c)
        refs=opus_inputs(bed);data.update(refs)
        expected_opus=['Opus E0a','Opus E0b','Opus E1'] if bed!='owner39' else ['Opus '+a+' '+r for a in ('E0a','E0b') for r in ('r1','r2')]
        for name in expected_opus:status[name]='OK' if name in refs else 'MISSING'
        readers={};norm={}
        for name,actual in data.items():
            if set(actual)-set(truth[bed]):raise ValueError('unknown IDs in '+bed+'/'+name)
            official=official_score(scorer,bed,name,actual,truth);norm[name]=normalized(bed,actual,items)
            unresolved=0;p=ROOT/f'answers/{bed}/S2.unresolved.json'
            if name=='Sol S2' and p.exists():unresolved=read_json(p).get('unresolved_units',0)
            readers[name]=dict(raw=actual,official_scorer=official,accuracy=accuracy_metrics(bed,norm[name],truth[bed]),undecided=undecided(bed,norm[name],unresolved),answered_items=len(actual),partial=set(actual)!=set(truth[bed]) or name=='Sol r3')
        matrix_names=[n for n in ('Sol r1','Sol r2','Sol S2',*expected_opus) if n in data]
        # Each cell uses its own overlap: partial readers have no global common cohort.
        cohort=set.intersection(*(set(norm[n]) for n in matrix_names)) if matrix_names else set()
        matrix=agreement_matrix(scorer,bed,norm,matrix_names,truth[bed]);pairwise=copy_value(matrix)
        variance={}
        for a,b in [('Sol r1','Sol r2'),('Opus E0a','Opus E0b')]+([('Opus E0a '+r,'Opus E0b '+r) for r in ('r1','r2')] if bed=='owner39' else []):
            if a in norm and b in norm:variance[a+' | '+b]=paired_agreement(scorer,bed,norm[a],norm[b],truth[bed])
        flattened={n:flat(bed,d,truth[bed]) for n,d in norm.items()};tf=flat(bed,truth[bed],truth[bed]);changes={};differences=[]
        for n in ('Sol r1','Sol r2'):
            if n in flattened and 'Sol S2' in flattened:
                # Separate fields/slots/anchor, rather than mixing their denominators.
                groups=(*BSB,'joint') if bed=='bsb' else ('slot','item') if bed=='yer' else ('base',*HEADS,'anchor')
                changes[n]={}
                for group in groups:
                    def values(data):
                        if bed=='bsb' and group=='joint':return {i:tuple(r[f] for f in BSB) for i,r in data.items()}
                        if bed=='yer' and group=='item':return {i:tuple(sorted(r['slots'].items())) for i,r in data.items()}
                        f=flat(bed,data,truth[bed]);return {u:v for u,v in f.items() if bed=='yer' or u.rsplit('/',1)[-1]==group}
                    changes[n][group]=change_accounting(values(norm[n]),values(norm['Sol S2']),values(truth[bed]))
        for sol in ('Sol r1','Sol r2','Sol S2'):
            if sol not in flattened:continue
            for reference in ['truth',*refs]:
                rf=tf if reference=='truth' else flattened[reference]
                for unit in sorted(set(flattened[sol])&set(rf)):
                    if flattened[sol][unit]==rf[unit]:continue
                    iid,field=unit.rsplit('/',1);entry=dict(unit=unit,item_id=iid,field=field,sol=sol,reference=reference,left=flattened[sol][unit],right=rf[unit])
                    if bed=='bsb':entry.update(sol_detail=data[sol][iid].get('detail',''),reference_detail=(truth[bed] if reference=='truth' else data[reference])[iid].get('detail',''),google_text=items[iid]['google_text'])
                    differences.append(entry)
        result['status'][bed]=status
        result['beds'][bed]=dict(readers=readers,controls=controls,leak_scans=scans,agreement_matrix=matrix,matrix_cohort_ids=sorted(cohort),pairwise_agreement=pairwise,variance=variance,S1_to_S2=changes,disagreements=differences,truth_items=len(truth[bed]),excluded_breathing=[i for i,t in truth[bed].items() if bed=='owner39' and 'breathing' not in t['scored_heads']])
    from b3_reports import augment, render_errors
    augment(result,truth)
    (ROOT/'results').mkdir(parents=True,exist_ok=True)
    (ROOT/'results/ERRORS.md').write_text(render_errors(result,truth))
    result['cost']=cost_tables(result['status'],result['beds']);dump(ROOT/'results/results.json',result)
    (ROOT/'results/TABLES.md').write_text(render(result));print(json.dumps({'output':str(ROOT/'results/results.json'),'tables':str(ROOT/'results/TABLES.md'),'status':result['status']},indent=2))
    return result

def render(result):
    lines=[]
    def table(columns,records):
        lines.append('| '+' | '.join(columns)+' |');lines.append('| '+' | '.join('---' for _ in columns)+' |')
        for record in records:
            lines.append('| '+' | '.join(str(v).replace('|','\\|').replace('\n',' ') for v in record)+' |')
        lines.append('')
    def number(v,n=1):return 'MISSING / '+str(n) if v is None else f'{v:.6g} / {n}' if isinstance(v,float) else f'{v} / {n}'
    def rate(m):return f"{m['correct']}/{m['n']} ({100*m['rate']:.2f}%)" if m['n'] else '0/0'
    def agreement_rows(bed,collection):
        output=[]
        for pair,v in collection.items():
            for f,m in v.get('fields',{}).items():output.append([bed,pair,f,f"{m['agree']}/{m['compared']}"])
            for f in ('slots','all_fields_per_card','all_slots_per_item','mark_tuple_per_slot'):
                if f in v:m=v[f];output.append([bed,pair,f,f"{m['agree']}/{m['compared']}"])
        return output
    table(['bed','run','status'],[[b,n,s] for b,d in result['status'].items() for n,s in d.items()])
    table(['bed','reader','metric','accuracy','coverage items','scope','flagged'],[[b,n,f,rate(m),f"{r['answered_items']}/{d['truth_items']}",'disputed only' if n=='Sol r3' else 'partial' if r['partial'] else 'full',d['controls'].get(n,{}).get('flagged','MISSING')] for b,d in result['beds'].items() for n,r in d['readers'].items() for f,m in r['accuracy'].items()])
    table(['bed','matrix pairwise overlap','metric','agreement'],[r for b,d in result['beds'].items() for r in agreement_rows(b,d['agreement_matrix'])])
    table(['bed','pairwise common items','metric','agreement'],[r for b,d in result['beds'].items() if b=='owner39' for r in agreement_rows(b,d['pairwise_agreement'])])
    table(['bed','variance pair','metric','agreement'],[r for b,d in result['beds'].items() for r in agreement_rows(b,d['variance'])])
    table(['bed','S1','metric','to correct','to wrong','between wrong','net correct','net accuracy change'],[[b,n,f,*[number(v[k],v['compared']) for k in ('changed_to_correct','changed_to_wrong','changed_between_wrong','net_correct')],number(v['net_correct'],v['compared'])] for b,d in result['beds'].items() for n,groups in d['S1_to_S2'].items() for f,v in groups.items()])
    table(['bed','reader','u','unknown','unreadable cards','unresolved'],[[b,n,number(r['undecided']['u'],r['undecided']['units']),number(r['undecided']['unknown'],r['undecided']['units']),number(r['undecided']['unreadable'],r['undecided']['items']),number(r['undecided']['unresolved'],r['undecided']['items'] if b=='owner39' else r['undecided']['units'])] for b,d in result['beds'].items() for n,r in d['readers'].items()])
    table(['bed','reader','control passes','control failures','flagged'],[[b,n,number(sum(x['passed'] for x in c['controls']),len(c['controls'])) if c else 'N/A',number(c['control_errors'],len(c['controls'])) if c else 'N/A',str(c['flagged']) if c else 'N/A'] for b,d in result['beds'].items() for n in d['readers'] for c in [d['controls'].get(n)]])
    table(['bed','run','leak scan'],[[b,n,('ok' if d['leak_scans'][n].get('ok') else 'VOID') if n in d['leak_scans'] else 'MISSING'] for b,d in result['beds'].items() for n in ('Sol r1','Sol r2','Sol r3')])
    table(['bed','Sol run','items','wall seconds','input','cached input','output','reasoning','total','tool calls','weekly before','weekly after','weekly delta','credits before','credits after','tokens/item','weekly points/100 items'],[[c['bed'],c['reader'],number(c.get('items')),*[number(c.get(f)) for f in ('wall_seconds',)],*[number(c['tokens'].get(f)) for f in ('input','cached_input','output','reasoning','total')],number(c.get('total_tool_calls')),*[number(c.get(f)) for f in ('weekly_used_before','weekly_used_after','weekly_delta','credits_balance_before','credits_balance_after')],number(c['tokens'].get('total'),c.get('unique_items',c.get('items'))),number(c.get('weekly_points_per_100_items'),100)] for c in result['cost']['sol']+result['cost']['S2']])
    table(['bed','S2/S1 baseline','tokens ratio','wall ratio','weekly ratio'],[[c['bed'],n,*[number(v.get(f)) for f in ('tokens','wall','weekly')]] for c in result['cost']['S2'] for n,v in c['S2_over_S1'].items()])
    table(['bed','Opus arm','reader','scope','answered items','total tokens','tool uses','duration ms','tokens/item','tools/item','duration ms/item'],[[c['bed'],c['arm'],c['reader'],'partial' if c['partial'] else 'full',number(c['items']),*[number(c[f]) for f in ('total_tokens','tool_uses','duration_ms')],*[number(c[f],c['items']) for f in ('total_tokens','tool_uses','duration_ms')]] for c in result['cost']['opus']+result['cost']['opus_arms']])
    table(['bed','item','unit','Sol','reference','Sol value','reference value','Sol detail','reference detail','Google'],[[b,e['item_id'],e['field'],e['sol'],e['reference'],json.dumps(e['left'],ensure_ascii=False),json.dumps(e['right'],ensure_ascii=False),e.get('sol_detail',''),e.get('reference_detail',''),e.get('google_text','')] for b,d in result['beds'].items() for e in d['disagreements']])
    from b3_reports import render_matched
    lines.append(render_matched(result))
    return '\n'.join(lines)+'\n'
if __name__=='__main__':run()
