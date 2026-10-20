"""Offline final tables; Sol and Opus retain their original independent meters."""
import re
from datetime import datetime, timezone
from b2_common import *
from b3_reports import unit_values, decided, mdtable
from score_all import normalized, paired_agreement, load_scorer

TOKEN_FIELDS = ('input', 'cached_input', 'uncached_input', 'output', 'reasoning', 'total')

def divide(a, b):
    return a / b if a is not None and b else None

def tokens(records):
    out = {f: sum(r['tokens'][f] for r in records) for f in TOKEN_FIELDS if f != 'uncached_input'}
    out['uncached_input'] = out['input'] - out['cached_input']
    return out

def cost(records, n, scope, bed, arm):
    records = sorted(records, key=lambda r: r['limit_probe_before'])
    t = tokens(records)
    before, after = records[0], records[-1]
    cb, ca = before['credits_balance_before'], after['credits_balance_after']
    return dict(bed=bed, arm=arm, runs=[r['reader'] for r in records],
        denominator_items=n, denominator_scope=scope,
        assigned_card_reads=sum(r['items'] for r in records),
        wall_seconds=sum(r['wall_seconds'] for r in records), tokens=t,
        tokens_per_item={f: divide(v, n) for f, v in t.items()},
        tool_calls=sum(r['total_tool_calls'] for r in records),
        weekly_percent_before=before['weekly_used_before'], weekly_percent_after=after['weekly_used_after'],
        weekly_delta_sum=sum(r['weekly_delta'] for r in records),
        weekly_probe_before=before['limit_probe_before'], weekly_probe_after=after['limit_probe_after'],
        credits_before=cb, credits_after=ca, credits_spent=cb-ca if cb is not None and ca is not None else None)

def build_usage():
    out=[]
    for log in sorted((SCRATCH/'logs').glob('SR-B*.codexlog')):
        match=re.search(r'^session id: ([0-9a-f-]+)\s*$',log.read_text(),re.M)
        if not match: raise ValueError('missing session id: '+str(log))
        sid=match[1]
        paths=list((Path.home()/'.codex/sessions').glob('*/*/*/*'+sid+'.jsonl'))
        if len(paths)!=1: raise ValueError('ambiguous/missing rollout: '+sid)
        usage=None; timestamp=None; complete=False
        for obj in rows(paths[0]):
            p=obj.get('payload') or {}
            if p.get('type')=='token_count' and (p.get('info') or {}).get('total_token_usage'):
                usage=p['info']['total_token_usage'];timestamp=obj['timestamp']
            if p.get('type')=='task_complete': complete=True
        if usage is None: raise ValueError('missing measured usage: '+sid)
        t={k:usage[v] for k,v in dict(input='input_tokens',cached_input='cached_input_tokens',output='output_tokens',reasoning='reasoning_output_tokens',total='total_tokens').items()}
        t['uncached_input']=t['input']-t['cached_input']
        out.append(dict(run=log.stem,session_id=sid,launcher_log=str(log),rollout=str(paths[0]),
            status='completed' if complete else 'in progress; lower-bound snapshot',
            usage_timestamp_utc=timestamp,tokens=t,denominator_runs=1))
    return out

def changes(left, right, truth):
    common=set(left)&set(right)&set(truth)
    out=dict(n=len(common),changed=0,changed_to_correct=0,changed_to_wrong=0,changed_between_wrong=0)
    for u in common:
        if left[u]==right[u]: continue
        out['changed']+=1
        ac=left[u]==truth[u] and decided(left[u]);bc=right[u]==truth[u] and decided(right[u])
        out['changed_to_correct' if bc else 'changed_to_wrong' if ac else 'changed_between_wrong']+=1
    out['net_correct']=out['changed_to_correct']-out['changed_to_wrong']
    out['net_accuracy_change']=divide(out['net_correct'],len(common))
    return out

def run():
    result=read_json(ROOT/'results/results.json');ledger=read_json(ROOT/'usage_ledger.json')
    truth=read_json(EFF/'keys/truth.json');truth['owner39']=read_json(EFF/'keys/owner39/truth.json')
    summary=dict(schema_version=1,generated_at_utc=datetime.now(timezone.utc).isoformat(),
        sources=dict(results='results/results.json',ledger='usage_ledger.json',opus='opus_reference/usage_log.tsv',r3_audit='validation/B4_r3_audit.json'),
        definitions={
            'accuracy':'correct/n scored units; unknown and unresolved are incorrect; bsb uses the C1 reader reference',
            'yer_item':'all slots correct; all 59 items included, including 28 zero-slot items',
            'owner39':'scored heads only; breathing excluded on one card; joint = base and all scored heads',
            'owner39_pool':'33 card-reads, retaining repeated cards once per Opus read; each head uses its eligible card-reads',
            'variance':'official scorer agreement; owner unknown/unknown is not confirmed agreement; accuracy differences use the same overlap',
            'changes':'per scored field/slot and joint/item; unresolved answers count as wrong and remain in denominators',
            'Sol_total':'input + output; cached input is part of input; reasoning is part of output; do not add either twice',
            'cost_run_denominator':'assigned items including controls; r3 includes only disputed items plus controls',
            'cost_arm_denominator':'unique scored bed items excluding controls; S1 is one reader, S2 is r1+r2+r3',
            'weekly':'10080-minute bucket; before/after are endpoint probes; delta_sum sums within-run deltas, excludes intervening work',
            'credits':'null before balance or spent means unavailable, not zero; ratios with zero or unavailable denominators are null',
            'meters':'Sol rollout tokens/limits and Opus usage-log tokens are separate; no conversion',
            'build':'launcher session id mapped to rollout; current B4 is a timestamped lower-bound snapshot; excluded from completed build totals'},
        r3_scans=read_json(ROOT/'validation/B4_r3_audit.json'),accuracy=[],variance=[],S1_to_S2=[],controls=[],Sol_cost_per_run=[],Sol_cost_per_arm=[],cost_ratios=[])
    scorer=load_scorer()
    for bed,d in result['beds'].items():
        items=source_items(bed);norm={n:normalized(bed,r['raw'],items) for n,r in d['readers'].items()}
        vals={n:unit_values(bed,v,truth[bed]) for n,v in norm.items()};tv=unit_values(bed,truth[bed],truth[bed])
        for name,r in d['readers'].items():
            if name=='Sol r3':continue
            summary['accuracy'].append(dict(bed=bed,reader=name,scope='partial' if r['partial'] else 'full',metrics=r['accuracy']))
        if bed=='owner39':
            for sol in ('Sol r1','Sol r2','Sol S2'):
                group=[e for e in d['matched_truth_comparisons'] if e['sol']==sol and e['opus']=='Opus partial pooled']
                for who,field in ((sol+' on Opus partial pooled','sol_correct'),('Opus partial pooled','opus_correct')):
                    if who=='Opus partial pooled' and sol!='Sol r1':continue
                    summary['accuracy'].append(dict(bed=bed,reader=who,scope='partial pooled card-reads',metrics={e['metric']:dict(correct=e[field],n=e['n'],rate=divide(e[field],e['n'])) for e in group}))
        pairs=[('Sol r1','Sol r2')]
        if bed!='owner39':pairs.append(('Opus E0a','Opus E0b'))
        else:
            for arm in ('E0a','E0b'):
                name='Opus '+arm+' partial combined';combined={}
                for n,v in norm.items():
                    if n.startswith('Opus '+arm+' '):
                        if set(combined)&set(v):raise ValueError('duplicate within Opus arm; cannot collapse card-reads')
                        combined.update(v)
                norm[name]=combined;vals[name]=unit_values(bed,combined,truth[bed])
            pairs.append(('Opus E0a partial combined','Opus E0b partial combined'))
        for a,b in pairs:
            agreement=paired_agreement(scorer,bed,norm[a],norm[b],truth[bed])
            for metric,lv in vals[a].items():
                rv=vals[b][metric];common=set(lv)&set(rv)&set(tv[metric]);n=len(common)
                ac=sum(lv[u]==tv[metric][u] and decided(lv[u]) for u in common)
                bc=sum(rv[u]==tv[metric][u] and decided(rv[u]) for u in common)
                m=(agreement['fields'][metric] if metric in agreement.get('fields',{}) else agreement[{'joint':'all_fields_per_card','joint_anchor':'all_fields_per_card','slot':'slots','item':'all_slots_per_item'}[metric]])
                assert m['compared']==n
                summary['variance'].append(dict(bed=bed,left=a,right=b,metric=metric,n=n,agree=m['agree'],agreement_rate=divide(m['agree'],n),left_correct=ac,right_correct=bc,absolute_accuracy_difference=divide(abs(ac-bc),n)))
        receipt=read_json(ROOT/f'answers/{bed}/S2.unresolved.json')
        for s1 in ('Sol r1','Sol r2'):
            for metric,lv in vals[s1].items():
                v=changes(lv,vals['Sol S2'][metric],tv[metric])
                if bed=='owner39':unresolved=sum(u['id'] in lv for u in receipt['unresolved'] if u['unit']=='anchor')
                elif metric in ('joint','item'):unresolved=len({u['id'] for u in receipt['unresolved'] if u['id'] in lv})
                elif bed=='bsb':unresolved=sum(u['unit']==metric for u in receipt['unresolved'])
                else:unresolved=sum(u['unit']!='missing_primary' for u in receipt['unresolved'])
                summary['S1_to_S2'].append(dict(bed=bed,S1=s1,metric=metric,unresolved=unresolved,**v))
        for reader in ('r1','r2','r3'):
            c=d['controls']['Sol '+reader];n=len(c['controls'])
            summary['controls'].append(dict(bed=bed,reader=reader,n=n,passed=n-c['control_errors'],failed=c['control_errors'],flagged=c['flagged']))
            r=next(r for r in ledger if r['bed']==bed and r['reader']==reader)
            summary['Sol_cost_per_run'].append(cost([r],r['items'],'assigned items including controls',bed,reader))
        records=[r for r in ledger if r['bed']==bed]
        s2=cost(records,len(items),'unique scored bed items',bed,'S2');summary['Sol_cost_per_arm'].append(s2)
        for reader in ('r1','r2'):
            s1=cost([r for r in records if r['reader']==reader],len(items),'unique scored bed items',bed,'S1 '+reader);summary['Sol_cost_per_arm'].append(s1)
            summary['cost_ratios'].append(dict(bed=bed,baseline=s1['arm'],numerator='S2',tokens={f:divide(s2['tokens'][f],s1['tokens'][f]) for f in TOKEN_FIELDS},wall_seconds=divide(s2['wall_seconds'],s1['wall_seconds']),tool_calls=divide(s2['tool_calls'],s1['tool_calls']),weekly_delta=divide(s2['weekly_delta_sum'],s1['weekly_delta_sum']),credits_spent=divide(s2['credits_spent'],s1['credits_spent'])))
    summary['Opus_cost_per_run']=result['cost']['opus'];summary['Opus_cost_per_arm']=result['cost']['opus_arms']
    build=build_usage();ordered=sorted(ledger,key=lambda r:r['limit_probe_before']);last=max(ledger,key=lambda r:r['limit_probe_after'])
    summary['whole_experiment']=dict(Sol_reading=dict(runs=len(ledger),assigned_card_reads=sum(r['items'] for r in ledger),tokens=tokens(ledger),first_probe=ordered[0]['limit_probe_before'],last_probe=last['limit_probe_after'],weekly_percent_first=ordered[0]['weekly_used_before'],weekly_percent_last=last['weekly_used_after']),build_brief_runs=build,completed_build_tokens={f:sum(r['tokens'][f] for r in build if r['status']=='completed') for f in TOKEN_FIELDS})
    dump(ROOT/'results/SUMMARY.json',summary)
    (ROOT/'results/SUMMARY.md').write_text(render(summary))
    return summary

def render(s):
    tables=[]
    def table(cols,rows):tables.append(mdtable(cols,rows))
    def num(v):return 'unavailable' if v is None else f'{v:.12g}' if isinstance(v,float) else str(v)
    def frac(a,n):return f'{a}/{n}'
    table(['definition','scope / denominator'],s['definitions'].items())
    table(['r3 bed','scan','violations','mapped scored items','controls','mapping complete'],[[r['bed'],'ok' if r['ok'] else 'violations',len(r['violations']),r['mapped_items'],r['controls'],r['mapping_complete']] for r in s['r3_scans']])
    for bed,metrics in [('bsb',(*BSB,'joint')),('yer',('slot','item')),('owner39',('base',*HEADS,'joint_anchor'))]:
        table([bed+' reader','scope',*[m+' correct/n' for m in metrics]],[[r['reader'],r['scope'],*[frac(r['metrics'][m]['correct'],r['metrics'][m]['n']) for m in metrics]] for r in s['accuracy'] if r['bed']==bed])
    table(['bed','variance pair','unit','agreement/n','left correct/n','right correct/n','absolute accuracy difference pp (same n)'],[[r['bed'],r['left']+' vs '+r['right'],r['metric'],frac(r['agree'],r['n']),frac(r['left_correct'],r['n']),frac(r['right_correct'],r['n']),num(100*r['absolute_accuracy_difference']) if r['n'] else 'unavailable (n=0)'] for r in s['variance']])
    table(['bed','S1','unit','n','changed/n','to correct/n','to wrong/n','between wrong/n','net correct/n','net accuracy pp (n)','unresolved/n'],[[r['bed'],r['S1'],r['metric'],r['n'],*[frac(r[f],r['n']) for f in ('changed','changed_to_correct','changed_to_wrong','changed_between_wrong','net_correct')],num(100*r['net_accuracy_change']) if r['n'] else 'unavailable',frac(r['unresolved'],r['n'])] for r in s['S1_to_S2']])
    table(['bed','run','control passes/n','failures/n','flagged'],[[r['bed'],r['reader'],frac(r['passed'],r['n']),frac(r['failed'],r['n']),r['flagged']] for r in s['controls']])
    costs=s['Sol_cost_per_run']+s['Sol_cost_per_arm']
    table(['Sol bed','run / arm','items n','item denominator','wall s / run or arm',*[f+' tokens / run or arm' for f in TOKEN_FIELDS],'total tokens/item n','tool calls / run or arm'],[[r['bed'],r['arm'],r['denominator_items'],r['denominator_scope'],r['wall_seconds'],*[r['tokens'][f] for f in TOKEN_FIELDS],num(r['tokens_per_item']['total']),r['tool_calls']] for r in costs])
    table(['Sol bed','run / arm','weekly % before','weekly % after','within-run weekly pp sum','credits before','credits after','credits spent'],[[r['bed'],r['arm'],*[num(r[f]) for f in ('weekly_percent_before','weekly_percent_after','weekly_delta_sum','credits_before','credits_after','credits_spent')]] for r in costs])
    table(['bed','ratio denominator S1','numerator',*[f+' tokens ratio' for f in TOKEN_FIELDS],'wall ratio','tool calls ratio','weekly delta ratio','credits spent ratio'],[[r['bed'],r['baseline'],r['numerator'],*[num(r['tokens'][f]) for f in TOKEN_FIELDS],*[num(r[f]) for f in ('wall_seconds','tool_calls','weekly_delta','credits_spent')]] for r in s['cost_ratios']])
    table(['Opus bed','arm','run','scope','answered items n','total tokens','tool uses','duration ms','tokens/item n','tools/item n','ms/item n'],[[r['bed'],r['arm'],r['reader'],'partial' if r['partial'] else 'full',r['items'],*[r[f] for f in ('total_tokens','tool_uses','duration_ms')],*[num(r['per_item'][f]) for f in ('total_tokens','tool_uses','duration_ms')]] for r in s['Opus_cost_per_run']+s['Opus_cost_per_arm']])
    w=s['whole_experiment'];r=w['Sol_reading']
    table(['whole experiment meter','run denominator','assigned card-reads',*[f+' tokens' for f in TOKEN_FIELDS],'weekly % first probe','weekly % last probe'],[['Sol reading',r['runs'],r['assigned_card_reads'],*[r['tokens'][f] for f in TOKEN_FIELDS],r['weekly_percent_first'],r['weekly_percent_last']],['completed Sol build/brief',sum(b['status']=='completed' for b in w['build_brief_runs']),'N/A',*[w['completed_build_tokens'][f] for f in TOKEN_FIELDS],'N/A','N/A']])
    table(['reading endpoint','ledger probe'],[['first',r['first_probe']],['last',r['last_probe']]])
    table(['build/brief run (n=1 each)','status','session id','usage timestamp UTC',*[f+' tokens' for f in TOKEN_FIELDS],'rollout'],[[b['run'],b['status'],b['session_id'],b['usage_timestamp_utc'],*[b['tokens'][f] for f in TOKEN_FIELDS],b['rollout']] for b in w['build_brief_runs']])
    return '\n'.join(tables)

if __name__=='__main__':
    s=run()
    print(json.dumps(dict(summary=str(ROOT/'results/SUMMARY.json'),reading_tokens=s['whole_experiment']['Sol_reading']['tokens'],build_runs=len(s['whole_experiment']['build_brief_runs'])),indent=2))
