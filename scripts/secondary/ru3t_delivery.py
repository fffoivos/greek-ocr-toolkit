"""RU2TF3 offline delivery: retained-geometry sheets and frozen-truth LQB deltas."""
import base64
from collections import Counter, defaultdict
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path
import random
import sys
import subprocess
from PIL import Image
import ru3t as m
import ru1_lead_sheets as sheets
from ru1_review import symbol_crops

SEED = '20261017:RU3T0:audit'
OUT = m.SCRATCH/'ru1_review/ru3t'
INPUTS = {}


def bind(path):
    path=Path(path);INPUTS[str(path)]=m.sha(path);return path


class Crops:
    def __init__(self):
        self.lookup={}
        for ctx in json.loads((m.ART/'build.json').read_text())['contexts']:
            name=ctx['context'];key=json.loads(bind(m.ART/f'keys/{name}.json').read_text())
            for item in m.rows(bind(m.PACK/name/'r1/items.jsonl')):
                self.lookup[name,item['item_id']]=(item,key['items'][item['item_id']])
        self.admitted={r['id']:r for r in m.rows(bind(m.WORK/'docs/records/harvest/cyrillic/admitted.jsonl'))}
        self.records={r['id']:r for r in m.rows(bind(m.WORK/'docs/records/harvest/cyrillic/records.jsonl'))}
        self.parent={r['id']:r for r in m.rows(bind(m.SOURCE)) if r['id'] in self.admitted}

    @lru_cache(maxsize=16)
    def doc(self,pid):
        assignment=json.loads(bind(m.WORK/f'docs/records/harvest/cyrillic/assignments/{pid}.json').read_text())
        if assignment['coordinate_frame']['converted']:raise ValueError('transformed geometry requires explicit mapping')
        storage=bind(m.SOURCE.parents[4]/assignment['reader']['storage_path'])
        if m.sha(storage)!=assignment['reader']['storage_sha256']:raise ValueError('raw storage changed')
        packed=json.loads(gzip.decompress(storage.read_bytes())) if storage.suffix=='.gz' else json.loads(storage.read_text())
        if 'image_references' in packed:
            raw=packed['response']
            for ref in packed['image_references']:
                image=bind(m.SOURCE.parents[4]/ref['path']);data=image.read_bytes()
                if m.sha(image)!=ref['sha256']:raise ValueError('raw image changed')
                raw['document']['pages'][ref['page']]['image']['content']=base64.b64encode(data).decode('ascii')
            blob=(json.dumps(raw,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
            if hashlib.sha256(blob).hexdigest()!=assignment['reader']['raw_sha256']:raise ValueError('raw reconstruction changed')
        else:raw=packed
        return raw['document']

    @lru_cache(maxsize=128)
    def get(self,ctx,iid,offset):
        if ctx=='retained':
            rid=iid;r=self.admitted[rid];path=bind(m.SOURCE.parents[4]/r['crop_path'])
            meta=dict(book=m.book_id(self.parent[rid]),source_crop_sha256=r['crop_sha256'])
        else:
            item,meta=self.lookup[ctx,iid];rid=meta['row_id'];r=self.admitted[rid]
            path=bind(m.PACK/ctx/'r1'/item['crop'])
        record=self.records[rid]
        if m.sha(path)!=meta['source_crop_sha256'] or m.sha(path)!=r['crop_sha256']:raise ValueError('crop custody mismatch')
        if r['label']!=self.parent[rid]['label']:raise ValueError('parent/admission text mismatch')
        doc=self.doc(r['page_id']);line=doc['pages'][0]['lines'][record['docai_index']]
        with Image.open(path) as im:image=im.convert('RGB')
        if image.size!=(r['crop_width'],r['crop_height']):raise ValueError('crop dimensions differ')
        word,final,geo=symbol_crops(image,r['label'],offset,doc,line,r['crop_bbox'][:2])
        return dict(line=image,word=word,final=final,geometry=geo,crop=str(path),crop_sha256=m.sha(path),book=meta['book'])


def build_sheets():
    INPUTS.clear()
    OUT.mkdir(parents=True,exist_ok=True);crops=Crops();positions={}
    for ctx in json.loads((m.ART/'build.json').read_text())['contexts']:
        name=ctx['context'];key=json.loads(bind(m.ART/f'keys/{name}.json').read_text())
        for iid,meta in key['items'].items():
            if meta['control']:continue
            for slot in meta['slots']:
                k=meta['row_id'],slot['offset']
                positions[k]=dict(row_id=k[0],offset=k[1],book=meta['book'],google=slot['google'],reads=[],ctx=name,iid=iid)
    decisions=list(m.rows(bind(m.ART/'decisions.jsonl')))
    for d in decisions:
        p=positions[d['row_id'],d['offset']];d.update(book=p['book'],ctx=p['ctx'],iid=p['iid'])
        p['reads']=[v for v in d['reads'].values() if v]
    rng=random.Random(SEED)
    hard_pool=[d for d in decisions if d['decision']=='edit_hard']
    hard,quotas=sheets.proportional(hard_pool,min(40,len(hard_pool)),rng) if hard_pool else ([],{})
    soft_pool=sorted([d for d in decisions if d['decision']=='keep_soft'],key=lambda d:(d['row_id'],d['offset']))
    soft=rng.sample(soft_pool,min(20,len(soft_pool)))
    review=[d for d in decisions if d['decision']=='lead_review'];cells=[]
    for kind,ds in [('review',review),('audit',hard+soft)]:
        for d in ds:cells.append(dict(d,cell=len(cells)+1,set=kind))
    refs={}
    for bi,book in enumerate(sorted({c['book'] for c in cells}),1):
        refs[book]={}
        for sign in ('ъ','ь'):
            candidates=sorted([p for p in positions.values() if p['book']==book and len(p['reads'])==2 and all(r['call']==sign for r in p['reads'])],key=lambda p:(p['row_id'],p['offset']))
            basis='agreement';status='agreement reference, not adjudicated'
            if not candidates:
                # No new reading: mechanically selected labelled glyph, visibly distinguished.
                basis='google_label';status='Google label only; not adjudicated'
                candidates=[dict(row_id=r['id'],offset=r['label'].index(sign),book=book,google=sign,reads=[],ctx='retained',iid=r['id'])
                            for r in sorted(crops.parent.values(),key=lambda r:r['id']) if m.book_id(r)==book and sign in r['label']]
            if not candidates:raise ValueError('no retained same-book reference: '+book+' '+sign)
            p=candidates[0];im=crops.get(p['ctx'],p['iid'],p['offset'])
            rid=f'book{bi:02}_{"hard" if sign=="ъ" else "soft"}';path=OUT/'references'/f'{rid}.png';path.parent.mkdir(exist_ok=True)
            sheets.scaled(im['final'],8).save(path)
            refs[book][sign]=dict(p,reference_id=rid,basis=basis,status=status,path=str(path),crop_sha256=im['crop_sha256'],geometry=im['geometry'])
    sheets.OUT=OUT
    index=sheets.render(cells,refs,crops)
    m.dump(OUT/'references.json',refs);m.dump(OUT/'sheets_index.json',dict(cells=len(index),items=index))
    template=m.ART/'lead_review_template.jsonl'
    m.jsonl(template,[{k:c[k] for k in ['cell','row_id','offset','set']} | dict(lead=None,note='') for c in cells])
    assert len(index)==len(list(m.rows(template)))==len(review)+len(hard)+len(soft)
    assert Counter(c['decision'] for c in cells if c['set']=='audit')==Counter(d['decision'] for d in hard+soft)
    for path in OUT.rglob('*.png'):
        with Image.open(path) as im:im.load()
    assert all(m.sha(p)==h for p,h in INPUTS.items())
    return dict(path=str(OUT),review_cells=len(review),audit_cells=len(hard)+len(soft),audit_requested=dict(edit_hard=40,keep_soft=20),audit_shortfall=dict(edit_hard=40-len(hard),keep_soft=20-len(soft)),seed=SEED,hard_book_quotas=quotas,reference_basis='same-book two-reader agreement; Soviet hard sign uses labelled internal Google glyph only; neither basis is adjudicated',inputs=INPUTS,outputs={str(p):m.sha(p) for p in [*OUT.rglob('*.png'),OUT/'references.json',OUT/'sheets_index.json',template]},validation='index/template counts, exact geometry alignment, PNG decoding; no visual reading performed')


def score_lqb(manifest):
    target=m.WORK/'docs/records/labelfix/lqb'/('score_'+manifest['version']+'.json')
    python=Path.home()/'Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python'
    truth=m.WORK/'docs/records/labelfix/lqb/truth_v1_1.jsonl'
    subprocess.run(['/usr/bin/arch','-arm64',str(python),'-B','-m','greekocr.labelfix.lqb','trend','--truth',str(truth),'--registry',str(m.REGISTRY),'--output',str(target)],cwd=m.WORK,check=True)
    score=json.loads(target.read_text());delta=score['paired']['collection_v2_train→'+manifest['version']]
    m.dump(m.ART/'lqb_delta.json',delta)
    return dict(registered=True,score=str(target),sha256=m.sha(target),truth_sha256=m.sha(truth),delta=delta)

def deliver(manifest):
    result=dict(status='FINALISED',manifest=manifest,sheets=build_sheets(),lqb=score_lqb(manifest),network=False,new_readings=False,git_writes=False)
    m.dump(m.ART/'FINALIZED_RECEIPT.json',result)
    return result
