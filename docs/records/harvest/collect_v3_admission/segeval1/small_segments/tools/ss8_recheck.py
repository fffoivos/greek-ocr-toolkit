"""SS8 metadata-only gate sensitivity analysis; never opens crops or uses network."""
from pathlib import Path
import collections as C
import json
import os
import shutil
import subprocess
import sys
import pandas as pd
import ss1_q1 as q1
import ss2_q2 as q2
import ss6_build as q3
from ss8_key_v2 import gate_flag, build, verify
SS=q1.SMALL
OUT=SS/'gate_recheck'
REC=('C7_chars_le_8_A_le_6','C7',8,6)

def load(p): return json.loads(p.read_text())
def rows(p): return list(q1.read_rows(p))

def load_frame():
    result=[]
    for r in q1.read_rows(q1.BASE/q1.INPUTS[0]):
        v={k:r[k] for k in ['row_id','crop_sha256','source','wave','primary_class','script_class','verdict_05']}
        v['chars']=q1.chars(r)
        v.update(q1.rotation(r['width_px'],r['height_px']))
        v.update(q1.xheight(r.get('xheight_px'),v['L'],v['S']))
        v['output_type']=q1.output_type(r['raw_text'],r['is_numeric_output'])
        v['wave_group']=q1.wave_group(r['wave'])
        v['category']=q1.reason_category(r['verdict_05'],r['reason_05'])
        v['box_fail']=q1.box_fail(v['category'])
        v['book'],v['page'],_=q2.book_page(r['row_id'])
        result.append(v)
    df=pd.DataFrame(result)
    assert len(df)==592466 and df.row_id.is_unique
    return df

def owner_data(df):
    return q2.prepare_owners(df,[{} for _ in q1.INPUTS])[:3]

def subset(df, owners, joined, replay, exclude):
    keep=~df.row_id.isin(exclude)
    remap={old:new for new,old in enumerate(df.index[keep])}
    def remapped(rs):
        return [dict(r,census_index=remap[r['census_index']]) if r['census_index'] is not None else dict(r)
                for r in rs if r['census_index'] is None or r['census_index'] in remap]
    return df[keep].reset_index(drop=True),remapped(owners),remapped(joined),C.defaultdict(list,{remap[i]:rr for i,rr in replay.items() if i in remap})

def curves(df, correctly_sized=False):
    # T2 buckets and breakdowns are imported from SS1; no crop-size judgment is inferred.
    upper=list(range(1,31))+[40,60]
    labels=['≤0']+[q1.char_bucket(v,upper) for v in [1]+[x+1 for x in upper]]
    out=[]
    for typ in ['all','numeric','nonnumeric+mixed']:
        for rot in ['all','yes','no']:
            f=df if typ=='all' else df[df.output_type.eq('numeric') if typ=='numeric' else ~df.output_type.eq('numeric')]
            if rot!='all': f=f[f.rotated.eq(rot=='yes')]
            if correctly_sized: f=f[~f.box_fail]
            buckets=f.chars.map(lambda x:q1.char_bucket(x,upper))
            for label in labels:
                cell=f[buckets.eq(label)]
                d=dict(output_type=typ,rotated=rot,chars_bucket=label,**q1.breaks(cell))
                if correctly_sized:
                    d.update(n_nonKEEP=int((~cell.verdict_05.eq('KEEP')).sum()),pct_nonKEEP=q1.pct((~cell.verdict_05.eq('KEEP')).sum(),len(cell)))
                out.append(d)
    return out

def compute_q1(df, owners, joined, replay):
    return dict(T4=q1.clean(q2.t4_copy(df,owners,joined,replay,q1.candidate_definitions())),
                T2=q1.clean(curves(df)),correctly_sized=q1.clean(curves(df,True)),
                owner_unique=sum(r['census_index'] is not None for r in owners),census_n=len(df))

def compute_q2(df):
    return q1.clean(q2.analyze(df,q2.DEFINITIONS['D_rec'],q2.concentration(df.groupby('book').size())))

def weighted(sample, sources, key, categories):
    total=sum(sources.values()); n=len(sample); out=[]
    for value in categories:
        k=sum(r[key]==value for r in sample)
        terms=[]
        for s,size in sources.items():
            source=[r for r in sample if r['source']==s]
            if size and not source: raise ValueError('No surviving sample for positive source pool: '+s)
            terms.append(size/total * sum(r[key]==value for r in source)/len(source) if size else 0.)
        p=sum(terms)
        out.append(dict(value=value,n=k,weighted_share=p,estimated_pool_rows=p*total,
                        unweighted_share=k/n if n else None,wilson95_unweighted=q3.wilson(k,n) if n else None))
    return out

def compute_q3(sample, key, marks, exclude):
    selected=[r for r in sample if r['line_id'] not in exclude]
    bed=[r for r in selected if not r['control']]
    inside=[r for r in bed if r['stratum']=='inside_by_source']
    pool=load(SS/'q3/SS3_RECEIPT.json')['pools']['inside_by_source']['by_source']
    removed=C.Counter(r['source'] for r in key if r['row_id'] in exclude and r['output_type'] in {'nonnumeric','mixed'})
    sources={s:size-removed[s] for s,size in pool.items()}
    assert all(v>=0 for v in sources.values()) and not set(removed)-set(pool)
    scopes={'bed':bed,'inside':[r for r in bed if r['inside']], 'inside_by_source':inside}
    return dict(n=len(inside),pool_total=sum(sources.values()),source_pools=sources,removed_from_pool=dict(removed),
        T8={k:weighted(inside,sources,k,cats) for k,cats in [('final_class',q3.CLASSES),('final_type',q3.ORDER)]},
        bed_counts={name:dict(n=len(rs),classes={c:sum(r['final_class']==c for r in rs) for c in q3.CLASSES}) for name,rs in scopes.items()},
        label_ok={name:{scope:dict(n=len(rr),label_ok_n=sum(r['label_ok'] for r in rr),label_ok_share=sum(r['label_ok'] for r in rr)/len(rr) if rr else None)
            for scope,rs in scopes.items() for rr in [[r for r in rs if (r['final_class']=='legit_text' if name=='legit_text' else r['final_type']=='punctuation')]]}
            for name in ['legit_text','punctuation']},
        owner_marks=dict(C.Counter(r['owner_mark'] for r in marks if r['line_id'] not in exclude)))

def delta(a,b):
    if isinstance(a,bool) or isinstance(b,bool): return None
    if isinstance(a,(int,float)) and isinstance(b,(int,float)): return b-a
    if isinstance(a,dict) and isinstance(b,dict): return {k:delta(a.get(k),b.get(k)) for k in a.keys()|b.keys()}
    if isinstance(a,list) and isinstance(b,list) and len(a)==len(b): return [delta(x,y) for x,y in zip(a,b)]
    return None

def compare(a,b):
    # Match semantic group/page/book identities before computing differences.
    return dict(before=a,after=b,delta={r['measure']:r['delta'] for r in comparison_table(a,b)})

def flattened(v,prefix=''):
    out={}
    if isinstance(v,dict):
        for k,x in v.items(): out.update(flattened(x,prefix+'/'+str(k)))
    elif isinstance(v,list):
        for i,x in enumerate(v):
            label=str(i)
            if isinstance(x,dict):
                ids=[str(x[k]) for k in ['candidate','side','section','group','output_type','rotated','chars_bucket','value','share','bucket','proxy','page','book','source','wave','primary_class'] if k in x and isinstance(x[k],str)]
                if ids: label=':'.join(ids)
            out.update(flattened(x,prefix+'/'+label))
    elif v is None or isinstance(v,(int,float,bool)): out[prefix]=v
    return out

def comparison_table(a,b):
    aa,bb=flattened(a),flattened(b)
    return [dict(measure=k,before=aa.get(k),after=bb.get(k),delta=delta(aa.get(k),bb.get(k))) for k in sorted(aa.keys()|bb.keys())]

def reconcile(foreign,mixed,df,key,sample,opus,marks):
    result={}; mismatches=[]
    populations={'census':set(df.row_id),'key':{r['row_id'] for r in key},
        'bed':{r['line_id'] for r in sample if not r['control']},'controls':{r['line_id'] for r in sample if r['control']},
        'key_opus':{r['line_id'] for r in opus},'owner_marks':{r['line_id'] for r in marks}}
    expected={'census':(1006,1698),'key':(672,37),'bed':(18,3),'key_opus':(7,2),'owner_marks':(0,1)}
    for name,ids in populations.items():
        f,m=ids&foreign,ids&mixed
        result[name]=dict(rows=len(ids),foreign=len(f),mixed=len(m),overlap=len(f&m),gate_failed=len(f|m),
                          foreign_ids=sorted(f),mixed_ids=sorted(m))
        if name in expected and (len(f),len(m))!=expected[name]: mismatches.append(dict(scope=name,expected=expected[name],actual=[len(f),len(m)],foreign_ids=sorted(f),mixed_ids=sorted(m)))
    missing=sorted((foreign|mixed)-populations['census'])
    if missing: mismatches.append(dict(scope='not_in_census',ids=missing))
    result.update(not_in_census=missing,mismatches=mismatches,
        input_lists=dict(foreign=len(foreign),mixed=len(mixed),overlap=len(foreign&mixed)),
        sample_rows=[dict(line_id=r['line_id'],control=r['control'],final_type=r['final_type'],final_class=r['final_class'],Google_text=r['raw_text'],**gate_flag(r['line_id'],foreign,mixed)) for r in sample if r['line_id'] in foreign|mixed])
    if 'bed' in expected and result['bed']['foreign'] + result['controls']['foreign'] == expected['bed'][0]:
        result['bed_expectation_explanation'] = dict(message='Expected 18 foreign matches counts all sample rows including one control; bed alone has 17.',control_foreign_ids=result['controls']['foreign_ids'])
    return result

def main():
    explicit=['gate_recheck/foreign_mixed_ids_20261019.json','tools/ss1_q1.py','tools/ss2_q2.py','tools/ss6_build.py','tools/ss7_key.py',
        'q1/q1.json','q1/SS1_RECEIPT.json','q1/owner_joined.jsonl','q2/q2.json','q2/SS2_RECEIPT.json',
        'briefs/SS1_q1_dimensions.md','briefs/SS2_q2_origin.md','samples.jsonl','q3/q3.json','q3/Q3_TABLES.md','q3/SS3_RECEIPT.json',
        'q3/key_opus.jsonl','owner_marks_smallseg.jsonl','small_population_key.jsonl.gz']
    inputs={SS/p for p in explicit}|{q1.BASE/p for p in q1.INPUTS}
    for rp in ['q1/SS1_RECEIPT.json','q2/SS2_RECEIPT.json']:
        receipt=load(SS/rp)
        for field in ['inputs','auxiliary_inputs']:
            for item in receipt.get(field,[]): inputs.add(Path(item['path']))
    hashes={str(p):q1.sha(p) for p in sorted(inputs)}
    ids=load(SS/explicit[0]);foreign,mixed=set(ids['foreign']),set(ids['mixed']);exclude=foreign|mixed
    assert hashes[str(SS/explicit[0])].startswith('74d8a280') and hashes[str(SS/explicit[0])].endswith('6f58')
    assert len(ids['foreign'])==len(foreign) and len(ids['mixed'])==len(mixed)
    print('Loading census and original owner joins',flush=True)
    df=load_frame();owners,joined,replay=owner_data(df)
    key=rows(SS/'small_population_key.jsonl.gz');sample=rows(SS/'samples.jsonl');marks=rows(SS/'owner_marks_smallseg.jsonl')
    recon=reconcile(foreign,mixed,df,key,sample,rows(SS/'q3/key_opus.jsonl'),marks)
    q1.write_json(OUT/'RECONCILIATION.json',recon)
    (OUT/'RECONCILIATION.md').write_text('# Supplied gate ID reconciliation\n\n'+q1.md_table([dict(scope=k,**{f:v[f] for f in ['rows','foreign','mixed','overlap','gate_failed']}) for k,v in recon.items() if isinstance(v,dict) and 'gate_failed' in v])+ '\nMismatches: '+json.dumps(recon['mismatches'],ensure_ascii=False)+'\n\nIDs absent from census: '+json.dumps(recon['not_in_census'])+'\n\n'+json.dumps(recon.get('bed_expectation_explanation'),ensure_ascii=False)+'\n\n'+q1.md_table(recon['sample_rows']))
    print('Computing unexcluded reference tables',flush=True)
    before1=compute_q1(df,owners,joined,replay);before2=compute_q2(df);before3=compute_q3(sample,key,marks,set())
    q1.write_json(OUT/'EMPTY_EXCLUSION_REFERENCE.json',dict(Q1=before1,Q2=before2,Q3=before3))
    filtered= subset(df,owners,joined,replay,exclude)
    print('Computing excluded tables',flush=True)
    after1=compute_q1(*filtered);after2=compute_q2(filtered[0]);after3=compute_q3(sample,key,marks,exclude)
    for n,a,b in [(1,before1,after1),(2,before2,after2),(3,before3,after3)]: q1.write_json(OUT/f'Q{n}_GATE.json',compare(a,b))
    text=['# Q1 gate exclusion sensitivity\n','All percentages are 0–100; delta = after − before (percentage points for percentages). **Recommended: chars ≤ 8 & A ≤ 6**. All 45 definitions and all owner groups are retained.\n',
          f"Owner-judged unique matched census lines: {before1['owner_unique']} → {after1['owner_unique']}; removed {before1['owner_unique']-after1['owner_unique']}.\n",'## Candidates (full T4)\n']
    table=comparison_table(before1['T4'],after1['T4'])
    for r in table:
        if REC[0] in r['measure']: r['measure']='**'+r['measure']+'**'
    text.append(q1.md_table(table))
    text+=['## Failure curves by saved chars — original T2\n','These preserve the SS1 denominator and box-failure categories.\n',q1.md_table(comparison_table([r for r in before1['T2'] if r['output_type']!='all'],[r for r in after1['T2'] if r['output_type']!='all'])),
        '## Failure curves after excluding recorded box failures\n','“Correctly sized” here means the metadata proxy box_fail = false, using SS1’s exact three box-failure categories. It is not a new crop judgment; other non-KEEP reasons can still involve crop faults. pct_nonKEEP is the remaining failure rate. The original T2 above is retained for exact reproduction.\n',
        q1.md_table(comparison_table([r for r in before1['correctly_sized'] if r['output_type']!='all'],[r for r in after1['correctly_sized'] if r['output_type']!='all']))]
    (OUT/'Q1_GATE.md').write_text('\n'.join(text))
    (OUT/'Q2_GATE.md').write_text('# Q2 gate exclusion sensitivity\n\n**chars ≤ 8 & A ≤ 6**. Percentages are 0–100; delta = after − before. All shares and densities use the surviving census as denominator. G2 nonnumeric_only is literal nonnumeric; G4 includes mixed. Page IDs and concentration rules are imported unchanged from SS2. Full page measures and book rankings follow.\n\n'+q1.md_table(comparison_table(before2,after2)))
    (OUT/'Q3_GATE.md').write_text('# Q3 gate exclusion sensitivity\n\n'+f"T8 sample n: {before3['n']} → **{after3['n']}**. Pool rows: {before3['pool_total']} → {after3['pool_total']}.\n\n"+
        'Source pools are the stored SS3 residual pool counts minus every supplied gate-failed small nonnumeric/mixed key row per source, exactly as requested. This subtraction includes rows from earlier strata and mixed output; it is an adjusted sensitivity frame, not a reconstructed SS3 residual sampling frame. The residual-pool selection caveat from Q3 continues to apply. Weighted share = sum(source pool share × surviving within-source sample share). Wilson 95% intervals apply only to the new unweighted shares, not the weighted estimate. Shares are 0–1; delta = after − before.\n\n'+
        'Bed inside means the saved inside flag (306 before); T8 uses only inside_by_source (150 before). label_ok uses saved final labels; punctuation is final_type=punctuation, legit_text is final_class=legit_text. No new judgments.\n\n'+q1.md_table(comparison_table(before3,after3)))
    target=SS/'small_population_key.v2.jsonl.gz'
    count=verify(SS/'small_population_key.jsonl.gz',target,foreign,mixed) if target.exists() else build(foreign,mixed)
    tmp=OUT/'tmp';tmp.mkdir(exist_ok=True)
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',TMPDIR=str(tmp.resolve()))
    test=subprocess.run([sys.executable,'-B','-m','pytest','-c','/dev/null','-p','no:cacheprovider','--basetemp',str(tmp/'pytest'),str(SS/'tests/test_ss8.py'),'-q'],capture_output=True,text=True,env=env)
    (OUT/'tests.log').write_text(test.stdout+test.stderr)
    shutil.rmtree(tmp)
    after_hashes={p:q1.sha(p) for p in hashes}
    assert after_hashes==hashes,'input changed'
    outputs=[OUT/p for p in ['RECONCILIATION.json','RECONCILIATION.md','EMPTY_EXCLUSION_REFERENCE.json','Q1_GATE.json','Q1_GATE.md','Q2_GATE.json','Q2_GATE.md','Q3_GATE.json','Q3_GATE.md','tests.log']]+[SS/'small_population_key.v2.jsonl.gz',Path(__file__),SS/'tools/ss8_key_v2.py',SS/'tests/test_ss8.py']
    # Expected-count discrepancies are findings, not permission to alter inputs.
    ready=test.returncode==0 and not recon['not_in_census']
    receipt=dict(status='READY' if ready else 'FAILED',inputs=[dict(path=p,sha256=h,sha256_after=after_hashes[p]) for p,h in hashes.items()],outputs=[dict(path=str(p),sha256=q1.sha(p)) for p in outputs],reconciliation=recon,test_results=dict(returncode=test.returncode,output=test.stdout+test.stderr),
        census_sha256_before=hashes[str(q1.BASE/q1.INPUTS[0])],census_sha256_after=after_hashes[str(q1.BASE/q1.INPUTS[0])],input_hashes_unchanged=True,
        excluded_census_rows=recon['census']['gate_failed'],excluded_small_rows=recon['key']['gate_failed'],key_v2_rows=count,key_v1_serialized_fields_byte_identical=True,gzip_mtime=0,
        python_executable=sys.executable,python=sys.version,pandas=pd.__version__,temporary_files_removed=not tmp.exists(),receipt_self_hash='Excluded to avoid circular self hash')
    q1.write_json(OUT/'SS8_RECEIPT.json',receipt)
    if not ready: raise RuntimeError('tests or reconciliation failed; see receipt')
    print(f"SS8 READY: excluded {recon['census']['gate_failed']} census rows ({recon['key']['gate_failed']} small), key v2 {count} rows, tables gate_recheck/Q{{1,2,3}}_GATE.md")

if __name__=='__main__':
    try: main()
    except Exception as exc:
        print('SS8 FAILED: '+str(exc),flush=True)
        raise
