"""RUC1 offline mechanical pack preparation; never launches a reader."""
from __future__ import annotations
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import hashlib,json,random,shutil,os,unicodedata
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[4]
PROJECTS=REPO.parent
REFERENCE=PROJECTS/'greek-ocr-toolkit-sol-reading/docs/harvest/sol_reading'
COLLECTOR=PROJECTS/'greek-ocr-toolkit-sol-collect'
W1=PROJECTS/'collect-v3-data/run/W1'
RU1=PROJECTS/'greek-ocr-toolkit-secondary/artifacts/ru1/ru1_v1.jsonl'
EXPECTED='1fb0a9f5bde4a166fd480ffb414d5e376596b600fd728b6e099b6b1803af2db0'
EXCLUSIONS=COLLECTOR/'docs/harvest/collect_v3/release_exclusions'
PACK_ROOT=Path('/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs')
BED=PACK_ROOT/'ruc1'
SEED='ruc1:ia_russian:cyrillic'
FIELDS={'card_id','crop','google_text','word_scripts'}
PYTHON=COLLECTOR/'.venv/bin/python'
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
def rows(path):
 with Path(path).open() as f:return [json.loads(l) for l in f if l.strip()]
def dump(path,value):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def jsonl(path,value):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(''.join(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n' for r in value))
def io_guard():
 allowed=(HERE.resolve(),BED.resolve(),(PACK_ROOT/'launchers').resolve())
 def writable(p):
  if isinstance(p,int) or os.fsdecode(p)==os.devnull:return
  p=Path(os.fsdecode(p)).resolve()
  if not any(p==a or a in p.parents for a in allowed):raise PermissionError('RUC1 output outside task: '+str(p))
 def audit(event,args):
  if event.startswith('socket.'):raise PermissionError('RUC1 network OFF: '+event)
  if event=='open' and args[2] & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND):writable(args[0])
  elif event in ('os.mkdir','os.remove','os.rmdir','os.chmod','os.truncate'):writable(args[0])
  elif event in ('os.rename','os.link','os.symlink'):writable(args[0]);writable(args[1])
 sys.addaudithook(audit)
def word_scripts(text):
 result=[]
 for word in text.split():
  scripts={next((s for s in ('Greek','Latin','Cyrillic') if s.upper() in unicodedata.name(c,'')),'Other') for c in word if c.isalpha()}
  result.append([word,next(iter(scripts)) if len(scripts)==1 else 'Mixed' if scripts else 'none'])
 return result
def inputs():
 assert sha(RU1)==EXPECTED
 manifest=RU1.with_name('ru1_v1_manifest.json');m=json.loads(manifest.read_text());assert m['sha256']==EXPECTED
 repair=rows(RU1);assert len(repair)==314 and len({r['id'] for r in repair})==314
 assert sum(r['status']=='ok' for r in repair)==311 and sum(r['status']=='hold' for r in repair)==3
 repair={r['id']:r for r in repair}
 allrows={}
 with (W1/'features.jsonl').open() as f:
  for line in f:
   r=json.loads(line)
   if r['source']=='ia_russian' or r['id'] in repair:
    assert r['id'] not in allrows;allrows[r['id']]=r
 for rid,r in repair.items():assert allrows[rid]['label']==r['label_parent'],rid
 cpath=W1/'c1/ia_russian__cyrillic_key.json';c1={r['line_id'] for r in json.loads(cpath.read_text()).values() if isinstance(r,dict) and 'line_id' in r};assert len(c1)==100
 cfgpath=EXCLUSIONS/'release_exclusions.json';cfg=json.loads(cfgpath.read_text())
 bindings={str(p):sha(p) for p in (RU1,manifest,W1/'features.jsonl',cpath,cfgpath,REFERENCE/'HANDOVER.md',REFERENCE/'prompts/bsb.md',COLLECTOR/'collect_v3/storage.py',COLLECTOR/'collect_v3/common.py')}
 classes={}
 for name,meta in cfg['classes'].items():
  p=EXCLUSIONS/meta['file'];assert sha(p)==meta['sha256']
  ids={l.strip() for l in p.read_text().splitlines() if l.strip() and not l.lstrip().startswith('#')};assert len(ids)==meta['n']
  classes[name]=ids;bindings[str(p)]=sha(p)
 assert 'rotated_crop' in classes
 holds={rid for rid,r in repair.items() if r['status']=='hold'}
 excluded=set.union(c1,holds,*classes.values())
 pool=sorted([r for r in allrows.values() if r['source']=='ia_russian' and r['primary_class']=='cyrillic' and r['candidate_usable'] is True and r['id'] not in excluded],key=lambda r:r['id'])
 return pool,repair,classes,c1,bindings
def draw(pool):return random.Random(SEED).sample(sorted(pool,key=lambda r:r['id']),100)
def order_seed(context):return SEED+':order:'+context
def label(row,repair):
 r=repair.get(row['id']);return r['label_ru1_v1'] if r and r['status']=='ok' else row['label']
def build():
 assert Path(sys.executable).resolve()==PYTHON.resolve() and Path(sys.prefix).resolve()==PYTHON.parent.parent.resolve(), 'Run only with collector .venv/bin/python'
 io_guard();assert not BED.exists(),'Refuse to overwrite pack'
 pool,repair,classes,c1,bindings=inputs();selected=draw(pool)
 prior=HERE.parent/'caps1';old=json.loads((prior/'keys/caps1.json').read_text());controls=json.loads((prior/'keys/control_truth.json').read_text())
 assert {c['source_card']['card_id'] for c in controls}=={'c057','c009','c013','c026','c046','c041','c029','c072','c035','c066'}
 for p in (prior/'keys/caps1.json',prior/'keys/control_truth.json'):bindings[str(p)]=sha(p)
 existing={c['card_id'] for p in PACK_ROOT.glob('*/*/cards.jsonl') for c in rows(p)}
 sys.path.insert(0,str(COLLECTOR));from collect_v3.storage import ensure_crop
 key=dict(bed='ruc1',protocol='bsb',seed=SEED,readers={},items={});custody=[]
 for n,context in enumerate(('c1','c2')):
  batch=[(r,None) for r in selected[n*50:(n+1)*50]]+[(None,c) for c in controls if c['context']==context]
  random.Random(order_seed(context)).shuffle(batch);directory=BED/context;(directory/'crops').mkdir(parents=True);public=[]
  for row,control in batch:
   if control:
    meta=dict(old['items'][control['opaque_id']]);card=control['source_card'];rid=meta['line_id']
    previous=next(c for c in rows(PACK_ROOT/'caps1'/context/'cards.jsonl') if c['card_id']==control['opaque_id'])
    source=PACK_ROOT/'caps1'/context/previous['crop'];text=card['google_text'];scripts=card['word_scripts'];method='reused lead-approved CAPS1b control'
   else:
    rid=row['id'];source=HERE/'cache'/(row['crop_sha256']+'.png');assert not source.exists(),'Regeneration requires fresh cache'
    assert ensure_crop(dict(row,crop=str(source)))==source
    text=label(row,repair);scripts=word_scripts(text);method='collector storage.ensure_crop; collector interpreter'
    meta=dict(control=False,source_id=rid,line_id=rid,source=row['source'],primary_class=row['primary_class'],crop_sha256=row['crop_sha256'],label_parent=row['label'],label_used=text,ru1_ok=rid in repair and repair[rid]['status']=='ok',label_repaired=text!=row['label'])
   digest=meta['crop_sha256'];assert sha(source)==digest
   iid='k'+hashlib.sha256((SEED+':'+context+':'+rid).encode()).hexdigest()[:10];assert iid not in existing and iid not in key['items']
   dest=directory/'crops'/(digest+'.png');shutil.copyfile(source,dest)
   assert sha(dest)==digest and dest.stat().st_nlink==1 and not dest.is_symlink() and not os.path.samefile(source,dest)
   public.append(dict(card_id=iid,crop='crops/'+dest.name,google_text=text,word_scripts=scripts));key['items'][iid]=meta
   custody.append(dict(opaque_id=iid,context=context,line_id=rid,source=str(source),destination=str(dest),sha256=digest,method=method));bindings[str(source)]=sha(source)
  key['readers'][context]=[c['card_id'] for c in public];jsonl(directory/'cards.jsonl',public);jsonl(HERE/'pack_inventory'/(context+'.cards.jsonl'),public)
 dump(HERE/'keys/ruc1.json',key);shutil.copyfile(prior/'keys/control_truth.json',HERE/'keys/control_truth.json');dump(HERE/'keys/crop_custody.json',custody)
 jsonl(HERE/'keys/pool.jsonl',[dict(id=r['id'],label_parent=r['label'],label_used=label(r,repair),label_repaired=label(r,repair)!=r['label'],ru1_ok=r['id'] in repair and repair[r['id']]['status']=='ok') for r in pool])
 jsonl(HERE/'keys/draw.jsonl',[dict(id=r['id'],label_repaired=label(r,repair)!=r['label']) for r in selected])
 (HERE/'prompts').mkdir(exist_ok=True);shutil.copyfile(REFERENCE/'prompts/bsb.md',HERE/'prompts/ruc1.md')
 dump(HERE/'adapter_approval.json',dict(approved=True,authority='User RUC1 explicitly requests CAPS1 adapter',scope='grayscale original crops and disjoint contexts',reference_files_read_only=True))
 receipt=dict(seed=SEED,pool=len(pool),pool_repaired=sum(label(r,repair)!=r['label'] for r in pool),pool_ru1_ok=sum(r['id'] in repair and repair[r['id']]['status']=='ok' for r in pool),cards=100,draw_repaired=sum(label(r,repair)!=r['label'] for r in selected),draw_ru1_ok=sum(r['id'] in repair and repair[r['id']]['status']=='ok' for r in selected),controls=10,crops_regenerated=100,interpreter=sys.executable,invoked_interpreter=str(PYTHON),inputs=bindings,readers_started=0,network='OFF',release_exclusion_classes={k:len(v) for k,v in classes.items()},parent_labels_verified=314)
 dump(HERE/'build_receipt.json',receipt);print(json.dumps({k:v for k,v in receipt.items() if k!='inputs'}))
if __name__=='__main__':build()
