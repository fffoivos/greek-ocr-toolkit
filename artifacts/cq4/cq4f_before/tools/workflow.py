"""CQ4 later reading workflow. Merely importing/building never invokes a reader."""
import argparse,collections as C,json,re,subprocess,sys
from pathlib import Path
from build import OUT,ROOT,SCANNER_SHA,PREREG_SHA,sha,load,rows,dump,jsonl,build_context

def reread_trigger(answer,ink_available=False,spacing_or_preposed=None):
 # Conservative fallback: all breathing-only answers, as allowed by CQ4.
 return answer['breathing']=='unreadable' or answer['accent']=='unreadable' or (answer['breathing'] in ('smooth','rough') and answer['accent']=='none' and (not ink_available or spacing_or_preposed is not False))

def overlay_rows(old,overlay):
 """R2J4 identity semantics; used by the later manifest consumer, not this build."""
 index=C.defaultdict(list)
 for i,x in enumerate(old):index[tuple(x['slot_id'])].append(i)
 out=list(old);touched=set()
 for x in overlay:
  sid=tuple(x['slot_id']);target=tuple(x.get('replaces',x['slot_id']))
  if len(index.get(sid,[]))>1 or len(index.get(target,[]))>1:raise ValueError('ambiguous old identity for replacement')
  if sid in touched or target in touched:raise ValueError('slot modified more than once')
  touched.update((sid,target))
  if target in index:
   if sid!=target:raise ValueError('replacement identity must match existing key')
   out[index[target][0]]=x|dict(replaces=list(target))
  else:
   if sid in index:raise ValueError('existing identity cannot append')
   out.append(x)
 return out

def verified_control_pool():
 review=load(OUT/'control_review/lead_review.json');pool=load(OUT/'keys/control_pool.json')
 assert review['status']=='verified','STOP: lead must pixel-verify the control sheet'
 assert review['sheet_sha256']==sha(OUT/'control_review/controls.png'),'STOP: sheet changed'
 ids=[x['source_id'] for x in pool];reviews=[x['source_id'] for x in review['items']]
 assert len(set(ids))==len(ids) and len(set(reviews))==len(reviews) and set(ids)==set(reviews),'STOP: control review identity mismatch'
 verified={x['source_id'] for x in review['items'] if x.get('verified') is True}
 return [x for x in pool if x['source_id'] in verified]

def controls_verified(contexts=None):
 pool={x['source_id']:x for x in verified_control_pool()}
 if contexts is None:
  contexts=load(OUT/'contexts.json')
  if (OUT/'reread_contexts.json').exists():contexts+=load(OUT/'reread_contexts.json')
 for c in contexts:
  controls=[x for x in load(c['key'])['items'].values() if x['control']]
  ids=[x['source_id'] for x in controls]
  assert len(ids)==10 and len(set(ids))==10,'STOP: context needs ten distinct controls'
  for x in controls:
   assert x['source_id'] in pool,'STOP: every placed control needs verified=true'
   assert {k:v for k,v in x.items() if k!='public'}==pool[x['source_id']],'STOP: placed control differs from reviewed pool'

def frozen_verified():
 for rel,value in load(OUT/'build_hashes.json').items():
  p=OUT/rel;h=__import__('hashlib').sha256(p.read_bytes()).hexdigest();assert h==value,'STOP frozen build changed: '+str(p)
 assert sha(OUT/'tools/scan_rollout.py')==SCANNER_SHA
 controls_verified()

def probe(tag):
 result=subprocess.run(['bash',str(OUT/'launchers/limit_probe.sh'),tag],text=True,capture_output=True)
 match=re.search(r'weekly_used=([\d.]+) limit_id=codex ',result.stdout)
 if result.returncode or not match:raise RuntimeError('weekly probe unavailable; '+result.stdout+result.stderr)
 used=float(match[1]);return dict(weekly_used=used,output=result.stdout)

def decode(context):
 key=load(context['key']);data=rows(Path(context['directory'])/'answers.jsonl');items=key['items']
 assert [r.get('item_id') for r in data]==list(items),'answer count/order mismatch'
 result={}
 for a in data:
  assert set(a)=={'item_id','breathing','accent','confidence','note'}
  assert a['confidence'] in ('high','low') and isinstance(a['note'],str)
  p=items[a['item_id']]['public'];assert a['breathing'] in p['breathing_options'] and a['accent'] in p['accent_options']
  result[a['item_id']]=dict(breathing=p['breathing_options'][a['breathing']],accent=p['accent_options'][a['accent']])
 errors=sum(result[i]!=x['expected'] for i,x in items.items() if x['control'])
 return result,errors

def run_all(phase):
 frozen_verified();contexts=load(OUT/('contexts.json' if phase=='initial' else 'reread_contexts.json'));ledger_path=OUT/f'{phase}_ledger.json'
 ledger=load(ledger_path) if ledger_path.exists() else []
 done={x['tag'] for x in ledger}
 for c in contexts:
  if c['tag'] in done:continue
  rd=Path(c['directory']);assert not (rd/'answers.jsonl').exists(),'STOP: unexplained answers already present'
  record=dict(tag=c['tag'],set=c['set'],phase=phase,scanner_sha256=SCANNER_SHA,status='VOID')
  before=probe(c['tag']+'_before');record['before']=before
  if before['weekly_used']>=78:raise RuntimeError('weekly usage >=78%; refuse reader')
  try:
   # Verify original pack bytes immediately before reading.
   mp=rd.parent/f'MANIFEST.{rd.name}.json';assert __import__('hashlib').sha256(mp.read_bytes()).hexdigest()==c['manifest_sha256'],'manifest custody changed'
   man=load(mp)
   for rel,h in man['files'].items():assert __import__('hashlib').sha256((rd/rel).read_bytes()).hexdigest()==h
   run=subprocess.run(['bash',str(OUT/'launchers/run_read.sh'),c['tag'],str(rd),str(OUT/'prompts/cap1.md'),'medium'],text=True,capture_output=True)
   record['run_stdout']=run.stdout;record['run_stderr']=run.stderr
   objects=[json.loads(l) for l in run.stdout.splitlines() if l.startswith('{')]
   if not objects:raise ValueError('reader rollout metadata missing')
   meta=objects[-1];record['run']=meta
   import scan_rollout
   scan=scan_rollout.inspect(Path(meta['rollout']),rd);scan['scanner_sha256']=SCANNER_SHA;dump(OUT/'scans'/f'{c["tag"]}.json',scan)
   if run.returncode or not scan['ok']:raise ValueError('reader/closure leak scan failed')
   answers,errors=decode(c);record['control_errors']=errors
   if errors>1:raise ValueError('more than one control error')
   record.update(status='VALID',answers=answers)
  except Exception as exc:
   record.pop('answers',None);record['void_reason']=str(exc)
  try:record['after']=probe(c['tag']+'_after')
  except Exception as exc:
   record.pop('answers',None);record.update(status='VOID',void_reason='post-probe failure: '+str(exc));ledger.append(record);dump(ledger_path,ledger);raise
  ledger.append(record);dump(ledger_path,ledger)
  if record['after']['weekly_used']>=78:raise RuntimeError('weekly usage >=78%; refuse next reader')

def valid_answers(phase):
 contexts=load(OUT/('contexts.json' if phase=='initial' else 'reread_contexts.json'));ledger=load(OUT/f'{phase}_ledger.json');bytag={x['tag']:x for x in ledger}
 assert len(bytag)==len(ledger) and set(bytag)=={c['tag'] for c in contexts},'RUN_ALL incomplete'
 result={}
 for c in contexts:
  record=bytag[c['tag']]
  if record['status']!='VALID':continue
  assert record['scanner_sha256']==SCANNER_SHA
  key=load(c['key'])
  for i,a in record['answers'].items():
   x=key['items'][i]
   if not x['control']:result[tuple(x['slot_id'])]=(x,a,c['set'])
 return result

def build_reread():
 frozen_verified();answers=valid_answers('initial');pool=verified_control_pool();contexts=[];selected=C.defaultdict(list)
 for sid,(x,a,name) in answers.items():
  if reread_trigger(a):selected[name].append(x)
 for name,data in sorted(selected.items()):
  __import__('random').Random(20261017+1).shuffle(data)
  for n,i in enumerate(range(0,len(data),90)):contexts.append(build_context(data[i:i+90],pool,name,n,'reread'))
 controls_verified(contexts)
 dump(OUT/'reread_contexts.json',contexts);dump(OUT/'reread_build_receipt.json',dict(scanner_sha256=SCANNER_SHA,preregistration_sha256=PREREG_SHA,contexts=len(contexts),slots=sum(len(v) for v in selected.values()),trigger='all unreadable and every breathing-only answer (conservative ink fallback)'))
 if not contexts:dump(OUT/'reread_ledger.json',[])

def aggregate():
 frozen_verified();initial=valid_answers('initial');second=valid_answers('reread');truth=C.defaultdict(list);queue=[];agree=0;triggered=0;quarantine=C.defaultdict(list)
 # Every unscored/VOID bed slot is explicitly quarantined.
 selected={name:rows(OUT/'keys'/f'{name}_selected.jsonl') for name in ('wcap','topup')}
 for name,data in selected.items():
  for x in data:
   sid=tuple(x['slot_id'])
   if sid not in initial:
    reason='VOID/missing initial context';quarantine[name].append(dict(slot_id=list(sid),reason=reason));queue.append(x|dict(initial=None,reread=None,reason=reason,set=name));continue
   _,a,_=initial[sid];reason=None
   if reread_trigger(a):
    triggered+=1;r=second.get(sid)
    if r is None:reason='missing/VOID reread'
    elif r[1]!=a:reason='reread disagreement'
    else:agree+=1
    if reason is None and 'unreadable' in a.values():reason='agreed unreadable'
    if reason:
     q=x|dict(initial=a,reread=second[sid][1] if sid in second else None,reason=reason,set=name);queue.append(q);quarantine[name].append(dict(slot_id=list(sid),reason=reason));continue
   truth[name].append(dict(slot_id=list(sid),line_id=x['line_id'],doc=x['doc'],source=x['source'],role=x['role'],teacher_seen_document=x.get('teacher_seen_document',False),breathing=a['breathing'],accent=a['accent'],truth_tier='C_sol_one_reader_reread',set=name,overlay_action='replace_if_unique_old_identity_else_append_new' if name=='topup' else 'witness_only'))
 for name in selected:
  jsonl(OUT/'truth'/f'{name}.jsonl',truth[name]);jsonl(OUT/'quarantine'/f'{name}.jsonl',quarantine[name])
 jsonl(OUT/'lead_queue.jsonl',queue);contact_sheet(queue)
 ledgers=load(OUT/'initial_ledger.json')+load(OUT/'reread_ledger.json')
 summary=dict(scanner_sha256=SCANNER_SHA,preregistration_sha256=PREREG_SHA,counts={k:dict(resolved=len(truth[k]),quarantined=len(quarantine[k]),classes=dict(C.Counter('bare' if x['breathing']=='none' and x['accent']=='none' else 'marked' for x in truth[k]))) for k in selected},reread_triggered=triggered,reread_agreed=agree,reread_agreement_rate=agree/triggered if triggered else None,lead_queue=len(queue),codex_before=ledgers[0]['before'] if ledgers else None,codex_after=ledgers[-1]['after'] if ledgers else None)
 dump(OUT/'aggregate_receipt.json',summary)
 report=ROOT/'docs/labelfix/spellcheck/R2/CQ4_REPORT.md';text=report.read_text().split('\n## Reading results')[0];report.write_text(text+'\n## Reading results\n\n```json\n'+json.dumps(summary,ensure_ascii=False,indent=2)+'\n```\n')

def contact_sheet(queue):
 from PIL import Image,ImageDraw
 # A grid keeps a fully quarantined run within PNG and memory dimensions.
 columns=5;cell_width=500;cell_height=160
 sheet=Image.new('RGB',(columns*cell_width,max(100,((len(queue)+columns-1)//columns)*cell_height)),'white');draw=ImageDraw.Draw(sheet)
 for i,x in enumerate(queue):
  left=(i%columns)*cell_width;top=(i//columns)*cell_height
  with Image.open(x['native_asset']) as im:im=im.convert('RGB').crop(x['word_box'])
  im=im.resize((im.width*3,im.height*3));bb=x['target_box_native'];l=x['word_box'][0];ImageDraw.Draw(im).rectangle([(bb[0]-l)*3,1,(bb[2]-l)*3,im.height-2],outline=(220,0,0),width=2);im.thumbnail((cell_width-20,100));sheet.paste(im,(left+10,top+50))
  draw.text((left+10,top+5),f"{i+1}: {x['set']} {x['slot_id'][0][:16]}:{x['slot_id'][1]}",fill='black');draw.text((left+10,top+22),x['reason'],fill='black')
 sheet.save(OUT/'lead_queue.png')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['run','reread','aggregate']);p.add_argument('--phase',choices=['initial','reread'],default='initial');a=p.parse_args()
 {'run':lambda:run_all(a.phase),'reread':build_reread,'aggregate':aggregate}[a.action]()
