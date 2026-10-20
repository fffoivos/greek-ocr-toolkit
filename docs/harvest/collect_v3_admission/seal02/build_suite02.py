#!/usr/bin/env python3
"""Fail-closed benchmark 0.2 adapter. Standard library only; no inference/scoring."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import importlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parent
W = Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3')
ROLES = ('candidates','draw_plan','counts','readout','tags_receipt','census_current',
         'census_summary','final_list','final_receipt','verdicts','w1_receipt','w2_receipt')
PENDING = ('final_list','final_receipt','verdicts','w1_receipt','w2_receipt')
HEX = re.compile(r'^[0-9a-f]{64}$')

def need(ok, message):
    if not ok: raise ValueError(message)

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024), b''): h.update(b)
    return h.hexdigest()

def load(path):
    return json.loads(Path(path).read_bytes())

def rows(path):
    return [json.loads(b) for b in Path(path).read_bytes().splitlines() if b.strip()]

def encoded(obj):
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',',':'), allow_nan=False)+'\n').encode('utf-8')

def dump(path, obj):
    Path(path).write_bytes(encoded(obj))

def jsonl(path, records):
    Path(path).write_bytes(b''.join(encoded(r) for r in records))

def key(r): return (r['parent_id'], r['row_id'])

def index(records):
    d = {key(r):r for r in records}
    need(len(d)==len(records), 'duplicate parent/row key')
    need(len({r['row_id'] for r in records})==len(records), 'row_id is not globally unique (0.1 IDs)')
    return d

def resolve(config_path):
    c = load(config_path)
    need(set(c['inputs'])==set(ROLES), 'input role set differs')
    for e in c['inputs'].values():
        p = Path(e['path'])
        e['path'] = str(p if p.is_absolute() else Path(config_path).resolve().parent/p)
    return c

def scope_quotas(plan):
    result = {}
    for split, name in [('test','quotas'), ('dev','dev_quotas')]:
        for cl, q in plan[name].items():
            subs = plan.get('subquotas',{}).get(split,{}).get(cl,{})
            if subs:
                for sub, n in subs.items(): result[f'{split}:{cl}:{sub}']=n
            else: result[f'{split}:{cl}']=q
    return result

def candidates_checked(candidates, plan):
    idx=index(candidates); limits=scope_quotas(plan)
    seen=defaultdict(set)
    for r in candidates:
        scope=r['quota_scope']; parts=scope.split(':')
        need(scope in limits and parts[:2]==[r['split'],r['class']], 'invalid scope')
        if len(parts)==3:
            field={'font_extremes':'font_size','modern_cyrillic':'cyrillic_language'}[r['class']]
            need(r['tags'][field]==parts[2], 'subgroup differs')
        rank=r['scope_rank']
        need(type(rank) is int and rank>0 and rank not in seen[scope], 'duplicate/invalid scope rank')
        seen[scope].add(rank)
        need(r['in_quota'] is (rank<=limits[scope]), 'rank/quota boundary differs')
    return idx

def image_path(c, r):
    parent=r['parent_id']
    need(parent.startswith(('collect-v3-W1-','collect-v3-W2-')), 'unknown crop tranche')
    tranche='W1' if parent.startswith('collect-v3-W1-') else 'W2'
    for s in (r['source'],r['row_id']):
        need(s and Path(s).name==s and s not in ('.','..'), 'unsafe crop component')
    return Path(c['image_roots'][tranche])/r['source']/(r['row_id']+'.png')

def receipt_checked(role, rec, c):
    if role=='census_current':
        need(rec['status']=='completed', 'census not completed')
        need(rec['summary_sha256']==c['inputs']['census_summary']['sha256'], 'census summary binding differs')
    elif role=='census_summary':
        need(rec['complete'] is True, 'census summary incomplete')
    elif role in ('w1_receipt','w2_receipt'):
        tranche='W1' if role=='w1_receipt' else 'W2'
        need(rec['status']=='ok' and rec['mode']=='full' and rec['mismatches']==0 and rec['failures']==0
             and rec['sha256check_exit']==0 and rec['selected']==rec['byte_exact'], 'CROPS4 not complete/byte exact')
        need(Path(rec['output_base'])/('collection_'+tranche.lower()+'_originals')==Path(c['image_roots'][tranche]) and rec['context']['tranche']==tranche and rec['context']['include_heldout'] is True, 'CROPS4 output root/tranche/heldout differs')
        need(rec['context']['inputs']['summary.json']==c['inputs']['census_summary']['sha256'], 'CROPS4 census differs')
        manifest=Path(c['inputs'][role]['path']).parent/'crops_sha256.txt'
        try:
            entries=manifest.read_text().splitlines()
        except (FileNotFoundError, PermissionError):
            print('CROPS4_PREFIX_CHECK_SKIPPED: '+str(manifest)+' (unavailable)',file=sys.stderr)
        else:
            prefix='collection_'+tranche.lower()+'_originals/'
            need(bool(entries) and all(len(line.split('  ',1))==2 and line.split('  ',1)[1].startswith(prefix)
                 for line in entries), 'CROPS4 crop manifest prefix differs')

def verify_inputs(config_path, *, partial=False):
    start=time.monotonic(); c=resolve(config_path); bound=[];pending=[];observed={}
    for role in ROLES:
        e=c['inputs'][role]; p=Path(e['path']); expected=e['sha256']
        if expected is None or not p.is_file():
            need(partial, 'missing or unbound input: '+role)
            pending.append(role)
            if p.is_file(): observed[role]=sha(p)
            continue
        need(isinstance(expected,str) and HEX.fullmatch(expected), 'invalid input SHA: '+role)
        need(sha(p)==expected, 'input hash differs: '+role)
        if role in ('census_current','census_summary','w1_receipt','w2_receipt'):
            receipt_checked(role,load(p),c)
        bound.append(role)
    if {'census_current','census_summary','tags_receipt'} <= set(bound):
        current=load(c['inputs']['census_current']['path']); summary=load(c['inputs']['census_summary']['path'])
        need(current['export_id']==summary['export_id'], 'census generation differs')
        tags=load(c['inputs']['tags_receipt']['path'])
        for path,digest in tags['input_shas'].items():
            name=Path(path).stem
            need(summary['outputs'][name]['sha256']==digest, 'tags census provenance differs')
    # Never read census JSONL files, corpus shards, source pages, or tags population.
    cs=rows(c['inputs']['candidates']['path']); readout=index(rows(c['inputs']['readout']['path']))
    candidates_checked(cs,load(c['inputs']['draw_plan']['path']))
    need(set(readout)==set(index(cs)), 'candidate/readout join differs')
    images=Counter(); byte_count=0
    for r in cs:
        p=image_path(c,r)
        if not p.is_file(): images['pending']+=1; continue
        need(sha(p)==readout[key(r)]['crop_sha256'], 'image hash differs: '+r['row_id'])
        images['ok']+=1;byte_count+=p.stat().st_size
    if not partial: need(not images['pending'], 'missing candidate images')
    return c,dict(bound=len(bound),total=len(ROLES),bound_roles=bound,pending=pending,
                  observed_unbound_shas=observed,images=dict(images),image_bytes=byte_count,
                  seconds=time.monotonic()-start)

def final_checked(c, cs, mock):
    inp=c['inputs']; fr=rows(inp['final_list']['path']); rc=load(inp['final_receipt']['path'])
    need(set(rc)=={'status','mock','final_list_sha256','verdicts_sha256','candidates_sha256','counts'}, 'final receipt interface differs')
    need(rc.get('mock',False) is mock, 'MOCK/production final receipt mismatch')
    need(rc['final_list_sha256']==inp['final_list']['sha256'] and rc['verdicts_sha256']==inp['verdicts']['sha256'], 'final receipt SHA differs')
    need(rc['candidates_sha256']==inp['candidates']['sha256'], 'final receipt draw differs')
    need(rc['status']=='FINALIZED', 'final list not finalized')
    need(set(rc['counts'])=={'flagged','REPLACED','UNFILLED'}, 'final receipt count interface differs')
    need(all(type(rc['counts'][k]) is int and rc['counts'][k]>=0 for k in ('flagged','REPLACED','UNFILLED')), 'invalid final counts')
    # LF1 line_id=row_id: preserve ledger evidence verbatim, never use readings as labels.
    vs=rows(inp['verdicts']['path']); vd={v['line_id']:v for v in vs}
    need(len(vd)==len(vs) and set(vd)=={r['row_id'] for r in cs}, 'LF1 ledger incomplete/duplicate/foreign')
    if not mock: need(not any(v.get('mock') for v in vs), 'MOCK LF1 evidence forbidden')
    groups=defaultdict(list)
    for r in cs: groups[r['quota_scope']].append(r)
    expected={}; counts=Counter(); unfilled=[]
    for scope, group in sorted(groups.items()):
        reserve=sorted((r for r in group if not r['in_quota']),key=lambda r:r['scope_rank'])
        used=set()
        for old in sorted((r for r in group if r['in_quota']),key=lambda r:r['scope_rank']):
            if vd[old['row_id']]['verdict']=='OK':
                expected[key(old)]=(old,None);continue
            counts['flagged']+=1
            replacement=next((r for r in reserve if key(r) not in used and r['source']==old['source'] and vd[r['row_id']]['verdict']=='OK'),None)
            if replacement is None:
                counts['UNFILLED']+=1;unfilled.append(dict(parent_id=old['parent_id'],row_id=old['row_id'],quota_scope=scope));continue
            used.add(key(replacement));counts['REPLACED']+=1
            expected[key(replacement)]=(replacement,dict(parent_id=old['parent_id'],row_id=old['row_id']))
    need(rc['counts']=={k:counts[k] for k in ('flagged','REPLACED','UNFILLED')}, 'final receipt counts differ')
    fi=index(fr);need(set(fi)==set(expected), 'final selection/replacement order differs')
    for k, r in fi.items():
        need(set(r)=={'parent_id','row_id','split','quota_scope','lf1_verdict','replaces','lf1_receipt_ref','mock'}, 'final row interface differs')
        need(r['mock'] is mock, 'MOCK row forbidden')
        candidate,replaces=expected[k]
        need(r['lf1_verdict']=='OK' and vd[r['row_id']]['verdict']=='OK', 'non-OK final verdict')
        need(r['split']==candidate['split'] and r['quota_scope']==candidate['quota_scope'], 'final scope differs')
        need(isinstance(r['lf1_receipt_ref'],dict), 'invalid LF1 reference')
        need(r['replaces']==replaces, 'replacement must match split, class, scope, source and reserve rank')
        need(r['lf1_receipt_ref']==dict(verdicts_sha256=inp['verdicts']['sha256'],line_id=r['row_id']), 'LF1 receipt ref differs')
    return fi,rc,vd,unfilled

def pixel_overlap_checked(panel_rows, scope_counts):
    """Apply the dev-drop ruling, then reject duplicates in either retained panel.

    Cross-panel drops take precedence: multiple dev copies of a test image are
    all deficits. Inputs are not mutated; order and unaffected counts stay exact.
    """
    identity=lambda r: {k:r[k] for k in ('parent_id','row_id','split','quota_scope')}
    test_images=defaultdict(list)
    for r in panel_rows['test']: test_images[r['image_sha256']].append(r)
    retained={split:list(panel_rows[split]) for split in ('test','dev')}
    retained['dev']=[]; drops=[]
    adjusted={scope:dict(counts) for scope,counts in scope_counts.items()}
    for r in panel_rows['dev']:
        digest=r['image_sha256']
        if digest not in test_images:
            retained['dev'].append(r);continue
        drops.append(dict(image_sha256=digest,dropped=identity(r),
                          kept=[identity(t) for t in test_images[digest]]))
        counts=adjusted[r['quota_scope']]
        counts['sealed']-=1;counts['deficit']+=1
        counts['pixel_duplicate_drops']=counts.get('pixel_duplicate_drops',0)+1
    for split,records in retained.items():
        grouped=defaultdict(list)
        for r in records: grouped[r['image_sha256']].append(r)
        duplicates={digest:[identity(r) for r in group]
                    for digest,group in grouped.items() if len(group)>1}
        need(not duplicates, 'duplicate image within panel '+split+': '+
             json.dumps(duplicates,sort_keys=True))
    return retained,drops,adjusted

def verify_package():
    # Parse own package manifest, refusing traversal. No bytecode writes.
    for line in (ROOT/'DEPLOY_SHA256SUMS').read_text().splitlines():
        digest, rel=line.split('  ',1); p=ROOT/rel
        need(not Path(rel).is_absolute() and '..' not in Path(rel).parts, 'unsafe deploy path')
        need(sha(p)==digest, 'package hash differs: '+rel)
    sys.path.insert(0,str(ROOT/'v01'))
    for module in ('bench.benchmark_suite','bench.score','bench.common','train.cer'):
        importlib.import_module(module)
    baseline=load(ROOT/'V01_BINDING.json')
    for rel,digest in baseline['files'].items(): need(sha(ROOT/'v01'/rel)==digest, '0.1 code differs: '+rel)
    return dict(status='ok',python=sys.executable,python_sha256=sha(sys.executable),version=sys.version.split()[0],imports='ok')

def build(config_path, output, *, mock=False):
    need(Path(output).is_absolute(), '--output must be absolute')
    output=Path(output);need(not output.exists(), 'output already exists')
    c,verification=verify_inputs(config_path)
    need(c.get('mock',False) is mock,'MOCK configuration forbidden')
    cs=rows(c['inputs']['candidates']['path']); plan=load(c['inputs']['draw_plan']['path'])
    ci=candidates_checked(cs,plan); ri=index(rows(c['inputs']['readout']['path']))
    fi,final_receipt,verdicts,unfilled=final_checked(c,cs,mock)
    counts=load(c['inputs']['counts']['path'])
    # Publish only after all joins, receipts, images and panels pass. Never overwrite a seal.
    output.parent.mkdir(parents=True,exist_ok=True)
    temp=Path(tempfile.mkdtemp(prefix='.'+output.name+'.',dir=output.parent))
    try:
        (temp/'images').mkdir(); (temp/'evidence').mkdir()
        evidence={}
        for role,e in c['inputs'].items():
            target=temp/'evidence'/(role+Path(e['path']).suffix)
            shutil.copyfile(e['path'],target)
            need(sha(target)==e['sha256'], 'input changed during copy: '+role)
            evidence[role]=dict(path=str(target.relative_to(temp)),sha256=e['sha256'])
        panel_rows=defaultdict(list)
        for k,f in sorted(fi.items()):
            r=ci[k]; label=ri[k];text=label['final_text']
            need(isinstance(text,str) and bool(text), 'missing literal final_text')
            need(isinstance(label['edits'],list) and HEX.fullmatch(label['raw_text_sha256']), 'bad reference provenance')
            source=image_path(c,r); crop_sha=label['crop_sha256'];target=temp/'images'/(crop_sha+'.png')
            if not target.exists(): shutil.copyfile(source,target)
            need(sha(target)==crop_sha,'copied pixels differ')
            p=dict(id=r['row_id'],parent_id=r['parent_id'],row_id=r['row_id'],split=r['split'],
                primary=r['class'],**{'class':r['class']},quota_scope=r['quota_scope'],tags=r['tags'],
                facets=sorted(k for k,v in r['tags'].items() if v is True),doc=r['edition_id'],source=r['source'],
                text=text,reference=text,reference_kind='pipeline_corrected_lf1_filtered',
                edits=label['edits'],raw_text_sha256=label['raw_text_sha256'],
                crop_path='images/'+target.name,crop_sha256=crop_sha,image_path='images/'+target.name,image_sha256=crop_sha,
                lf1_receipt_ref=f['lf1_receipt_ref'],lf1_evidence=verdicts[r['row_id']],replaces=f['replaces'],
                work_identity_status='unreviewed',global_holdout_status='unknown',mock=mock)
            panel_rows[r['split']].append(p)
        scopes=Counter(r['quota_scope'] for records in panel_rows.values() for r in records)
        scope_counts={s:dict(quota=q,sealed=scopes[s],deficit=q-scopes[s])
                      for s,q in scope_quotas(plan).items()}
        panel_rows,pixel_drops,scope_counts=pixel_overlap_checked(panel_rows,scope_counts)
        panels={}
        for split in ('test','dev'):
            records=panel_rows[split]; name='benchmark_v02_'+split; path=temp/(name+'.jsonl');jsonl(path,records)
            panels[name]=dict(path=path.name,sha256=sha(path),rows=len(records),scorable=not mock,
                reference_kind='pipeline_corrected_lf1_filtered',comparison_claim='diagnostic_only until checkpoint exposure and work identity reviewed')
        quota_counts={}
        for split,name in [('test','quotas'),('dev','dev_quotas')]:
            measured=Counter(r['primary'] for r in panel_rows[split])
            for cl,quota in plan[name].items():
                scope=split+':'+cl; need(measured[cl]<=quota,'quota overflow')
                quota_counts[scope]=dict(quota=quota,sealed=measured[cl],deficit=quota-measured[cl],draw_report=counts['classes'][scope])
        suite=dict(schema='ocr-benchmark-suite-v1',version='0.2',mock=mock,panels=panels,
            taxonomy=dict(primary_targets=plan['quotas']),inputs=evidence,input_shas={k:e['sha256'] for k,e in c['inputs'].items()},
            draw_plan=plan,quota_counts=quota_counts,scope_counts=scope_counts,
            comparison_status='diagnostic_only',v01=load(ROOT/'V01_BINDING.json'))
        dump(temp/'suite.json',suite)
        # Loader is acceptance only, not scoring. MOCK panels intentionally unscorable.
        sys.path.insert(0,str(ROOT/'v01'));from bench.benchmark_suite import load_suite, read_panel
        load_suite(temp/'suite.json')
        if not mock:
            for name in panels: read_panel(temp/'suite.json',name)
        receipt=dict(status='MOCK' if mock else 'SEALED',version='0.2',suite_sha256=sha(temp/'suite.json'),
            bindings_sha256=sha(config_path),package_manifest_sha256=sha(ROOT/'DEPLOY_SHA256SUMS'),
            interpreter=sys.executable,interpreter_sha256=sha(sys.executable),
            input_shas=suite['input_shas'],rows=sum(len(rs) for rs in panel_rows.values()),images=len(list((temp/'images').iterdir())),
            quota_counts=quota_counts,scope_counts=suite['scope_counts'],lf1_counts=final_receipt['counts'],unfilled=unfilled,
            comparison_status='diagnostic_only',mock=mock,
            cross_panel_pixel_duplicates_dropped=pixel_drops)
        need(receipt['rows']==receipt['images'], 'row/image counts differ')
        dump(temp/'SEAL_RECEIPT.json',receipt)
        # Directory rename is atomic; output existence rechecked, with parent-local reservation.
        lock=output.with_name(output.name+'.seal-lock')
        fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.close(fd)
        try:
            need(not output.exists(),'output appeared concurrently');os.rename(temp,output)
        finally: lock.unlink()
        return receipt
    finally:
        if temp.exists(): shutil.rmtree(temp)

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='action',required=True)
    b=sub.add_parser('build');b.add_argument('--bindings',required=True,type=Path);b.add_argument('--output',required=True,type=Path);b.add_argument('--mock',action='store_true')
    v=sub.add_parser('verify');v.add_argument('mode',choices=['package','inputs']);v.add_argument('--bindings',type=Path);v.add_argument('--require-complete',action='store_true')
    bind=sub.add_parser('bind');bind.add_argument('--bindings',required=True,type=Path);bind.add_argument('--output',required=True,type=Path)
    bind.add_argument('--input',nargs=3,action='append',metavar=('ROLE','ABS_PATH','SHA256'),required=True)
    a=p.parse_args()
    try:
        if a.action=='build': print(json.dumps(build(a.bindings,a.output,mock=a.mock),sort_keys=True))
        elif a.action=='bind':
            c=resolve(a.bindings);need(a.output.is_absolute() and not a.output.exists(),'new absolute bindings output required')
            for role,path,digest in a.input:
                need(role in PENDING and Path(path).is_absolute() and HEX.fullmatch(digest),'invalid explicit binding')
                need(sha(path)==digest,'new binding differs');c['inputs'][role]=dict(path=path,sha256=digest)
            need(all(e['sha256'] for e in c['inputs'].values()),'pending input binding remains')
            dump(a.output,c)
        elif a.mode=='package': print('VERIFY_PACKAGE_OK '+json.dumps(verify_package(),sort_keys=True))
        else:
            need(a.bindings is not None,'--bindings required');_,r=verify_inputs(a.bindings,partial=not a.require_complete)
            print('VERIFY_INPUTS '+json.dumps(r,sort_keys=True))
            if r['pending'] or r['images'].get('pending'): return 3
        return 0
    except (ValueError,KeyError,TypeError,OSError) as e:
        print('SEAL02_FAIL: '+str(e),file=sys.stderr);return 2
if __name__=='__main__': sys.exit(main())
