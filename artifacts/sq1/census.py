"""Read-only SF6 overlay census; stdin execution on Clariden, no imports of gate/model code."""
import pathlib,json,gzip,hashlib,unicodedata as u,re,time,collections,signal
signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('210 second budget')));signal.alarm(210)
start=time.monotonic();base=pathlib.Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017');run=base/'l1e_20261017/l1r_sf6_3680729'
selection=base/'artifacts/labelfix_l1/binding/selection.jsonl'
aliases='“”«»„"' + "'’´ʼ"; breathing='᾿᾽'; marks=set('\u0313\u0314\u0301\u0300\u0342'); rx=re.compile(r'"line_id"\s*:\s*"([^"\\]+)"')
def letters(t):
 out=[]
 for c in u.normalize('NFD',t):
  if u.category(c).startswith('M'):
   if out:out[-1][1]+=c
  elif c.isalpha() and c not in "'’ʼ᾽᾿":out.append([c,''])
 return out

def sites(t,chars):
 t=u.normalize('NFD',t);out=[];k=0
 for i,c in enumerate(t):
  if c in chars and i+1<len(t) and 'GREEK' in u.name(t[i+1],'') and t[i+1].isupper():out.append((k,c))
  if c.isalpha() and c not in "'’ʼ᾽᾿":k+=1
 return out
def spacing_sites(t):
 t=u.normalize('NFD',t);out=[];k=0
 for i,c in enumerate(t):
  if c in breathing and i+1<len(t) and (t[i+1] in 'ΑΕΗΙΟΥΩΡ' or t[i+1] in 'αεηιουω' and (i==0 or not t[i-1].isalpha())):out.append((k,c))
  if c.isalpha() and c not in "'’ʼ᾽᾿":k+=1
 return out
sel={}; candidates={};sp={}
with selection.open() as f:
 for line in f:
  r=json.loads(line);lid=r['id'];assert lid not in sel;sel[lid]=r
  a=sites(r['label'],aliases);b=spacing_sites(r['label'])
  if a:candidates[lid]=a
  if b:sp[lid]=b
receipt=json.loads((run/'receipt.json').read_text());assert receipt['complete'];assert receipt['policy']['schema']=='sf6-release-v1'
result=dict(schema='sq1-quote-breathing-census-v1',run=str(run),selection=str(selection),selection_sha256=hashlib.sha256(selection.read_bytes()).hexdigest(),receipt_sha256=hashlib.sha256((run/'receipt.json').read_bytes()).hexdigest(),policy=receipt['policy'],selected_lines=len(sel),candidate_lines=len(candidates),definition='Released labels only (corrected/unchanged); HOLD proposals counted separately. Site matches by Greek/other alphabetic-letter ordinal; exact base sequence required. Added marks are NFD psili/dasia/acute/grave/circumflex absent from Google capital. Counts are unique lines, site counts separate.',modes={})
for mode in ('presence','full','ensemble_ab'):
 p=run/'release'/f'overlay_{mode}.jsonl.gz'; counts=collections.Counter({k:0 for k in ('i_kept_lines','ii_removed_lines','i_kept_sites','ii_removed_sites','hold_candidate_sites','hold_candidate_lines','spacing_google_lines','spacing_google_sites','spacing_released_lines','spacing_attached_sites')});groups=collections.defaultdict(collections.Counter);seen=set();ex=[];held=[];target=None
 for a in aliases:groups['alias:'+a].update(i_kept_lines=0,ii_removed_lines=0,hold_lines=0)
 for r in sel.values():
  for group in ('wave:'+str(r.get('wave')),'source:'+str(r.get('source')),'wave_source:'+str(r.get('wave'))+'/'+str(r.get('source'))):groups[group].update(i_kept_lines=0,ii_removed_lines=0,hold_lines=0)
 with gzip.open(p,'rt') as f:
  for line in f:
   m=rx.search(line)
   if not m:raise ValueError('missing line_id')
   lid=m[1];assert lid in sel and lid not in seen;seen.add(lid)
   if lid not in candidates and lid not in sp:continue
   r=json.loads(line);s=sel[lid];g=letters(s['label']);status=r['status'];text=r.get('label') if status in ('corrected','unchanged') else r.get('composed_text');q=letters(text or '');same=[x[0] for x in g]==[x[0] for x in q]
   tags=set()
   for k,a in candidates.get(lid,[]):
    if not same or k>=len(q) or not (set(q[k][1])-set(g[k][1]))&marks:continue
    kept=(k,a) in sites(text,aliases);kind='i_kept' if kept else 'ii_removed'
    if status not in ('corrected','unchanged'):
     counts['hold_candidate_sites']+=1;tags.add('hold_candidate')
     for group in ('alias:'+a,'wave:'+str(s.get('wave')),'source:'+str(s.get('source')),'wave_source:'+str(s.get('wave'))+'/'+str(s.get('source'))):groups[group]['hold_lines_set:'+lid]=1
     if len(held)<10:held.append(dict(line_id=lid,status=status,kind=kind,alias=a,proposal=text,reasons=r.get('hold_slots')))
     continue
    counts[kind+'_sites']+=1;tags.add(kind);groups['alias:'+a][kind+'_sites']+=1
    for group in ('alias:'+a,'wave:'+str(s.get('wave')),'source:'+str(s.get('source')),'wave_source:'+str(s.get('wave'))+'/'+str(s.get('source'))):groups[group][kind+'_lines_set:'+lid]=1
    if kind=='i_kept' and len(ex)<10:ex.append(dict(line_id=lid,alias=a,wave=s.get('wave'),source=s.get('source'),google=s['label'],release=text))
    if kind=='ii_removed':
     leading=s['label'].lstrip('“”«»„" ').find(a)<0
     rule='leading-quote lstrip in _compose_reading' if leading and a in '“”«»„"' else 'other: inspect deletion_checks'
     counts['removed_rule:'+rule]+=1
   if sp.get(lid):
    counts['spacing_google_lines']+=1
    counts['spacing_google_sites']+=len(sp[lid])
    for group in ('wave:'+str(s.get('wave')),'source:'+str(s.get('source'))):groups[group]['spacing_google_lines']+=1
    if status in ('corrected','unchanged'):
     counts['spacing_released_lines']+=1
     counts['spacing_attached_sites']+=r.get('elision_census',{}).get('spacing_breathings_attached',0)
   for tag in tags:counts[tag+'_lines']+=1
 assert seen==set(sel),(len(seen),len(sel))
 finalgroups={}
 for group,c in groups.items():
  z=collections.Counter()
  for k,v in c.items():z[k.split('_set:')[0] if '_set:' in k else k]+=v
  finalgroups[group]=dict(z)
 result['modes'][mode]=dict(counts=dict(counts),groups=finalgroups,examples_i=ex,hold_examples=held,overlay=str(p),overlay_compressed_bytes=p.stat().st_size,lines=len(seen))
result['elapsed_seconds']=time.monotonic()-start
print(json.dumps(result,ensure_ascii=False,indent=2))
