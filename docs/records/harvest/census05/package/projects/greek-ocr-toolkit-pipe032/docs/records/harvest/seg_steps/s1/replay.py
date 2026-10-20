"""Offline native 0.8/0.9-s1 replay; gate2 inputs/scoring, plus frozen cells."""
from pathlib import Path
import os,sys,json,gzip,hashlib,importlib.util,signal,time
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'docs/harvest/collect_v3_admission/segeval1';SITE=R.parent/'ocr-review-sites-20261018'
sys.path.insert(0,str(R))
os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',PYTHONDONTWRITEBYTECODE='1')
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[k]='1'
def offline(event,args):
 if event in ('socket.connect','socket.connect_ex','socket.getaddrinfo'):raise RuntimeError('network OFF: SEG S1')
sys.addaudithook(offline)
from greekocr.harvest.line_pipeline_native import NativeSegmenter,character_count
spec=importlib.util.spec_from_file_location('gate2',S/'gate2/replay.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return [json.loads(s) for s in Path(p).read_text().splitlines() if s.strip()]
def dump(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def write(p,rs):Path(p).write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True,allow_nan=False)+'\n' for r in rs))
def inputs():
 feats=g.load(S/'keys/selected_features.jsonl','row_id');sealed=g.load(S/'keys/sealed_decisions.jsonl','row_id');owner=g.load(S/'scored/owner_rows.jsonl','line_id')
 out=[]
 for old in read(S/'gate2/replay_segeval1.jsonl'):
  rid=old['line_id'];s=sealed[rid];state,faults=g.owner_state(owner[rid])
  row=dict(feats[rid],**s['segmentation']['binding'],raw_text=s['google_text'],crop_path=str(S/'crops'/f'{rid}.png'))
  out.append(dict(cohort='segeval1',line_id=rid,row=row,owner_standard_state=state,owner_faults=faults,reader_answer=owner[rid]['reader_answer']))
 report=json.loads((SITE/'review-data/box-length-experiment.json').read_text())['rows']
 natives={r['id']:r for r in json.loads(gzip.decompress((SITE/'review-data/font-normalized/predicted-rows.json.gz').read_bytes()))}
 pop=json.loads((SITE/'review-data/population.json').read_text());chunks={}
 for old in report:
  rid=old['id'];meta=natives[rid]
  if meta.get('google_text') is None or 'content_class' not in meta:
   chunk=old['index']//pop['detail_chunk_size']
   if chunk not in chunks:chunks[chunk]=json.loads(gzip.decompress((SITE/f'population-data/details/{chunk:05d}.json.gz').read_bytes()))
   detail=chunks[chunk][old['index']%pop['detail_chunk_size']];assert detail[0]==rid and detail[4]==old['image_sha256']
   codes=dict(part.split(':') for part in detail[8].split('|'));meta['google_text']=detail[2];meta['content_class']=pop['codebooks']['classes'][int(codes['class'])]
  assert character_count(meta['google_text'])==old['characters']
  row=dict(id=rid,parent_id='accepted-calibration-888',split='unassigned',crop_sha256=old['image_sha256'],crop_path=str(SITE/'population-images'/(old['image_sha256']+'.png')),raw_text=meta['google_text'],script_class=old['script'],primary_class=meta['content_class'])
  out.append(dict(cohort='calibration',line_id=rid,row=row,owner_rating=old['owner_rating']))
 for s in read(S/'cells/samples.jsonl'):
  rid=s['row_id'];p=S/'cells/samples'/f'{rid}.png';assert sha(p)==s['crop_sha256']
  row=dict(id=rid,parent_id=s['parent_id'],split='unassigned',crop_sha256=s['crop_sha256'],crop_path=str(p),raw_text=s['text'],script_class=s['script_class'],primary_class=s['primary_class'])
  out.append(dict(cohort='cells',line_id=rid,row=row,sample_group=s['sample_group']))
 assert [sum(r['cohort']==c for r in out) for c in ('segeval1','calibration','cells')]==[150,888,250]
 return out

def timeout(*args):raise TimeoutError('native row exceeded gate2 120s bound')

def run():
 rows=inputs();write(D/'inputs.jsonl',rows)
 versions=json.loads((R/'docs/harvest/line_pipeline/tool_versions.json').read_text())['tools']
 oldv=json.loads((D/'baseline/docs/harvest/line_pipeline/tool_versions.json').read_text())['tools']
 predictor=R/'scripts/harvest/filter_runtime/target/debug/greekocr-frozen-font-predict'
 old=NativeSegmenter(oldv,predictor);new=NativeSegmenter(versions,predictor)
 spec=importlib.util.spec_from_file_location('crop_tools_08',D/'baseline/greekocr/harvest/filtering_assets/crop-tools.py');old.crop_tools=importlib.util.module_from_spec(spec);spec.loader.exec_module(old.crop_tools)
 contexts={r['id']:r for r in json.loads((SITE/'qa/word-tolerance/context-evidence.json').read_text())['rows']}
 witnesses={'gazette_modern--80e8a42cbf8e629f--s000-l0120','129cff40-p000009-l0107'}
 captures={};active=[None]
 orig=new.crop_tools.line_inventory
 def capture(glyphs,lines,components,angle):
  result=orig(glyphs,lines,components,angle)
  if active[0] in witnesses:
   captures[active[0]]=dict(width=glyphs.width,height=glyphs.height,xheight=float(glyphs.band.xh),components=components,lines=[dict(side=l.side,mean=l.mean.tolist(),base=l.base.tolist()) for l in lines],angle=angle)
  return result
 new.crop_tools.line_inventory=capture
 signal.signal(signal.SIGALRM,timeout);start=time.monotonic()
 try:
  with (D/'replay.jsonl').open('w') as f:
   for i,inp in enumerate(rows,1):
    cohort=inp['cohort'];row=inp['row'];active[0]=inp['line_id']
    for worker in (old,new):
     if cohort=='calibration':worker.context=lambda r,*args:contexts.get(r['id'],dict(status='unavailable',reason='no saved calibration source context'))
     else:worker.context=NativeSegmenter.context.__get__(worker)
    signal.alarm(120);a=old(row);b=new(row);signal.alarm(0)
    assert a['binding']==b['binding'] and a['raw_text_sha256']==b['raw_text_sha256']
    rec=dict(inp,before=a,after=b,verdict_08=a['verdict'],verdict_09=b['verdict'])
    f.write(json.dumps(rec,ensure_ascii=False,sort_keys=True,allow_nan=False)+'\n');f.flush()
    if i%25==0:print(f'{i}/1288 {cohort}',flush=True)
 finally:signal.alarm(0);old.close();new.close()
 dump(D/'witness_native.json',captures);dump(D/'replay_receipt.json',dict(rows=len(rows),elapsed_seconds=time.monotonic()-start,network='OFF via audit hook',readers=0,predictor_sha256=sha(predictor)))
if __name__=='__main__':run()
