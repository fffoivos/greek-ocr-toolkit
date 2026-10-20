"""Lead-operated AU1 runner, re-read builder and fail-closed partial scorer."""
import argparse, datetime, glob, os, re, shutil, subprocess, sys, time
from build import *
REPORT=REPO/'docs/labelfix/spellcheck/SF7_AUDIT_PARTIAL.md'

def unique(pairs):
 d={}
 for k,v in pairs:
  if k in d:raise ValueError('duplicate JSON field: '+k)
  d[k]=v
 return d

def strict_rows(p):return [json.loads(s,object_pairs_hook=unique) for s in Path(p).read_text().splitlines() if s.strip()]
def integrity(c):
 assert sha(c['key'])==c['key_sha256'],'private key changed'
 rd=Path(c['reader_dir']);manifest=rd.parent/f'MANIFEST.{rd.name}.json';assert sha(manifest)==c['manifest_sha256'],'manifest changed';files=load(manifest)['files']
 for rel,digest in files.items():
  p=rd/rel;assert not p.is_symlink() and p.is_file() and sha(p)==digest and p.stat().st_nlink==1,rel
 for p in rd.rglob('*'):
  rel=str(p.relative_to(rd));assert not p.is_symlink(),rel
  if p.is_file():assert rel in files or rel=='answers.jsonl' or rel.startswith('zoom/'),rel
 return files

def validate(c,path):
 key=load(c['key']);pub=rows(Path(c['reader_dir'])/'items.jsonl');answers=strict_rows(path)
 assert [a['item_id'] for a in answers]==[p['item_id'] for p in pub],'coverage/order/duplicates'
 out={};bad=[]
 for p,a in zip(pub,answers):
  required={'item_id','accent','confidence','note'}|({'breathing'} if c['track']=='capital' else set())
  assert set(a)==required and a['confidence'] in ('high','low') and isinstance(a['note'],str),'answer schema'
  decoded={}
  for head in ('breathing','accent') if c['track']=='capital' else ('accent',):
   if c['track']=='capital':assert a[head] in p[head+'_options'];decoded[head]=p[head+'_options'][a[head]]
   else:assert a[head] in ('none','acute','grave','circumflex','unreadable');decoded[head]=a[head]
  out[a['item_id']]=dict(decoded,confidence=a['confidence'],note=a['note'])
  m=key[a['item_id']]
  if m['control'] and any(decoded[h]!=v for h,v in m['expected'].items()):bad.append(a['item_id'])
 assert sum(m['control'] for m in key.values())==10
 return out,dict(total=10,errors=len(bad),bad_items=bad,passed=len(bad)<=1)

def rollout_from(log):
 text=Path(log).read_text();text=re.sub(r'\x1b\[[0-9;]*m','',text);m=re.search(r'session id:\s*([0-9a-f-]+)',text)
 assert m,'no session id in CLI log';found=list((Path.home()/'.codex/sessions').glob('*/*/*/rollout-*'+m[1]+'.jsonl'));assert len(found)==1,found
 return found[0]
def cli(cwd,prompt,folder,label,effort='medium',probe=False):
 cmd=['codex','exec','-m','gpt-6.1-sol','-c','model_reasoning_effort='+effort,'-c','approval_policy=never','-c','project_doc_max_bytes=0','-c','features.multi_agent=false','-c','features.remote_plugin=false','-c','features.apps=false','-c','sandbox_workspace_write.network_access=false','-c','web_search="disabled"','--sandbox','read-only' if probe else 'workspace-write','--skip-git-repo-check','-C',str(cwd),'-o',str(folder/(label+'.final.txt')),'-']
 log=folder/(label+'.codexlog');start=time.time()
 with log.open('w') as f:proc=subprocess.run(cmd,input=prompt,text=True,stdout=f,stderr=subprocess.STDOUT)
 roll=rollout_from(log);data=rows(roll);contexts=[x['payload'] for x in data if x.get('type')=='turn_context'];assert contexts,'missing model context'
 assert all(x.get('model')=='gpt-6.1-sol' for x in contexts),'wrong reader model'
 assert all(x.get('approval_policy')=='never' for x in contexts),'approval policy drift'
 if not probe:assert all(x.get('sandbox_policy',{}).get('type')=='workspace-write' and x['sandbox_policy'].get('network_access') is False for x in contexts),'sandbox/network policy drift'
 if not probe:assert all(x.get('effort',x.get('reasoning_effort'))=='medium' for x in contexts),'wrong effort'
 assert proc.returncode==0,f'CLI failure {proc.returncode}'
 return dict(rollout=str(roll),rollout_sha256=sha(roll),log=str(log),wall_s=time.time()-start,model='gpt-6.1-sol',effort=effort,argv=cmd)

def weekly(roll):
 result=None
 for x in rows(roll):
  p=x.get('payload') or {};rl=p.get('rate_limits') if isinstance(p,dict) else None
  if not rl:continue
  candidates=rl if isinstance(rl,list) else [rl]
  if isinstance(rl,dict) and 'codex' in rl:candidates.append(dict(rl['codex'],limit_id='codex'))
  for candidate in candidates:
   if candidate.get('limit_id')!='codex':continue
   for bucket in ('primary','secondary'):
    b=candidate.get(bucket) or {}
    if b.get('window_minutes')==10080:result=float(b['used_percent'])
 assert result is not None,'no verified codex 10080-minute bucket'
 return result

def probe(folder,label):
 rd=folder/(label+'.workspace');rd.mkdir()
 info=cli(rd,'Reply with the single word ok.\n',folder,label,effort='low',probe=True);info['weekly_used_percent']=weekly(info['rollout']);dump(folder/(label+'.json'),info);return info

def scanner(folder):
 info=canonical_binding();expected=info['expected']
 if (A/'scanner_binding.json').exists():
  pinned=load(A/'scanner_binding.json')
  assert info==pinned,'canonical binding changed since build; build fresh contexts'
 dump(folder/'scanner_binding.json',info)
 target=folder/'scanner';target.mkdir()
 for name in ('scan_rollout.py','common.py','replay_literal.py'):shutil.copyfile(SR/'tools'/name,target/name)
 assert {p.name:sha(p) for p in target.iterdir()}==info['dependencies'],'scanner copy/dependency drift'
 assert canonical_binding()==info,'canonical source changed during copy'
 dump(folder/'scanner_binding.json',info)
 return target/'scan_rollout.py'

def input_binding():
 b=load(A/'build_receipt.json')
 for path,digest in b['inputs'].items():
  if Path(path)!=SR/'HANDOVER.md':assert sha(path)==digest,'build input changed: '+path
 for track,source in [('accent',SR/'prompts/grave.md'),('capital',CQ/'cq1/prompts/cap1.md')]:assert (A/'prompts'/f'{track}.md').read_bytes()==source.read_bytes(),'prompt drift'

def all_contexts():
 contexts=load(A/'contexts.json')+(load(A/'reread_contexts.json') if (A/'reread_contexts.json').exists() else [])
 archive=A/'au1d/previous_reread_contexts.json'
 if archive.exists():
  names={c['name'] for c in contexts}
  contexts += [c for c in load(archive) if c['name'] not in names]
 return contexts

def reader_prompt(c):
 base=A/'prompts'/f'{c["track"]}.md'
 if 'prompt' not in c:return base.read_text()
 prompt=Path(c['prompt']);assert sha(prompt)==c['prompt_sha256'],'context prompt drift'
 wrapper=(A/'prompts/path_addendum.md').read_bytes()+b'\ndo not iterate over image paths in code; call the view tool once per image, with the literal path\n'
 assert prompt.read_bytes()==base.read_bytes()+wrapper,'context protocol/addendum drift'
 return prompt.read_text()
def run(phase,only=None):
 input_binding()
 failed=False
 for c in all_contexts():
  if c['phase']!=phase or only and c['name']!=only:continue
  folder=A/'runs'/c['name'];assert not folder.exists(),f'Existing attempt: {folder}; preserve it and build a fresh context instead.';folder.mkdir(parents=True)
  rec=dict(context=c['name'],status='BLOCKED',started=datetime.datetime.now().isoformat());read_started=False
  try:
   integrity(c);assert not (Path(c['reader_dir'])/'answers.jsonl').exists(),'answers already present'
   prompt=reader_prompt(c);rec['prompt_sha256']=hashlib.sha256(prompt.encode()).hexdigest()
   scan=scanner(folder) # bind before spending any reader budget
   before=probe(folder,'before');rec['before']=before
   assert before['weekly_used_percent']<78,'weekly used >=78%; refuse to start'
   read_started=True
   runinfo=cli(c['reader_dir'],prompt,folder,'read');rec['read']=runinfo
   with (folder/'scan.json').open('w') as f:sc=subprocess.run([sys.executable,'-B',str(scan),runinfo['rollout'],c['reader_dir']],stdout=f,stderr=subprocess.STDOUT)
   rec['scan_sha256']=sha(folder/'scan.json');assert sc.returncode==0 and load(folder/'scan.json')['ok'],'canonical scanner VOID'
   integrity(c);answer=Path(c['reader_dir'])/'answers.jsonl';decoded,gate=validate(c,answer);rec['controls']=gate;dump(folder/'controls.json',gate)
   assert gate['passed'],'controls gate >1 errors'
   shutil.copyfile(answer,folder/'answers.jsonl');rec['answers_sha256']=sha(folder/'answers.jsonl');rec['status']='VALID'
  except Exception as e:
   rec.update(status='VOID' if read_started else 'BLOCKED',error=str(e));failed=True
  finally:
   if read_started:
    try:
     rec['after']=probe(folder,'after')
     if rec['after']['weekly_used_percent']>=80:rec['stop_weekly']=True
    except Exception as e:rec.update(status='VOID',post_probe_error=str(e));failed=True
   dump(folder/'receipt.json',rec)
  print(json.dumps(rec,ensure_ascii=False),flush=True)
  if rec.get('stop_weekly') or rec.get('after',{}).get('weekly_used_percent',0)>=78 or rec['status']=='BLOCKED':break
 return int(failed)

def observations():
 out={};receipts=[]
 rescans=load(A/'au1c/rescan_receipts.json') if (A/'au1c/rescan_receipts.json').exists() else {}
 for c in all_contexts():
  folder=A/'runs'/c['name'];p=folder/'receipt.json'
  if not p.exists():continue
  rec=load(p)
  if c['name'] in rescans:
   replacement=rescans[c['name']]
   assert sha(p)==replacement['original_receipt_sha256'],'original receipt drift'
   assert replacement['scanner_binding']==load(A/'scanner_binding.json'),'rescan binding drift'
   assert sha(replacement['read']['rollout'])==replacement['read']['rollout_sha256'],'rollout drift'
   assert sha(replacement['scan_path'])==replacement['scan_sha256'],'rescan drift'
   rec=replacement
  receipts.append(rec)
  if rec['status']!='VALID':continue
  answer=Path(rec.get('answers_path',folder/'answers.jsonl'));scan=Path(rec.get('scan_path',folder/'scan.json'))
  assert sha(answer)==rec['answers_sha256'] and sha(scan)==rec['scan_sha256']
  assert load(scan)['ok'];integrity(c);answers,gate=validate(c,answer);assert gate['passed']
  key=load(c['key'])
  for ident,a in answers.items():
   m=key[ident]
   if not m['control']:
    for h in m['heads']:out.setdefault(h,{})[c['phase']]=dict(a,context=c['name'],item_id=ident)
 return out,receipts

def trigger(track,first,released=None):
 if track=='capital':return 'unreadable' in (first['breathing'],first['accent']) or first['breathing']!='none' and first['accent']=='none'
 return first['accent']=='unreadable' or first['accent']!=released or first['confidence']=='low'

def reread():
 input_binding()
 if (A/'reread_contexts.json').exists():
  contexts=load(A/'reread_contexts.json')
  for c in contexts:integrity(c);reader_prompt(c)
  assert canonical_binding()==load(A/'scanner_binding.json'),'canonical binding drift'
  print(json.dumps({'reread_contexts':len(contexts),'status':'already built; reuse selected contexts'}));return
 obs,_=observations();assert obs,'No valid initial readings; no re-read packs built'
 heads={h['head_id']:h for h in load(A/'routing.json')['heads']};groups={'accent':{},'capital':{}}
 for c in load(A/'contexts.json'):
  for ident,m in load(c['key']).items():
   if m['control']:continue
   first=obs.get(m['heads'][0],{}).get('initial')
   if first and trigger(c['track'],first,heads[m['heads'][0]]['released_label']):groups[c['track']][(m['line_id'],m['slot'])]=m
 contexts=[]
 for track,group in groups.items():
  entries=list(group.values());random.Random(f'{SEED}:fresh:reread:{track}').shuffle(entries)
  for start in range(0,len(entries),90):contexts.append(write_context(f'{track}_reread_{start//90+1:03d}',track,entries[start:start+90],load(A/'keys'/f'{track}_control_pool.json'),'reread'))
 dump(A/'reread_contexts.json',contexts);print(json.dumps({'reread_contexts':len(contexts),'targets':{t:len(v) for t,v in groups.items()}}))

def score():
 routing=load(A/'routing.json');obs,receipts=observations();lead=load(A/'lead_review.json') if (A/'lead_review.json').exists() else {};result=[];queue=[]
 for h in routing['heads']:
  r=dict(h);r['status']='PENDING' if h['route']=='Opus-later' else 'UNREAD';o=obs.get(h['head_id'],{});first=o.get('initial');second=o.get('reread')
  if first:
   value=first[h['head']];r.update(initial=first,reading=value,released_right_initial=None if value=='unreadable' else value==h['released_label'])
   needs=trigger('capital' if h['route']=='Sol-capital' else 'accent',first,h['released_label'])
   status='SCORED' if value!='unreadable' else 'NEEDS_LEAD'
   if needs:
    r['reread']=second
    if not second:status='NEEDS_REREAD'
    elif h['route']=='Sol-accent':status='NEEDS_LEAD' # every accent flag requires a human eye
    elif any(first[x]!=second[x] for x in ('breathing','accent')) or any(second[x]=='unreadable' for x in ('breathing','accent')):status='NEEDS_LEAD'
   review=lead.get(h['head_id'])
   if review:
    assert review.get('verified') is True and review.get('reviewer') and review.get('note'),'invalid lead adjudication'
    allowed=('none','smooth','rough') if h['head']=='breathing' else ('none','acute','grave','circumflex');assert review['reading'] in allowed
    value=review['reading'];status='SCORED';r['lead_review']=review
   r.update(status=status,reading=value,released_right=value==h['released_label'] if status=='SCORED' else None)
   if status!='SCORED':queue.append(r)
  result.append(r)
 byid={r['head_id']:r for r in result};lines=[]
 for f in routing['lines']:
  hs=[byid[i] for i in f['heads']];sol=[h for h in hs if h['route']!='Opus-later'];opus=[h for h in hs if h['route']=='Opus-later'];complete=bool(sol) and all(h['status']=='SCORED' for h in sol)
  right=all(h['released_right'] for h in sol) if complete else None
  lines.append(dict(audit_id=f['audit_id'],line_id=f['line_id'],doc=f['doc'],sol_heads=len(sol),opus_pending_heads=len(opus),sol_scored=complete,sol_correct=right,status='PENDING' if opus else 'UNRESOLVED' if not complete else 'CORRECT' if right else 'INCORRECT'))
 eligible=[l for l in lines if not l['opus_pending_heads']];scored=[l for l in eligible if l['sol_scored']];sol_scored=[l for l in lines if l['sol_scored']]
 summary=dict(frame_lines=100,opus_pending_lines=sum(bool(l['opus_pending_heads']) for l in lines),sol_eligible_lines=len(eligible),sol_eligible_scored_lines=len(scored),sol_eligible_unresolved_lines=len(eligible)-len(scored),partial_line_precision={'correct':sum(l['sol_correct'] for l in scored),'denominator':len(scored),'value':sum(l['sol_correct'] for l in scored)/len(scored) if scored else None},all_sol_scored_lines=len(sol_scored),pending_lines_never_imputed=True,full_audit_pass=None,head_counts=routing['counts'])
 # Cluster bootstrap is descriptive on the resolved, Sol-only subset; never a full audit CI.
 if scored:
  docs=sorted({l['doc'] for l in scored});rng=random.Random(SEED);rates=[]
  for _ in range(10000):
   sample=[l for doc in rng.choices(docs,k=len(docs)) for l in scored if l['doc']==doc];rates.append(sum(l['sol_correct'] for l in sample)/len(sample))
  rates.sort();summary['partial_cluster_bootstrap_95']=[rates[249],rates[9749]]
 dump(A/'score.json',dict(summary=summary,heads=result,lines=lines,contexts=receipts));jsonl(A/'lead_queue.jsonl',queue)
 write_report(summary,receipts)
 print(json.dumps(summary,ensure_ascii=False))

def resume_rereads():
 """Run staged initial retries, then their triggered rereads and staged rereads."""
 reread()
 selected=load(A/'reread_contexts.json')
 def execute(c):
  path=A/'runs'/c['name']/'receipt.json'
  if not path.exists() and run(c['phase'],c['name']):return False
  rec=load(path)
  return rec['status']=='VALID' and not rec.get('stop_weekly') and rec.get('after',{}).get('weekly_used_percent',100)<78
 for c in selected:
  if c['phase']=='initial' and not execute(c):return 1
 obs,_=observations();heads={h['head_id']:h for h in load(A/'routing.json')['heads']}
 covered={h for c in selected if c['phase']=='reread' for m in load(c['key']).values() for h in m['heads']}
 for c in list(selected):
  if c['phase']!='initial':continue
  entries=[]
  for m in load(c['key']).values():
   if m['control'] or any(h in covered for h in m['heads']):continue
   first=obs.get(m['heads'][0],{}).get('initial')
   if first and trigger(c['track'],first,heads[m['heads'][0]]['released_label']):entries.append(m)
  if entries:
   name=c['name'].replace('_initial_','_reread_')
   fresh=write_context(name,c['track'],entries,load(A/'keys'/f'{c["track"]}_control_pool.json'),'reread')
   if 'prompt' in c:fresh.update(prompt=c['prompt'],prompt_sha256=c['prompt_sha256'])
   selected.append(fresh)
   dump(A/'reread_contexts.json',selected)
 for c in selected:
  if c['phase']=='reread' and not execute(c):return 1
 score();return 0

def write_report(s,receipts):
 b=load(A/'build_receipt.json');p=s['partial_line_precision'];pending=s['opus_pending_lines'];c=b['counts'];contexts=load(A/'contexts.json');meters=[r[k]['weekly_used_percent'] for r in receipts for k in ('before','after') if k in r]
 text=f'''# SF7 AU1 partial audit — build and lead-run results

Status: PARTIAL; {sum('read' in r for r in receipts)} reader contexts run. Release A, uniform 100-line frame, seed {SEED}. No full-audit result or pass is asserted. AU1C rescans, when present, supersede original scanner verdicts while preserving original receipts. Current bound scanner: {load(A/'scanner_binding.json')['version']}.

Routing covers all 107 released edits in all 100 frame lines. Sol lowercase accent: **{c['Sol-accent']} heads**; Sol capitals: **{c['Sol-capital']} heads** (3 breathing edits, no capital accent edits); Opus later: **{c['Opus-later']} heads** (21 lowercase breathing and 4 subscript; no dialytika). Each changed head has its own entry in `artifacts/sf7_rc1/audit/routing.json`; combined-letter edits stay separate. Capital cards ask both heads, but only changed heads count in the audit.

Initial packs: **{len(contexts)} contexts**, {sum(x['items'] for x in contexts)} bed cards plus {sum(x['controls'] for x in contexts)} verified controls. Each context is at most 90 bed cards + 10 controls. Opaque IDs, seed-shuffled order, clean RGB content-hash PNGs, full native line strips and 3× word zooms; the accent pass also has an 8× letter zoom. The grave prompt's required bare letters identify the target; no marked release or Google text is exposed. Capital option mappings are independently shuffled. Keys, source bindings and reports stay outside pack root.

Packs: `{PACK}`. Prompt files are byte-for-byte copies of HANDOVER grave.md and CQ1 cap1.md. Accent controls reuse lead-reviewed SR-G1 Lekythos/Kosmopolis pixels (all 58 SR-G1 items were lead-reviewed; NLG controls excluded); capital controls use only CQ4 verified=true entries. Saved recogniser slot spans and physical body/mark bounds locate bed targets; no inference was run during building. Full native height and horizontal overhang are retained. Control provenance and native hashes are in private keys. Build input hashes are in build_receipt.json.

Lead commands (from any cwd):

```bash
bash {A/'RUN.sh'}
bash {A/'REREAD.sh'}
bash {A/'SCORE.sh'}
```

RUN binds the canonical scanner from the live HANDOVER hash, copies exact bytes and records scanner/dependency hashes; a mismatch stops before probes/readers. Each reading uses gpt-6.1-sol, medium, network off, web disabled, apps/plugins/multi-agent disabled, project documents disabled, cwd confined to its pack. Sequence: weekly limit probe → read → canonical rollout scan → strict answer validation and controls gate (≤1 wrong control) → probe → receipt. It reads the codex 10080-minute bucket, refuses ≥78%, and stops at ≥80%. Failures after read start are recorded VOID and excluded. Original attempts cannot be overwritten. Live budget: {str(meters) if meters else 'NOT PROBED (build only)'}.

REREAD reuses staged fresh contexts after integrity and binding checks; if none exist it builds them. It runs any staged initial retry first, builds its triggered re-read if necessary, then runs the staged re-reads. Existing failed attempts are preserved and require fresh contexts. On capitals, every breathing-only answer (conservative trigger when preposed ink is not independently classified) and every unreadable tuple is re-read; agreement keeps the reading, disagreement or unreadable goes to the lead queue. Every lowercase accent mismatch, unreadable or low-confidence flag is re-read and still requires a human eye. `REREAD.sh --build-only` builds/checks without readers. Any missing/VOID context remains unresolved. For a human decision, supply `lead_review.json` keyed by head_id with `verified: true`, `reviewer`, `reading`, and `note`; SCORE validates it. Opus cards are listed only and are not built.

Current partial result: **{p['correct']}/{p['denominator']}** resolved Sol-only lines ({p['value'] if p['value'] is not None else 'precision unavailable'}). Sol-only eligible lines: {s['sol_eligible_lines']}; unresolved: {s['sol_eligible_unresolved_lines']}. **{pending} lines have Opus PENDING heads**, counted separately and never imputed. All-head line correctness requires every changed head; on a partial line, all Sol-scored heads must be correct, but Opus-pending heads prevent a full verdict. Per-head and per-line records, plus Sol-only subset correctness for mixed lines, are in score.json. A 10,000-draw document-cluster bootstrap is reported once the resolved Sol-only subset exists; this is descriptive and does not qualify the full audit. Final preregistered gate remains ≥83/100 plus the line-class constraint; both await the complete audit, including Opus.

Scanner at build: HANDOVER `{b['scanner_expected_at_build']}`, file `{b['scanner_actual_at_build']}`. {'MATCH' if b['scanner_expected_at_build']==b['scanner_actual_at_build'] else 'MISMATCH: canonical owner must align HANDOVER and scanner before RUN can proceed; no local fork or bypass is allowed.'}

Validation: pack closure, PNG hashes/metadata, no links, strict public fields, controls provenance, input coverage and prompt byte equality are checked by validate.py. Reader execution remains with the lead.
'''
 REPORT.write_text(text)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['build','run','reread','resume-rereads','score']);p.add_argument('--phase',default='initial',choices=['initial','reread']);p.add_argument('--context');p.add_argument('--fresh');args=p.parse_args()
 if args.action=='build':build(args.fresh)
 elif args.action=='run':sys.exit(run(args.phase,args.context))
 elif args.action=='reread':reread()
 elif args.action=='resume-rereads':sys.exit(resume_rereads())
 else:score()
