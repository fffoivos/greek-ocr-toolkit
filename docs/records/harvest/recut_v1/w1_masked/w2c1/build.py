"""W2C1 mechanical preparation. Never launches Codex or touches live-run locks."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import hashlib,json,random,shutil,os,re,unicodedata
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[4];PROJECTS=REPO.parent
COLLECTOR=PROJECTS/'greek-ocr-toolkit-sol-collect';LIVE=PROJECTS/'collect-v3-data/run'
REFERENCE=PROJECTS/'greek-ocr-toolkit-sol-reading/docs/harvest/sol_reading'
PACK_ROOT=Path('/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs')
CANONICAL='dd2fc59d6385601146f8cfb3f23ff48aec2e769188f65def282f4b72e489c547'
SNAPSHOT=PROJECTS/'collect-v3-data/snapshots/W2_features_20261018_0524.jsonl'
SNAPSHOT_SHA='4954a94cc3c051aeb36e367101bc3448233448422bb05834d3276e090de987b4'
SNAPSHOT_ROWS=219381
STRATA=[('bsb_poly1850','poly1850'),('ia_poly1850','poly1850'),('nlg','poly1850'),('nlg','poly1900'),('nlg','greek_poly'),('serbia','cyrillic'),('elstat','numerics_tables'),('gazette_modern','modern_scanned')]
FIELDS={'card_id','crop','google_text','word_scripts'}
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def snapshot_rows(path=SNAPSHOT,expected_sha=SNAPSHOT_SHA,expected_rows=SNAPSHOT_ROWS):
 # Verify the complete immutable input before returning any sampling rows.
 h=hashlib.sha256();selected=[];n=0
 with Path(path).open('rb') as f:
  for line in f:
   h.update(line);r=json.loads(line);n+=1
   if r['tranche']!='W2':raise ValueError('snapshot contains non-W2 row')
   if (r['source'],r['primary_class']) in STRATA:selected.append(r)
 if h.hexdigest()!=expected_sha:raise ValueError('snapshot sha256 mismatch')
 if n!=expected_rows:raise ValueError('snapshot row count mismatch')
 return selected
def rows(p):return [json.loads(l) for l in Path(p).read_text().splitlines() if l.strip()]
def dump(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def jsonl(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in v))
def bedname(source,cls):return 'w2c1_'+source+'_'+cls
def seed(source,cls):return 'w2c1:'+source+':'+cls
def draw(pool,source,cls):return random.Random(seed(source,cls)).sample(sorted(pool,key=lambda r:r['id']),min(100,len(pool)))
def rotated(r):
 a,b,c,d=r['crop_bbox'];return d-b>c-a and sum(not x.isspace() for x in r['label'])>=4
def exclusions():
 base=COLLECTOR/'docs/harvest/collect_v3/release_exclusions';p=base/'release_exclusions.json';cfg=json.loads(p.read_text());classes={};bindings={str(p):sha(p)}
 for name,meta in cfg['classes'].items():
  f=base/meta['file'];assert sha(f)==meta['sha256'],name
  ids={l.strip() for l in f.read_text().splitlines() if l.strip() and not l.lstrip().startswith('#')};assert len(ids)==meta['n'];classes[name]=ids;bindings[str(f)]=sha(f)
 return cfg,classes,bindings
def eligible(r,source,cls,excluded):return r['tranche']=='W2' and r['source']==source and r['primary_class']==cls and r['candidate_usable'] is True and not r['screen_merged'] and not rotated(r) and r['id'] not in excluded and (source!='gazette_modern' or r.get('gazette_stratum')=='measured_1986_1990')
def scripts(text):
 result=[]
 for w in text.split():
  s={next((s for s in ('Greek','Latin','Cyrillic') if s.upper() in unicodedata.name(c,'')),'Other') for c in w if c.isalpha()};result.append([w,next(iter(s)) if len(s)==1 else 'Mixed' if s else 'none'])
 return result
def guard():
 allowed=[HERE,PACK_ROOT/'launchers']+[PACK_ROOT/bedname(*s) for s in STRATA]
 def audit(event,args):
  if event.startswith('socket.'):raise PermissionError('W2C1 network OFF')
  if event=='open' and not isinstance(args[0],int):
   p=Path(args[0]).resolve()
   if LIVE.resolve() in p.parents and p.name.startswith('features'):raise PermissionError('live features reads forbidden')
  if event=='open' and args[2]&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND):
   if not isinstance(args[0],int) and str(args[0])!=os.devnull:
    p=Path(args[0]).resolve()
    if not any(p==a or a in p.parents for a in allowed):raise PermissionError('W2C1 outside output: '+str(p))
 sys.addaudithook(audit)
def build():
 assert Path(sys.prefix).resolve()==(COLLECTOR/'.venv').resolve();guard()
 f=SNAPSHOT;method='verified W2_features_20261018_0524.jsonl snapshot; no replay'
 rr=snapshot_rows()
 cfg,classes,bindings=exclusions();dump(HERE/'keys/release_exclusions_at_start.json',cfg)
 excluded=set().union(*classes.values());bindings[str(f)]=SNAPSHOT_SHA
 prior=HERE.parent/'caps1';old=json.loads((prior/'keys/caps1.json').read_text());controls=json.loads((prior/'keys/control_truth.json').read_text())
 assert {c['source_card']['card_id'] for c in controls}=={'c057','c009','c013','c026','c046','c041','c029','c072','c035','c066'}
 for p in [prior/'keys/caps1.json',prior/'keys/control_truth.json',REFERENCE/'prompts/bsb.md',REFERENCE/'HANDOVER.md']:bindings[str(p)]=sha(p)
 dump(HERE/'keys/control_truth.json',controls)
 existing={c['card_id'] for p in PACK_ROOT.glob('*/*/cards.jsonl') for c in rows(p)};summary={};custody=[];closure=[]
 sys.path.insert(0,str(COLLECTOR));from collect_v3.storage import ensure_crop
 for source,cls in STRATA:
  bed=bedname(source,cls);root=PACK_ROOT/bed;assert not root.exists(),'Refuse overwrite '+bed
  pool=sorted([r for r in rr if eligible(r,source,cls,excluded)],key=lambda r:r['id']);selected=draw(pool,source,cls)
  assert len({r['id'] for r in pool})==len(pool)
  jsonl(HERE/'keys'/bed/'pool.jsonl',pool);jsonl(HERE/'keys'/bed/'draw.jsonl',selected)
  key=dict(bed=bed,protocol='bsb',seed=seed(source,cls),readers={},items={})
  for n,ctx in enumerate(('c1','c2')):
   # Pools below 100 retain all rows; split at 50, preserve five controls/context.
   batch=[(r,None) for r in selected[n*50:(n+1)*50]]+[(None,c) for c in controls if c['context']==ctx]
   random.Random(seed(source,cls)+':order:'+ctx).shuffle(batch);directory=root/ctx;(directory/'crops').mkdir(parents=True);public=[]
   for row,control in batch:
    if control:
     meta=dict(old['items'][control['opaque_id']]);rid=meta['line_id'];card=control['source_card'];text=card['google_text'];ws=card['word_scripts']
     previous=next(c for c in rows(PACK_ROOT/'caps1'/ctx/'cards.jsonl') if c['card_id']==control['opaque_id']);original=PACK_ROOT/'caps1'/ctx/previous['crop'];methodcrop='lead-approved CAPS1/CAPS1b reuse'
    else:
     rid=row['id'];original=Path(row['crop']);methodcrop='existing original'
     if not original.exists():
      original=HERE/'cache'/(row['crop_sha256']+'.png');ensure_crop(dict(row,crop=str(original)));methodcrop='collector storage.ensure_crop, collector interpreter'
     text=row['label'];ws=scripts(text);meta=dict(control=False,source_id=rid,line_id=rid,source=source,primary_class=cls,tranche='W2',crop_sha256=row['crop_sha256'])
    digest=meta['crop_sha256'];assert sha(original)==digest
    iid='k'+hashlib.sha256((seed(source,cls)+':'+ctx+':'+rid).encode()).hexdigest()[:10];assert iid not in existing;existing.add(iid)
    dest=directory/'crops'/(digest+'.png');shutil.copyfile(original,dest);assert sha(dest)==digest
    public.append(dict(card_id=iid,crop='crops/'+dest.name,google_text=text,word_scripts=ws));key['items'][iid]=meta
    custody.append(dict(bed=bed,context=ctx,opaque_id=iid,line_id=rid,source=str(original),destination=str(dest),sha256=digest,method=methodcrop))
   key['readers'][ctx]=[r['card_id'] for r in public];jsonl(directory/'cards.jsonl',public);jsonl(HERE/'pack_inventory'/bed/(ctx+'.cards.jsonl'),public)
  dump(HERE/'keys'/(bed+'.json'),key)
  summary[bed]=dict(source=source,primary_class=cls,seed=seed(source,cls),pool=len(pool),draw=len(selected),below_100=len(pool)<100,w2_rows=sum(r['source']==source and r['primary_class']==cls for r in rr),candidate_before_filters=sum(r['source']==source and r['primary_class']==cls and r['candidate_usable'] is True for r in rr))
 dump(HERE/'keys/crop_custody.json',custody)
 dump(HERE/'build_receipt.json',dict(pool_method=method,features_path=str(f),features_sha256=bindings[str(f)],w2_rows=SNAPSHOT_ROWS,gazette_filter={'field':'gazette_stratum','value':'measured_1986_1990'},bsb_snapshot_pages=298,strata=summary,inputs=bindings,release_exclusion_classes={k:len(v) for k,v in classes.items()},canonical_scanner_sha256=CANONICAL,readers_started=0,network='OFF',interpreter=sys.executable,bsb_partial=True))
 print(json.dumps(summary,indent=2))
if __name__=='__main__':build()
