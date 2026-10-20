"""CQ4c offline intake, deterministic selection and blind pack build."""
import sys
sys.dont_write_bytecode=True
import collections as C
import functools,gzip,hashlib,io,json,math,random,re,socket,shutil,unicodedata as U
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'artifacts/cq4';R2=ROOT/'docs/labelfix/spellcheck/R2';P=ROOT.parent
sys.path.insert(0,str(ROOT))
from greekocr.labelfix import ink,case,segmentation
from greekocr.labelfix.ctc_align import Alignment
SEED=20261017
SCANNER_SHA='e44f8c8a3c6d478c3dc299863478fcab210298f1c1429870d516c546f0f54ad1'
PREREG_SHA='dbac559fe9792a4f7c879f1fc7b08d03c6a82611bbb42ecce1ffd4ae31ccbebc'
SCRATCH=OUT/'packs'
PREP=P/'greek-ocr-toolkit-spellcheck-r2prep';EXPORT=PREP/'artifacts/labelfix_r2/output_3681404'
HASHES={}
def forbidden(*a,**kw):raise RuntimeError('CQ4c build is offline')
socket.socket.connect=forbidden;socket.create_connection=forbidden
@functools.lru_cache(None)
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def bind(p):p=Path(p);HASHES[str(p)]=sha(p);return p
def load(p):return json.loads(bind(p).read_text())
def rows(p):
 p=bind(p)
 with (gzip.open(p,'rt') if p.suffix=='.gz' else p.open()) as f:return [json.loads(s) for s in f if s.strip()]
def dump(p,x):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def jsonl(p,x):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in x))
def alias(d):return d.removesuffix(':human').split(':')[-1]
def identity(r):return tuple(r['slot_id'])
def digest(s):return hashlib.sha256(s.encode()).hexdigest()
def marked(text,start):
 # Combining marks on the base or a spacing/preposed compound immediately before it.
 text=U.normalize('NFD',text);end=start+1
 while end<len(text) and U.combining(text[end]):end+=1
 segment=text[start:end]
 if start and text[start-1] in '᾿῾᾽':segment=text[start-1:end]
 return any(c in '\u0313\u0314\u0301\u0300\u0342᾿῾᾽' for c in segment)
def label_marked(label,pred,start):
 letters=lambda s:''.join(c for c in U.normalize('NFD',s) if c.isalpha() and c not in '᾿᾽῾')
 if letters(label)!=letters(pred):return False
 n=sum(c.isalpha() and c not in '᾿᾽῾' for c in pred[:start]);offsets=[i for i,c in enumerate(U.normalize('NFD',label)) if c.isalpha() and c not in '᾿᾽῾']
 return n<len(offsets) and marked(label,offsets[n])
def save(im,rd):
 b=io.BytesIO();im.convert('RGB').save(b,format='PNG');data=b.getvalue();name=hashlib.sha256(data).hexdigest()+'.png';p=rd/'img'/name
 if not p.exists():p.write_bytes(data)
 return 'img/'+name

def intake():
 prereg=PREP/'docs/labelfix/spellcheck/R2/R2A2_PREREGISTRATION.md';assert sha(bind(prereg))==PREREG_SHA
 src=P/'greek-ocr-toolkit-sol-reading/docs/harvest/sol_reading/tools/scan_rollout.py'
 assert sha(bind(src))==SCANNER_SHA and sha(OUT/'tools/scan_rollout.py')==SCANNER_SHA
 old=load(OUT/'prior_cq4b/excluded_docs.json');groups=old['by_reason']
 # T2 and old training documents cease to be document exclusions for TOP-UP.
 topgroups={k:v for k,v in groups.items() if k not in ('T2','old_pool_316')}
 validation=set(groups['validation']);unused=set(load(OUT/'prior_cq4/inventory.json')['wcap_candidate_documents'])
 wdocs=validation|unused
 topgroups['W_CAP']=sorted(wdocs);tex=set().union(*(set(v) for v in topgroups.values()))
 wex=set(old['wcap']['documents']);assert not wdocs&wex
 dump(OUT/'excluded_docs.json',dict(by_reason=topgroups,documents=sorted(tex),count=len(tex),topup=dict(documents=sorted(tex)),wcap=dict(documents=sorted(wex),eligible_documents=sorted(wdocs)),allowed_topup_document_groups=['T2/supervision','old_pool_316 except held-out and other exclusions'],scanner_sha256=SCANNER_SHA))
 pop={r['line_id']:r for r in rows(PREP/'artifacts/labelfix_r2/population/population.jsonl')}
 meta={r['id']:r for r in rows(R2/'eligible_lines.jsonl')}
 # Population also contains teacher-seen training lines outside R2C.
 for r in rows(P/'greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_train.jsonl'):
  if r['id'] in pop:meta.setdefault(r['id'],r)
 v2={identity(r) for r in rows(PREP/'artifacts/r2a_manifest/r2a_slots_v2.jsonl')}
 t2keys=rows(R2/'decks/T2/private/key.jsonl');t2slots=set()
 # Exclude every letter slot represented on a T2 word, not merely its anchor.
 for k in t2keys:
  t2slots.update((k['crop_sha256'],k['crop_letter_offset']+j) for j,c in enumerate(''.join(c for c in U.normalize('NFD',k['mining_key']) if U.category(c).startswith('L'))))
 duplicate=load(PREP/'docs/labelfix/spellcheck/R2/evidence/r2a/old_pool_duplicates.json')
 dupkeys={tuple(g['slot_id']) for g in duplicate['groups']};assert len(dupkeys)==duplicate['repeated_keys']==5
 receipt=load(EXPORT/'READBACK_RECEIPT.json');assert not receipt['failures'];verified={r['path']:r for r in receipt['files']}
 pools={'wcap':[],'topup':[]};seen=set();aligned=C.Counter();rejected=C.Counter()
 for number,f in enumerate(sorted((EXPORT/'B').glob('*-alignments.jsonl.gz'))):
  def verify(p):
   r=verified[str(p.relative_to(EXPORT))];assert r['sha256_verified'] and sha(bind(p))==r['sha256'];return p
  ars=rows(verify(f));wanted={}
  for ar in ars:
   r=pop[ar['line_id']];d=alias(r['doc']);aligned[d]+=1
   which='wcap' if d in wdocs else 'topup' if r['role']=='train' and d not in tex else None
   if not which:continue
   pred=ar['alignment']['prediction']
   assert ''.join(s[0] for s in ar['alignment']['spans'])==pred
   for start,c in enumerate(pred):
    if c not in 'ΑΕΗΙΟΥΩΡ':continue
    sid=(r['crop_sha256'],start);li=sum(U.category(ch).startswith('L') for ch in pred[:start])
    if which=='topup' and (sid in v2 or (r['crop_sha256'],li) in t2slots):rejected['existing_slot']+=1;continue
    if sid in dupkeys:raise RuntimeError('ambiguous old identity for replacement')
    if sid in seen:rejected['duplicate_candidate']+=1;continue
    seen.add(sid)
    a=start
    while a>0 and not pred[a-1].isspace():a-=1
    b=start+1
    while b<len(pred) and not pred[b].isspace():b+=1
    spans=ar['alignment']['spans'];word=pred[a:b];label=meta.get(r['line_id'],{}).get('text','')
    likely=marked(pred,start) or label_marked(label,pred,start)
    kind='all_caps' if ''.join(ch for ch in word if ch.isalpha()).isupper() and sum(ch.isalpha() for ch in word)>1 else 'numeral_adjacent' if any(ch.isdigit() for ch in pred[max(0,a-4):min(len(pred),b+4)]) else 'sentence_initial'
    x=dict(slot_id=list(sid),line_id=r['line_id'],doc=d,source=r['source'],role=r['role'],teacher_seen_document=r.get('teacher_seen_document',False),crop=r['crop'],alignment=ar['alignment'],letter_index=li,likely='marked' if likely else 'bare',bare_kind=kind,word_start=a,word_end=b,source_era=meta.get(r['line_id'],{}).get('year','unknown'),page=meta.get(r['line_id'],{}).get('page_id',re.sub(r'-l\d+$','',r['line_id'])),set=which)
    wanted[sid]=x
  # Locate capitals against physically separate teacher exports, never another role.
  for role in ('validation_reserve','train','witness'):
   if not any(pop[x['line_id']]['role']==role for x in wanted.values()):continue
   tf=f.with_name(f.name.replace('alignments',role));verify(tf)
   with gzip.open(tf,'rt') as inp:
    for line in inp:
     if not re.search(r'"base": "[ΑΕΗΙΟΥΩΡ]"',line):continue
     t=json.loads(line);sid=identity(t);x=wanted.get(sid)
     if x is None:continue
     if t['line_id']!=x['line_id'] or t['role']!=x['role']:continue
     assert alias(t['doc'])==x['doc']
     x['teacher_export']=str(tf);x['coverage']=t['coverage'];x['crop_validity']=t['crop_validity'];pools[x['set']].append(x)
  if number%400==0:print('intake chunks',number,'capital candidates', {k:len(v) for k,v in pools.items()},flush=True)
 dropped=sorted(d for d in unused if not aligned[d]);dump(OUT/'keys/intake.json',dict(scanner_sha256=SCANNER_SHA,aligned_lines_per_document=dict(aligned),unused_documents_dropped=dropped,unused_reason='no saved alignment' if dropped else None,rejected=dict(rejected)))
 dump(OUT/'keys/candidates.json',pools);dump(OUT/'keys/intake_hashes.json',HASHES)
 return pools

@functools.lru_cache(None)
def local_paths():
 return {r['sha256']:str(Path(r['local']) if Path(r['local']).is_absolute() else PREP/r['local']) for r in rows(PREP/'artifacts/labelfix_r2/population/local_crops.jsonl')}

@functools.lru_cache(256)
def physical(line_id,crop,expected,alignment_json):
 p=Path(crop)
 if not p.exists():
  candidates=[Path(local_paths().get(expected,'/nonexistent')),PREP/'artifacts/labelfix_r2/population/upload'/f'{expected}.png',P/'greek-ocr-toolkit'/crop,R2/'native_crops'/f'{expected}.png']
  p=next((q for q in candidates if q.exists()),p)
 assert p.exists(),p
 assert sha(bind(p))==expected,p
 with Image.open(p) as im:im=im.convert('RGB')
 al=Alignment.from_record(json.loads(alignment_json));ii=ink.analyse(im);case.estimate_font(ii);ss=segmentation.recogniser_slots(ii,al.prediction,al);case.prepare(ii,ss)
 return p,im,{s['start']:s for s in ss}
def qualify(x):
 p,im,ss=physical(x['line_id'],x['crop'],x['slot_id'][0],json.dumps(x['alignment'],sort_keys=True))
 s=ss.get(x['slot_id'][1]);
 if not s or s.get('case_class')!='capital' or s.get('localisation_unknown') or s.get('segmentation_uncertain'):return None
 c=s['component'];a=x['word_start'];b=x['word_end'];sp=x['alignment']['spans'];lo=max(0,min(math.floor(sp[a][3])-12,c.x0-12));hi=min(im.width,max(math.ceil(sp[b-1][4])+12,c.x1+12))
 if hi<=lo:return None
 y={k:v for k,v in x.items() if k!='alignment'};y.update(native_asset=str(p),native_size=list(im.size),target_box_native=[c.x0,0,c.x1,im.height],word_box=[lo,0,hi,im.height],case_evidence={k:s.get(k) for k in ('case_class','case_source','capital_probability','recogniser_upper','case_disagreement','segmentation_source')})
 return y

def choose(pool,targets,doccap,pagecap=5):
 rng=random.Random(SEED);pool=sorted(pool,key=lambda x:(x['doc'],x['line_id'],x['slot_id'][1]));rng.shuffle(pool)
 counts=C.Counter();pages=C.Counter();out=[];classcounts=C.Counter();bad=0
 # Round-robin documents avoids concentrating the result in a few books.
 groups=C.defaultdict(list)
 for x in pool:groups[x['doc']].append(x)
 ds=sorted(groups);rng.shuffle(ds)
 while any(groups.values()) and any(classcounts[k]<v for k,v in targets.items()):
  for d in ds:
   if not groups[d] or counts[d]>=doccap:groups[d]=[];continue
   x=groups[d].pop();key=x['likely']
   if classcounts[key]>=targets[key] or pages[x['page']]>=pagecap:continue
   y=qualify(x)
   if y is None:bad+=1;continue
   out.append(y);counts[d]+=1;pages[x['page']]+=1;classcounts[key]+=1
 print('selected',dict(classcounts),'docs',len(counts),'case/geometry rejected',bad,flush=True)
 return out,dict(classcounts)

def render(x,rd,rng,tag):
 with Image.open(x['native_asset']) as im:line=im.convert('RGB')
 assert sha(bind(x['native_asset']))==x['slot_id'][0]
 l,t,r,b=x['word_box'];word=line.crop((l,t,r,b)).resize(((r-l)*3,(b-t)*3),Image.Resampling.LANCZOS)
 box=x['target_box_native'];ImageDraw.Draw(word).rectangle([(box[0]-l)*3,1,(box[2]-l)*3,word.height-2],outline=(220,0,0),width=2)
 bo=['none','smooth','rough','unreadable'];ao=['none','acute','grave','circumflex','unreadable'];rng.shuffle(bo);rng.shuffle(ao)
 ident='k'+digest(f'{SEED}:{tag}:{x["slot_id"]}')[:10]
 return dict(item_id=ident,word_image=save(word,rd),line_image=save(line,rd),breathing_options=dict(zip('ABCD',bo)),accent_options=dict(zip('ABCDE',ao)))

def controls():
 key={x['card_id']:x for x in rows(R2/'decks/T2/private/key.jsonl')};pool=[]
 for r in rows(ROOT/'artifacts/r2_resolve/T2/final/resolved.jsonl'):
  k=key[r['card_id']]
  if r['readability']!='readable' or k['anchor_index']!=0:continue
  h=next((h for h in r['letter_heads'] if h['index']==0),None)
  if not h or h['base'] not in 'αεηιουω' or h['breathing'] not in ('none','psili','dasia') or h['accent'] not in ('none','acute','grave','circumflex') or (h['breathing'],h['accent'])==('none','none'):continue
  # Exact base agreement keeps the resolved control tied to its native word.
  bare=lambda t:''.join(c for c in U.normalize('NFD',t) if U.category(c).startswith('L'))
  if bare(r['printed_form'])!=bare(k['mining_key']):continue
  path=Path(k['crop'])
  if not path.exists():path=Path(local_paths().get(k['crop_sha256'],'/nonexistent'))
  if not path.exists():path=PREP/'artifacts/labelfix_r2/population/upload'/(k['crop_sha256']+'.png')
  if not path.exists():path=R2/'decks/T2/blind'/k['public']['line_image']
  # Use the same native component box method as CQ1, with conservative first-glyph bounds.
  with Image.open(path) as im:im=im.convert('RGB');ii=ink.analyse(im)
  l,t,rr,b=k['word_box'];cs=[c for c in ii.components if c.role=='letter' and l<=c.cx<rr]
  if not cs:continue
  c=min(cs,key=lambda c:c.x0)
  if c.w>1.3*ii.xh or c.h<.6*ii.xh:continue # skip a fused multi-letter control target
  pool.append(dict(slot_id=[k['crop_sha256'],k['crop_letter_offset']],line_id=k['line_id'],doc=alias(k['doc']),native_asset=str(path),native_size=list(im.size),word_box=k['word_box'],target_box_native=[c.x0,0,c.x1,im.height],control=True,source_id=k['card_id'],expected=dict(breathing={'psili':'smooth','dasia':'rough','none':'none'}[h['breathing']],accent=h['accent'])))
 pool.sort(key=lambda x:digest(str(SEED)+x['source_id']));assert len(pool)>=40,len(pool)
 chosen=pool[:40];dump(OUT/'keys/control_pool.json',chosen)
 review=OUT/'control_review';review.mkdir(exist_ok=True);sheet=Image.new('RGB',(1800,40*180),'white');d=ImageDraw.Draw(sheet)
 for i,x in enumerate(chosen):
  with Image.open(x['native_asset']) as im:im=im.convert('RGB')
  l,t,r,b=x['word_box'];word=im.crop((l,t,r,b)).resize(((r-l)*3,(b-t)*3));bb=x['target_box_native'];ImageDraw.Draw(word).rectangle([(bb[0]-l)*3,1,(bb[2]-l)*3,word.height-2],outline=(220,0,0),width=2);word.thumbnail((1500,140));sheet.paste(word,(10,i*180+30));d.text((10,i*180+5),f'{i+1:02d} '+x['source_id']+' '+json.dumps(x['expected']),fill='black')
 sheet.save(review/'controls.png');dump(review/'lead_review.json',dict(scanner_sha256=SCANNER_SHA,status='pending',sheet_sha256=sha(review/'controls.png'),instruction='Lead pixel-verifies all 40 before any reading.',items=[dict(source_id=x['source_id'],verified=False) for x in chosen]))
 return chosen

def build_context(data,ctrls,setname,n,phase='initial'):
 rng=random.Random(SEED+n+len(setname)+1000*(phase=='reread'));tag=f'{setname}_{phase}_{n:03d}';rd=SCRATCH/f'solcap_{setname}'/tag/'r1'
 assert not rd.exists(),f'Refuse overwrite {rd}'
 (rd/'img').mkdir(parents=True);allitems=[x|dict(control=False) for x in data]+rng.sample(ctrls,10);rng.shuffle(allitems);private={};public=[]
 for x in allitems:
  item=render(x,rd,rng,tag);public.append(item);private[item['item_id']]=x|dict(public=item)
 jsonl(rd/'items.jsonl',public)
 for name in ('README.md','answer_schema.json'):
  source=OUT/'templates'/name
  shutil.copyfile(source,rd/name)
 dump(OUT/'keys'/f'{tag}.json',dict(set=setname,phase=phase,items=private,readers={'r1':[r['item_id'] for r in public]}))
 from closure import scan
 closure=scan(rd,private);assert closure['ok'],closure;dump(OUT/'closure'/f'{tag}.json',closure)
 return dict(tag=tag,set=setname,phase=phase,manifest_sha256=sha(rd.parent/f'MANIFEST.{rd.name}.json'),directory=str(rd),key=str(OUT/'keys'/f'{tag}.json'),items=len(public),bed_items=len(data),controls=10,scanner_sha256=SCANNER_SHA)

def main():
 pools=intake() if not (OUT/'keys/candidates.json').exists() else load(OUT/'keys/candidates.json')
 if (OUT/'keys/intake_hashes.json').exists():HASHES.update(load(OUT/'keys/intake_hashes.json'))
 selected={};counts={}
 for name,targets,cap,minimum in [('wcap',dict(marked=150,bare=150),30,210),('topup',dict(marked=470,bare=735),120,844)]:
  selected[name],counts[name]=choose(pools[name],targets,cap)
  jsonl(OUT/'keys'/f'{name}_selected.jsonl',selected[name])
  inv=dict(scanner_sha256=SCANNER_SHA,set=name,target=sum(targets.values()),minimum=minimum,selected=len(selected[name]),classes=counts[name],documents=dict(C.Counter(x['doc'] for x in selected[name])),raw_by_document={d:dict(C.Counter(x['likely'] for x in pools[name] if x['doc']==d)) for d in sorted({x['doc'] for x in pools[name]})})
  dump(OUT/f'{name}_inventory.json',inv);print('INVENTORY',name,json.dumps(inv,ensure_ascii=False),flush=True)
  assert len(selected[name])>=minimum,('STOP 70% inventory gate',name,len(selected[name]),minimum)
 assert not {x['doc'] for x in selected['wcap']}&{x['doc'] for x in selected['topup']}
 dump(OUT/'keys/selection_hashes.json',HASHES)
 ctrls=controls();contexts=[]
 for name,data in selected.items():
  random.Random(SEED).shuffle(data)
  for n,i in enumerate(range(0,len(data),90)):contexts.append(build_context(data[i:i+90],ctrls,name,n))
 dump(OUT/'contexts.json',contexts)
 dump(OUT/'build_receipt.json',dict(status='BUILD_READY_PENDING_LEAD_CONTROL_REVIEW',seed=SEED,preregistration_sha256=PREREG_SHA,scanner_sha256=SCANNER_SHA,scanner_version='v4.4-canonical',inputs_sha256=HASHES,selected={k:dict(documents=len({x['doc'] for x in v}),slots=len(v),classes=counts[k]) for k,v in selected.items()},contexts=len(contexts),controls_pool=40,codex_estimated_points=round(sum(x['items'] for x in contexts)*.002,3),reader_runs=0,training_runs=0,manifest_builds=0,weekly_usage=None,overlay_policy='Replace existing unique R1 identities in place; never append an existing key; STOP ambiguous old key. No manifest built.',old_duplicate_guard=load(PREP/'docs/labelfix/spellcheck/R2/evidence/r2a/old_pool_duplicates.json')['repeated_keys']))
 print('BUILD contexts',len(contexts),flush=True)
if __name__=='__main__':main()
