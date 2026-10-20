"""AU1 offline construction. No reader, network, inference, or git invocation."""
import argparse, collections, gzip, hashlib, io, json, math, random, re, unicodedata as U
from pathlib import Path
from PIL import Image, ImageDraw
A=Path(__file__).resolve().parent
REPO=A.parents[2]
PROJECTS=REPO.parent
SR=PROJECTS/'greek-ocr-toolkit-sol-reading/docs/harvest/sol_reading'
CQ=PROJECTS/'greek-ocr-toolkit-spellcheck-r2cards/artifacts'
PACK=Path('/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/sf7_audit')
SEED=20261017

def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def load(p):return json.loads(Path(p).read_text())
def rows(p):return [json.loads(s) for s in Path(p).read_text().splitlines() if s.strip()]
def dump(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def jsonl(p,x):Path(p).write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in x))
def bare(s):return ''.join(c for c in U.normalize('NFD',s) if c.isalpha())
def clusters(s):
 out=[]
 for c in U.normalize('NFD',s):
  if U.combining(c) and out:out[-1]+=c
  else:out.append(c)
 return out

def save(im,rd):
 b=io.BytesIO();im.convert('RGB').save(b,format='PNG');data=b.getvalue();name=hashlib.sha256(data).hexdigest()+'.png';(rd/'img'/name).write_bytes(data);return 'img/'+name

def render(m,rd,track):
 with Image.open(m['native_asset']) as im:line=im.convert('RGB')
 l,t,r,b=m['word_box'];a,_,z,_=m['target_box_native'];assert 0<=l<r<=line.width and 0<=a<z<=line.width
 word=line.crop((l,0,r,line.height));word=word.resize((word.width*3,word.height*3),Image.Resampling.LANCZOS)
 p=dict(word_image=save(word,rd),line_image=save(line,rd))
 if track=='capital':
  ImageDraw.Draw(word).rectangle(((a-l)*3,3,(z-l)*3,line.height*3-4),outline=(220,0,0),width=2)
  p['word_image']=save(word,rd)
  # Remove the unboxed image unless another item references it (closure removes unused images later).
 else:
  pad=max(6,(z-a)//2);letter=line.crop((max(0,a-pad),0,min(line.width,z+pad),line.height));letter=letter.resize((letter.width*8,letter.height*8),Image.Resampling.NEAREST)
  p.update(letter_image=save(letter,rd),word_bare=m['word_bare'],anchor_index=m['anchor_index'],anchor_base=m['anchor_base'])
 return p

def controls(track,excluded_docs):
 if track=='capital':
  review=load(CQ/'cq4/control_review/lead_review.json');assert review['status']=='verified'
  verified={x['source_id'] for x in review['items'] if x.get('verified') is True}
  pool=[dict(x) for x in load(CQ/'cq4/keys/control_pool.json') if x['source_id'] in verified and x['doc'] not in excluded_docs]
  for m in pool:m['verification']=str(CQ/'cq4/control_review/lead_review.json')
 else:
  review=SR/'grave/keys/control_review/LEAD_REVIEW.md';assert 'Controls, 6/6 valid' in review.read_text() and '26/26' in review.read_text()
  pool=[]
  for ident,x in load(SR/'grave/keys/key.json').items():
   # All 58 were lead-reviewed; do not use NLG members of the tested population.
   if x['stratum'] not in ('lekythos__poly1900','kosmopolis__poly1900'):continue
   g=x['geometry'];native=Path(g['source_crop']);assert sha(native)==g['source_crop_sha256']
   pool.append(dict(source_id=ident,doc=x['stratum']+':'+x['line_id'],line_id=x['line_id'],native_asset=str(native),word_box=g['render_word_box'],target_box_native=g['anchor']['box'],word_bare=bare(x['printed_word']),anchor_index=x['anchor_index'],anchor_base=x['anchor_base'],expected={'accent':x['truth_accent']},verification=str(review)))
 assert len(pool)>=10,(track,len(pool))
 rng=random.Random(f'{SEED}:{track}:controls');rng.shuffle(pool)
 if track=='accent':
  selected=[]
  for j in range(10):
   kind=['acute','grave','circumflex','none'][j%4];selected.append(next(m for m in pool if m['expected']['accent']==kind and m not in selected))
  pool=selected
 else:pool=pool[:10]
 for m in pool:m.update(control=True,heads=[])
 return pool

def write_context(name,track,entries,control_pool,phase='initial',order_name=None):
 rd=PACK/track/name;assert not rd.exists(),f'Refusing overwrite: {rd}';(rd/'img').mkdir(parents=True)
 rng=random.Random(f'{SEED}:{order_name or name}');mixed=[dict(m) for m in entries]+[dict(m) for m in control_pool];rng.shuffle(mixed)
 public=[];key={}
 for i,m in enumerate(mixed):
  ident='k'+hashlib.sha256(f'AU1:{SEED}:{name}:{i}'.encode()).hexdigest()[:10]
  p=render(m,rd,track);p['item_id']=ident
  if track=='capital':
   for head,vals,letters in [('breathing',['none','smooth','rough','unreadable'],'ABCD'),('accent',['none','acute','grave','circumflex','unreadable'],'ABCDE')]:
    rng.shuffle(vals);p[head+'_options']=dict(zip(letters,vals))
  public.append(p);key[ident]=dict(m,public=p,native_asset_sha256=sha(m['native_asset']))
 jsonl(rd/'items.jsonl',public)
 if track=='capital':
  (rd/'README.md').write_text('Judge the boxed letter from word_image and line_image. Use the independently permuted option mappings. Write answers.jsonl in item order.\n')
  dump(rd/'answer_schema.json',dict(type='object',additionalProperties=False,required=['item_id','breathing','accent','confidence','note'],properties={'item_id':{'type':'string','pattern':'^k[0-9a-f]{10}$'},'breathing':{'enum':list('ABCD')},'accent':{'enum':list('ABCDE')},'confidence':{'enum':['high','low']},'note':{'type':'string'}}))
 used={p[f] for p in public for f in ('word_image','letter_image','line_image') if f in p}
 for p in (rd/'img').iterdir():
  if str(p.relative_to(rd)) not in used:p.unlink()
 files={str(p.relative_to(rd)):sha(p) for p in sorted(rd.rglob('*')) if p.is_file()}
 dump(rd.parent/f'MANIFEST.{name}.json',{'files':files})
 dump(A/'keys'/f'{name}.json',key)
 return dict(name=name,track=track,phase=phase,reader_dir=str(rd),items=len(entries),controls=10,key=str(A/'keys'/f'{name}.json'),key_sha256=sha(A/'keys'/f'{name}.json'),manifest_sha256=sha(rd.parent/f'MANIFEST.{name}.json'))

def canonical_binding():
 handover=SR/'HANDOVER.md';data=handover.read_bytes()
 matches=re.findall(r'Canonical(?: (v[0-9.]+))? file sha256\s*=\s*([0-9a-f]{64})',data.decode())
 assert len(matches)==1,'ambiguous/missing canonical hash'
 version,expected=matches[0];src=SR/'tools/scan_rollout.py'
 assert sha(src)==expected,'canonical scanner mismatch'
 assert re.search(r"VERSION\s*=\s*['\"]"+re.escape(version.lstrip('v'))+r"['\"]",src.read_text()),'scanner version mismatch'
 return dict(version=version,source=str(src),expected=expected,actual=expected,handover=str(handover),handover_sha256=hashlib.sha256(data).hexdigest(),dependencies={name:sha(SR/'tools'/name) for name in ('scan_rollout.py','common.py','replay_literal.py')})

def build(fresh=None):
 binding_now=canonical_binding()
 preserved={}
 if fresh:
  assert re.fullmatch(r'[a-z][a-z0-9_]*',fresh),'invalid fresh namespace'
  archive=A/'build_history'/fresh;assert not archive.exists(),'fresh build already exists'
  assert not (A/'reread_contexts.json').exists(),'cannot replace contexts after reread construction'
  old=load(A/'contexts.json')
  for c in old:
   assert not (Path(c['reader_dir'])/'answers.jsonl').exists(),'cannot replace answered contexts'
   name=re.sub(r'(_initial_[0-9]{3}).*',r'\1',c['name'])+'_'+fresh
   assert not (PACK/c['track']/name).exists() and not (A/'keys'/f'{name}.json').exists() and not (A/'runs'/name).exists(),'fresh namespace collision'
  for path in [A.parent/'audit100_frame.jsonl',A/'routing.json',*sorted((A/'prompts').glob('*.md')),*sorted((A/'runs').rglob('*'))]:
   if path.is_file():preserved[str(path)]=sha(path)
  archive.mkdir(parents=True)
  for name in ('contexts.json','build_receipt.json','validation.json','handoff_hashes.json'):
   (archive/name).write_bytes((A/name).read_bytes())

 frame=rows(A.parent/'audit100_frame.jsonl');assert len(frame)==len({r['line_id'] for r in frame})==100
 selected={r['line_id']:r for r in frame};release={r['line_id']:r for r in rows(A.parent/'release_edits_only_A.jsonl') if r['line_id'] in selected};assert set(release)==set(selected)
 heads=[];items={'accent':{},'capital':{}};route_lines=[]
 for f in frame:
  r=release[f['line_id']];ll=[c for c in clusters(r['text']) if c[0].isalpha()];word_indices={};slot=0
  for wi,match in enumerate(re.finditer(r'\S+',r['text'])):
   chars=[c for c in clusters(match.group()) if c[0].isalpha()]
   for ai,c in enumerate(chars):word_indices[slot]=(wi,ai,bare(match.group()),c[0]);slot+=1
  assert slot==len(ll)
  lineheads=[]
  for ei,e in enumerate(r['edits']):
   c=ll[e['slot']];assert e['head'] in ('accent','breathing','subscript','dialytika'),e
   route='Sol-capital' if c[0].isupper() and e['head'] in ('breathing','accent') else 'Sol-accent' if c[0].islower() and e['head']=='accent' else 'Opus-later'
   uid=f'{f["audit_id"]}:{e["slot"]}:{e["head"]}'
   h=dict(head_id=uid,audit_id=f['audit_id'],line_id=f['line_id'],slot=e['slot'],head=e['head'],kind=e['kind'],base=c[0],route=route,released_label=e['to_part'] or 'none',edit_index=ei)
   if h['released_label'] in ('psili','dasia'):h['released_label']={'psili':'smooth','dasia':'rough'}[h['released_label']]
   heads.append(h);lineheads.append(uid)
   if route!='Opus-later':
    track='capital' if route=='Sol-capital' else 'accent';loc=(f['line_id'],e['slot']);wi,ai,word,base=word_indices[e['slot']]
    m=items[track].setdefault(loc,dict(line_id=f['line_id'],audit_id=f['audit_id'],slot=e['slot'],word_index=wi,word_bare=word,anchor_index=ai,anchor_base=base,heads=[],control=False,frame_crop=f['crop'],doc=f['doc']))
    m['heads'].append(uid)
  route_lines.append(dict(**f,heads=lineheads))
 counts=dict(collections.Counter(h['route'] for h in heads));assert sum(counts.values())==107
 dump(A/'routing.json',dict(frame_lines=100,seed=SEED,counts=counts,by_route_head={route:dict(collections.Counter(h['head'] for h in heads if h['route']==route)) for route in counts},lines=route_lines,heads=heads,opus_later_protocol='List only; two-reader four-head cards after Claude reset; not built.'))
 # Extract exactly the saved localisation evidence needed for these 82 targets.
 needed=set(release);cache=A/'keys/localisation.json'
 if not cache.exists():
  saved={}
  with gzip.open(A.parent/'output_3687228/release/overlay_A.jsonl.gz','rt') as stream:
   for line in stream:
    x=json.loads(line)
    if x['line_id'] in needed:
     ev=x['changes'][0]['evidence'];saved[x['line_id']]={'slots':ev['slots'],'recogniser_text':ev['recogniser_text']}
     if len(saved)==100:break
  assert set(saved)==needed;dump(cache,saved)
 saved=load(cache)
 for track,group in items.items():
  for (lid,slot),m in group.items():
   ev=saved[lid];ss=ev['slots'];s=ss[slot];assert bare(''.join(x['letter'] for x in ss))==bare(release[lid]['text'])
   # All slot starts refer to NFD recogniser coordinates. Verify word and anchor alignment independently.
   text=U.normalize('NFD',ev['recogniser_text']);matches=list(re.finditer(r'\S+',text));match=matches[m['word_index']]
   assert bare(match.group())==m['word_bare'];inword=[x for x in ss if match.start()<=x['start']<match.end()];assert inword[m['anchor_index']]==s
   native=PROJECTS/'greek-ocr-toolkit'/m.pop('frame_crop');assert native.is_file()
   with Image.open(native) as im:w,h=im.size
   spans=[]
   for x in inword:
    assert x['locator_span'];spans.extend(x['locator_span']);e=x.get('evidence') or {};spans.extend(e.get('body') or [])
    for part in ('above','below','apostrophes'):
     for component in e.get(part,[]):
      if component.get('bbox'):spans.extend([component['bbox'][0],component['bbox'][2]])
   target=(s.get('evidence') or {}).get('body') or s['locator_span'];a=max(0,math.floor(target[0]-1));z=min(w,math.ceil(target[1]+1));assert a<z
   l=max(0,math.floor(min(spans)-.4*h));r=min(w,math.ceil(max(spans)+.4*h))
   m.update(native_asset=str(native),native_size=[w,h],word_box=[l,0,r,h],target_box_native=[a,0,z,h],geometry_source='Saved release A recogniser-aligned slots + physical body/mark bounds; full native height retained')
 (A/'prompts').mkdir(exist_ok=True)
 for track,src in [('accent',SR/'prompts/grave.md'),('capital',CQ/'cq1/prompts/cap1.md')]:
  (A/'prompts'/f'{track}.md').write_bytes(src.read_bytes())
 excluded={r['doc'] for r in frame};contexts=[]
 for track,group in items.items():
  pool=controls(track,excluded);dump(A/'keys'/f'{track}_control_pool.json',pool)
  entries=list(group.values());random.Random(f'{SEED}:{track}:order').shuffle(entries)
  for start in range(0,len(entries),90):
   original=f'{track}_initial_{start//90+1:03d}';name=original+'_'+fresh if fresh else original
   contexts.append(write_context(name,track,entries[start:start+90],pool,order_name=original))
 assert canonical_binding()==binding_now,'canonical source changed during build'
 dump(A/'contexts.json',contexts)
 binding={str(p):sha(p) for p in [A.parent/'audit100_frame.jsonl',A.parent/'release_edits_only_A.jsonl',REPO/'docs/labelfix/spellcheck/SF7_PREREGISTRATION.md',SR/'HANDOVER.md',SR/'prompts/grave.md',CQ/'cq1/prompts/cap1.md',SR/'grave/keys/control_review/LEAD_REVIEW.md',CQ/'cq4/control_review/lead_review.json',CQ/'cq4/keys/control_pool.json',SR/'grave/keys/key.json']}
 binding.update({str(A/'keys'/f'{t}_control_pool.json'):sha(A/'keys'/f'{t}_control_pool.json') for t in ('accent','capital')})
 dump(A/'build_receipt.json',dict(status='BUILT_ONLY',seed=SEED,counts=counts,contexts=contexts,inputs=binding,reader_runs=0,network=False,git_writes=False,geometry='Saved localisation only; no new inference',scanner_expected_at_build=binding_now['expected'],scanner_actual_at_build=sha(SR/'tools/scan_rollout.py')))
 dump(A/'scanner_binding.json',binding_now)
 if fresh:
  for path,digest in preserved.items():assert sha(path)==digest,'preserved input/attempt changed: '+path
  dump(archive/'receipt.json',dict(status='BUILT_ONLY',namespace=fresh,old_contexts=old,new_contexts=contexts,preserved_sha256=preserved,scanner_binding=binding_now,reader_runs=0,network=False))
 print(json.dumps(dict(frame_lines=100,counts=counts,contexts=len(contexts))))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--fresh');args=p.parse_args();build(args.fresh)
