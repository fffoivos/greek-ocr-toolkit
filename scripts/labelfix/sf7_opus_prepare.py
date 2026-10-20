"""OC1 offline build only. Never invokes a reader, network or git."""
import sys
sys.dont_write_bytecode=True
import hashlib, io, json, math, random, re, shutil, unicodedata as U
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
A=ROOT/'artifacts/sf7_rc1/audit'; K=A/'opus_keys'
sys.path.insert(0,str(K/'vendor'))
from greekocr.ops.data_root import input_path as _data_input
from adjudicate.deck import leak_scan
PACK=Path('/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/sf7_audit_opus')
R2=ROOT.parent/'greek-ocr-toolkit-spellcheck-r2cards/docs/labelfix/spellcheck/R2/decks'
def sha(p): return hashlib.sha256(_data_input(Path(p)).read_bytes()).hexdigest()
def load(p): return json.loads(_data_input(Path(p)).read_text())
def rows(p): return [json.loads(s) for s in _data_input(Path(p)).read_text().splitlines() if s.strip()]
def dump(p,x): Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def write(p,x): Path(p).write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in x))
def bare(x): return ''.join(c for c in U.normalize('NFD',x) if not U.combining(c))
def letters(x): return ''.join(c for c in bare(x) if c.isalpha())
def save(im):
 b=io.BytesIO();Image.frombytes('RGB',im.size,im.convert('RGB').tobytes()).save(b,'PNG');v=b.getvalue();name='img/'+hashlib.sha256(v).hexdigest()+'.png';(K/'deck/blind'/name).write_bytes(v);return name

def render(native,wordbox,targetbox):
 with Image.open(native) as im: line=im.convert('RGB')
 word=line.crop(wordbox);word=word.resize((word.width*3,word.height*3),Image.Resampling.LANCZOS)
 # Only the full line is outlined, leaving zoom pixels unobscured.
 ImageDraw.Draw(line).rectangle(targetbox,outline=(220,0,0),width=1)
 return dict(line_image=save(line),word_image=save(word))

def main():
 assert not PACK.exists(),'reader tree already exists; never overwrite readers'
 assert not (K/'deck').exists(),'deck already exists'
 (K/'deck/blind/img').mkdir(parents=True);(K/'deck/private').mkdir()
 routing=load(A/'routing.json');score=load(A/'score.json');loc=load(A/'keys/localisation.json')
 assert score['summary']['partial_line_precision']==dict(correct=70,denominator=70,value=1.0)
 hs=[h for h in score['heads'] if h['status']!='SCORED']
 assert len(hs)==32 and len({h['line_id'] for h in hs})==30
 assert {h['head_id'] for h in hs if h['route']=='Sol-capital'}=={'RB7-053:0:breathing','RB7-055:6:breathing','RB7-065:17:breathing'}
 pending=set(re.findall(r'`(RB7-\d+:\d+:\w+)`',(A/'OPUS_PENDING.md').read_text()))
 assert pending=={h['head_id'] for h in hs if h['route']=='Opus-later'}
 cap=load(A/'keys/capital_initial_001_au1d.json')
 assert {h for x in cap.values() if not x['control'] for h in x['heads']}=={h['head_id'] for h in hs if h['route']=='Sol-capital'}
 frame={l['line_id']:l for l in routing['lines']};keys=[];controls=[];public=[]
 for h in hs:
  ev=loc[h['line_id']];ss=ev['slots'];slot=ss[h['slot']];text=U.normalize('NFD',ev['recogniser_text'])
  matches=list(re.finditer(r'\S+',text));wi=next(i for i,m in enumerate(matches) if m.start()<=slot['start']<m.end());m=matches[wi]
  wordslots=[s for s in ss if m.start()<=s['start']<m.end()];ai=wordslots.index(slot);base=bare(m.group())
  assert letters(base)[ai]==h['base']
  native=ROOT.parent/'greek-ocr-toolkit'/frame[h['line_id']]['crop']
  with Image.open(native) as im:w,height=im.size
  spans=[]
  for s in wordslots:
   spans+=s['locator_span'];e=s.get('evidence') or {};spans+=e.get('body') or []
   for part in ('above','below','apostrophes'):
    for c in e.get(part,[]):
     if c.get('bbox'):spans += [c['bbox'][0],c['bbox'][2]]
  wb=[max(0,math.floor(min(spans)-6)),0,min(w,math.ceil(max(spans)+6)),height]
  target=(slot.get('evidence') or {}).get('body') or slot['locator_span'];tb=[max(0,math.floor(target[0]-1)),1,min(w-1,math.ceil(target[1]+1)),height-2]
  ident=hashlib.sha256(('OC1:'+h['head_id']).encode()).hexdigest()[:24]
  # Options derive only from BASE letters, never the released word.
  options=[]
  for mark in (['','\u0313','\u0314'] if h['head']=='breathing' else ['','\u0345'] if h['head']=='subscript' else ['','\u0301','\u0300','\u0342']):
   chars=list(base);indices=[i for i,c in enumerate(chars) if c.isalpha()];chars[indices[ai]]+=mark;options.append(U.normalize('NFC',''.join(chars)))
  random.Random('OC1:options:'+ident).shuffle(options)
  p=dict(card_id=ident,**render(native,wb,tb),base_letters=base,anchor_index=ai,anchor_base=h['base'],options={chr(65+i):v for i,v in enumerate(options)},extra_options={'literal':'transcribe the complete printed word','unreadable':'unreadable / cut'})
  k=dict(card_id=ident,public=p,control=False,head_id=h['head_id'],slice='audit',crop_sha256=sha(native),word_index=wi,crop_letter_offset=h['slot']-ai,anchor_index=ai,target_head=h['head'],native=str(native),word_box=wb,target_box_native=tb,doc=frame[h['line_id']]['doc'],**{n:h[n] for n in ('audit_id','line_id','slot','head','kind','released_label')})
  keys.append(k);public.append(p)
 # Short two-letter controls permit an exact body-gap target box, with no mark inference.
 excluded={l['doc'].split(':')[-1] for l in routing['lines']};control_sources=[]
 for track in ('T2','T4'):
  d=R2/track;kk={x['card_id']:x for x in rows(d/'private/key.jsonl')};pp=rows(d/'blind/cards.jsonl')
  for c in load(d/'private/controls_proposed.json')['controls']:
   k=kk[c['card_id']]
   if not c.get('lead_verified') or (track=='T2' and pp.index(k['public'])+1==61) or k['doc'].split(':')[-1] in excluded or len(letters(c['expected_form']))!=2:continue
   native=Path(k['crop']);x0,y0,x1,y1=k['token_box']
   with Image.open(native) as im: ar=np.asarray(im.convert('L'))
   # Full-height inter-letter blank projection; reject joined/ambiguous pairs.
   profile=(ar[y0:y1,x0:x1]<160).sum(axis=0);n=len(profile);candidates=[i for i in range(max(1,int(n*.25)),min(n-1,int(n*.75))) if profile[i]==0]
   if not candidates:continue
   split=x0+min(candidates,key=lambda i:abs(i-n/2));ai=k['anchor_index'];assert ai in (0,1)
   tb=[x0 if ai==0 else split,1,split if ai==0 else x1,ar.shape[0]-2]
   ident=hashlib.sha256(('OC1:check:'+track+':'+c['card_id']).encode()).hexdigest()[:24]
   p=dict(card_id=ident,**render(native,k['word_box'],tb),base_letters=bare(c['expected_form']),anchor_index=ai,anchor_base=letters(c['expected_form'])[ai],options=k['public']['options'],extra_options=k['public']['extra_options'])
   # Public option content is BASE-derived in original R2; strip paired views/provenance.
   ck=dict(k,card_id=ident,public=p,control=True,target_box_native=tb,control_source=str(d),original_card_id=c['card_id'])
   cc=dict(c,card_id=ident,word_image=p['word_image'],line_image=p['line_image'])
   controls.append(cc);keys.append(ck);public.append(p);control_sources.append(dict(deck=track,position=pp.index(k['public'])+1,original_card_id=c['card_id'],doc=k['doc'],key_sha256=sha(d/'private/key.jsonl'),verification_sha256=sha(d/'private/controls_proposed.json')))
   if len(controls)==4:break
  if len(controls)==4:break
 assert len(controls)==4
 random.Random(20261019).shuffle(public)
 write(K/'deck/blind/cards.jsonl',public);write(K/'deck/private/key.jsonl',keys)
 dump(K/'deck/private/controls_proposed.json',dict(controls=controls))
 shutil.copyfile(R2/'T2/blind/answer_schema.json',K/'deck/blind/answer_schema.json')
 readme='''# Literal printed Greek\nRead cards.jsonl in its given order. Each card has a full native line with the target outlined and a 3× word zoom. base_letters removes every combining mark; anchor_index counts letters from zero.\nTranscribe ink, including misprints. Never infer marks from grammar. Give all four anchor_heads: breathing, accent, diaeresis (dialytika), subscript. Unknown is allowed for every head. Use literal with a complete transcription if no option is exact. A head set to a known value must match that transcription. Set ownership_ok to null for an unmarked anchor; otherwise true/false describes whether mark ink belongs to it. None means visibly blank. Give readability, confidence and a note; optional letter_heads covers other letters. Write exactly one answer per card in the assigned order, incrementally, to answers.jsonl. Set usage to {"input_tokens":0,"output_tokens":0}.\n'''
 (K/'deck/blind/README.md').write_text(readme)
 for reader,order in [('r1',public),('r2',list(reversed(public)))]:
  rd=PACK/reader;shutil.copytree(K/'deck/blind',rd);write(rd/'cards.jsonl',order);(rd/'answers.jsonl').write_text('')
 prompt='''You are an independent blind Claude Opus subagent reading printed Greek ink. Work ONLY inside the assigned folder: <BATCH_DIR>\nOpen only README.md, answer_schema.json, cards.jsonl, and the PNG files under img/ explicitly named by those cards. Do not open, list or search any other folder or file, including parents, keys, private files, other batches or other readers' answers. Do not use web search or network. This isolation is a file allowlist instruction, not an OS sandbox.\nRead README.md and answer_schema.json first. Follow cards.jsonl IN ITS GIVEN ORDER; your assigned order is already prepared, including reader 2's reverse order. For every card open both the native full line and the 3× word zoom. The outline identifies the target letter. Read only the central target word in the zoom. Transcribe exactly the printed ink, including misprints. Never correct spelling or infer a mark from grammar or an offered option. Choose literal with the complete exact word whenever no option is exact. Give all four anchor heads (breathing, accent, diaeresis/dialytika, subscript), readability, ownership, confidence and note. Each known head must agree with the transcription; preserve unknown when ink is undecidable. None requires a clearly visible blank area. ownership_ok must be null on an unmarked anchor, otherwise true/false for whether mark ink belongs to this letter.\nWrite answers.jsonl in this folder incrementally: exactly one JSON object per card in the same order, following answer_schema.json. Optional enlargements or helper files go only into a new zoom/ subfolder here. Open image paths literally, one explicit image-view call per path; do not loop over image paths. Never overwrite or delete a viewed image. Set usage to {"input_tokens":0,"output_tokens":0}. You may inspect your own answers.jsonl solely to write and verify coverage/order.\nBefore finishing, count cards and answer records, verify that both counts equal <COUNT>, and check exact card_id order and no duplicates. Reply with cards answered, literal count, unreadable count and hard cards. Do not read any other reader's observations.\n'''
 (A/'READER_PROMPT.md').write_text('# Exact lead instructions\n\nFor each subagent use the text below, replacing only <BATCH_DIR> with its assigned absolute folder and <COUNT> with the manifest count (36 for r1/r2). For a tiebreak use its own manifest count and folder. Do not launch until the owner authorizes reads.\n\n'+prompt)
 # Pin upstream copies plus all consumed evidence; no git commands.
 sources={str(p):sha(p) for p in [A/'routing.json',A/'score.json',A/'OPUS_PENDING.md',A/'lead_queue.jsonl',A/'AU1D_HANDOFF.md',A/'keys/localisation.json',A/'keys/capital_initial_001_au1d.json',ROOT/'docs/records/labelfix/spellcheck/R2_evidence/READER_PROTOCOL_R2.md',ROOT/'scripts/labelfix/r2_cards_resolve.py',*sorted((K/'vendor/adjudicate').glob('*.py'))]}
 for name in ('deck.py','protocol.py','score.py'):
  p=ROOT.parent/'greek-ocr-toolkit-cleanup/greekocr/adjudicate'/name;assert sha(p)==sha(K/'vendor/adjudicate'/name);sources[str(p)]=sha(p)
 dump(K/'target_heads.json',hs);dump(K/'control_sources.json',control_sources);dump(K/'config.json',dict(pack=str(PACK),targets=32,lines=30,controls=4,seed=20261019))
 upstream=ROOT.parent/'greek-ocr-toolkit-spellcheck-r2cards/scripts/labelfix/r2_cards_resolve.py';assert sha(upstream)==sha(ROOT/'scripts/labelfix/r2_cards_resolve.py');sources[str(upstream)]=sha(upstream)
 for p in [K/'target_heads.json',K/'control_sources.json',K/'config.json',*sorted((K/'deck').rglob('*'))]:
  if p.is_file():sources[str(p)]=sha(p)
 dump(K/'sources.json',sources)
 forbidden=[l['audit_id'] for l in routing['lines']]+[l['line_id'] for l in routing['lines']]+[l['doc'] for l in routing['lines']]+['released_label','sampling','stratum','source_id']
 scans={r:leak_scan(PACK/r,forbidden) for r in ('r1','r2')};assert all(s['passed'] for s in scans.values()),scans
 hashes={str(p):sha(p) for r in ('r1','r2') for p in sorted((PACK/r).rglob('*')) if p.is_file()}
 dump(K/'build_receipt.json',dict(target_cards=32,lines=30,controls_per_folder=4,cards_per_folder=36,leak_scan=scans,hashes=hashes,sources=sources,readers='Claude Opus subagents; isolation by folder plus file-allowlist instruction as in T2/T4. Codex rollout scanner does not apply.',reads_launched=0,network_calls=0,git_writes=0,discrepancy='Seven unresolved Sol lines comprise three capital breathing heads and four lowercase accent heads. All seven included.'))
 print(json.dumps(dict(pack=str(PACK),targets=32,controls=4,scans=scans)))
if __name__=='__main__':main()
