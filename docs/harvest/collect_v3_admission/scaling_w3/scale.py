#!/usr/bin/env python3
"""SCALE1 fail-closed unique-row preparation. Standard library only."""
import argparse
import ast
from collections import Counter, defaultdict, deque
from fractions import Fraction
import gzip
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import random
import re
import sys

HERE = Path(__file__).resolve().parent
W = Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3')
VC = 'collection-v2-train'
CODE_SHA = 'aa950a88f02b083ce4ffb0739c70183000048b9167f7ca8bf99f50ba9d1faff1'
TAG_PRODUCER_SHA = '3de88fc645d2b165191094ec5244bf56d5ee7286189218f40b2383cd33f3adea'
TAG_PATH_SHA = 'a962ebfd13d812366f90a1e6329af01bd28e44655e6b67e3080fb70b0df2ff64'
TAG_FUNCTIONS = ['require', 'sha', 'info', 'dump', 'rows', 'key', 'classifier', 'inputs', 'census_row', 'relative_flags', 'tag_job']
REF_SEED = 'scale1:reference:20261020'
CLASS_SEED = 'scale1:target:20261020:'

def require(ok, message):
    if not ok: raise ValueError(message)

def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def info(p):
    p=Path(p); return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)

def dump(p,d):
    Path(p).write_text(json.dumps(d,ensure_ascii=False,sort_keys=True,indent=2)+'\n')

def rows(p):
    p=Path(p)
    with (gzip.open(p,'rt',encoding='utf-8') if p.suffix=='.gz' else p.open(encoding='utf-8')) as f:
        for line in f:
            require(bool(line.strip()),'blank JSONL row'); yield json.loads(line)

def key(r): return (r['parent_id'],r.get('row_id',r.get('id')))

def classifier():
    p=HERE/'vendor/bench02_draw.py'; require(sha(p)==CODE_SHA,'classifier SHA mismatch')
    spec=importlib.util.spec_from_file_location('scale_bench02',p)
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def quotas():
    d=json.loads((HERE/'vendor/counts.json').read_text())
    q={k.split(':',1)[1]:v['quota'] for k,v in d['classes'].items() if k.startswith('test:')}
    require(len(q)==16 and sum(q.values())==2460,'benchmark quotas mismatch')
    order=classifier().PRECEDENCE; require(set(order)==set(q),'quota classes mismatch')
    return {c:q[c] for c in order}

def inputs(mode, full=False):
    manifest=json.loads((HERE/'inputs.json').read_text())
    names={'admitted_train','live_CURRENT','live_summary'} if mode=='tags' else {x['name'] for x in manifest}
    result={}
    for x in manifest:
        if x['name'] not in names: continue
        p=Path(x['path']); require(p.is_file(),f'missing input {p}')
        require(p.stat().st_size==x['bytes'],f'input size mismatch {p}')
        if full or x['kind']=='small': require(sha(p)==x['sha256'],f'input SHA mismatch {p}')
        result[x['name']]=x
    summary=json.loads(Path(result['live_summary']['path']).read_text())
    vc=sum(x['rows'] for x in summary['by_stratum'] if x['parent']==VC and x['disposition']=='ADMIT' and x['split']=='train')
    require(vc==196234,'summary v_c count mismatch')
    if 'release_receipt' in result:
        rec=json.loads(Path(result['release_receipt']['path']).read_text())
        require(rec['status']=='ok' and rec['counts']['released']==168637,'release receipt count/status mismatch')
        expected=rec['outputs']['release_v3_admission.jsonl']
        require(all(expected[k]==result['release'][k] for k in ('sha256','bytes')),'release receipt input mismatch')
    return result

def census_row(r,m):
    d=r['decision']; k=key(r)
    require(k==m.key(d),'census decision key mismatch')
    require(d.get('admitted') is True and d['disposition']=='ADMIT','non-admitted train row')
    require(r['split']=='train' and d['binding']['split']=='train','non-train row')
    require(k[0]==VC or m.w12(k[0]),'unexpected parent')
    require(r['crop_sha256']==d['binding']['crop_sha256'],'decision crop mismatch')
    require(r['final_text']==d['final_text'],'census final_text conflict')
    require(isinstance(k[1],str) and bool(k[1]),'missing key')
    require(r.get('source') and r.get('edition_id') and Path(r['crop_path']).is_absolute(),'missing source/edition/absolute crop')
    return m.slim(d,r)

def relative_flags(populations):
    flagged=set(); report={}
    for source,pop in sorted(populations.items()):
        ranked=sorted((x for x in pop if x[0] is not None),key=lambda x:(x[0],x[1]))
        picked=ranked[:math.ceil(.05*len(pop))]; flagged.update(k for _,k in picked)
        report[source]=dict(population=len(pop),ranked=len(ranked),flagged=len(picked),missing_confidence=len(pop)-len(ranked))
    return flagged,report

def tag_job(dest, _vc_expected=196234):
    bound=inputs('tags',True); m=classifier(); p=bound['admitted_train']['path']
    dest=Path(dest); dest.mkdir(parents=True,exist_ok=False)
    populations=defaultdict(list); seen=set()
    # Two streamed passes; only compact confidence/key populations retained in pass one.
    for r in rows(p):
        s=census_row(r,m); k=key(s); require(k not in seen,'duplicate census key'); seen.add(k)
        populations[r['source']].append((s['evidence'].get('confidence'),k))
    flagged,report=relative_flags(populations); del populations,seen
    counts=defaultdict(Counter); availability=defaultdict(lambda:defaultdict(Counter)); n=0
    out=dest/'train_tags.jsonl.gz'
    with out.open('wb') as raw, gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as f:
        for r in rows(p):
            s=census_row(r,m); t=m.tag(s,relative_flag=key(s) in flagged)
            parent=r['parent_id']; counts[parent][t['primary_class'] or 'unclassified']+=1
            for field in m.FEATURES:
                value=s['evidence'].get(field)
                availability[parent]['evidence.'+field]['unavailable' if value is None else 'available']+=1
            for field in ('crop_bbox','doc','book_id','edition_id','crop_path','crop_sha256','final_text'):
                availability[parent]['census.'+field]['unavailable' if r.get(field) is None else 'available']+=1
            for field in ('greek_letters','latin_letters','cyrillic_letters','letter_count','observed_scripts','characters','mixed_words','numeric','has_upper','has_lower','punctuation_share','orthography','cyrillic_orthography','scripts','languages'):
                value=s['text_facets'].get(field)
                availability[parent]['text_facets.'+field]['unavailable' if value is None else 'available']+=1
            for field,value in t['tags'].items():
                availability[parent]['tags.'+field]['unavailable' if value=='unavailable' or value is None else 'available']+=1
            o=dict(parent_id=parent,row_id=key(s)[1],key=list(key(s)),source=t['source'],edition_id=r['edition_id'],doc=r.get('doc',r.get('book_id')),primary_class=t['primary_class'],tags=t['tags'],crop_path=r['crop_path'],crop_sha256=r['crop_sha256'])
            f.write((json.dumps(o,ensure_ascii=False,sort_keys=True)+'\n').encode()); n+=1
    require(sum(counts[VC].values())==_vc_expected,'v_c population mismatch')
    dump(dest/'TAGS_RECEIPT.json',dict(status='ok',output=info(out),inputs=bound,code_sha=CODE_SHA,wrapper_sha=sha(__file__),benchmark_counts=info(HERE/'vendor/counts.json'),rows=n,per_parent_class=counts,availability=availability,relative_degraded=dict(population='all admitted train rows, both parents, grouped by source',ranking='(confidence,(parent_id,row_id)); first ceil(.05 * population); missing confidence never ranked',sources=report)))

def reference(pool):
    rr=sorted(pool,key=key); random.Random(REF_SEED).shuffle(rr); return rr

def rotation(pool,cl):
    rng=random.Random(CLASS_SEED+cl); groups=defaultdict(lambda:defaultdict(list))
    for r in pool: groups[r['source']][r['edition_id']].append(r)
    sources=sorted(groups); rng.shuffle(sources); queues={}
    for s in sources:
        es=sorted(groups[s]); rng.shuffle(es); queues[s]=deque(es)
        for e in es:
            rr=sorted(groups[s][e],key=key); rng.shuffle(rr); groups[s][e]=deque(rr)
    selected=[]
    while any(queues.values()):
        for s in sources:
            q=queues[s]
            if not q: continue
            e=q.popleft(); rr=groups[s][e]; selected.append(rr.popleft())
            if rr:q.append(e)
    return selected

def allocation(supply,q,n):
    # Exact rational water filling; bind saturated classes then renormalize original weights.
    active=[c for c in q if supply.get(c,0)>0]; fixed={c:0 for c in q}; left=n; trace=[]
    while active:
        weight=sum(q[c] for c in active)
        ideal={c:Fraction(left*q[c],weight) for c in active}
        short=[c for c in active if supply[c]<=ideal[c]]
        trace.append(dict(remaining=left,active=active[:],ideal={c:str(v) for c,v in ideal.items()},exhausted=short))
        if short:
            for c in short: fixed[c]=supply[c]; left-=supply[c]
            active=[c for c in active if c not in short]; continue
        ints={c:int(v) for c,v in ideal.items()}; extra=left-sum(ints.values())
        order=sorted(active,key=lambda c:(-(ideal[c]-ints[c]),list(q).index(c)))
        for c in order[:extra]:ints[c]+=1
        fixed.update(ints); left=0; break
    return fixed,left,trace

def targeted(ref,q,n):
    groups=defaultdict(list)
    for r in ref:
        require(r['primary_class'] is None or r['primary_class'] in q,'unknown primary class')
        if r['primary_class']:groups[r['primary_class']].append(r)
    alloc,fill,trace=allocation({c:len(v) for c,v in groups.items()},q,n)
    out=[]
    for c in q:out.extend(rotation(groups[c],c)[:alloc[c]])
    out.extend([r for r in ref if r['primary_class'] is None][:fill])
    require(len(out)==n,'insufficient universe'); require(len({key(r) for r in out})==n,'target duplicate')
    return out,dict(allocations=alloc,unclassified_fill=fill,redistribution_trace=trace)

def resolve_crop(census, release=None):
    """Bind subset crops to REL3 originals for W1/W2, census for v_c."""
    k=key(census)
    require(census['crop_sha256']==census['decision']['binding']['crop_sha256'],'decision crop mismatch')
    if k[0]==VC:
        return dict(crop_path=census['crop_path'],crop_sha256=census['crop_sha256'])
    require(re.fullmatch(r'collect-v3-W[12]-.*',k[0]) is not None,'unexpected crop parent')
    require(release is not None and key(release)==k,'release crop key mismatch')
    for field in ('source','edition_id'):
        require(release[field]==census[field],'release/census mismatch '+field)
    require(release['crop_sha256']==census['decision']['binding']['crop_sha256'],'release/decision crop mismatch')
    relative=Path(release['crop_relative_path'])
    original='collection_w1_originals' if k[0].startswith('collect-v3-W1-') else 'collection_w2_originals'
    require(not relative.is_absolute() and '..' not in relative.parts and relative.parts==
            (original,census['source'],k[1]+'.png'),'invalid REL3 crop relative path')
    path=W/relative
    require(str(path)!=census['crop_path'],'W1/W2 resolved to census crop_path')
    return dict(crop_path=str(path),crop_sha256=release['crop_sha256'])

def tag_path_sha():
    source=Path(__file__).read_text()
    tree=ast.parse(source)
    return hashlib.sha256('\n'.join(ast.get_source_segment(source,n) for n in tree.body
        if isinstance(n,ast.FunctionDef) and n.name in TAG_FUNCTIONS).encode()).hexdigest()

def vc_row(r,t):
    require(r['final_text']==r['decision']['final_text'],'v_c label conflict')
    for field in ('crop_path','crop_sha256','edition_id','source'):
        require(r[field]==t[field],f'v_c tag mismatch {field}')
    return dict(t,label=r['final_text'],doc=r['doc'],**resolve_crop(r))

def exposure(pool,blocked,bkeys,bhashes,vdocs):
    count=Counter(dict(dev_test_editions=0,benchmark_keys=0,benchmark_crop_hashes=0,v2_dev_test_docs=0,crops_rehashed=0))
    for r in pool:
        count['dev_test_editions']+=r['edition_id'] in blocked
        count['benchmark_keys']+=key(r) in bkeys
        count['benchmark_crop_hashes']+=r['crop_sha256'] in bhashes
        count['v2_dev_test_docs']+=r['parent_id']==VC and r['doc'] in vdocs
    for field in ('dev_test_editions','benchmark_keys','benchmark_crop_hashes','v2_dev_test_docs'):
        require(count[field]==0,'exposure: '+field)
    for r in pool:
        p=Path(r['crop_path']); require(p.is_file(),'missing crop '+str(p))
        require(sha(p)==r['crop_sha256'],'crop SHA mismatch '+str(p)); count['crops_rehashed']+=1
    return dict(count)

def tags_binding(receipt,expected,full):
    receipt=Path(receipt); require(re.fullmatch('[0-9a-f]{64}',expected) is not None,'invalid tags receipt SHA')
    require(sha(receipt)==expected,'tags receipt SHA mismatch'); d=json.loads(receipt.read_text())
    require(d['status']=='ok' and d['code_sha']==CODE_SHA and (d['wrapper_sha']==sha(__file__) or (d['wrapper_sha']==TAG_PRODUCER_SHA and tag_path_sha()==TAG_PATH_SHA)),'tags receipt status/code mismatch')
    for name,x in d['inputs'].items():
        require(x==next(y for y in json.loads((HERE/'inputs.json').read_text()) if y['name']==name),'tags input binding mismatch')
    require(set(d['inputs'])=={'admitted_train','live_CURRENT','live_summary'},'incomplete tags inputs')
    p=receipt.parent/'train_tags.jsonl.gz'; require(str(p)==d['output']['path'],'tags output location mismatch')
    require(p.stat().st_size==d['output']['bytes'],'tags size mismatch')
    if full:require(sha(p)==d['output']['sha256'],'tags SHA mismatch')
    return d,p

def build_job(dest,receipt,expected, _expected=(168637,196234,364871), _size=208000):
    bound=inputs('subsets',True)
    release_receipt=json.loads(Path(bound['release_receipt']['path']).read_text())
    require(release_receipt['status']=='ok','release receipt status')
    release_output=release_receipt['outputs']['release_v3_admission.jsonl']
    require(all(release_output[k]==bound['release'][k] for k in ('sha256','bytes')),'release receipt binding mismatch')
    rec,tp=tags_binding(receipt,expected,True); m=classifier(); q=quotas()
    tags={}
    for t in rows(tp):
        require(key(t) not in tags,'duplicate tag'); tags[key(t)]=t
    require(len(tags)==rec['rows'],'tags row count mismatch')
    universe={}; release_bindings={}; release_count=0
    for r in rows(bound['release']['path']):
        k=key(r); require(m.w12(k[0]) and r['split']=='train','release parent/split')
        require(k in tags and k not in universe,'release key missing/duplicate'); t=tags[k]
        for field in ('source','edition_id','crop_sha256'): require(t[field]==r[field],'release/tag mismatch '+field)
        universe[k]=dict(t,label=r['label']); release_count+=1
        release_bindings[k]={f:r[f] for f in ('parent_id','row_id','source','edition_id','crop_relative_path','crop_sha256')}
    vc_count=0
    for r in rows(bound['admitted_train']['path']):
        if r['parent_id']!=VC:
            k=key(r)
            if k in universe:
                census_row(r,m)
                require(k in release_bindings,'duplicate release census key')
                universe[k].update(resolve_crop(r,release_bindings.pop(k)))
            continue
        census_row(r,m); k=key(r); require(k in tags and k not in universe,'v_c key missing/duplicate')
        universe[k]=vc_row(r,tags[k]); vc_count+=1
    require(not release_bindings,'release census binding missing')
    require((release_count,vc_count,len(universe))==_expected,'universe counts mismatch')
    del tags
    blocked=set(); splits={}
    for r in rows(bound['edition_map.jsonl']['path']):
        e=r['edition_id']; require(e not in splits,'duplicate edition'); splits[e]=r['split']
        if r['split'] in ('dev','test'):blocked.add(e)
    seen=set()
    for r in rows(bound['row_split.jsonl.gz']['path']):
        k=key(r); require(k not in seen,'duplicate split key'); seen.add(k)
        require(r['edition_id'] in splits and splits[r['edition_id']]==r['split'],'split/edition conflict')
        if r['split'] in ('dev','test'): blocked.add(r['edition_id'])
        if k in universe:
            require(universe[k]['edition_id']==r['edition_id'] and r['split']=='train','universe split conflict')
    require(all(k in seen for k in universe if m.w12(k[0])),'release split key missing')
    candidates=list(rows(bound['candidates_v3.jsonl']['path'])); readout=list(rows(bound['candidates_readout.jsonl']['path']))
    bkeys={key(r) for r in candidates}; require(len(bkeys)==len(candidates),'duplicate benchmark key')
    require({key(r) for r in readout}==bkeys and len(readout)==len(bkeys),'benchmark readout keys mismatch')
    bhashes={r['crop_sha256'] for r in readout}
    bhashes.update(r['crop_sha256'] for r in candidates if r.get('crop_sha256'))
    vdocs=set()
    for name in ('v2_dev','v2_test'):
        for r in rows(bound[name]['path']):require(bool(r.get('doc')),'missing v2 doc'); vdocs.add(r['doc'])
    ref=reference(universe.values()); tgt,report=targeted(ref,q,_size)
    subsets={'ref_208k':ref[:_size],'ref_364871':ref,'tgt_208k':tgt}
    require({key(r) for r in subsets['ref_208k']} < {key(r) for r in ref},'prefix nesting failed')
    dest=Path(dest);dest.mkdir(parents=True,exist_ok=False); results={}
    for name,pool in subsets.items():
        audit=exposure(pool,blocked,bkeys,bhashes,vdocs); out=dest/(name+'.jsonl')
        with out.open('w',encoding='utf-8') as f:
            for r in pool:
                o={k:r[k] for k in ('key','parent_id','row_id','source','primary_class','label','crop_path','crop_sha256')}
                f.write(json.dumps(o,ensure_ascii=False,sort_keys=True)+'\n')
        results[name]=dict(output=info(out),rows=len(pool),per_parent=Counter(r['parent_id'] for r in pool),per_source=Counter(r['source'] for r in pool),per_primary_class=Counter(r['primary_class'] or 'unclassified' for r in pool),audit=audit)
    plan=dict(reference_seed=REF_SEED,class_seed=CLASS_SEED+'<class>',class_order=list(q),target_shares={c:dict(quota=q[c],denominator=2460,share=q[c]/2460,target_count=q[c]*208000/2460) for c in q},rounding='exact rational water filling: saturate supply <= ideal; renormalize original test-quota weights over unsaturated classes; final largest remainder, ties in class_order',rotation='one RNG per class: shuffle sorted sources, then sorted editions/source, then sorted (parent_id,row_id) rows/edition; one row/source/round, persistent edition cursor',edition_cap=None,series_cap=None,reference='sort (parent_id,row_id), Random(reference_seed).shuffle; prefixes',emission='class_order concatenation of class rotations; unclassified fill appended in reference order',maximum_label='actual maximum; targeted = reference at full universe',**report)
    dump(dest/'subsets_plan.json',plan)
    dump(dest/'SUBSETS_RECEIPT.json',dict(status='ok',inputs=bound,tags_receipt=info(receipt),tags=rec['output'],code=info(__file__),classifier_sha=CODE_SHA,benchmark_counts=info(HERE/'vendor/counts.json'),subsets=results,nesting=True,target_shares=plan['target_shares'],targeted=report,plan=info(dest/'subsets_plan.json')))

def verify(mode,receipt=None,expected=None):
    if mode=='package':
        lines=(HERE/'DEPLOY_SHA256SUMS').read_text().splitlines()
        for line in lines:
            digest,name=line.split('  ',1); require(sha(HERE/name)==digest,'package SHA '+name)
        require(set((HERE/'DEPLOY_PATHS.txt').read_text().splitlines())=={line.split('  ',1)[1] for line in lines}|{'DEPLOY_SHA256SUMS','DEPLOY_PATHS.txt'},'package path manifest mismatch')
        classifier();quotas();print('VERIFY package ok',len(lines));return
    bound=inputs(mode.removeprefix('inputs-')); print(f'VERIFY {mode} {len(bound)}/{len(bound)} (large files: existence/bytes only)')
    if mode=='inputs-subsets':
        if not receipt:print('tags output PENDING; subsets pending tags job');return
        require(expected is not None,'tags receipt sha required'); tags_binding(receipt,expected,False);print('tags receipt SHA and tags size ok; tags SHA deferred to job')

def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=['tags','subsets','verify']);p.add_argument('--mode');p.add_argument('--output');p.add_argument('--tags-receipt');p.add_argument('--tags-receipt-sha');a=p.parse_args()
    if a.command=='verify':verify(a.mode,a.tags_receipt,a.tags_receipt_sha)
    else:
        require(a.output and Path(a.output).is_absolute(),'absolute output required')
        if a.command=='tags':tag_job(a.output)
        else:build_job(a.output,a.tags_receipt,a.tags_receipt_sha)
if __name__=='__main__':main()
