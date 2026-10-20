#!/usr/bin/env python3
"""Train-only unlabelled selection. No submission, network or crop generation."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import sqlite3
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent/'vendor'))
import build_release_v4 as rel4

ALLOWED = frozenset(('correction_unresolved', 'required_evidence_unresolved'))
FIELDS = frozenset(('parent_id','row_id','source','book_id','edition_id','split','crop_path','crop_sha256','disposition','reason_class','reasons','primary_class'))
RECON = ('crop_source_image','crop_source_sha256','crop_bbox','crop_color_mode')

def no_labels(row, reconstruction=False):
    rel4.require(set(row) <= FIELDS | (set(RECON) if reconstruction else set()), 'unexpected or label field')
    rel4.require(row['split']=='train', 'nontrain output')

def reasons(d):
    return sorted({x['reason'] if isinstance(x,dict) else x for x in d.get('reasons',[])})

def eligible(r, version='0.3.3'):
    d=r['decision']; rel4.require(d['pipeline_version']==version,'pipeline version mismatch')
    rel4.require(d['binding']==dict(parent_id=r['parent_id'],id=r['row_id'],split=r['split'],crop_sha256=r['crop_sha256']), 'decision identity mismatch')
    if r['disposition'] != d['disposition']: raise ValueError('disposition mismatch')
    if r['split']!='train' or r['parent_id'] not in {'collection-v2-train','collect-v3-W1-20261018-0524','collect-v3-W2-20261018-0524'}:return 'nontrain_parent_or_split'
    if d['disposition']=='DROP':return 'DROP'
    rr=reasons(d)
    if d['disposition']!='ADMIT' and not (d['disposition']=='HOLD' and rr and set(rr)<=ALLOWED):return 'other_HOLD'
    rel4.require(d['toolchain_versions']['content_gate']=='0.3' and d['toolchain_versions']['segmentation']=='0.13','gate/segmentation version mismatch')
    stages=d['stages']; gates=[s for s in stages if s['stage']=='content_gate']; seg=[s for s in stages if s['stage']=='segmentation']
    if len(gates)!=1 or gates[0].get('excluded') or len(seg)!=1 or seg[0]['result'].get('verdict')!='KEEP':return 'gate_or_segmentation'
    return None

def exposures(paths, policy):
    from rel4_exposure import union
    editions,books,candidates,pixels=union(paths)
    bench_editions={r['edition_id'] for r in rel4.records(paths['candidates_v3.jsonl'])}
    for n in ('seal04_test','seal04_dev'):
        for r in rel4.records(paths[n]):
            if r.get('edition_id'):bench_editions.add(r['edition_id'])
            if r.get('book_id') in books:bench_editions.add(books[r['book_id']])
            if r.get('doc'):bench_editions.add(r['doc'])
    return dict(editions=editions,books=books,keys=candidates,pixels=pixels,benchmark_editions=bench_editions,
                heldout_editions=set(policy['heldout_editions']),heldout_pixels=set(policy['heldout_crop_sha256']))

def exclude(row, ex, flags):
    ed=row['edition_id'];book=row['book_id'];is_w=row['parent_id'].startswith('collect-v3-')
    if row['row_id'] in flags:return 'historical_flag_key'
    if is_w:
        rel4.require(book in ex['books'] and ex['books'][book]==ed,'SPLIT2 edition identity mismatch')
        if ex['editions'][ed] in ('dev','test'):return 'dev_test_edition'
        rel4.require(ex['editions'][ed]=='train','unknown edition split')
    if ed in ex['heldout_editions'] or book in ex['heldout_editions']:return 'heldout_edition'
    if ed in ex['benchmark_editions'] or book in ex['benchmark_editions']:return 'benchmark_edition'
    if (row['parent_id'],row['row_id']) in ex['keys']:return 'benchmark_key'
    if row['crop_sha256'] in ex['pixels']:return 'benchmark_pixels'
    if row['crop_sha256'] in ex['heldout_pixels']:return 'heldout_pixels'
    return None

def dedup(rows):
    # Stable identity tie-break for exact PNG/pixel digest. Then edition member election.
    unique={};counts=Counter()
    for r in sorted(rows,key=lambda r:(r['parent_id'],r['row_id'])):
        if r['crop_sha256'] in unique:counts['pixel_rows_removed']+=1
        else:unique[r['crop_sha256']]=r
    members=defaultdict(Counter)
    for r in unique.values():
        if r['parent_id'].startswith('collect-v3-'):members[r['edition_id']][r['book_id']]+=1
    elected={ed:min(c,key=lambda b:(-c[b],b)) for ed,c in members.items()}
    counts['multi_member_editions']=sum(len(c)>1 for c in members.values())
    out=[]
    for r in unique.values():
        if r['parent_id'].startswith('collect-v3-') and r['book_id']!=elected[r['edition_id']]:counts['edition_member_rows_removed']+=1
        else:out.append(r)
    return sorted(out,key=lambda r:(r['parent_id'],r['row_id'])),dict(counts),elected

def build(config, output, crop_attempt):
    root,cfg=rel4.load_config(config);paths,receipts,pending=rel4.input_check(root,cfg)
    rel4.require(not pending,'pending REL4/census06 bindings: '+','.join(pending))
    rel4.require(cfg['schema']=='release-v4-package-v1','production REL4 binding required')
    out=Path(output);rel4.require(not out.exists(),'new selection attempt required')
    cropbase=Path(cfg['work_root'])/'p1pool_crops'/crop_attempt
    rel4.require(cropbase.parent==Path(cfg['work_root'])/'p1pool_crops' and crop_attempt not in ('','.','..'),'unsafe crop attempt')
    cc=json.loads(paths['census06_config.json'].read_text());ex=exposures(paths,cc['final_policy'])
    flags={r['row_id'] for r in rel4.records(Path(__file__).with_name('flags.jsonl'))}
    crops,crop_receipts=rel4.crop_index(cfg)
    ledger=Path(cfg['census_attempt'])/'ledger.sqlite';wal=Path(str(ledger)+'-wal')
    rel4.require(not wal.exists() or wal.stat().st_size==0,'unfinished WAL')
    readout=json.loads(paths['readout.json'].read_text())
    ledger_receipt=next(f for f in readout['files'] if Path(f['path']).resolve()==ledger.resolve())
    rel4.require(rel4.sha(ledger)==ledger_receipt['sha256'],'ledger readout sha mismatch')
    counts=Counter();selected=[];flag_joins=0;seen=set()
    with sqlite3.connect(ledger.resolve().as_uri()+'?mode=ro&immutable=1',uri=True) as db:
        binding=json.loads(db.execute("SELECT value FROM run WHERE key='binding'").fetchone()[0])
        rel4.require(binding==cfg['census_run_binding'],'ledger binding drift')
        observations=iter(db.execute('SELECT parent,id,payload FROM observations ORDER BY parent,id'))
        for a in rel4.records(paths['admission_records']):
            parent,ident,payload=next(observations);rel4.require((parent,ident)==(a['parent_id'],a['row_id']),'ledger/export order or identity mismatch')
            r=json.loads(payload);key=(parent,ident)
            rel4.require(key not in seen,'duplicate row');seen.add(key)
            rel4.require(a['decision']['run_binding_sha256']==rel4.digest(rel4.canonical(binding)),'row run binding mismatch')
            rel4.require(a['crop_sha256']==r['crop_sha256'] and a['split']==r['split'] and a['source']==r['source'],'observation binding mismatch')
            flag_joins+=ident in flags
            why=eligible(a)
            if why:counts[why]+=1;continue
            compact=dict(parent_id=parent,row_id=ident,source=a['source'],book_id=r['book_id'],edition_id=r['edition_id'],split='train',crop_sha256=a['crop_sha256'],disposition=a['disposition'],reason_class='admit' if a['disposition']=='ADMIT' else 'correction_hold',reasons=reasons(a['decision']),primary_class=a.get('primary_class'))
            why=exclude(compact,ex,flags)
            if why:counts[why]+=1;continue
            if parent=='collection-v2-train':
                image=Path(r['crop_path']);rel4.require(image.resolve().is_relative_to(Path(cfg['work_root'])/'collection_v2/crops'),'v2 crop outside custody')
                rel4.require(image.is_file() and rel4.sha(image)==r['crop_sha256'],'v2 crop missing/mismatch')
            elif key in crops:
                h,path,size=crops[key];image=Path(cfg['work_root'])/path
                rel4.require(h==r['crop_sha256'] and image.is_file() and image.stat().st_size==size and rel4.sha(image)==h,'existing crop mismatch')
            else:
                rel4.require(a['disposition']=='HOLD','ADMIT crop missing from CROPS4 union')
                image=cropbase/parent/a['source']/(ident+'.png')
                for part in (parent,a['source'],ident):
                    rel4.require('/' not in part and part not in ('.','..'),'unsafe crop component')
                compact.update({k:r.get(k,'L' if k=='crop_color_mode' else None) for k in RECON})
                rel4.require(all(compact[k] is not None for k in RECON),'HOLD reconstruction metadata missing')
            compact['crop_path']=str(image);no_labels(compact,True);selected.append(compact)
        rel4.require(next(observations,None) is None,'unexported observations')
    rel4.require(rel4.sha(ledger)==ledger_receipt['sha256'],'ledger changed')
    selected,dd,elected=dedup(selected);rel4.require(selected,'empty pool')
    rel4.require(len({r['crop_sha256'] for r in selected})==len(selected),'pixel exposure audit')
    rel4.require(all(exclude(r,ex,flags) is None and r['split']=='train' for r in selected),'final exposure audit')
    out.mkdir(parents=True)
    manifest=out/'selection.jsonl'
    manifest.write_text(''.join(rel4.canonical(r)+'\n' for r in selected))
    dimensions={field:dict(Counter(str(r[field]) for r in selected)) for field in ('parent_id','source','primary_class','disposition','reason_class')}
    dimensions['disposition_reason']=dict(Counter(r['disposition']+':'+reason for r in selected for reason in (r['reasons'] or ['ADMIT'])))
    rel4.input_check(root,cfg)
    for receipt in crop_receipts:
        for f in receipt['files'].values():rel4.require(rel4.sha(f['path'])==f['sha256'],'crop union changed')
    receipt=dict(status='selected_pending_crops',input_shas=receipts+[ledger_receipt,dict(name='historical_flags',sha256=rel4.sha(Path(__file__).with_name('flags.jsonl')))],exposure_audit=dict(status='PASS',benchmark_keys=0,benchmark_pixels=0,heldout_editions=0,dev_test_editions=0,duplicate_pixels=0),crop_custody=crop_receipts,rel4_config=dict(path=str(Path(config).resolve()),sha256=rel4.sha(config)),counts=dimensions,exclusions=dict(counts),dedup=dd,edition_members=elected,historical_flag_joins=flag_joins,no_labels_asserted=True,raw_text_sha256_used=False,crops=dict(existing=sum('crop_source_image' not in r for r in selected),to_write=sum('crop_source_image' in r for r in selected),written=None),output_shas={'selection.jsonl':rel4.sha(manifest)},crop_root=str(cropbase))
    rel4.write_json(out/'P1POOL_RECEIPT.json',receipt)
    return receipt

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--rel4-config',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--attempt',required=True);a=p.parse_args()
    rel4.require(a.output.parent.resolve()==Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/scaling_w3/p1pool_attempts'),'output outside P1POOL attempts')
    print(rel4.canonical(build(a.rel4_config,a.output,a.attempt)['dedup']))
