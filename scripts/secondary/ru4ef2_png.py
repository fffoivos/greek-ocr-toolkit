"""Offline PNG-only RU4EF2 lead sheets using RU3T renderer and retained symbols."""
import base64
from collections import Counter, defaultdict
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path
import random
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ru4ef1 as f
import ru1_lead_sheets as sheets
from ru1_review import symbol_crops
from PIL import Image
m=f.m
OUT=f.OUT/'png'
SEED='RU4EF2:20261018:post-replacement:audit:20+10'
INPUTS={}

def bind(p):
    p=Path(p);INPUTS[str(p)]=m.sha(p);return p

class Crops:
    def __init__(self):
        self.lookup={}
        self.parent={r['id']:r for r in m.rows(bind(f.ART/'census_all_rows.jsonl'))}
        self.families={}
        for c in json.loads(bind(f.ART/'build.json').read_text())['contexts']:
            ctx=c['context'];key=json.loads(bind(f.ART/f'keys/{ctx}.json').read_text())['items']
            for item in m.rows(bind(f.PACK/ctx/'r1/items.jsonl')):
                meta=key[item['item_id']]
                if not meta['control']:self.lookup[meta['row_id']]=(f.PACK/ctx/'r1'/item['crop'],item,meta)

    def family(self,rid):
        if rid in self.lookup:
            original=Path(self.lookup[rid][2]['original_crop'])
        else:
            r=self.parent[rid];original=Path(r['crop'])
            if not original.is_absolute():original=m.SOURCES[r['ru4e_split']].parents[4]/original
        parts=original.parts;idx=parts.index('harvest_big')
        family=parts[idx+1];root=Path(*parts[:idx-2])
        return root,family,original

    def records(self,root,family):
        key=root,family
        if key not in self.families:
            base=root/'docs/harvest'/family
            self.families[key]=({r['id']:r for r in m.rows(bind(base/'admitted.jsonl'))},
                                {r['id']:r for r in m.rows(bind(base/'records.jsonl'))})
        return self.families[key]

    @lru_cache(maxsize=16)
    def doc(self,root,family,pid):
        assignment=json.loads(bind(root/'docs/harvest'/family/'assignments'/f'{pid}.json').read_text())
        if assignment.get('coordinate_frame',{}).get('converted'):raise ValueError('transformed coordinates')
        storage=bind(root/assignment['reader']['storage_path'])
        if m.sha(storage)!=assignment['reader']['storage_sha256']:raise ValueError('raw storage changed')
        packed=json.loads(gzip.decompress(storage.read_bytes())) if storage.suffix=='.gz' else json.loads(storage.read_text())
        if 'image_references' in packed:
            raw=packed['response']
            for ref in packed['image_references']:
                path=bind(root/ref['path'])
                if m.sha(path)!=ref['sha256']:raise ValueError('raw image changed')
                raw['document']['pages'][ref['page']]['image']['content']=base64.b64encode(path.read_bytes()).decode('ascii')
            blob=(json.dumps(raw,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
            if hashlib.sha256(blob).hexdigest()!=assignment['reader']['raw_sha256']:raise ValueError('raw reconstruction changed')
        else:raw=packed
        return raw.get('document',raw)

    @lru_cache(maxsize=128)
    def get(self,ctx,iid,offset):
        rid=iid;root,family,original=self.family(rid)
        admitted,records=self.records(root,family);r=admitted[rid]
        if m.sha(bind(original))!=r['crop_sha256']:raise ValueError('native crop custody changed')
        if rid in self.lookup:
            path,item,meta=self.lookup[rid];bind(path)
            if m.sha(path)!=meta['source_crop_sha256']:raise ValueError('pack crop changed')
        else:path=original
        with Image.open(path) as src:image=src.convert('RGB')
        with Image.open(original) as src:
            if src.convert('RGB').tobytes()!=image.tobytes() or src.size!=image.size:raise ValueError('pack/native pixels differ')
        if image.size!=(r['crop_width'],r['crop_height']):raise ValueError('crop frame changed')
        if self.parent[rid]['label']!=r['label']:raise ValueError('parent/admitted text differs')
        doc=self.doc(root,family,r['page_id']);line=doc['pages'][0]['lines'][records[rid]['docai_index']]
        word,final,geo=symbol_crops(image,r['label'],offset,doc,line,r['crop_bbox'][:2])
        return dict(line=image,word=word,final=final,geometry=geo,crop=str(path),crop_sha256=m.sha(path),book=m.bid(self.parent[rid]))

def build():
    report=json.loads(bind(f.ART/'RU4EF2_COMBINE.json').read_text())
    ds=m.rows(bind(f.ART/'decisions.jsonl'))
    assert report['decisions_sha256']==m.sha(f.ART/'decisions.jsonl')
    OUT.mkdir(parents=True,exist_ok=True);crops=Crops();rng=random.Random(SEED)
    hard=sorted([d for d in ds if d['decision']=='edit_hard'],key=lambda d:(d['row_id'],d['offset']))
    soft=sorted([d for d in ds if d['decision']=='keep_soft'],key=lambda d:(d['row_id'],d['offset']))
    audit=rng.sample(hard,20)+rng.sample(soft,10)
    review=[d for d in ds if d['reason'] in ('reader_disagreement','uncertain_read')]
    cells=[]
    for kind,group in [('audit',audit),('review',review if len(review)<=40 else [])]:
        for d in group:
            reads={r['logical_reader']:r for r in d['reads']}
            cells.append(dict(d,cell=len(cells)+1,set=kind,ctx='native',iid=d['row_id'],reads=reads))
    targets={(c['row_id'],c['offset']) for c in cells};positions=defaultdict(list)
    for identity,state in report['contexts'].items():
        if state['status']!='VALID':continue
        if len(identity.split('/'))==2:a=f.ART;ctx,reader=identity.split('/')
        else:
            repl=next(r for r in report['replacements']+report.get('r5_replacements',[]) if r['identity']==identity)
            a=Path(repl['art']);ctx,reader=repl['context'],repl['reader']
        for p in m.rows(bind(a/'answers'/(m.stem(ctx,reader)+'.mapped.jsonl'))):
            if not p['control']:positions[p['row_id'],p['offset']].append(p)
    refs={}
    for bi,book in enumerate(sorted({c['book'] for c in cells}),1):
        refs[book]={}
        for sign in ('ъ','ь'):
            eligible=sorted([k for k,v in positions.items() if k not in targets and m.bid(crops.parent[k[0]])==book and len(v)==2 and all(p['call']==sign for p in v)])
            basis='agreement';status='agreement reference, not adjudicated'
            if not eligible:
                basis='google_label';status='Google label only; not adjudicated'
                eligible=[(r['id'],i) for r in sorted(crops.parent.values(),key=lambda r:r['id']) if m.bid(r)==book for i,ch in enumerate(r['label']) if ch==sign and (r['id'],i) not in targets]
            for rid,off in eligible:
                try:im=crops.get('native',rid,off)
                except (ValueError,KeyError):continue
                break
            else:raise ValueError('no aligned same-book reference '+book+' '+sign)
            refid=f'book{bi:02}_{"hard" if sign=="ъ" else "soft"}'
            refs[book][sign]=dict(reference_id=refid,ctx='native',iid=rid,row_id=rid,offset=off,book=book,basis=basis,status=status,geometry=im['geometry'],crop_sha256=im['crop_sha256'],reads=positions.get((rid,off),[]))
    sheets.OUT=OUT
    index=sheets.render(cells,refs,crops)
    m.dump(OUT/'references.json',refs);m.dump(OUT/'sheets_index.json',dict(cells=len(index),items=index))
    template=[{k:c[k] for k in ('cell','set','row_id','offset','sheet','sheet_cell','crop_sha256','decision','reason')} | dict(call=None,pixel_checked=False,reviewer=None,note=None) for c in index]
    m.jsonl(OUT/'template.jsonl',template)
    for kind in ('audit','review'):m.jsonl(OUT/(kind+'_template.jsonl'),[c for c in template if c['set']==kind])
    assert Counter(c['decision'] for c in index if c['set']=='audit')==dict(edit_hard=20,keep_soft=10)
    assert len({(c['row_id'],c['offset']) for c in index})==len(index)
    assert max(Counter(c['sheet'] for c in index).values())<=10
    assert len(index)==30+(len(review) if len(review)<=40 else 0)
    for p in OUT.glob('*.png'):
        with Image.open(p) as im:im.load()
    assert all(m.sha(p)==h for p,h in INPUTS.items())
    result=dict(path=str(OUT),seed=SEED,audit_cells=30,review_cells=len(review),review_rendered=len(review)<=40,audit_pngs=len({c['sheet'] for c in index if c['set']=='audit'}),review_pngs=len({c['sheet'] for c in index if c['set']=='review'}),inputs=INPUTS,outputs=m.bindings([*OUT.glob('*.png'),*[p for p in OUT.glob('*.json') if p.name!='manifest.json'],*OUT.glob('*.jsonl')]),validation='native pixel custody, retained exact text-anchor geometry, scales 8x/4x, index/template distinct positions and PNG decoding; no lead rulings')
    m.dump(OUT/'manifest.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('inputs','outputs')},indent=2))
if __name__=='__main__':build()
