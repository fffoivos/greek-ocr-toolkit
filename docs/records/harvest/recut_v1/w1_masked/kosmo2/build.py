"""KR1 blinded packs; controls and closure policy inherited from CAPS1."""
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
BED=PACK_ROOT/'kosmo2'
SEED='kr1:kosmo:poly1850'
FIELDS={'card_id','crop','google_text','word_scripts'}
SOURCE=HERE.parent/'cards_kosmo_poly1850/reader'

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
def io_guard():
    def audit(event,args):
        if event.startswith('socket.'):raise PermissionError('KR1 network OFF: '+event)
    sys.addaudithook(audit)

def draw(cards):
    result=sorted(cards,key=lambda c:c['card_id'])
    random.Random(SEED).shuffle(result)
    return result

def order_seed(context):return SEED+':order:'+context

def build():
    io_guard()
    assert not BED.exists(), 'Refuse to overwrite an existing pack'
    prior=HERE.parent/'caps1'
    t6gkey=HERE.parent/'cards_kosmo_poly1850_key.json'
    sourcekey=json.loads(t6gkey.read_text())
    cards=rows(SOURCE/'cards.jsonl');assert len(cards)==100
    selected=draw(cards)
    old=json.loads((prior/'keys/caps1.json').read_text())
    controls=json.loads((prior/'keys/control_truth.json').read_text())
    assert {c['source_card']['card_id'] for c in controls}=={'c057','c009','c013','c026','c046','c041','c029','c072','c035','c066'}
    existing=set()
    for f in PACK_ROOT.glob('*/*/cards.jsonl'):
        existing.update(c['card_id'] for c in rows(f))
    key=dict(bed='kosmo2',protocol='bsb',seed=SEED,readers={},items={})
    custody=[];inputs=[t6gkey,SOURCE/'cards.jsonl',prior/'keys/caps1.json',prior/'keys/control_truth.json',HERE.parent/'cards_kosmo_poly1850_sol_key.json',REFERENCE/'HANDOVER.md',REFERENCE/'prompts/bsb.md']
    for n,context in enumerate(('c1','c2')):
        batch=[(c,None) for c in selected[n*50:(n+1)*50]]+[(None,c) for c in controls if c['context']==context]
        random.Random(order_seed(context)).shuffle(batch)
        directory=BED/context;(directory/'crops').mkdir(parents=True)
        public=[]
        for card,control in batch:
            if control:
                meta=dict(old['items'][control['opaque_id']]);card=control['source_card']
                previous=next(c for c in rows(PACK_ROOT/'caps1'/context/'cards.jsonl') if c['card_id']==control['opaque_id'])
                source=PACK_ROOT/'caps1'/context/previous['crop'];digest=meta['crop_sha256']
            else:
                meta=dict(sourcekey[card['card_id']]);meta.update(control=False,source='kosmopolis',source_id=meta['line_id'],source_public_id=card['card_id'],crop_sha256=meta['card_crop_sha256'])
                source=SOURCE/card['crop'];digest=meta['crop_sha256']
            rid=meta['line_id'];iid='k'+hashlib.sha256((SEED+':'+context+':'+rid).encode()).hexdigest()[:10]
            assert iid not in existing and iid not in key['items']
            assert sha(source)==digest
            dest=directory/'crops'/(digest+'.png');shutil.copyfile(source,dest)
            assert dest.stat().st_nlink==1 and not dest.is_symlink() and not os.path.samefile(source,dest)
            public.append(dict(card_id=iid,crop='crops/'+dest.name,google_text=card['google_text'],word_scripts=card['word_scripts']))
            key['items'][iid]=meta
            custody.append(dict(opaque_id=iid,context=context,line_id=rid,source=str(source),destination=str(dest),sha256=digest))
            inputs.append(source)
        key['readers'][context]=[c['card_id'] for c in public]
        jsonl(directory/'cards.jsonl',public);jsonl(HERE/'pack_inventory'/(context+'.cards.jsonl'),public)
    dump(HERE/'keys/kosmo2.json',key);dump(HERE/'keys/control_truth.json',controls);dump(HERE/'keys/crop_custody.json',custody)
    jsonl(HERE/'keys/draw.jsonl',[dict(id=sourcekey[c['card_id']]['line_id'],source_public_id=c['card_id']) for c in selected])
    (HERE/'prompts').mkdir(exist_ok=True);shutil.copyfile(REFERENCE/'prompts/bsb.md',HERE/'prompts/kosmo2.md')
    dump(HERE/'adapter_approval.json',dict(approved=True,authority='User KR1 explicitly requests CAPS1 adapter',scope='CAPS1 grayscale and disjoint-context adapter; kosmopolis poly1850 bed / bsb poly1850 controls',reference_files_read_only=True))
    dump(HERE/'build_receipt.json',dict(seed=SEED,cards=100,controls=10,inputs={str(p):sha(p) for p in inputs},readers_started=0,network='OFF',crops_regenerated=0,prior_run=dict(commit='87db4392',label='pre-handover, no controls',letters=96,crop_ok=99)))

if __name__=='__main__':build()
