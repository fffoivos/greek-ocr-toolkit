"""Offline CQ1 builder. Existing-v2 reuse must be explicitly selected."""
import argparse,collections,hashlib,io,json,random,unicodedata
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from common import ROOT,PACK_ROOT,rows,dump,jsonl,sha
W=ROOT.parents[1]
T2=W/'artifacts/r2_resolve/T2/final/resolved.jsonl'
V2=W.parent/'greek-ocr-toolkit-spellcheck-r2prep/artifacts/r2a_manifest/r2a_slots_v2.jsonl'
DECK=W/'docs/labelfix/spellcheck/R2/decks'
SEED=20261017

def inventory():
 key={r['card_id']:r for r in rows(DECK/'T2/private/key.jsonl')}
 forbidden={r['doc'] for r in rows(DECK/'T4/private/key.jsonl')}
 v2=rows(V2); bycard=collections.defaultdict(list)
 for v in v2:bycard[v['card_id']].append(v)
 candidates=[]
 for r in rows(T2):
  k=key[r['card_id']]
  if k['doc'] in forbidden or r['readability']!='readable':continue
  h=next((h for h in r['letter_heads'] if h['index']==r['anchor_index']),None)
  if not h or h['breathing'] not in ('none','psili','dasia') or h['accent'] not in ('none','acute','grave','circumflex'):continue
  # Require the full printed base sequence to match the originally located word.
  bare=lambda s:''.join(c for c in unicodedata.normalize('NFD',s) if unicodedata.category(c).startswith('L'))
  if bare(r['printed_form'])!=bare(k['mining_key']):continue
  candidates.append(dict(card=r,key=k,head=h,v2=bycard[r['card_id']],compound=h['breathing']!='none' and h['accent']!='none'))
 return candidates

def select(pool):
 rng=random.Random(SEED);pool=sorted(pool,key=lambda x:(x['card']['card_id'],x['head']['index']));rng.shuffle(pool)
 caps=[x for x in pool if x['head']['base'] in 'ΑΕΗΙΟΥΩΡ' and x['v2']]
 used=collections.Counter(); chosen=[]
 def take(group,n):
  got=[]
  for x in group:
   if x in chosen or used[x['key']['doc']]>=3:continue
   chosen.append(x);got.append(x);used[x['key']['doc']]+=1
   if len(got)==n:break
  assert len(got)==n,('insufficient candidates',n,len(got))
  return got
 pos=[x for x in caps if (x['head']['breathing'],x['head']['accent'])!=('none','none')]
 take([x for x in pos if x['compound']],8)
 # Represent every available tuple, then balance the remaining draw across tuples.
 for pair in sorted({(x['head']['breathing'],x['head']['accent']) for x in pos}):
  if any((x['head']['breathing'],x['head']['accent'])==pair for x in chosen):continue
  take([x for x in pos if (x['head']['breathing'],x['head']['accent'])==pair],1)
 while len(chosen)<30:
  counts=collections.Counter((x['head']['breathing'],x['head']['accent']) for x in chosen)
  avail=[x for x in pos if x not in chosen and used[x['key']['doc']]<3]
  avail.sort(key=lambda x:counts[x['head']['breathing'],x['head']['accent']]);take(avail,1)
 neg=[x for x in caps if (x['head']['breathing'],x['head']['accent'])==('none','none')]
 # Anchor zero makes the physical target unambiguous without OCR letter segmentation.
 neg=[x for x in neg if x['head']['index']==0]
 allcaps=[x for x in neg if x['card']['printed_form'].isupper() and len(x['card']['letter_heads'])>1]
 if allcaps:take(allcaps,3)
 numeral=[x for x in neg if any(c.isdigit() for c in x['card']['printed_form'])]
 if numeral:take(numeral,1)
 take(neg,60-len(chosen))
 controls=[x for x in pool if x['head']['base'] in 'αεηιουω' and x['head']['index']==0 and (x['head']['breathing']!='none' or x['head']['accent']!='none') and len(x['card']['letter_heads'])<=8]
 # Diverse control tuples, including breathing-only and compound hooks.
 selected=[]
 for pair in [('dasia','none'),('psili','none'),('psili','acute'),('dasia','acute'),('psili','circumflex'),('none','acute')]:
  group=[x for x in controls if (x['head']['breathing'],x['head']['accent'])==pair and x not in chosen and x not in selected and used[x['key']['doc']]<3]
  assert group,('missing control',pair)
  preferred={('psili','none'):'e88b2522905b12354076b342',('dasia','acute'):'65d292cdac821a32e6f1b723'}
  x=next((v for v in group if v['key']['card_id']==preferred.get(pair)),group[0]);selected.append(x);used[x['key']['doc']]+=1
 for x in chosen:x['control']=False
 for x in selected:x['control']=True
 return chosen+selected

def first_letter_box(line,k):
 # Connected native ink identifies the first body glyph, including separate strokes.
 assert k['anchor_index']==0
 left,top,right,bottom=k['word_box'];token=k['token_box']; gray=line.convert('L')
 overrides=json.loads((ROOT/'keys/box_overrides.json').read_text())
 if k['card_id'] in overrides:
  a,b=overrides[k['card_id']]['word_relative_x'];return [left+a,top+1,left+b,bottom-2]
 pixels={(xx,yy) for xx in range(left,right) for yy in range(top,bottom) if gray.getpixel((xx,yy))<190}
 components=[]
 while pixels:
  seed=pixels.pop();stack=[seed];points=[seed]
  while stack:
   xx,yy=stack.pop()
   for dx,dy in ((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)):
    q=(xx+dx,yy+dy)
    if q in pixels:pixels.remove(q);stack.append(q);points.append(q)
  xs=[v[0] for v in points];ys=[v[1] for v in points]
  if max(ys)-min(ys)>=.32*(token[3]-token[1]) and len(points)>=8:
   components.append((min(xs),min(ys),max(xs)+1,max(ys)+1))
 components.sort();assert components,k['card_id'];a,y0,b,y1=components[0]
 return [max(left,a-2),top+1,min(right,b+2),bottom-2]

def save(im,rd):
 b=io.BytesIO();im.convert('RGB').save(b,format='PNG');data=b.getvalue();name=hashlib.sha256(data).hexdigest()+'.png';p=rd/'img'/name
 if not p.exists():p.write_bytes(data)
 return 'img/'+name

def build():
 pool=inventory();selected=select(pool);rng=random.Random(SEED);rng.shuffle(selected)
 rd=PACK_ROOT/'cap1/r1';assert not (rd/'items.jsonl').exists(),'Refuse to overwrite a built pack';(rd/'img').mkdir(parents=True,exist_ok=True)
 public=[];private={};controls=[];review=[]
 for n,x in enumerate(selected):
  k=x['key'];h=x['head'];ident='k'+hashlib.sha256(f'{SEED}:cq1:{k["card_id"]}:{h["index"]}'.encode()).hexdigest()[:10]
  native=Path(k['crop'])
  if native.exists():assert sha(native)==k['crop_sha256']
  else:native=DECK/'T2/blind'/k['public']['line_image']
  with Image.open(native) as im:line=im.convert('RGB')
  assert list(line.size)==k['native_size']
  x['native_asset']=str(native)
  box=first_letter_box(line,k);l,t,r,b=k['word_box'];word=line.crop((l,t,r,b)).resize(((r-l)*3,(b-t)*3),Image.Resampling.LANCZOS)
  d=ImageDraw.Draw(word);d.rectangle(tuple((v-[l,t,l,t][i])*3 for i,v in enumerate(box)),outline=(220,0,0),width=2)
  bo=['none','smooth','rough','unreadable'];ao=['none','acute','grave','circumflex','unreadable'];rng.shuffle(bo);rng.shuffle(ao)
  item=dict(item_id=ident,word_image=save(word,rd),line_image=save(line,rd),breathing_options=dict(zip('ABCD',bo)),accent_options=dict(zip('ABCDE',ao)))
  public.append(item);expected=dict(breathing={'psili':'smooth','dasia':'rough','none':'none'}[h['breathing']],accent=h['accent'])
  private[ident]=dict(native_asset=str(native),native_asset_sha256=sha(native),source_id=k['card_id'],doc=k['doc'],line_id=k['line_id'],crop_sha256=k['crop_sha256'],letter_index=h['index'],crop_letter_index=k['crop_letter_offset']+h['index'],expected=expected,control=x['control'],compound=x['compound'],printed_form=x['card']['printed_form'],v2_slots=x['v2'],target_box_native=box,public=item)
  if x['control']:
   letter=line.crop((max(l,box[0]-8),t,min(r,box[2]+10),b));letter=letter.resize((letter.width*8,letter.height*8),Image.Resampling.NEAREST)
   controls.append(private[ident]|dict(item_id=ident));review.append((ident,word,letter,expected))
 jsonl(rd/'items.jsonl',public)
 (rd/'README.md').write_text('Read the boxed letter from word_image and line_image. Choose one option letter for each head from the mappings in items.jsonl. Do not transcribe words. Write answers.jsonl in item order using answer_schema.json.\n')
 schema={'type':'object','additionalProperties':False,'required':['item_id','breathing','accent','confidence','note'],'properties':{'item_id':{'type':'string','pattern':'^k[0-9a-f]{10}$'},'breathing':{'enum':list('ABCD')},'accent':{'enum':list('ABCDE')},'confidence':{'enum':['high','low']},'note':{'type':'string'}}}
 dump(rd/'answer_schema.json',schema);dump(ROOT/'keys/cap1.json',dict(readers={'r1':[x['item_id'] for x in public]},items=private))
 # Review sheet uses native-derived pixels only and is never copied to PACK_ROOT.
 width=max(1100,max(w.width+z.width+70 for _,w,z,_ in review));height=sum(max(w.height,z.height)+65 for _,w,z,_ in review)
 sheet=Image.new('RGB',(width,height),'white');draw=ImageDraw.Draw(sheet);y=0
 for ident,word,letter,expected in review:
  draw.text((10,y+5),ident+'  '+json.dumps(expected),fill='black');sheet.paste(word,(10,y+30));sheet.paste(letter,(word.width+30,y+30));y+=max(word.height,letter.height)+65
 sheet.save(ROOT/'control_review/controls.png');dump(ROOT/'control_review/index.json',controls)
 dump(ROOT/'control_review/lead_review.json',dict(status='pending',sheet_sha256=sha(ROOT/'control_review/controls.png'),items=[c['item_id'] for c in controls],instruction='Lead must inspect word and letter pixels and record verified=true per item before RUN_CMD.sh.'))
 bed=[x for x in selected if not x['control']]
 dump(ROOT/'keys/v2_overlap.json',[dict(item_id=i,source_id=v['source_id'],crop_letter_index=v['crop_letter_index'],v2_slots=v['v2_slots']) for i,v in private.items() if not v['control']])
 dump(ROOT/'build_receipt.json',dict(seed=SEED,bed=len(bed),positive=30,negative=30,controls=6,compounds=sum(x['compound'] for x in bed),max_per_document=max(collections.Counter(x['key']['doc'] for x in selected).values()),tuple_counts=dict(collections.Counter(str((x['head']['breathing'],x['head']['accent'])) for x in bed)),capital_grave_available=0,limitations=['No capital grave in T2 resolved truth; grave stratum cannot be qualified.'],v2_reuse_policy='Existing v2 cards for qualification only; all qualification slots reserved from future top-up.',inputs={str(p):sha(p) for p in [T2,V2,DECK/'T2/private/key.jsonl',DECK/'T4/private/key.jsonl']}))
 jsonl(ROOT/'keys/topup_exclusions.jsonl',[dict(crop_sha256=v['crop_sha256'],crop_letter_index=v['crop_letter_index'],source_id=v['source_id']) for v in private.values()])
 print(json.dumps(json.loads((ROOT/'build_receipt.json').read_text()),indent=2))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--allow-existing-v2',action='store_true');args=p.parse_args()
 if not args.allow_existing_v2:raise SystemExit('Explicit existing-v2 qualification reuse required. No pack written.')
 build()
