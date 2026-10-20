"""Offline sep2 packs; original N1/N1-R2 folders are never read or written."""
import hashlib
import json
import math
from pathlib import Path
import random
import shutil
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from greekocr.numerics.combine_v2 import MEANINGS, DASHES
from n1_pack_closure import scan


def rows(p): return [json.loads(x) for x in Path(p).read_text().splitlines() if x.strip()]
def dump(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x') as f: json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def typed_controls(approved, assignments):
    expected={r['slot_id'] for r in approved if r['truth']=='hyphen or dash'}
    supplied={r['slot_id']:r for r in assignments}
    if len(supplied)!=len(assignments) or set(supplied)!=expected:
        raise ValueError('dash assignments must cover exactly all 27 approved dash controls')
    missing=[s for s in expected if supplied[s].get('truth') not in (*DASHES, 'any dash')]
    if missing: raise ValueError(f'Lead dash types pending for {len(missing)} controls; fill dash_types_template.jsonl before calibration n1cal2')
    return [dict(r,truth=supplied[r['slot_id']]['truth']) if r['slot_id'] in expected else dict(r) for r in approved]


def build(bed, controls, pack_root, out, locks, calibration=False, readers=None, seed="20261017:N1T:sep2", evaluation_ids=None, frozen_rule=None):
    pack_root=Path(pack_root);out=Path(out)
    repo=Path(__file__).resolve().parents[2]
    if pack_root.resolve().is_relative_to(repo.resolve()):
        raise ValueError('refusing in-repo pack root')
    if evaluation_ids is not None:
        from greekocr.numerics.ink_rule import load_rule
        if frozen_rule is None:raise ValueError('freeze rule before locked packs')
        load_rule(frozen_rule)
        if not set(evaluation_ids) <= locks.reserved_line_ids:raise ValueError('unreserved evaluation ids')
        if any(r['line_id'] not in evaluation_ids for r in bed):raise ValueError('bed outside locked draw')
        if any(c['line_id'] in evaluation_ids for c in controls):raise ValueError('locked controls overlap')
    if pack_root.exists() and any(pack_root.iterdir()): raise ValueError('refusing to overwrite packs')
    if not controls or any(c['truth'] not in (*MEANINGS, 'any dash') for c in controls):
        raise ValueError('lead dash types pending or invalid control meaning; seal controls before calibration')
    if calibration and len(controls)!=82: raise ValueError('calibration requires all 82 approved controls')
    ids=[r['slot_id'] for r in bed];cids=[c['slot_id'] for c in controls]
    if len(set(ids))!=len(ids) or len(set(cids))!=len(cids) or set(ids)&set(cids): raise ValueError('duplicate/overlapping slots')
    records={r['slot_id']:r for r in bed+controls};truth={r['slot_id']:r['truth'] for r in controls}
    locks.assert_fit_rows(r['line_id'] for r in (records.values() if evaluation_ids is None else controls))
    for r in records.values():
        if r['geometry']['geom_status']!='ok' and r.get('render_scope')!='whole_line_unlocalized': raise ValueError('unrenderable slot '+r['slot_id'])
        for name in ('line','zoom'):
            if sha(r[name])!=r[name+'_sha256']: raise ValueError('image hash mismatch')
    rng=random.Random(seed);rng.shuffle(ids)
    groups=[]
    if calibration: groups=[cids]
    else:
        raised=[s for s in cids if truth[s]=='raised dot']
        if not raised: raise ValueError('raised-dot controls required')
        other=[s for s in cids if s not in raised];rng.shuffle(other)
        if len(other)<8: raise ValueError('nine distinct approved controls required')
        n=max(1,math.ceil(len(ids)/80))
        for i in range(n):
            cc=[raised[i%len(raised)]]
            for kind in DASHES:
                pool=[s for s in cids if truth[s]==kind]
                if pool: cc.append(pool[i%len(pool)])
            fill=[s for s in other if s not in cc]
            cc += [fill[(i*8+j)%len(fill)] for j in range(9-len(cc))]
            group=ids[i::n]+cc;rng.shuffle(group);groups.append(group)
    summaries=[];used=set()
    for i,group in enumerate(groups,1):
        ctx=('cal' if calibration else 'ctx')+f'{i:02}'
        orders={};previous={}
        for reader in (readers or (('r1',) if calibration else ('r1','r2'))):
            directory=pack_root/ctx/reader;(directory/'img').mkdir(parents=True,exist_ok=False)
            order=list(reversed(group)) if reader=='r2' else group; public=[];private={}
            for sid in order:
                meanings=list(MEANINGS)
                while True:
                    rng.shuffle(meanings);options=dict(zip('ABCDEFGHIJ',meanings))
                    if reader!='r2' or all(options[k]!=previous[sid][k] for k in options): break
                if reader=='r1': previous[sid]=dict(options)
                while True:
                    iid='k'+f'{rng.getrandbits(40):010x}'
                    if iid not in used: break
                used.add(iid);r=records[sid];item=dict(item_id=iid,options=options)
                for name in ('line','zoom'):
                    target=directory/'img'/(r[name+'_sha256']+'.png')
                    if not target.exists(): shutil.copyfile(r[name],target)
                    item[name]='img/'+target.name
                public.append(item)
                private[iid]=dict(slot_id=sid,line_id=r['line_id'],option_map=options,
                    control_truth=truth.get(sid),geometry=r['geometry'],google_glyph=r.get('google_glyph',r.get('glyph')),
                    measurements=r.get('measurements'),dash=r.get('dash'))
            (directory/'items.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in public))
            suffix='' if reader=='r1' else '.'+reader
            dump(out/'keys'/(ctx+suffix+'.json'),dict(readers={reader:[r['item_id'] for r in public]},items=private,calibration=calibration,schema='sep2'))
            orders[reader]=len(public)
        summaries.append(dict(context=ctx,readers=orders,bed=0 if calibration else sum(s in ids for s in group),
            controls=sum(s in truth for s in group),raised_controls=sum(truth.get(s)=='raised dot' for s in group),
            dash_controls={t:sum(truth.get(s)==t for s in group) for t in DASHES}))
    closures=[]
    for s in summaries:
        for reader in s['readers']:
            r=scan(pack_root/s['context']/reader,out,meanings=MEANINGS)
            if not r['ok']: raise ValueError(r['violations'])
            closures.append(r)
    return dict(contexts=summaries,closure=closures)


def main():
    import argparse
    from n1_render import SCRATCH
    from greekocr.numerics.locks import load_locks
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--calibration',action='store_true');a=p.parse_args()
    root=Path(__file__).resolve().parents[2];base=root/'artifacts/n1'
    approved=rows(base/'controls/approved.jsonl')
    if a.calibration:
        controls=typed_controls(approved,rows(base/'controls/dash_types.jsonl'));bed=[];name='n1cal2'
    else:
        controls=[c for c in approved if c['truth']!='hyphen or dash']
        bed=[s for s in rows(base/'n1t/slots.jsonl') if s['geometry']['geom_status']=='ok'];name='n1t'
    out=base/name
    controlpath=out/'controls/approved.jsonl';controlpath.parent.mkdir(parents=True,exist_ok=True)
    with controlpath.open('x') as f: f.write(''.join(json.dumps(c,ensure_ascii=False)+'\n' for c in controls))
    print(json.dumps(build(bed,controls,SCRATCH/'sol_packs'/name,out,load_locks(base),a.calibration),ensure_ascii=False))
if __name__=='__main__': main()
