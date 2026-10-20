"""Offline RU1 line packs, adapted from Sol build_packs.py; no reader or visual review.
All W1 crops are regenerated through a shallow row copy. V2 control crops are
original adjudication inputs pinned by the earlier builder's source mapping.
"""
import json
import math
import random
import secrets
import platform
import sys
from collections import Counter
from pathlib import Path
from PIL import Image, __version__ as pillow_version
from ru1_census import *

WORK = Path(__file__).resolve().parents[2]
SCRATCH = Path('/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad')
CACHE = SCRATCH/'ru1_cache'
PACK_ROOT = SCRATCH/'sol_packs/ru1'
YER = COLLECT/'docs/records/harvest/collect_v3/c1/yer_adjudication'
C1KEY = PROJECTS/'collect-v3-data/run/W1/c1/ia_russian__cyrillic_key.json'
OLDMAP = YER.parent/'efficiency/keys/input_mapping.json'
SEED = 'RU10b:20261017:r1'
COLLECTOR_PYTHON = COLLECT/'.venv/bin/python'


def control_inventory(byid, vocab, books, inputs):
    def read(p): inputs[str(p)]=sha(p);return json.loads(p.read_text())
    table=read(YER/'table.json'); key=read(YER/'key.json'); c1=read(C1KEY); old=read(OLDMAP)['yer']
    for n in ['items_a.jsonl','items_b.jsonl','ink_a.jsonl','ink_b.jsonl','prior.jsonl','INK.md','PRIOR.md']:
        inputs[str(YER/n)]=sha(YER/n)
    saved={r['item_id']:r for n in ['items_a.jsonl','items_b.jsonl'] for r in rows(YER/n)}
    ink={r['item_id']:r for n in ['ink_a.jsonl','ink_b.jsonl'] for r in rows(YER/n)}
    out=[]
    for t in table:
        iid=t['item_id'];m=key[iid];text=m['google_text'];rid=c1[m['card_id']]['line_id'] if m['set']=='c1' else None
        row=byid.get(rid) if rid else None
        if rid and row is None: raise ValueError('C1 row missing')
        if row and row['label']!=text:raise ValueError('control current label differs')
        masked,ps=mask(text);truth={}
        if saved[iid]['masked_text']!=masked or saved[iid]['slots']!=len(ps):
            raise ValueError('saved adjudication mask differs')
        if row is None and saved[iid]['crop']!=old[iid]['source_crop']:
            raise ValueError('saved adjudication crop path differs from hash record')
        import re
        for s in t['slots']:
            mm=re.fullmatch(r'(\d+):g=([ъь]) ink=(ъ|ь|other|u) prior=.+',s)
            if not mm: raise ValueError('invalid table truth')
            n,g,call=mm.groups();truth[n]=call
            if ps[int(n)-1]['google']!=g:raise ValueError('control glyph differs')
        if len(ps)!=len(truth) or truth!=ink[iid]['slots']:raise ValueError('truth/slot coverage differs')
        for n,p in enumerate(ps,1):p.update(prior=prior(p,vocab,leave_one_out=bool(row)),control_truth=truth[str(n)])
        b=row['source']+':'+row['item'] if row else 'ia_russian:'+old[iid]['line_id'].rsplit('--',1)[0]
        out.append(dict(control=True,adjudication_id=iid,row_id=rid,w1_id=rid,source_id=rid or old[iid]['line_id'],
                        w1_mapping='exact C1 key' if row else 'absent: v2 source population, not W1',
                        source_set=m['set'],book=b,orthography=books[b]['orthography'] if row else
                        ('pre1918' if t['pre1918']=='yes' else 'modern' if t['pre1918']=='no' else 'unclear'),
                        masked_text=masked,slots=ps,row=row,legacy=old[iid] if row is None else None))
    assert len(out)==59 and sum(len(c['slots']) for c in out)==65
    return out



def record_blocked(rr, pp, census, controls, inputs, unavailable):
    ctrlids={c['row_id'] for c in controls if c['row_id']}
    soft=[p for p in pp if p['usable'] and p['google']=='ь' and p['kind']=='final' and p['row_id'] not in ctrlids]
    preids={p['row_id'] for p in soft if p['orthography']=='pre1918'}
    prepositions=[p for p in pp if p['row_id'] in preids]
    inventory=[{k:v for k,v in c.items() if k not in ['row','legacy','image']} for c in controls]
    dump(ART/'keys/control_inventory.json',inventory)
    jsonl(ART/'keys/planned_bed_positions.jsonl',prepositions)
    jsonl(ART/'keys/modern_spot_positions.jsonl',[])
    PACK_ROOT.mkdir(parents=True,exist_ok=True)
    counts=dict(census['counts'],bed_lines=0,bed_slots=0,
                planned_bed_lines=len(preids),planned_bed_slots=len(prepositions),
                planned_bed_soft_final_positions=sum(p['row_id'] in preids for p in soft),
                modern_spot_requested=20,modern_spot_positions=0,modern_spot_lines=0,
                controls_lines=59,controls_slots=65,controls_w1_lines=19,controls_v2_lines=40,
                controls_available_lines=40,controls_used_unique=0,control_appearances=0,
                contexts=0,planned_contexts=math.ceil(len(preids)/90),
                crop_unavailable=len(unavailable),usable_crops_verified=0)
    result=dict(status='BLOCKED',counts=counts,contexts=[],inputs=inputs,seed=SEED,
                usable_rule=RULE,prior_method=PRIOR_METHOD,
                limitations=['All 1146 usable W1 ensure_crop attempts fail regenerated crop hash verification. No substitutes used; zero packs built.',
                             'No modern books in W1: 20 modern positions cannot be sampled.',
                             '40 v2 controls have original source IDs, not W1 IDs; 28 controls have zero slots.'],
                image_method='Only automatic decoding/hash checks; no images viewed; no reader/probe launched')
    dump(ART/'build.json',result)
    return result


def build():
    if platform.machine()!='arm64' or pillow_version!='12.3.0' or Path(sys.executable).resolve()!=COLLECTOR_PYTHON.resolve():
        raise ValueError('run crop regeneration with the collector arm64 Pillow 12.3.0 interpreter')
    if PACK_ROOT.exists() and any(PACK_ROOT.iterdir()):raise ValueError('refuse to overwrite nonempty pack root')
    rr,pp,census,vocab=__import__('ru1_census').build();inputs=census['inputs'];byid={r['id']:r for r in rr}
    controls=control_inventory(byid,vocab,census['books'],inputs)
    ctrlids={c['row_id'] for c in controls if c['row_id']}
    # Include zero-yer usable rows for crop availability verification as well.
    exclusions,_=exclusion_ids();usable_ids={r['id'] for r in rr if usable(r,exclusions)}
    sys.path.insert(0,str(COLLECT))
    from collect_v3.storage import ensure_crop
    inputs[str(COLLECT/'collect_v3/storage.py')]=sha(COLLECT/'collect_v3/storage.py')
    available={};unavailable=[];source_checks={}
    def regenerate(r):
        dest=CACHE/'crops'/ (r['crop_sha256']+'.png')
        try:
            src=r['crop_source_image']
            if src not in source_checks:source_checks[src]=sha(src)
            inputs[src]=source_checks[src]
            if source_checks[src]!=r['crop_source_sha256']:raise ValueError('crop source hash mismatch')
            copied=dict(r,crop=str(dest))
            assert Path(copied['crop']).is_relative_to(CACHE/'crops')
            p=ensure_crop(copied)
            if sha(p)!=r['crop_sha256']:raise ValueError('crop hash mismatch')
            with Image.open(p) as im:
                im.load()
                if im.size!=(r['crop_bbox'][2]-r['crop_bbox'][0],r['crop_bbox'][3]-r['crop_bbox'][1]):raise ValueError('crop dimensions differ')
            return p
        except (OSError,ValueError,KeyError) as e:
            unavailable.append(dict(row_id=r['id'],reason=str(e)));return None
    needed=usable_ids|ctrlids
    for rid in sorted(needed):
        p=regenerate(byid[rid])
        if p:available[rid]=p
    for c in controls:
        if c['row_id']:c['image']=available.get(c['row_id'])
        else:
            src=Path(c['legacy']['source_crop'])
            try:
                h=sha(src);inputs[str(src)]=h
                if h!=c['legacy']['source_crop_sha256']:raise ValueError('adjudicated v2 crop hash mismatch')
                with Image.open(src) as im:im.load()
                dest=CACHE/'crops'/(h+'.png');dest.parent.mkdir(parents=True,exist_ok=True)
                if not dest.exists():dest.write_bytes(src.read_bytes())
                if sha(dest)!=h:raise ValueError('cached adjudication crop hash mismatch')
                c['image']=dest
            except (OSError,ValueError) as e:
                c['image']=None;unavailable.append(dict(row_id=None,source_id=c['source_id'],reason=str(e)))
    jsonl(ART/'crop_unavailable.jsonl',unavailable)
    if unavailable or any(c['image'] is None for c in controls):
        record_blocked(rr,pp,census,controls,inputs,unavailable)
        raise SystemExit('BLOCKED: crop verification failed; see artifacts/ru1/build.json')
    soft=[p for p in pp if p['usable'] and p['google']=='ь' and p['kind']=='final' and p['row_id'] not in ctrlids]
    preids={p['row_id'] for p in soft if p['orthography']=='pre1918'}
    rng=random.Random(SEED);selected=[];modernids=set()
    jsonl(ART/'keys/modern_spot_positions.jsonl',[])
    bed=[]
    for rid in sorted(preids|modernids):
        r=byid[rid];b=r['source']+':'+r['item'];masked,ps=mask(r['label'])
        if rid not in available:continue
        for p in ps:p.update(prior=prior(p,vocab),control_truth=None)
        bed.append(dict(control=False,row_id=rid,w1_id=rid,source_id=rid,book=b,orthography=census['books'][b]['orthography'],
                        masked_text=masked,slots=ps,image=available[rid],spot_check=rid in modernids))
    rng.shuffle(bed)
    # Only slot-bearing controls count toward the context gate.
    pool=[c for c in controls if c['slots']]
    rng.shuffle(pool)
    contexts=[];usedcontrols=Counter();opaque=set();inventory=[]
    for c in controls:
        inventory.append({k:v for k,v in c.items() if k not in ['row','legacy','image']})
    dump(ART/'keys/control_inventory.json',inventory)
    nctx=math.ceil(len(bed)/90);cursor=0
    for j in range(nctx):
        name=f'ctx{j+1:02d}';batch=bed[j*len(bed)//nctx:(j+1)*len(bed)//nctx]
        nc=min(9,100-len(batch));assert len(batch)<=90 and nc<=len(pool)
        chosen=[pool[(cursor+i)%len(pool)] for i in range(nc)];cursor+=nc
        assert len({c['adjudication_id'] for c in chosen})==len(chosen)
        combined=batch+chosen;rng.shuffle(combined);dest=PACK_ROOT/name/'r1';dest.mkdir(parents=True)
        public=[];private={}
        for m in combined:
            iid='k'+secrets.token_hex(5)
            if iid in opaque:raise ValueError('opaque id collision')
            opaque.add(iid)
            # Preserve verified original PNG bytes, including W1 grayscale mode.
            blob=Path(m['image']).read_bytes()
            h=hashlib.sha256(blob).hexdigest();rel='crops/'+h+'.png';path=dest/rel;path.parent.mkdir(exist_ok=True)
            if not path.exists():path.write_bytes(blob)
            assert sha(path)==sha(m['image'])
            public.append(dict(item_id=iid,crop=rel,masked_text=m['masked_text'],slots=len(m['slots'])))
            private[iid]={k:v for k,v in m.items() if k not in ['row','legacy','image','masked_text']}
            private[iid]['source_crop_sha256']=sha(m['image'])
            if m['control']:usedcontrols[m['adjudication_id']]+=1
        jsonl(dest/'items.jsonl',public)
        dump(ART/f'keys/{name}.json',dict(context=name,seed=SEED,readers={'r1':[r['item_id'] for r in public]},items=private))
        contexts.append(dict(context=name,bed_lines=len(batch),bed_slots=sum(len(m['slots']) for m in batch),
                             control_lines=nc,control_slots=sum(len(m['slots']) for m in chosen),items=len(public),path=str(dest)))
    counts=dict(census['counts'],bed_lines=sum(not b.get('spot_check') for b in bed),
                bed_slots=sum(len(b['slots']) for b in bed if not b.get('spot_check')),
                bed_target_soft_positions=sum(p['row_id'] in preids for p in soft),
                modern_spot_positions=len(selected),modern_spot_requested=0,modern_spot_lines=len(modernids),
                modern_spot_all_masked_slots=sum(len(b['slots']) for b in bed if b.get('spot_check')),
                controls_lines=len(controls),controls_slots=65,controls_w1_lines=len(ctrlids),controls_v2_lines=40,
                controls_available_lines=len(controls),controls_available_slots=65,controls_slot_bearing_lines=len(pool),
                crops_regenerated=len(available),crops_needed=len(needed),controls_used_unique=len(usedcontrols),control_appearances=sum(usedcontrols.values()),
                contexts=nctx,crop_unavailable=len(unavailable),usable_crops_verified=sum(i in available for i in usable_ids))
    result=dict(status='READY',counts=counts,contexts=contexts,inputs=inputs,seed=SEED,
                regeneration=dict(interpreter_path=str(COLLECTOR_PYTHON),sys_executable=sys.executable,
                                  python_version=platform.python_version(),architecture=platform.machine(),pillow_version=pillow_version),
                control_usage=dict(usedcontrols),usable_rule=RULE,prior_method=PRIOR_METHOD,
                limitations=['Modern spot check dropped by RU1-0b: all 10 W1 books are pre1918.',
                            '40 v2 control lines have no W1 row id; kept original v2 source IDs and hash-pinned adjudication crops.',
                            '28 of the 59 control lines have zero adjudicated slots; slot errors are scored only where truth exists.'],
                image_method='W1 ensure_crop hash verification under collector interpreter; all pack PNGs copied byte-exactly from verified originals, no links; no visual inspection')
    assert all(sha(p)==h for p,h in inputs.items()),'input changed during build'
    dump(ART/'build.json',result);print(json.dumps(dict(counts=counts,contexts=contexts),ensure_ascii=False,indent=2))

if __name__=='__main__':build()
