"""Build sealed N1 v3 packs offline; never starts a reading run."""
import argparse
import hashlib
import json
import math
import random
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from greekocr.numerics.locks import load_locks
from n1_render import clean_png, SCRATCH
from n1_pack_closure import scan
from PIL import Image
MEANINGS = ('raised dot','baseline dot','comma','hyphen or dash','space','nothing','other','unreadable')
ROOT = Path(__file__).resolve().parents[2]


def rows(path):
    return [json.loads(s) for s in Path(path).read_text().splitlines() if s.strip()]


def write_new(path, data):
    path = Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f: f.write(data)


def build(bed, controls, records, pack_root, key_root, locks, calibration=False, require_raised=False):
    """controls are explicit slot_id/truth approvals; records contain private geometry/images."""
    rng = random.Random('20261017:N1-1')
    pack_root, key_root = Path(pack_root), Path(key_root)
    if pack_root.exists() and any(pack_root.iterdir()): raise ValueError('pack root is not empty')
    ids = [s['slot_id'] for s in bed]
    cids = [s['slot_id'] for s in controls]
    if len(set(ids)) != len(ids) or len(set(cids)) != len(cids) or set(ids)&set(cids):
        raise ValueError('duplicate/overlapping slots')
    if not controls: raise ValueError('approved controls required')
    for c in controls:
        if c['truth'] not in MEANINGS: raise ValueError('invalid approved meaning')
    allids = cids if calibration else ids+cids
    locks.assert_fit_rows(records[s]['line_id'] for s in allids)
    for sid in allids:
        if records[sid]['geometry']['geom_status'] != 'ok' or not all(records[sid].get(k) for k in ['line','zoom']):
            raise ValueError('unrenderable slot: '+sid)
    rng.shuffle(ids); rng.shuffle(cids)
    if calibration:
        if len(cids)>100: raise ValueError('calibration exceeds 100')
        batches = [cids]
    else:
        n = max(1,math.ceil(len(ids)/80))
        by_class = {}
        for sid in cids:
            meaning = next(c['truth'] for c in controls if c['slot_id']==sid)
            by_class.setdefault(meaning, []).append(sid)
        raised = by_class.pop('raised dot', [])
        if require_raised and not raised: raise ValueError('raised-dot control required in every bed context')
        # One rotating raised slot, then round-robin classes and slots within class.
        classes = sorted(by_class)
        offsets = {c: 0 for c in classes}
        turn = 0
        batches=[]
        for i in range(n):
            group=ids[i::n]; count=max(2,round(len(group)/9))
            cc=[raised[i % len(raised)]] if raised else []
            while len(cc)<count:
                eligible = [c for c in classes if any(s not in cc for s in by_class[c])]
                if not eligible: raise ValueError('too few distinct controls')
                c=classes[turn % len(classes)]; turn+=1
                if c not in eligible: continue
                pool=by_class[c]
                while pool[offsets[c] % len(pool)] in cc: offsets[c]+=1
                cc.append(pool[offsets[c] % len(pool)]); offsets[c]+=1
            if len(group)+len(cc)>100: raise ValueError('context exceeds 100')
            batches.append(group+cc)
    truth={c['slot_id']:c['truth'] for c in controls}; summaries=[]
    for i,group in enumerate(batches,1):
        rng.shuffle(group); ctx=f'cal{i:02d}' if calibration else f'ctx{i:02d}'; directory=pack_root/ctx/'r1'
        (directory/'img').mkdir(parents=True,exist_ok=False)
        public=[]; private={}
        for sid in group:
            record=records[sid]; meanings=list(MEANINGS);rng.shuffle(meanings)
            options=dict(zip('ABCDEFGH',meanings))
            item_id='k'+hashlib.sha256((str(rng.getrandbits(256))+sid).encode()).hexdigest()[:10]
            if item_id in private: raise ValueError('opaque id collision')
            item=dict(item_id=item_id,options=options)
            for name in ['line','zoom']:
                if record.get(name+'_sha256') and hashlib.sha256(Path(record[name]).read_bytes()).hexdigest()!=record[name+'_sha256']:
                    raise ValueError('render hash mismatch: '+sid)
                with Image.open(record[name]) as im: data=clean_png(im)
                digest=hashlib.sha256(data).hexdigest(); target=directory/'img'/(digest+'.png')
                if not target.exists(): target.write_bytes(data)
                item[name]='img/'+target.name
            public.append(item)
            private[item_id]=dict(slot_id=sid,option_map=options,control_truth=truth.get(sid),
                geometry_record_ref=record.get('geometry_record_ref'),geometry=record['geometry'],
                measurements=record.get('measurements'),google_glyph=record['google_glyph'],line_id=record['line_id'],
                bed_class=record.get('grammar'),control_class=truth.get(sid))
        write_new(directory/'items.jsonl',''.join(json.dumps(r)+'\n' for r in public))
        key=dict(readers={'r1':[r['item_id'] for r in public]},items=private,calibration=calibration)
        write_new(key_root/'keys'/(ctx+'.json'),json.dumps(key,indent=2)+'\n')
        result=scan(directory,key_root)
        if not result['ok']: raise ValueError(result['violations'])
        summaries.append(dict(context=ctx,items=len(group),controls=sum(s in truth for s in group),closure=result))
    return summaries


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--calibration',action='store_true')
    p.add_argument('--approved',type=Path,default=ROOT/'artifacts/n1/controls/approved.jsonl')
    p.add_argument('--pack-root',type=Path,default=None)
    a=p.parse_args()
    if a.pack_root is None: a.pack_root=SCRATCH/('sol_packs/n1cal' if a.calibration else 'sol_packs/n1')
    approved=rows(a.approved)
    records=rows(ROOT/'artifacts/n1/step1_rendered_v3.jsonl')+approved
    recordmap={r['slot_id']:r for r in records}
    bed=rows(ROOT/'artifacts/n1/step1_rendered_v3.jsonl')
    print(json.dumps(build(bed,approved,recordmap,a.pack_root,ROOT/'artifacts/n1',load_locks(ROOT/'artifacts/n1'),a.calibration,require_raised=True),indent=2))
if __name__=='__main__': main()
