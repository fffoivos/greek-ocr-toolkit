"""CAPS3 blinded packs; controls and closure policy inherited from CAPS1."""
from __future__ import annotations
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import hashlib
import json
import random
import shutil
import os
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[4]
REFERENCE=REPO.parent/'greek-ocr-toolkit-sol-reading/docs/harvest/sol_reading'
PACK_ROOT=Path('/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs')
BED=PACK_ROOT/'caps3'
SEED='caps3:headings_caps:masked'
FIELDS={'card_id','crop','google_text','word_scripts'}
OUT=HERE.parent/'caps_masked'

def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def rows(path):
    return [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]
def dump(path,value):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def jsonl(path,value):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(''.join(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n' for r in value))
def draw(pool):return random.Random(SEED).sample(sorted(pool,key=lambda r:r['id']),100)
def order_seed(c):return SEED+':order:'+c

def io_guard():
    from pipeline import network_off
    network_off()

def build():
    from pipeline import network_off
    network_off()
    prior=HERE.parent/'caps1'
    old=json.loads((prior/'keys/caps1.json').read_text())
    excluded={r['id'] for r in rows(prior/'keys/draw.jsonl')}
    features={r['id']:r for r in rows(HERE/'keys/pool.jsonl')}
    records=rows(OUT/'records.jsonl')
    pool=[r for r in records if r['matched'] and r['id'] not in excluded]
    selected=draw(pool)
    jsonl(HERE/'keys/eligible.jsonl',pool)
    jsonl(HERE/'keys/draw.jsonl',selected)
    controls=json.loads((prior/'keys/control_truth.json').read_text())
    assert {c['source_card']['card_id'] for c in controls}=={'c057','c009','c013','c026','c046','c041','c029','c072','c035','c066'}
    key=dict(bed='caps3',protocol='bsb',seed=SEED,readers={},items={})
    custody=[]
    for i,context in enumerate(('c1','c2')):
        batch=[(r,None) for r in selected[i*50:(i+1)*50]]+[(None,c) for c in controls if c['context']==context]
        random.Random(order_seed(context)).shuffle(batch)
        directory=BED/context
        (directory/'crops').mkdir(parents=True,exist_ok=True)
        cards=[]
        for r,c in batch:
            if c:
                oldid=c['opaque_id'];meta=dict(old['items'][oldid]);source=PACK_ROOT/'caps1'/context/next(x['crop'] for x in rows(PACK_ROOT/'caps1'/context/'cards.jsonl') if x['card_id']==oldid)
                text=c['source_card']['google_text'];scripts=c['source_card']['word_scripts'];rid=c['line_id'];digest=meta['crop_sha256']
            else:
                rid=r['id'];f=features[rid];digest=r['masked_crop_sha256'];source=OUT/r['masked_crop'];text=r['google_text']
                # Same public script rendering as CAPS1/T6b.
                import unicodedata
                scripts=[]
                for word in text.split():
                    ss={next((s for s in ('Greek','Latin','Cyrillic') if s.upper() in unicodedata.name(ch,'')),'Other') for ch in word if ch.isalpha()}
                    scripts.append([word,next(iter(ss)) if len(ss)==1 else 'Mixed' if ss else 'none'])
                meta=dict(control=False,source_id=rid,line_id=rid,source=r['source'],primary_class='headings_caps',crop_sha256=digest,original_crop_sha256=r['original_crop_sha256'],output_kind=r['output_kind'],usable_final=f['usable_final'],crop_tight_page=f['crop_tight_page'])
            iid='k'+hashlib.sha256((SEED+':'+context+':'+rid).encode()).hexdigest()[:10]
            assert iid not in key['items'] and iid not in old['items']
            dest=directory/'crops'/(digest+'.png')
            assert sha(source)==digest
            shutil.copyfile(source,dest)
            assert not dest.is_symlink() and dest.stat().st_nlink==1 and not os.path.samefile(source,dest)
            cards.append(dict(card_id=iid,crop='crops/'+dest.name,google_text=text,word_scripts=scripts))
            key['items'][iid]=meta
            custody.append(dict(opaque_id=iid,context=context,line_id=rid,source=str(source),destination=str(dest),sha256=digest))
        key['readers'][context]=[r['card_id'] for r in cards]
        jsonl(directory/'cards.jsonl',cards)
        jsonl(HERE/'pack_inventory'/(context+'.cards.jsonl'),cards)
    dump(HERE/'keys/caps3.json',key)
    dump(HERE/'keys/control_truth.json',controls)
    dump(HERE/'keys/crop_custody.json',custody)
    (HERE/'prompts').mkdir(exist_ok=True)
    shutil.copyfile(REFERENCE/'prompts/bsb.md',HERE/'prompts/caps3.md')
    inputs=[HERE/'keys/n1_locked_eval_observed_ids.txt',HERE/'exclusion_drift.json',HERE/'keys/release_exclusions_observed.json',HERE/'screen_receipt.json',prior/'keys/pool.jsonl',prior/'keys/caps1.json',prior/'keys/draw.jsonl',prior/'keys/control_truth.json',REFERENCE/'HANDOVER.md',REFERENCE/'prompts/bsb.md',OUT/'records.jsonl',OUT/'binding.json',HERE/'screen.jsonl',HERE.parent/'run.py']
    artifact_files=[OUT/'selection.json']+sorted(OUT.glob('*/pages/*_provenance.json'))
    dump(OUT/'artifact_receipt.json',dict(records_sha256=sha(OUT/'records.jsonl'),selection_sha256=sha(OUT/'selection.json'),files=[dict(path=str(p.relative_to(OUT)),sha256=sha(p)) for p in artifact_files]))
    dump(HERE/'build_receipt.json',dict(seed=SEED,pool=len(pool),masked_total=len(records),excluded_caps1=sum(r['id'] in excluded and r['matched'] for r in records),cards=100,controls=10,inputs={str(p):sha(p) for p in inputs},draw_per_source=dict(__import__('collections').Counter(r['source'] for r in selected)),readers_started=0,network='OFF'))

if __name__=='__main__':build()
