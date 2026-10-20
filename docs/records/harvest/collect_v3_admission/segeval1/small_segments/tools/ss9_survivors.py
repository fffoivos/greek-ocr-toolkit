"""SS9 metadata-only admission analysis; no network or crop access."""
from pathlib import Path
import ast
import collections as C
import gzip
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata as ud
import ss1_q1 as q1
import ss2_q2 as q2
import ss8_recheck as s8
import ss8_key_v2

SS=q1.SMALL
OUT=SS/'r1_survivors'
REF=Path.home()/'Projects/greek-ocr-toolkit-segcensus'
FIELDS=['letters','alnum','reason','admit','survivor']
SCOPE='Only owner gate 0.3 part 2 + supplied gate failures; no other admission rules'
REASONS=['single_character_cell','numeric_shape','short_line','cell_status_unresolved']

def numeric_grammar(text):
    """Reproduce segcensus numeric_text on raw text, including Unicode whitespace."""
    s=(text or '').strip()
    if not s: return False
    separators=set(".,:;/-–—%()+'′§№° ")
    if any(c.isdecimal() for c in s) and all(c.isdecimal() or c in separators or c.isspace() for c in s): return True
    token=s[:-1] if s[-1] in '.)' else s
    return bool(token and re.fullmatch(r'M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})',token))

def short_line_exclusion(row):
    """Owner rule in reference order; census dimensions and primary_class role only."""
    text=row['raw_text']
    letters=sum(ud.category(c).startswith('L') for c in text)
    alnum=sum(ud.category(c).startswith('L') or ud.category(c)=='Nd' for c in text)
    w,h=row.get('width_px'),row.get('height_px')
    if w is None or h is None or min(w,h)<=0: return 'cell_status_unresolved'
    if max(w,h)/min(w,h)<=6: return 'single_character_cell' if alnum<=1 else None
    role=row.get('primary_class') or 'prose'
    if role=='numerics_tables' or numeric_grammar(text): return 'numeric_shape' if alnum<=1 else None
    return 'short_line' if letters<(4 if role=='headings_caps' else 10) else None

def additions(row,gate=False):
    text=row['raw_text'];reason=short_line_exclusion(row)
    return dict(letters=sum(ud.category(c).startswith('L') for c in text),alnum=sum(ud.category(c).startswith('L') or ud.category(c)=='Nd' for c in text),reason=reason,admit=reason is None,survivor=reason is None and not gate)

def reference_numeric():
    """Load only the reference function AST, never import the reference module."""
    tree=ast.parse((REF/'greekocr/harvest/line_pipeline.py').read_text())
    node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='numeric_text')
    ns={'re':re};exec(compile(ast.Module(body=[node],type_ignores=[]),'<reference numeric_text>','exec'),ns)
    return ns['numeric_text']

def build_key(extra):
    target=SS/'small_population_key.v3.jsonl.gz'
    with gzip.open(SS/'small_population_key.v2.jsonl.gz','rb') as src,target.open('xb') as raw:
        with gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0) as dst:
            for line in src:
                r=json.loads(line);v=extra[r['row_id']]
                dst.write(line.rstrip(b'\r\n')[:-1]+b', '+json.dumps(v).encode()[1:]+b'\n')

def verify_key():
    from itertools import zip_longest
    n=0
    with gzip.open(SS/'small_population_key.v2.jsonl.gz','rb') as a,gzip.open(SS/'small_population_key.v3.jsonl.gz','rb') as b:
        for old,new in zip_longest(a,b):
            assert old is not None and new is not None
            x,y=json.loads(old),json.loads(new)
            assert list(y)==list(x)+FIELDS
            assert {k:v for k,v in y.items() if k not in FIELDS}==x
            assert new.startswith(old.rstrip(b'\r\n')[:-1]+b', "letters": ')
            assert y['survivor']==(y['admit'] and not y['gate_failed'])
            n+=1
    assert (SS/'small_population_key.v3.jsonl.gz').read_bytes()[4:8]==b'\0'*4
    assert n==59002
    return n

def recompute(df,owners,joined,replay,sample,key,marks,exclude):
    filtered=s8.subset(df,owners,joined,replay,exclude)
    return dict(Q1=s8.compute_q1(*filtered),Q2=s8.compute_q2(filtered[0]),Q3=s8.compute_q3(sample,key,marks,exclude))

def three_table(a,b,c):
    aa,bb,cc=map(s8.flattened,(a,b,c))
    return q1.md_table([{'measure — '+SCOPE:k,'original (SS1/SS2)':aa.get(k),'gate-removed (SS8)':bb.get(k),'admitted + gate':cc.get(k)} for k in sorted(aa.keys()|bb.keys()|cc.keys())])

def table(rs):
    # Every table carries the restricted rule scope in its first header.
    if not rs: return '(no rows)'
    first=next(iter(rs[0]))
    return q1.md_table([{(k+' — '+SCOPE if k==first else k):v for k,v in r.items()} for r in rs])

def main():
    explicit=['small_population_key.v2.jsonl.gz','q1/owner_joined.jsonl','samples.jsonl','owner_marks_smallseg.jsonl','q3/q3.json','q3/SS3_RECEIPT.json','q1/q1.json','q2/q2.json']
    inputs={SS/p for p in explicit}|{p for p in (SS/'gate_recheck').rglob('*') if p.is_file()}|{q1.BASE/p for p in q1.INPUTS}
    inputs|={REF/'greekocr/harvest/line_pipeline.py',REF/'docs/briefs/GATE_03b_short_lines.md'}
    for p in ['q1/SS1_RECEIPT.json','q2/SS2_RECEIPT.json']:
        inputs.add(SS/p);receipt=s8.load(SS/p)
        for field in ['inputs','auxiliary_inputs']:
            inputs|={Path(i['path']) for i in receipt.get(field,[])}
    inputs|=set((SS/'tools').glob('ss[1268]*.py'))
    hashes={str(p):q1.sha(p) for p in sorted(inputs)}
    print('Computing raw-text admission and diagnostics',flush=True)
    ids=s8.load(SS/'gate_recheck/foreign_mixed_ids_20261019.json');gate=set(ids['foreign'])|set(ids['mixed'])
    key=s8.rows(SS/'small_population_key.v2.jsonl.gz');smallids={r['row_id'] for r in key}
    assert len(key)==59002
    extra={};excluded=set(gate);mismatch=0;nfc=0;census_reasons=C.Counter();small_raw={}
    for row in q1.read_rows(q1.BASE/q1.INPUTS[0]):
        rid=row['row_id'];v=additions(row,rid in gate)
        census_reasons[v['reason'] or 'admitted']+=1
        mismatch+=numeric_grammar(row['raw_text'])!=row['is_numeric_output']
        if v['reason']: excluded.add(rid)
        if rid in smallids:
            extra[rid]=v;small_raw[rid]=row
            nfc+=short_line_exclusion(dict(row,raw_text=ud.normalize('NFC',row['raw_text'])))!=v['reason']
    for r in key:
        assert r['gate_failed']==(r['row_id'] in gate)
        assert r['A']<=6
    build_key(extra);verify_key()
    combined=[dict(r,**extra[r['row_id']]) for r in key]
    removed=[r for r in combined if not r['gate_failed'] and not r['admit']]
    survivors=[r for r in combined if r['survivor']]
    sample=s8.rows(SS/'samples.jsonl');marks=s8.rows(SS/'owner_marks_smallseg.jsonl')
    bedremoved=[r for r in sample if not r['control'] and r['line_id'] in {x['row_id'] for x in removed}]
    def counts(rs,k): return dict(C.Counter(r[k] for r in rs))
    text_removed=sum(r['output_type']!='numeric' for r in removed)
    cls=counts(bedremoved,'final_class')
    removal=dict(small_n=len(key),by_gate_and_reason=[dict(gate_failed=g,reason=reason,n=sum(r['gate_failed']==g and r['reason']==reason for r in combined)) for g in [False,True] for reason in [None]+REASONS],
        removed_non_gate=dict(n=len(removed),by_alnum={str(k):sum(r['alnum']==k for r in removed) for k in [0,1]},by_output_type=counts(removed,'output_type'),numeric=sum(r['output_type']=='numeric' for r in removed),text=text_removed,by_primary_class=counts(removed,'primary_class'),by_source=counts(removed,'source')),
        removed_bed=dict(n=len(bedremoved),by_final_class=cls,by_final_type=counts(bedremoved,'final_type')),
        estimated_population_by_final_class=[dict(final_class=c,sample_n=cls.get(c,0),removed_sample_share=cls.get(c,0)/len(bedremoved) if bedremoved else None,estimated_rows=text_removed*cls.get(c,0)/len(bedremoved) if bedremoved else None) for c in s8.q3.CLASSES],
        diagnostics=dict(census_numeric_grammar_disagrees_with_is_numeric_output=mismatch,small_NFC_admission_reason_changes=nfc,census_by_reason=dict(census_reasons)),survivors=dict(n=len(survivors),by_output_type=counts(survivors,'output_type')),gate_removed_small=sum(r['gate_failed'] for r in key))
    q1.write_json(OUT/'REMOVED.json',removal)
    (OUT/'REMOVED.md').write_text('# SS9 removals\n\n'+SCOPE+'. Raw Google text; dimensions width_px/height_px. No normalization, crop reading or new judgments. Gate failures are counted separately; single-character removal totals below exclude gate failures.\n\n'+table(removal['by_gate_and_reason'])+'\n\n'+three_table({}, {},removal['removed_non_gate'])+'\n\nRemoved rows in the 417 bed (non-gate only):\n\n'+three_table({}, {},removal['removed_bed'])+'\n\n**Estimate:** each class share among removed bed rows × removed population nonnumeric/mixed count. This is a sample projection, not observed population labels.\n\n'+table(removal['estimated_population_by_final_class'])+'\n\nDiagnostics:\n\n'+three_table({}, {},removal['diagnostics']))
    del small_raw
    print('Loading census metadata and recomputing all admitted Q1/Q2 tables',flush=True)
    df=s8.load_frame();owners,joined,replay=s8.owner_data(df)
    # Recompute original independently for exact off-rule/empty-gate regression.
    baseline=recompute(df,owners,joined,replay,sample,key,marks,set())
    q1.write_json(OUT/'RULE_OFF_EMPTY_GATE.json',baseline)
    after=recompute(df,owners,joined,replay,sample,key,marks,excluded)
    # SS9 owner requirement uses full survivor source pools, rather than SS3 residual pools.
    source_pools=dict(C.Counter(r['source'] for r in survivors if r['output_type']!='numeric'))
    selected=[r for r in sample if not r['control'] and r['stratum']=='inside_by_source' and r['line_id'] not in excluded]
    after['Q3']['source_pools']=source_pools;after['Q3']['pool_total']=sum(source_pools.values())
    after['Q3']['T8']={k:s8.weighted(selected,source_pools,k,cats) for k,cats in [('final_class',s8.q3.CLASSES),('final_type',s8.q3.ORDER)]}
    after['Q3']['owner_marks']=dict(C.Counter(r['owner_mark'] for r in marks if r['line_id'] in {x['row_id'] for x in survivors}))
    after['Q3'].pop('removed_from_pool')
    for n in [1,2,3]:
        orig=s8.load(SS/f'gate_recheck/Q{n}_GATE.json')['before'];gated=s8.load(SS/f'gate_recheck/Q{n}_GATE.json')['after'];new=after[f'Q{n}']
        result=dict(original=orig,gate_removed=gated,admitted_gate=new,delta_from_original=s8.compare(orig,new)['delta'],delta_from_gate=s8.compare(gated,new)['delta'])
        q1.write_json(OUT/f'Q{n}_R1.json',result)
        intro={1:'All candidate definitions and owner groups follow SS1/SS2 unchanged. Correctly sized means the SS1 metadata proxy box_fail=false; pct_nonKEEP is the failure rate on those crops. No new crop judgments. Percentages are 0–100. Owner rows remaining are included below.',2:'Recommended definition: chars ≤ 8 & A ≤ 6. Shares, density and page measures use each column’s census. Book concentration baseline is recomputed within each census. All G1–G6 measures and page/book identities are retained.',3:'T8 before/after/delta covers final_class and final_type. Shares are 0–1. New Wilson 95% intervals describe unweighted shares only. Original and SS8 use their saved residual source pools; SS9 uses full survivor nonnumeric/mixed small counts per source, as requested. Thus deltas combine filtering and this pool-frame change. Bed/inside counts and label_ok use saved labels only; owner marks are restricted to survivors.'}[n]
        content=f'# Q{n} SS9\n\n{SCOPE}.\n\n{intro}\n\n'+three_table(orig,gated,new)
        if n==1:
            filtered=s8.subset(df,owners,joined,replay,excluded)
            ownerrows=filtered[1]
            q1.write_json(OUT/'OWNER_LINES_R1.json',ownerrows)
            content+='\n\nOwner-judged lines remaining (metadata only):\n\n'+table([{k:r.get(k) for k in ['line_id','census_index','owner_good','owner_bad','owner_conflict','verdict_05']} for r in ownerrows])
        if n==3: content+='\n\nBefore / after / delta (after = SS9):\n\n'+table(s8.comparison_table(orig,new))
        (OUT/f'Q{n}_R1.md').write_text(content)
    print('Running SS9 verification',flush=True)
    tmp=OUT/'tmp';env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',TMPDIR=str(tmp.resolve()))
    test=subprocess.run([sys.executable,'-B','-m','pytest','-c','/dev/null','-p','no:cacheprovider','--basetemp',str(tmp/'pytest'),str(SS/'tests/test_ss9.py'),'-q'],capture_output=True,text=True,env=env)
    (OUT/'tests.log').write_text(test.stdout+test.stderr);shutil.rmtree(tmp)
    afterhash={p:q1.sha(p) for p in hashes};unchanged=hashes==afterhash
    ready=test.returncode==0 and unchanged
    types=removal['survivors']['by_output_type'];rn=removal['removed_non_gate']['numeric']
    final=f"SS9 READY: small 59002 → survivors {len(survivors)} (numeric {types.get('numeric',0)}, mixed {types.get('mixed',0)}, nonnumeric {types.get('nonnumeric',0)}); single-char rule removes {len(removed)} (numeric {rn}, text {text_removed}), gate removes {removal['gate_removed_small']}" if ready else 'SS9 FAILED: tests or input integrity; see receipt'
    outputs=[p for p in OUT.rglob('*') if p.is_file()]+[SS/'small_population_key.v3.jsonl.gz',Path(__file__),SS/'tests/test_ss9.py']
    census=str(q1.BASE/q1.INPUTS[0])
    receipt=dict(status='READY' if ready else 'FAILED',inputs=[dict(path=p,sha256=h,sha256_after=afterhash[p]) for p,h in hashes.items()],outputs=[dict(path=str(p),sha256=q1.sha(p)) for p in outputs],counts=removal,tests=dict(returncode=test.returncode,output=test.stdout+test.stderr),census_sha256_before=hashes[census],census_sha256_after=afterhash[census],input_hashes_unchanged=unchanged,gzip_mtime=0,v2_fields_byte_identical=True,temporary_files_removed=not tmp.exists(),numeric_parity_method='AST extraction of reference numeric_text only; no module import',python=sys.executable,final_line=final,receipt_self_hash='excluded to avoid circular hash')
    q1.write_json(OUT/'SS9_RECEIPT.json',receipt)
    print(final,flush=True)
    if not ready: raise RuntimeError(final)

if __name__=='__main__': main()
