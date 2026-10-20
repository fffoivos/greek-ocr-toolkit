import sys
sys.path.insert(0,'artifacts/sf7_rc1/audit')
from driver import *
input_binding();obs,_=observations();heads={h['head_id']:h for h in load(A/'routing.json')['heads']};selected=[];targets={}
for c in load(A/'contexts.json'):
 entries=[];res=load(A/'au1c/rescan_receipts.json')[c['name']]
 for m in load(c['key']).values():
  if m['control']:continue
  first=obs.get(m['heads'][0],{}).get('initial')
  if res['status']=='VOID' or first and trigger(c['track'],first,heads[m['heads'][0]]['released_label']):entries.append(m)
 phase='initial' if res['status']=='VOID' else 'reread';name=f'{c["track"]}_{phase}_001_au1c'
 assert len(entries)==(4 if c['track']=='accent' else 3)
 selected.append(write_context(name,c['track'],entries,load(A/'keys'/f'{c["track"]}_control_pool.json'),phase))
 targets[name]=[h for m in entries for h in m['heads']]
dump(A/'reread_contexts.json',selected)
oldids={ident for p in (A/'keys').glob('*.json') if p.stem not in [c['name'] for c in selected] and isinstance(load(p),dict) for ident in load(p)}
newids=[i for c in selected for i in load(c['key'])];assert len(newids)==len(set(newids)) and not oldids.intersection(newids)
for c in selected:integrity(c);assert not (Path(c['reader_dir'])/'answers.jsonl').exists() and not (A/'runs'/c['name']).exists()
dump(A/'au1c/context_build_receipt.json',dict(contexts=selected,targets=targets,fresh_item_ids=newids,disjoint_from_prior=True,reader_runs=0,network=False,model='gpt-6.1-sol',effort='medium'))
routing=load(A/'routing.json');pending=[f for f in routing['lines'] if any(heads[h]['route']=='Opus-later' for h in f['heads'])];assert len(pending)==23
text='# Opus pending — awaiting owner go\n\n23 lines; 25 pending heads (21 lowercase breathing, 4 subscript). No Opus packs or reads launched. Pending heads are excluded from partial precision.\n\n| Audit ID | Line ID | Pending heads |\n|---|---|---|\n'
for f in pending:
 hs=[heads[h] for h in f['heads'] if heads[h]['route']=='Opus-later']
 text+='| '+f['audit_id']+' | `'+f['line_id']+'` | '+'; '.join('`'+h['head_id']+'` (slot '+str(h['slot'])+', '+h['head']+', released '+h['released_label']+')' for h in hs)+' |\n'
(A/'OPUS_PENDING.md').write_text(text)
print(json.dumps({'contexts':selected,'targets':targets},ensure_ascii=False))
