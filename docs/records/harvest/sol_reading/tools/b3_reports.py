"""SR-B3 matched truth comparisons and private error inventory."""
from b2_common import *

def unit_values(bed,data,truth):
    if bed=='bsb':
        return {**{f:{i:r[f] for i,r in data.items()} for f in BSB},'joint':{i:tuple(r[f] for f in BSB) for i,r in data.items()}}
    if bed=='yer':return {'slot':{(i,s):v for i,r in data.items() for s,v in r['slots'].items()},'item':{i:tuple(sorted(r['slots'].items())) for i,r in data.items()}}
    return {**{h:{i:(r['base'] if h=='base' else r['heads'][h]) for i,r in data.items() if h=='base' or h in truth[i]['scored_heads']} for h in ('base',*HEADS)},'joint_anchor':{i:(r['base'],*(r['heads'][h] for h in truth[i]['scored_heads'])) for i,r in data.items()}}

def decided(value):return all(decided(v) for v in value) if isinstance(value,tuple) else value!='unknown'

def paired(left,right,truth):
    common=sorted(set(left)&set(right)&set(truth));a=b=better=worse=same=0
    for u in common:
        ac=left[u]==truth[u] and decided(left[u]);bc=right[u]==truth[u] and decided(right[u])
        a+=ac;b+=bc;better+=ac and not bc;worse+=bc and not ac;same+=ac==bc
    return dict(n=len(common),sol_correct=a,opus_correct=b,better=better,worse=worse,same=same)

def matched(bed,norm,truth):
    vals={n:unit_values(bed,d,truth) for n,d in norm.items()};tv=unit_values(bed,truth,truth);out=[]
    for sol in (n for n in norm if n.startswith('Sol ')):
        per=[]
        for opus in (n for n in norm if n.startswith('Opus ')):
            for metric,left in vals[sol].items():
                r=paired(left,vals[opus][metric],tv[metric]);entry=dict(sol=sol,opus=opus,metric=metric,**r)
                out.append(entry);per.append(entry)
        if bed=='owner39':
            for metric in vals[sol]:
                group=[e for e in per if e['metric']==metric]
                out.append(dict(sol=sol,opus='Opus partial pooled',metric=metric,**{k:sum(e[k] for e in group) for k in ('n','sol_correct','opus_correct','better','worse','same')}))
    return out

def augment(result,truth):
    from score_all import normalized
    for bed,d in result['beds'].items():
        items=source_items(bed)
        norm={n:normalized(bed,r['raw'],items) for n,r in d['readers'].items()}
        d['matched_truth_comparisons']=matched(bed,norm,truth[bed])
    result['agreement_scope']='Each matrix cell uses that pair\'s common items. The global intersection is diagnostic only; owner39 partial-reader intersection is empty.'
    result['paired_policy']='better/worse/same compare correctness against truth; same includes both correct and both wrong. Owner39 pooled units are card-reads, repeated cards retain multiplicity; head metrics use scored heads only.'

def mdtable(columns,records):
    return '\n'.join(['| '+' | '.join(columns)+' |','| '+' | '.join('---' for _ in columns)+' |']+['| '+' | '.join(str(v).replace('|','\\|').replace('\n',' ') for v in row)+' |' for row in records])+'\n'

def render_matched(result):
    return '\nMatched comparisons against truth. Same = both correct or both wrong. Owner39 pooled repeats each card once per Opus read; accuracy denominators are matched units.\n\n'+mdtable(['bed','Sol','Opus cohort','metric','Sol accuracy','Opus accuracy','better','worse','same'],[[bed,e['sol'],e['opus'],e['metric'],f"{e['sol_correct']}/{e['n']}",f"{e['opus_correct']}/{e['n']}",e['better'],e['worse'],e['same']] for bed,d in result['beds'].items() for e in d['matched_truth_comparisons']])

def render_errors(result,truth):
    mapping=read_json(EFF/'keys/input_mapping.json');owner=read_json(EFF/'keys/owner39/input_mapping.json');lines=['# Sol wrong answers (private)','','Scored units only: owner39 anchor, yer slot, bsb card (any scored field differs). Missing Opus reads are MISSING; bsb detail is context, not an accuracy target.','']
    for bed,d in result['beds'].items():
        items=source_items(bed);refs=[n for n in d['readers'] if n.startswith('Opus ')];records=[]
        def answer(row,i,slot=None,is_truth=False):
            if row is None:return 'MISSING'
            if bed=='yer':return row['slots'].get(slot,'MISSING')
            if bed=='bsb':return {f:row.get(f,'') for f in (*BSB,'detail')}
            if is_truth:return {k:row[k] for k in ('truth_word','base','heads','scored_heads') if k in row}
            return dict(form=row.get('transcription') if row['choice']=='literal' else items[i]['options'].get(row['choice'],'unreadable'),heads=row['anchor_heads'])
        for sol,r in d['readers'].items():
            if not sol.startswith('Sol '):continue
            for i,row in sorted(r['raw'].items()):
                t=truth[bed][i]
                if bed=='yer':wrong=[s for s,v in row['slots'].items() if v!=t['slots'][s]]
                elif bed=='bsb':wrong=[None] if any(row[f]!=t[f] for f in BSB) else []
                else:
                    n=normalize(row,items[i]);wrong=[None] if not (n['base']==t['base'] and decided(n['base']) and all(n['heads'][h]==t['heads'][h] and decided(n['heads'][h]) for h in t['scored_heads'])) else []
                original=owner[i]['db_id'] if bed=='owner39' else mapping[bed][i]['line_id']
                for slot in wrong:
                    cells=[sol,i,original,slot or ('anchor' if bed=='owner39' else 'card'),answer(row,i,slot),answer(t,i,slot,True),*[answer(d['readers'][ref]['raw'].get(i),i,slot) for ref in refs]]
                    records.append([json.dumps(v,ensure_ascii=False) if isinstance(v,dict) else v for v in cells])
        lines+=['## '+bed,'',mdtable(['Sol','item id','original source id','unit','Sol answer','truth',*refs],records),'']
    return '\n'.join(lines)
