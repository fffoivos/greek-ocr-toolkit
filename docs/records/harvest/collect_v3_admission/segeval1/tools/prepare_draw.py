"""Metadata-only draw preparation. Never invokes a filter or opens an image."""
import gzip,hashlib,json,random,re,sys
from collections import Counter,defaultdict
from pathlib import Path
D=Path(__file__).resolve().parents[1]; ROOT=D.parents[3]; P=ROOT.parent
RX=re.compile(r'[A-Za-z0-9_:.%\-]+-l\d+')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
def jl(p,x):p.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in x))
assert not (D/'keys/sealed_decisions.jsonl').exists(),'Refuse redraw'
files=set()
seg=D.parent/'seg'
files.add(seg/'calibration_ledger.json')
files.update((seg/'cp7').glob('**/keys/draw.jsonl'))
files.update((seg/'cp7').glob('**/keys/segcp7*.json'))
files.update(seg.glob('*ids*'))
files.update((P/'collect-v3-data/run').glob('W*/c1/*key.json'))
w2=ROOT/'docs/harvest/recut_v1/w1_masked/w2c1'
files.update(p for p in (w2/'keys').glob('*.json') if p.name not in {'release_exclusions_at_start.json','crop_custody.json'})
files.update((w2/'pack_inventory').glob('**/*.cards.jsonl'))
cleanup=P/'greek-ocr-toolkit-cleanup'
files.update((cleanup/'artifacts/owner_sheets').glob('**/*.html'))
files.update((cleanup/'artifacts/owner_sheets').glob('**/*cardmap*.json'))
files.update((cleanup/'docs/owner_sheets').glob('**/*labelmap*.json'))
# Other owner segmentation review sheets and their labelmaps, if present.
for project in [ROOT,P/'greek-ocr-toolkit-sol-collect',P/'ocr-review-sites-20261018']:
 for base in [project/'artifacts',project/'docs/harvest/collect_v3']:
  if base.exists():
   files.update(p for p in base.rglob('*') if p.is_file() and p.suffix in ('.json','.jsonl','.html','.txt') and ('labelmap' in p.name or ('seg' in p.name.lower() and ('review' in p.name.lower() or 'ids' in p.name.lower()))))
excluded=set(); bindings=[]
for p in sorted(files):
 if not p.is_file():continue
 text=p.read_text()
 if 'labelmap' in p.name:
  obj=json.loads(text);text=json.dumps(obj.get('cardmap',obj))
 elif p.suffix in ('.json','.jsonl'):
  objects=[json.loads(l) for l in text.splitlines() if l.strip()] if p.suffix=='.jsonl' else [json.loads(text)]
  # Draw feature records contain IDs of neighbour detector rows too; only target
  # row/line identities belong to the reviewed-card exclusion.
  if p.name=='draw.jsonl':text=json.dumps([o.get('row_id',o.get('id')) for o in objects])
 ids=set(RX.findall(text));excluded.update(ids)
 bindings.append(dict(path=str(p),sha256=sha(p),row_ids=len(ids)))
dump(D/'keys/exclusion_sources.json',bindings)
(D/'keys/excluded_ids.txt').write_text(''.join(i+'\n' for i in sorted(excluded)))
# Frozen source feature metadata; no image measurement.
meta={};features=[]
for wave in ['W1','W2']:
 p=P/f'collect-v3-data/snapshots/{wave}_features_20261018_0524.jsonl'
 h=hashlib.sha256()
 with p.open('rb') as f:
  for line in f:
   h.update(line);r=json.loads(line);rid=r.get('row_id',r.get('id'))
   assert rid not in meta
   meta[rid]=(r,wave)
 features.append(dict(path=str(p),sha256=h.hexdigest()))
with gzip.open(D/'keys/original_metadata.jsonl.gz','rt') as f:
 for line in f:
  r=json.loads(line)
  if '_parent_receipt' in r:
   features.append(r['_parent_receipt']);continue
  rid=r['id'];assert rid not in meta
  r['primary_class']=r.get('primary_class',r['script_class'])
  meta[rid]=(r,r['wave'])
raw=[];policies=Counter();verdicts=Counter();not_run=0;unmatched=[]
with gzip.open(D/'keys/pipeline_population.jsonl.gz','rt') as f:
 for line in f:
  r=json.loads(line)
  if '_provenance' in r:provenance=r['_provenance'];continue
  if '_receipt' in r:receipt=r['_receipt'];continue
  if r.get('not_evaluated'):not_run+=1;continue
  s=r['segmentation']; assert s['tool_version']=='0.5'
  policies[s['policy_sha256']]+=1;verdicts[s['verdict']]+=1
  if r['row_id'] not in meta:unmatched.append(r['row_id']);continue
  m,wave=meta[r['row_id']]
  if 'crop_sha256' in m:assert r['crop_sha256']==m['crop_sha256']
  else:m['crop_sha256']=r['crop_sha256']
  r.update(source=m['source'],primary_class=m['primary_class'],wave=wave,google_text=m.get('old_label',m.get('text',m.get('label'))))
  raw.append(r)
assert not unmatched,unmatched[:10]
# KEEP passes segmentation. DROP rejects. UNCERTAIN remains a distinct unresolved cohort.
pools={v:sorted([r for r in raw if r['segmentation']['verdict']==v and r['row_id'] not in excluded],key=lambda r:r['row_id']) for v in ['DROP','KEEP','UNCERTAIN']}
rng=random.Random(20261019)
# Full random permutation locks replacement order as well as the initial sample.
orders={v:rng.sample(p,len(p)) for v,p in pools.items() if v in ['DROP','KEEP']}
for v,p in orders.items():jl(D/f'keys/candidate_order_{v}.jsonl',p)
selected=orders['DROP'][:50]+orders['KEEP'][:100]
for r in selected:r['decision']='REJECT' if r['segmentation']['verdict']=='DROP' else 'ACCEPT'
jl(D/'keys/sealed_decisions.jsonl',selected)
counts={v:dict(sorted(Counter(r['source']+'|'+r['primary_class'] for r in p).items())) for v,p in pools.items()}
dump(D/'draw_receipt.json',dict(seed=20261019,algorithm='CPython random.Random(seed); sorted row_id input; sample entire DROP pool then entire KEEP pool; first 50/100; remainder is replacement order',pool_sizes={v:len(p) for v,p in pools.items()},per_source_class=counts,exclusion_ids=len(excluded),excluded_matching=sum(r['row_id'] in excluded for r in raw),verdicts_before_exclusion=dict(verdicts),not_evaluated=not_run,policies=dict(policies),source=provenance,export_receipt=receipt,features=features,seal_sha256=sha(D/'keys/sealed_decisions.jsonl'),candidate_order_hashes={v:sha(D/f'keys/candidate_order_{v}.jsonl') for v in orders},reject_composition=dict(sorted(Counter(r['source']+'|'+r['segmentation']['reason'] for r in selected[:50]).items()))))
# Selected regeneration inputs, locked before invoking ensure_crop.
jl(D/'keys/selected_features.jsonl',[dict(meta[r['row_id']][0],row_id=r['row_id']) for r in selected])
print(json.dumps(json.loads((D/'draw_receipt.json').read_text()),indent=2,ensure_ascii=False))
